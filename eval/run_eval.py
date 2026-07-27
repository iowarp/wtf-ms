#!/usr/bin/env python3
"""
run_eval -- the paid eval runner. Measures ONE research step (a wtf-MS command)
in isolation and records its cost/usage. The research process is a pipeline of
such steps -- a DAG, since question steps can loop back to identify-research --
so run each step to build a per-step cost profile. metrics.py does the parsing
and aggregation offline.

A step runs its command N reps from a fixed input (a committed `fixture` state,
or a live `seed` command run once, or nothing for the first step) and aggregates
the cost. There are no "arms": a step is one command, not a branch point.

Optional `checks` are the cheap guardrails a command already runs (e.g.
verify_citations on the literature review). They are part of the step's normal
cost. Pass --price-checks to price one: the step is re-run with the check
disabled, and the cost difference is reported as that check's increment.

Only this file spends money / touches the network, so it never runs in CI and
is plan-only unless you pass --live. Hardening vs the throwaway it replaces:
transient failures retried with backoff; a 429 aborts early; every cell
persisted for --resume-run; per-call and whole-run USD ceilings; original state
backed up and restored on exit (git can't restore untracked .research).

Step schema (see eval/steps/literature-review.json):
  name, description, model, reps
  state   : {reset: "backup", paths: [".research", ...]}
  session : "fresh" | "resume-fork"              # resume-fork carries a seed's context
  fixture : "eval/fixtures/state/<name>"         # frozen input, laid down before each rep
  seed    : {command, prompt, timeout, artifact} # OR a live upstream, run once
  measure : {command, prompt, timeout, artifact} # the command this step measures
  checks  : [{name, disable_suffix}]             # optional; priced with --price-checks
Use at most one of fixture / seed. resume-fork needs a seed.

Usage:
  python3 eval/run_eval.py eval/steps/literature-review.json                 # plan only
  python3 eval/run_eval.py eval/steps/literature-review.json --live
  python3 eval/run_eval.py eval/steps/literature-review.json --live --price-checks
  python3 eval/run_eval.py eval/steps/literature-review.json --live --resume-run <id>
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RESULTS_DIR = os.path.join(HERE, "results")
sys.path.insert(0, HERE)
import metrics  # noqa: E402  (sibling module, path set above)

BACKOFF_BASE = 5          # seconds; retry delay grows BACKOFF_BASE * 2**attempt
RETRYABLE = ("timeout", "non-json", "crash")   # transient; api-* are not


# ---- claude invocation ----------------------------------------------------

def run_claude(prompt, session_id, model, timeout, max_usd, resume=False, fork=False):
    """One headless claude turn. Returns (result_dict, raw_stdout). result_dict
    is a decoded claude result or a runner-failure marker {"_error": ...}."""
    cmd = ["claude", "-p", prompt, "--model", model,
           "--output-format", "json", "--max-budget-usd", str(max_usd),
           "--permission-mode", "bypassPermissions"]
    if resume:
        cmd += ["--resume", session_id] + (["--fork-session"] if fork else [])
    else:
        cmd += ["--session-id", session_id]
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"_error": "timeout"}, ""
    if p.returncode != 0 and not p.stdout.strip():
        return {"_error": "crash", "_rc": p.returncode}, p.stderr
    return metrics.parse_stdout(p.stdout), p.stdout


# ---- state snapshot / restore ---------------------------------------------

def _snap_dir(run_id):
    return os.path.join(RESULTS_DIR, run_id + "_seed")   # post-seed, per-rep reset


def _orig_dir(run_id):
    return os.path.join(RESULTS_DIR, run_id + "_orig")   # user's pre-run state, restored on exit


def snapshot_state(paths, dst):
    """Freeze the state paths into dst/<basename> for later restore."""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for rel in paths:
        src = os.path.join(REPO, rel)
        if os.path.exists(src):
            shutil.copytree(src, os.path.join(dst, os.path.basename(rel)))


def restore_state(paths, src):
    """Reset the state paths back to a snapshot (or clear them if src is None)."""
    for rel in paths:
        live = os.path.join(REPO, rel)
        if os.path.exists(live):
            shutil.rmtree(live)
        if src:
            frozen = os.path.join(src, os.path.basename(rel))
            if os.path.exists(frozen):
                shutil.copytree(frozen, live)


def artifact_bytes(rel):
    """Size of the artifact the command should have written; None if the step
    declares none, 0 if declared but absent."""
    if not rel:
        return None
    p = os.path.join(REPO, rel)
    return os.path.getsize(p) if os.path.exists(p) else 0


# ---- measuring one rep ----------------------------------------------------

def compose_prompt(base, suffix):
    """Base prompt plus an optional appended suffix (e.g. a check's disable text)."""
    return f"{base}\n\n{suffix}" if suffix else base


def run_rep(prompt, session, seed_session, model, timeout, max_usd, retries):
    """Run the measure command once with retry-on-transient. Returns
    (record, raw_stdout, attempts)."""
    res, raw, attempt = {"_error": "crash"}, "", 0
    for attempt in range(1, retries + 2):
        if session == "resume-fork":
            res, raw = run_claude(prompt, seed_session, model, timeout, max_usd,
                                  resume=True, fork=True)
        else:  # fresh session; new id each attempt
            res, raw = run_claude(prompt, str(uuid.uuid4()), model, timeout, max_usd)
        if metrics.classify(res) not in RETRYABLE:
            break
        if attempt <= retries:
            time.sleep(BACKOFF_BASE * 2 ** (attempt - 1))
    return res, raw, attempt


# ---- step loading / validation --------------------------------------------

def load_step(path):
    with open(path) as fh:
        return json.load(fh)


def validate(step):
    """Fail fast on the step shapes the runner relies on."""
    for key in ("name", "measure", "state"):
        if key not in step:
            sys.exit(f"step missing required key: {key!r}")
    if step["state"].get("reset") != "backup":
        sys.exit("only state.reset == 'backup' is supported (git can't restore "
                 "untracked runtime state like .research)")
    if not step["state"].get("paths"):
        sys.exit("state.paths must list at least one path to reset")
    if step.get("fixture") and step.get("seed"):
        sys.exit("step has both 'seed' and 'fixture'; use at most one input source")
    if step.get("session") == "resume-fork" and not step.get("seed"):
        sys.exit("session 'resume-fork' needs a 'seed' block to fork from")
    for chk in step.get("checks", []):
        if not chk.get("name") or not chk.get("disable_suffix"):
            sys.exit("each check needs a 'name' and a 'disable_suffix'")


def print_plan(step, model, reps, max_usd, max_total, price_checks):
    if step.get("seed"):
        source = f"seed {step['seed']['command']}"
    elif step.get("fixture"):
        source = f"fixture {step['fixture']}"
    else:
        source = "none (starts empty)"
    checks = step.get("checks", [])
    seed_calls = 1 if step.get("seed") else 0
    check_calls = reps * len(checks) if price_checks else 0
    calls = seed_calls + reps + check_calls
    print(f"step       : {step['name']}")
    print(f"model      : {model}    reps: {reps}    session: {step.get('session', 'fresh')}")
    print(f"input      : {source}")
    print(f"measure    : {step['measure']['command']} -> {step['measure'].get('artifact')}")
    if checks:
        priced = "priced" if price_checks else "not priced (pass --price-checks)"
        print(f"checks     : {', '.join(c['name'] for c in checks)}  [{priced}]")
    seedtxt = "1 seed + " if seed_calls else ""
    checktxt = f" + {check_calls} check" if check_calls else ""
    print(f"claude calls: {calls}  ({seedtxt}{reps} reps{checktxt})")
    print(f"caps       : ${max_usd}/call, ${max_total} total")


# ---- run ------------------------------------------------------------------

def spent_so_far(record):
    cells = list(record["cells"])
    for c in record.get("checks", {}).values():
        cells += c["cells"]
    return sum(c["record"].get("total_cost_usd", 0) or 0 for c in cells)


def main():
    ap = argparse.ArgumentParser(description="Measure one wtf-MS research step's cost.")
    ap.add_argument("step")
    ap.add_argument("--model")
    ap.add_argument("--reps", type=int)
    ap.add_argument("--max-usd", default="8.00", help="per-call USD cap")
    ap.add_argument("--max-total-usd", type=float, default=60.0,
                    help="abort once cumulative cost exceeds this")
    ap.add_argument("--retries", type=int, default=2,
                    help="retries per rep on transient failure")
    ap.add_argument("--price-checks", action="store_true",
                    help="also re-run the step with each check disabled, for its increment")
    ap.add_argument("--save-fixture", metavar="NAME",
                    help="after the baseline reps, snapshot the output state into "
                         "eval/fixtures/state/NAME (to seed the next step)")
    ap.add_argument("--resume-run", help="run_id to continue (skips done reps)")
    ap.add_argument("--no-stop-on-quota", action="store_true",
                    help="keep going after a 429 instead of aborting")
    ap.add_argument("--live", action="store_true",
                    help="actually spend money; without it, only the plan prints")
    args = ap.parse_args()

    step = load_step(args.step)
    validate(step)
    model = args.model or step.get("model", "opus")
    reps = args.reps or step.get("reps", 3)
    session = step.get("session", "fresh")
    paths = step["state"]["paths"]
    checks = step.get("checks", []) if args.price_checks else []

    if not args.live:
        print_plan(step, model, reps, args.max_usd, args.max_total_usd, args.price_checks)
        print("\n(plan only -- no money spent. re-run with --live to execute.)")
        return

    if not shutil.which("claude"):
        sys.exit("`claude` CLI not found on PATH -- install it to run a paid eval "
                 "(omit --live to validate the step without it).")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    if args.resume_run:
        run_id = args.resume_run
        results_path = os.path.join(RESULTS_DIR, run_id + ".json")
        if not os.path.exists(results_path):
            sys.exit(f"no results file for run {run_id}")
        record = load_step(results_path)
        if step.get("seed") and not os.path.isdir(_snap_dir(run_id)):
            sys.exit(f"seed snapshot for {run_id} is gone; cannot resume")
        seed_session = record.get("seed_session")
        print(f"== resuming {run_id} ==")
    else:
        run_id = datetime.now().strftime("%Y%m%dT%H%M%S")
        results_path = os.path.join(RESULTS_DIR, run_id + ".json")
        record = {"run_id": run_id, "step": step["name"], "command": step["measure"]["command"],
                  "model": model, "reps": reps, "session": session,
                  "seed_session": None, "seed": None, "cells": [],
                  "checks": {c["name"]: {"disable_suffix": c["disable_suffix"], "cells": []}
                             for c in checks}}
        seed_session = None

    orig_dir = _orig_dir(run_id)
    if not args.resume_run:
        snapshot_state(paths, orig_dir)   # back up the user's real state first
    raw_dir = os.path.join(RESULTS_DIR, run_id + "_raw")
    os.makedirs(raw_dir, exist_ok=True)

    def flush():
        with open(results_path, "w") as fh:
            json.dump(record, fh, indent=2)

    measure = step["measure"]
    base_prompt = measure["prompt"]
    art = measure.get("artifact")

    def do_rep(prompt, tag):
        """Run one measure rep, persist raw, return its record."""
        restore_state(paths, snap_source)       # reset input (clears when snap_source is None)
        res, raw, attempts = run_rep(prompt, session, seed_session, model,
                                     measure["timeout"], args.max_usd, args.retries)
        with open(os.path.join(raw_dir, tag + ".stdout"), "w") as fh:
            fh.write(raw)
        rec = metrics.parse_result(res, artifact_bytes=artifact_bytes(art))
        print(f"      {rec['error_kind']}  cost=${rec['total_cost_usd']:.4f}  "
              f"out={rec['output_tokens']}  turns={rec['num_turns']}")
        return rec, attempts

    try:
        # ---- seed once (live upstream), or point at the fixture ----
        if step.get("seed") and not seed_session:
            print("== seed:", step["seed"]["command"], "==")
            restore_state(paths, None)          # clear for a genuine first-time init
            seed_session = str(uuid.uuid4())
            sres, sraw = run_claude(step["seed"]["prompt"], seed_session, model,
                                    step["seed"]["timeout"], args.max_usd)
            with open(os.path.join(raw_dir, "seed.stdout"), "w") as fh:
                fh.write(sraw)
            record["seed_session"] = seed_session
            record["seed"] = metrics.parse_result(
                sres, artifact_bytes=artifact_bytes(step["seed"].get("artifact")))
            flush()
            if not record["seed"]["ok"]:
                print(f"!! seed failed ({record['seed']['error_kind']}); aborting")
                return
            snapshot_state(paths, _snap_dir(run_id))

        if step.get("seed"):
            snap_source = _snap_dir(run_id)
        elif step.get("fixture"):
            snap_source = os.path.join(REPO, step["fixture"])
            if not os.path.isdir(snap_source):
                sys.exit(f"fixture dir not found: {step['fixture']}")
        else:
            snap_source = None                  # seedless: each rep starts from empty state

        done = {c["tag"] for c in record["cells"] if c["record"]["ok"]}
        for name, c in record.get("checks", {}).items():
            done |= {cc["tag"] for cc in c["cells"] if cc["record"]["ok"]}

        # ---- baseline reps (the step's normal cost, checks included) ----
        for rep in range(1, reps + 1):
            tag = f"r{rep}"
            if tag in done:
                continue
            if spent_so_far(record) >= args.max_total_usd:
                print(f"!! run budget ${args.max_total_usd} reached; stopping")
                return
            print(f"  [{tag}] {session} ...", flush=True)
            rec, attempts = do_rep(base_prompt, tag)
            record["cells"] = [c for c in record["cells"] if c["tag"] != tag]
            record["cells"].append({"tag": tag, "rep": rep, "attempts": attempts, "record": rec})
            flush()
            if rec["error_kind"] == "api-429" and not args.no_stop_on_quota:
                print(f"!! 429 -- aborting (resume with --resume-run {run_id})")
                return

        # ---- optionally freeze the output as the next step's fixture ----
        # Done here (before check-pricing overwrites .research with a
        # check-disabled output) so the fixture is the canonical step output.
        if args.save_fixture and any(c["record"]["ok"] for c in record["cells"]):
            dst = os.path.join(REPO, "eval", "fixtures", "state", args.save_fixture)
            snapshot_state(paths, dst)
            print(f"  saved fixture -> eval/fixtures/state/{args.save_fixture}")

        # ---- optionally price each check (re-run with it disabled) ----
        for chk in checks:
            name = chk["name"]
            for rep in range(1, reps + 1):
                tag = f"{name}:r{rep}"
                if tag in done:
                    continue
                if spent_so_far(record) >= args.max_total_usd:
                    print(f"!! run budget ${args.max_total_usd} reached; stopping")
                    return
                print(f"  [{tag}] {session} (check disabled) ...", flush=True)
                rec, attempts = do_rep(compose_prompt(base_prompt, chk["disable_suffix"]), tag)
                cells = record["checks"][name]["cells"]
                record["checks"][name]["cells"] = [c for c in cells if c["tag"] != tag]
                record["checks"][name]["cells"].append(
                    {"tag": tag, "rep": rep, "attempts": attempts, "record": rec})
                flush()
                if rec["error_kind"] == "api-429" and not args.no_stop_on_quota:
                    print(f"!! 429 -- aborting (resume with --resume-run {run_id})")
                    return
    finally:
        _finalize(record)
        flush()
        print("== restoring original state from pre-run backup ==")
        restore_state(paths, orig_dir)
        _summary(record)
        print(f"\nresults -> {results_path}")


def _finalize(record):
    """Compute the step aggregate + each check's cost increment."""
    record["aggregate"] = metrics.aggregate([c["record"] for c in record["cells"]])
    base_cost = record["aggregate"]["metrics"]["total_cost_usd"]
    for name, c in record.get("checks", {}).items():
        c["aggregate"] = metrics.aggregate([cc["record"] for cc in c["cells"]])
        off_cost = c["aggregate"]["metrics"]["total_cost_usd"]
        # increment = cost with the check (baseline) - cost without it.
        c["increment_usd"] = (base_cost["mean"] - off_cost["mean"]
                              if base_cost["n"] and off_cost["n"] else None)


def _summary(record):
    agg = record.get("aggregate", {})
    cost = agg.get("metrics", {}).get("total_cost_usd", {"mean": 0, "min": 0, "max": 0, "n": 0})
    print("\n" + "=" * 60)
    print(f"{record['step']}  (model={record['model']})")
    errs = f"  errors={agg.get('error_kinds')}" if agg.get("error_kinds") else ""
    print(f"  n_ok={agg.get('n_ok', 0)}/{agg.get('n_total', 0)}  "
          f"mean_cost=${cost['mean']:.4f} [{cost['min']:.4f}-{cost['max']:.4f}]{errs}")
    for name, c in record.get("checks", {}).items():
        inc = c.get("increment_usd")
        print(f"  check {name}: {'+$%.4f' % inc if inc is not None else 'n/a'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
