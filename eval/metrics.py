#!/usr/bin/env python3
"""
Pure, deterministic parsing + aggregation of `claude -p --output-format json`
results. No network, no subprocess, no third-party deps -- this is the
CI-testable core of the eval harness. The paid runner (run_eval.py) shells out
to `claude` and hands the raw stdout here; everything numeric happens in this
module so it can be unit-tested offline against recorded fixtures.

Design notes:
  * A FAILED rep still carries misleading numbers: an api-429 result records a
    non-zero total_cost_usd and a large duration_api_ms while its usage axes
    are all zero. So every rep is classified first, and aggregate() computes
    numeric stats over OK reps ONLY.
  * We surface only hard-countable axes. No quality/prose scoring lives here --
    artifact_bytes is a completeness signal (did the command write its output
    file, and how big), not a judgment of that output.
  * stats() uses population stdev to match the throwaway harness. Whether a
    regression band should instead use sample stdev or a fixed percentage is a
    baseline.py concern, deferred to there.

Run the tests:  python3 eval/tests/test_metrics.py
"""
import json

# ---- normalized metric record ---------------------------------------------

# Countable axes lifted from the claude result. Order is display order.
NUMERIC_FIELDS = (
    "total_cost_usd",
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
    "num_turns",
    "duration_ms",
    "duration_api_ms",
    "web_search_requests",
    "web_fetch_requests",
)

# Every classify() outcome. "none" means the rep is usable; the rest are the
# ways a rep can be unusable (and excluded from numeric aggregates).
RESULT_KINDS = (
    "none",         # ok
    "timeout",      # runner killed the subprocess (subprocess.TimeoutExpired)
    "non-json",     # stdout was not parseable JSON
    "crash",        # runner-side / non-zero exit with no usable result
    "api-429",      # rate limit / session limit wall
    "budget",       # hit our --max-budget-usd cap mid-run (raise the cap, not an error)
    "api-other",    # any other API-reported error (is_error / api_error_status)
    "missing-artifact",  # run reported success but did not write its output file
)


def parse_stdout(text):
    """Decode `claude -p` stdout, or return {"_error": "non-json"} if it isn't
    a JSON object. Lives here so the decode path is unit-testable."""
    try:
        obj = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {"_error": "non-json"}
    return obj if isinstance(obj, dict) else {"_error": "non-json"}


def classify(result):
    """Map a raw result to one of RESULT_KINDS. `result` is either a decoded
    claude dict or a runner-failure marker {"_error": "timeout"|...}."""
    if not isinstance(result, dict):
        return "crash"
    marker = result.get("_error")
    if marker:
        return marker if marker in RESULT_KINDS else "crash"
    # We cut the run off at our own budget cap -- distinct from an API error.
    if (result.get("subtype") == "error_max_budget_usd"
            or result.get("terminal_reason") == "budget_exhausted"):
        return "budget"
    status = result.get("api_error_status")
    if status == 429:
        return "api-429"
    if status:
        return "api-other"
    if result.get("is_error"):
        return "api-other"
    return "none"


def parse_result(result, artifact_bytes=None):
    """Normalize one rep into a flat metric record.

    artifact_bytes: size of the file the measured command should have written,
    or None if the runner didn't check. 0 (expected but absent) turns an
    otherwise-clean run into "missing-artifact" -- but never masks a truer
    upstream error like api-429.

    Numeric fields are always present (0 when absent) so records aggregate
    uniformly; callers must gate on `ok`.
    """
    kind = classify(result)
    if kind == "none" and artifact_bytes == 0:
        kind = "missing-artifact"

    u = result.get("usage", {}) if isinstance(result, dict) else {}
    stu = u.get("server_tool_use", {}) if isinstance(u, dict) else {}
    return {
        "ok": kind == "none",
        "error_kind": kind,
        "artifact_bytes": artifact_bytes,
        "total_cost_usd": _num(result.get("total_cost_usd")),
        "input_tokens": _num(u.get("input_tokens")),
        "cache_creation_input_tokens": _num(u.get("cache_creation_input_tokens")),
        "cache_read_input_tokens": _num(u.get("cache_read_input_tokens")),
        "output_tokens": _num(u.get("output_tokens")),
        "num_turns": _num(result.get("num_turns")),
        "duration_ms": _num(result.get("duration_ms")),
        "duration_api_ms": _num(result.get("duration_api_ms")),
        "web_search_requests": _num(stu.get("web_search_requests")),
        "web_fetch_requests": _num(stu.get("web_fetch_requests")),
        # Per-model split. The top-level `usage` axes above are orchestrator-only;
        # a subagent on another model shows up here (and in total_cost_usd) but
        # not in `usage`, so this is where subagent tokens/cost surface.
        "model_usage": _model_usage(result),
    }


def _model_usage(result):
    """{model: {cost_usd, output_tokens, cache_read/creation, input_tokens}} from
    the result's `modelUsage` block (camelCase keys), normalized to snake_case."""
    mu = result.get("modelUsage") if isinstance(result, dict) else None
    out = {}
    for model, v in (mu or {}).items():
        out[model] = {
            "cost_usd": _num(v.get("costUSD")),
            "output_tokens": _num(v.get("outputTokens")),
            "input_tokens": _num(v.get("inputTokens")),
            "cache_read_input_tokens": _num(v.get("cacheReadInputTokens")),
            "cache_creation_input_tokens": _num(v.get("cacheCreationInputTokens")),
        }
    return out


def _num(v):
    """A number, or 0 for None / non-numeric."""
    return v if isinstance(v, (int, float)) else 0


def stats(values):
    """(n, mean, min, max, stdev) over a list of numbers; population stdev.
    Empty input yields zeros with n=0 so callers can branch on n."""
    vals = [v for v in values if v is not None]
    n = len(vals)
    if n == 0:
        return {"n": 0, "mean": 0.0, "min": 0.0, "max": 0.0, "stdev": 0.0}
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    return {"n": n, "mean": mean, "min": min(vals), "max": max(vals),
            "stdev": var ** 0.5}


def aggregate(records):
    """Summarize per-rep records: {n_total, n_ok, error_kinds, metrics,
    model_usage}. Numeric stats cover OK reps only; failed reps are tallied by
    kind. model_usage holds per-model cost/output means (diagnostic; the
    regression band stays on the complete total_cost_usd)."""
    ok = [r for r in records if r.get("ok")]
    kinds = {}
    for r in records:
        if not r.get("ok"):
            k = r.get("error_kind", "crash")
            kinds[k] = kinds.get(k, 0) + 1
    metrics = {f: stats([r.get(f, 0) for r in ok]) for f in NUMERIC_FIELDS}
    return {"n_total": len(records), "n_ok": len(ok), "error_kinds": kinds,
            "metrics": metrics, "model_usage": _agg_model_usage(ok)}


def _agg_model_usage(ok_records):
    """Per-model cost/output means over the OK reps that used each model."""
    by_model = {}
    for r in ok_records:
        for model, mv in (r.get("model_usage") or {}).items():
            by_model.setdefault(model, []).append(mv)
    return {model: {"n": len(vs),
                    "cost_usd": stats([v["cost_usd"] for v in vs]),
                    "output_tokens": stats([v["output_tokens"] for v in vs])}
            for model, vs in by_model.items()}
