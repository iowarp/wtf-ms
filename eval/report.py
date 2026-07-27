#!/usr/bin/env python3
"""
report -- render a step results file from run_eval into Markdown. Pure and
offline (reads a JSON results file only), so render() is unit-testable and this
never spends anything.

Usage:
  python3 eval/report.py eval/results/20260722T140312.json
  python3 eval/report.py eval/results/20260722T140312.json --out report.md
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import metrics  # noqa: E402

# Metrics worth showing for a step, with a formatter each.
_ROWS = (
    ("total_cost_usd", lambda v: f"${v:,.4f}"),
    ("cache_read_input_tokens", lambda v: f"{v:,.0f}"),
    ("cache_creation_input_tokens", lambda v: f"{v:,.0f}"),
    ("output_tokens", lambda v: f"{v:,.0f}"),
    ("num_turns", lambda v: f"{v:,.1f}"),
    ("duration_ms", lambda v: f"{v/1000:,.1f}s"),
    ("web_search_requests", lambda v: f"{v:,.0f}"),
)


def _cell(stat, fmt):
    if stat["n"] == 0:
        return "–"
    if stat["min"] == stat["max"]:
        return fmt(stat["mean"])
    return f"{fmt(stat['mean'])} [{fmt(stat['min'])}–{fmt(stat['max'])}]"


def render(record):
    """Return a Markdown report for a step results record."""
    agg = record.get("aggregate") or metrics.aggregate(
        [c["record"] for c in record.get("cells", [])])
    out = [f"# eval step: {record['step']}", ""]
    out.append(f"`{record.get('command', '')}` · model **{record['model']}** · "
               f"run `{record['run_id']}` · reps {record['reps']} · "
               f"session {record.get('session', 'fresh')}")
    out.append("")

    if agg["n_total"] == 0:
        out.append("_no reps recorded._")
        return "\n".join(out) + "\n"

    out += ["| metric | value |", "|---|---|"]
    out.append(f"| ok reps | {agg['n_ok']}/{agg['n_total']} |")
    for field, fmt in _ROWS:
        out.append(f"| {field} | {_cell(agg['metrics'][field], fmt)} |")
    if agg["error_kinds"]:
        ek = ", ".join(f"{k}×{v}" for k, v in agg["error_kinds"].items())
        out.append(f"| errors | {ek} |")
    out.append("")

    out += _model_lines(agg)
    out += _check_lines(record)
    return "\n".join(out) + "\n"


def _model_lines(agg):
    """Per-model cost split (where a subagent's model shows up)."""
    mu = agg.get("model_usage") or {}
    if len(mu) <= 1:
        return []
    parts = ", ".join(f"{model} ${s['cost_usd']['mean']:,.4f}" for model, s in mu.items())
    return ["**per-model cost**", f"- {parts}", ""]


def _check_lines(record):
    """One line per priced check: its cost increment over the step baseline."""
    checks = record.get("checks") or {}
    priced = {n: c for n, c in checks.items() if c.get("increment_usd") is not None}
    if not priced:
        return []
    lines = ["**checks** (cost each adds to the step)"]
    for name, c in priced.items():
        lines.append(f"- {name}: +${c['increment_usd']:,.4f}")
    return lines + [""]


def main():
    ap = argparse.ArgumentParser(description="Render an eval step results file to Markdown.")
    ap.add_argument("results")
    ap.add_argument("--out", help="write to this file instead of stdout")
    args = ap.parse_args()
    with open(args.results) as fh:
        record = json.load(fh)
    md = render(record)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(md)
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()
