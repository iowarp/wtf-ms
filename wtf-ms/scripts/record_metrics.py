#!/usr/bin/env python3
"""
record_metrics — passively collect per-step token usage during normal wtf-MS
operation, from Claude Code Stop and SubagentStop hooks. Tokens are the primary
metric (exact); a dollar figure is a secondary estimate.

How it works
------------
On each hook fire this reads a transcript and, for every assistant message it
hasn't seen before (deduped by message uuid), appends one record to
.research/metrics.jsonl: the step, the model, and the four token axes. A later
`--report` sums those per step.

Two events feed it:
  * Stop -- an orchestrator turn ends. Its messages are charged to the most
    recent `/wtfMS:<step>` invoked in that transcript.
  * SubagentStop -- a subagent ends. The event hands over the subagent's
    own transcript (`agent_transcript_path`, full per-message usage) plus the
    parent transcript (`transcript_path`) that names the command; the
    subagent's usage is charged to that step. This is how generation-heavy work
    (e.g. execute-task's subagent) gets counted -- install BOTH hooks.

Messages in a transcript that never ran a wtf-MS command are skipped, so
unrelated Claude Code work never pollutes the numbers. With only the Stop hook,
the report is orchestrator-side and undercounts subagent-heavy steps.

Cost is an ESTIMATE from the per-model price table below (edit it when prices
change); it is computed at report time from the stored tokens, so re-pricing is
retroactive. Token counts are exact. Zero third-party deps.

Usage
-----
  (hook)   stdin = hook JSON {transcript_path, cwd, agent_transcript_path?}
  --report [--cwd DIR]      print the per-step token/cost table
"""
import argparse
import json
import os
import re
import sys

# Per-model price, USD per 1M tokens. ESTIMATES -- edit when prices change.
# Keyed by a model-family substring so version suffixes (-4-8, -5, dated) match.
PRICING = {
    "opus":   {"input": 15.0, "output": 75.0, "cache_read": 1.50, "cache_write": 18.75},
    "sonnet": {"input": 3.0,  "output": 15.0, "cache_read": 0.30, "cache_write": 3.75},
    "haiku":  {"input": 1.0,  "output": 5.0,  "cache_read": 0.10, "cache_write": 1.25},
}
DEFAULT_PRICE = {"input": 5.0, "output": 15.0, "cache_read": 0.50, "cache_write": 6.0}

METRICS_REL = os.path.join(".research", "metrics.jsonl")
# Match only the slash-command INVOCATION marker Claude Code writes
# (<command-name>/wtfMS:x</command-name> or <command-message>wtfMS:x</...>),
# NOT bare /wtfMS: references -- the expanded command body mentions other
# commands, and matching those mis-attributes the step.
STEP_RE = re.compile(r"<command-(?:name|message)>\s*/?wtfMS:([a-z][a-z0-9-]*)")
TOKEN_FIELDS = ("input", "output", "cache_read", "cache_write")


# ---- transcript parsing (pure) --------------------------------------------

def _text_of(content):
    """A user message's content is a string or a list of blocks; return its text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def collect(transcript_path):
    """Read a transcript JSONL. Returns the list of records for assistant
    messages that fall under a /wtfMS command in this transcript; messages
    before any command (step is None) are included so the caller can drop them."""
    records, step = [], None
    with open(transcript_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = o.get("type")
            if kind == "user":
                m = STEP_RE.search(_text_of(o.get("message", {}).get("content")))
                if m:
                    step = m.group(1)
            elif kind == "assistant":
                msg = o.get("message", {})
                u = msg.get("usage")
                if not u or not o.get("uuid"):
                    continue
                records.append({
                    "uuid": o.get("uuid"),
                    "ts": o.get("timestamp"),
                    "session": o.get("session_id") or o.get("sessionId"),
                    "step": step,
                    "model": msg.get("model"),
                    "input": u.get("input_tokens", 0) or 0,
                    "output": u.get("output_tokens", 0) or 0,
                    "cache_read": u.get("cache_read_input_tokens", 0) or 0,
                    "cache_write": u.get("cache_creation_input_tokens", 0) or 0,
                })
    return records


def new_records(seen_uuids, records):
    """Records not already recorded and attributable to a step (drops the
    stepless ones -- non-wtf-MS turns and subagent transcripts)."""
    return [r for r in records if r["step"] and r["uuid"] not in seen_uuids]


def active_step_in(transcript_path):
    """The last /wtfMS step invoked in a transcript, or None."""
    step = None
    try:
        with open(transcript_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if o.get("type") == "user":
                    m = STEP_RE.search(_text_of(o.get("message", {}).get("content")))
                    if m:
                        step = m.group(1)
    except OSError:
        return None
    return step


# ---- cost + reporting (pure) ----------------------------------------------

def price_for(model):
    m = (model or "").lower()
    for family, price in PRICING.items():
        if family in m:
            return price
    return DEFAULT_PRICE


def est_cost(record):
    p = price_for(record.get("model"))
    return sum(record.get(f, 0) * p[f] for f in TOKEN_FIELDS) / 1_000_000


def aggregate(records):
    """Per-step totals: token sums, message count, estimated cost, and how much
    of that cost is the step's subagent."""
    by_step = {}
    for r in records:
        s = by_step.setdefault(r["step"], {f: 0 for f in TOKEN_FIELDS})
        for f in TOKEN_FIELDS:
            s[f] += r.get(f, 0)
        s["msgs"] = s.get("msgs", 0) + 1
        c = est_cost(r)
        s["cost"] = s.get("cost", 0.0) + c
        if r.get("agent"):
            s["subagent_cost"] = s.get("subagent_cost", 0.0) + c
    return by_step


