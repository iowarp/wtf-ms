#!/usr/bin/env python3
"""
baseline -- store a step's expected cost/usage, and compare later runs against
it so a change in cost is recorded and surfaced. This is observability, not a
gate: comparison always succeeds (exit 0) and simply reports what moved. The
band is a notability threshold for what's worth a human's attention, not a
pass/fail line.

Band: runs are non-deterministic, so a metric is compared as "new mean vs
baseline mean". A fixed percentage (default 20%, stored in the baseline file)
flags a move as notable -- three reps is too few for a sample stdev to trust,
and a plain percentage is legible and easy to widen for a jumpy metric.

compare()/build_baseline() are pure and offline -- unit-tested, no spend.

Usage:
  python3 eval/baseline.py eval/results/<run>.json --update    # (re)bless a baseline
  python3 eval/baseline.py eval/results/<run>.json             # report changes vs baseline
  python3 eval/baseline.py eval/results/<run>.json --all       # show every metric, not just notable
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINES = os.path.join(HERE, "baselines")
sys.path.insert(0, HERE)
import metrics  # noqa: E402

DEFAULT_BAND = 0.20


def _aggregate(record):
    """The step's aggregate, recomputed from cells so an edited/older results
    file still compares correctly."""
    return metrics.aggregate([c["record"] for c in record.get("cells", [])])


def build_baseline(record, band=DEFAULT_BAND):
    """Freeze the step's mean + rep count for every numeric metric (and any
    priced check increments)."""
    agg = _aggregate(record)
    metric_means = {f: {"mean": agg["metrics"][f]["mean"], "n": agg["metrics"][f]["n"]}
                    for f in metrics.NUMERIC_FIELDS}
    checks = {name: {"increment_usd": c.get("increment_usd")}
              for name, c in (record.get("checks") or {}).items()
              if c.get("increment_usd") is not None}
    return {"step": record["step"], "model": record["model"], "band": band,
            "metrics": metric_means, "checks": checks}


def compare(baseline, record):
    """Compare a results record to a baseline. Returns a finding per metric::

        {metric, base_mean, new_mean, pct, within_band, has_data}

    pct is (new-base)/base; within_band is |pct| <= band; has_data is False when
    the new run produced no OK reps for that metric.
    """
    band = baseline.get("band", DEFAULT_BAND)
    agg = _aggregate(record)
    findings = []
    for field, base in baseline["metrics"].items():
        ns = agg["metrics"].get(field, {"n": 0, "mean": 0.0})
        has_data = ns["n"] > 0
        bm = base["mean"]
        if not has_data:
            pct, within = None, False
        elif bm == 0:
            pct, within = None, True   # no magnitude to compare; not a notable move
        else:
            pct = (ns["mean"] - bm) / bm
            within = abs(pct) <= band
        findings.append({"metric": field, "base_mean": bm, "new_mean": ns["mean"],
                         "pct": pct, "within_band": within, "has_data": has_data})
    return findings


def notable(findings):
    """Findings worth surfacing: a metric that moved beyond the band (either
    direction) or has no data to compare. Informational -- not a failure."""
    return [f for f in findings if not f["has_data"] or not f["within_band"]]


# ---- CLI ------------------------------------------------------------------

def _baseline_path(step):
    return os.path.join(BASELINES, step + ".json")


def _fmt_pct(f):
    if not f["has_data"]:
        return "NO DATA"
    if f["pct"] is None:
        return "—"
    return f"{f['pct'] * 100:+.1f}%"


def _fmt_val(field, v):
    return f"${v:,.4f}" if field == "total_cost_usd" else f"{v:,.0f}"


def main():
    ap = argparse.ArgumentParser(description="Store/compare a step's cost baseline.")
    ap.add_argument("results")
    ap.add_argument("--update", action="store_true",
                    help="write the results as the new baseline")
    ap.add_argument("--band", type=float, help="notability threshold (default 0.20)")
    ap.add_argument("--all", action="store_true",
                    help="show every metric, not just the notable moves")
    args = ap.parse_args()

    with open(args.results) as fh:
        record = json.load(fh)

    if args.update:
        os.makedirs(BASELINES, exist_ok=True)
        bl = build_baseline(record, args.band or DEFAULT_BAND)
        path = _baseline_path(record["step"])
        with open(path, "w") as fh:
            json.dump(bl, fh, indent=2)
        print(f"baseline written -> {path}  (band ±{bl['band']*100:.0f}%)")
        return

    path = _baseline_path(record["step"])
    if not os.path.exists(path):
        sys.exit(f"no baseline for step {record['step']!r}; create one with --update")
    with open(path) as fh:
        baseline = json.load(fh)
    if args.band is not None:
        baseline["band"] = args.band

    findings = compare(baseline, record)
    moved = notable(findings)
    shown = findings if args.all else moved

    print(f"change report: {record['step']} vs baseline  (band ±{baseline['band']*100:.0f}%)")
    for f in shown:
        mark = "" if f["within_band"] else "  <- beyond band"
        print(f"  {f['metric']:28} {_fmt_val(f['metric'], f['base_mean'])} -> "
              f"{_fmt_val(f['metric'], f['new_mean'])}   {_fmt_pct(f)}{mark}")
    if moved:
        print(f"\n{len(moved)} metric(s) moved beyond ±{baseline['band']*100:.0f}%. "
              "Recorded for review -- informational, not a failure.")
    else:
        print("\nall metrics within band.")
    # Always exit 0: this reports change, it does not gate on it.


if __name__ == "__main__":
    main()