def report_text(records):
    if not records:
        return "No wtf-MS metrics recorded yet (.research/metrics.jsonl is empty)."
    agg = aggregate(records)
    order = sorted(agg, key=lambda s: agg[s]["cost"], reverse=True)
    head = (f"{'step':22} {'msgs':>5} {'input':>9} {'output':>9} "
            f"{'cache_rd':>12} {'cache_wr':>10}   {'~cost':>9}")
    lines = ["wtf-MS token usage by step  (tokens exact, cost estimated)",
             "", head, "-" * len(head)]
    tot = {f: 0 for f in TOKEN_FIELDS}
    tot_msgs, tot_cost, tot_sub = 0, 0.0, 0.0
    for s in order:
        a = agg[s]
        lines.append(f"{s:22} {a['msgs']:>5} {a['input']:>9,} {a['output']:>9,} "
                     f"{a['cache_read']:>12,} {a['cache_write']:>10,}   ${a['cost']:>8.4f}")
        for f in TOKEN_FIELDS:
            tot[f] += a[f]
        tot_msgs += a["msgs"]
        tot_cost += a["cost"]
        tot_sub += a.get("subagent_cost", 0.0)
    lines.append("-" * len(head))
    lines.append(f"{'TOTAL':22} {tot_msgs:>5} {tot['input']:>9,} {tot['output']:>9,} "
                 f"{tot['cache_read']:>12,} {tot['cache_write']:>10,}   ${tot_cost:>8.4f}")
    if tot_sub:
        lines += ["", "of which subagent (included above):"]
        for s in order:
            sc = agg[s].get("subagent_cost", 0.0)
            if sc:
                lines.append(f"  {s:22} ${sc:.4f}")
    else:
        lines += ["", "(no subagent usage recorded -- install the SubagentStop hook "
                  "to count it)"]
    return "\n".join(lines)


# ---- IO wrappers ----------------------------------------------------------

def _seen_uuids(metrics_path):
    seen = set()
    if os.path.exists(metrics_path):
        with open(metrics_path) as fh:
            for line in fh:
                try:
                    seen.add(json.loads(line)["uuid"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return seen


def _read_records(metrics_path):
    out = []
    if os.path.exists(metrics_path):
        with open(metrics_path) as fh:
            for line in fh:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def run_hook(cwd, payload):
    """Append new records for a Stop or SubagentStop event. Silent and never
    raises (a hook must not break the session)."""
    if not os.path.isdir(os.path.join(cwd, ".research")):
        return
    metrics_path = os.path.join(cwd, METRICS_REL)
    seen = _seen_uuids(metrics_path)
    parent_tp = payload.get("transcript_path")
    agent_tp = payload.get("agent_transcript_path")

    if agent_tp and os.path.exists(agent_tp):
        # SubagentStop: charge the subagent's own usage to the parent's step.
        step = active_step_in(parent_tp) if parent_tp and os.path.exists(parent_tp) else None
        if not step:
            return                      # subagent of a non-wtf-MS command
        agent = payload.get("agent_type") or "subagent"
        fresh = []
        for r in collect(agent_tp):
            if r["uuid"] in seen:
                continue
            r["step"], r["agent"] = step, agent
            fresh.append(r)
    else:
        # Stop: orchestrator messages from the parent transcript.
        if not parent_tp or not os.path.exists(parent_tp):
            return
        fresh = new_records(seen, collect(parent_tp))
        for r in fresh:
            r["agent"] = None

    if fresh:
        with open(metrics_path, "a") as fh:
            for r in fresh:
                fh.write(json.dumps(r) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Collect/report wtf-MS token metrics.")
    ap.add_argument("--report", action="store_true", help="print the per-step table")
    ap.add_argument("--cwd", default=os.getcwd(), help="project root (default: cwd)")
    args = ap.parse_args()

    if args.report:
        print(report_text(_read_records(os.path.join(args.cwd, METRICS_REL))))
        return

    # Hook mode: read the hook JSON from stdin. Swallow everything -- a hook
    # that errors or is slow must not disrupt the session.
    try:
        payload = json.load(sys.stdin)
        run_hook(payload.get("cwd") or args.cwd, payload)
    except Exception:
        pass


if __name__ == "__main__":
    main()
