#!/usr/bin/env python3
"""
Unit tests for the pure metric layer (eval/metrics.py). Deterministic, offline,
stdlib-only -- safe to run in CI. Fixtures under eval/fixtures/ are REAL
recorded `claude -p --output-format json` results plus one synthetic non-JSON
payload, so the parser is exercised against the actual CLI schema.

The load-bearing test is TestAggregate.test_failed_reps_excluded: a 429 rep
carries a nonzero cost with zeroed usage, and it must NOT pollute the numeric
aggregates -- that is the whole reason classification exists.

Run:  python3 eval/tests/test_metrics.py     (or: python3 -m unittest)
"""
import importlib.util
import json
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_MOD = os.path.join(_HERE, "..", "metrics.py")
_FX = os.path.join(_HERE, "..", "fixtures")
_spec = importlib.util.spec_from_file_location("metrics", _MOD)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def _fx(name):
    with open(os.path.join(_FX, name)) as fh:
        return fh.read()


GOOD = json.loads(_fx("result_good.json"))
API429 = json.loads(_fx("result_api429.json"))
BUDGET = json.loads(_fx("result_budget.json"))
NONJSON_TEXT = _fx("result_nonjson.txt")


class TestParseStdout(unittest.TestCase):
    def test_valid_json_returns_dict(self):
        obj = m.parse_stdout(json.dumps(GOOD))
        self.assertEqual(obj["total_cost_usd"], GOOD["total_cost_usd"])

    def test_garbage_is_marked_non_json(self):
        obj = m.parse_stdout(NONJSON_TEXT)
        self.assertEqual(obj.get("_error"), "non-json")

    def test_non_dict_json_is_non_json(self):
        # A syntactically valid but non-result payload is unusable.
        self.assertEqual(m.parse_stdout("[1, 2, 3]").get("_error"), "non-json")

    def test_empty_string_is_non_json(self):
        self.assertEqual(m.parse_stdout("").get("_error"), "non-json")


class TestClassify(unittest.TestCase):
    def test_good_is_none(self):
        self.assertEqual(m.classify(GOOD), "none")

    def test_api_429(self):
        self.assertEqual(m.classify(API429), "api-429")

    def test_budget_exhausted_is_its_own_kind(self):
        # Real budget-cap termination must not be mislabeled as an API error.
        self.assertEqual(m.classify(BUDGET), "budget")
        self.assertFalse(m.parse_result(BUDGET)["ok"])

    def test_api_other_from_status(self):
        self.assertEqual(m.classify({"api_error_status": 500}), "api-other")

    def test_api_other_from_is_error_flag(self):
        self.assertEqual(m.classify({"is_error": True}), "api-other")

    def test_runner_timeout_marker(self):
        self.assertEqual(m.classify({"_error": "timeout"}), "timeout")

    def test_unknown_marker_is_crash(self):
        self.assertEqual(m.classify({"_error": "weird"}), "crash")

    def test_non_dict_is_crash(self):
        self.assertEqual(m.classify(None), "crash")


class TestParseResult(unittest.TestCase):
    def test_good_record_fields(self):
        r = m.parse_result(GOOD)
        self.assertTrue(r["ok"])
        self.assertEqual(r["error_kind"], "none")
        self.assertEqual(r["total_cost_usd"], GOOD["total_cost_usd"])
        self.assertEqual(r["output_tokens"], GOOD["usage"]["output_tokens"])
        self.assertEqual(r["num_turns"], GOOD["num_turns"])
        self.assertEqual(r["duration_ms"], GOOD["duration_ms"])
        self.assertEqual(r["web_search_requests"],
                         GOOD["usage"]["server_tool_use"]["web_search_requests"])

    def test_failed_record_is_not_ok(self):
        r = m.parse_result(API429)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error_kind"], "api-429")

    def test_missing_fields_coerce_to_zero(self):
        r = m.parse_result({"total_cost_usd": 0.5})  # no usage block
        self.assertEqual(r["output_tokens"], 0)
        self.assertEqual(r["web_search_requests"], 0)

    def test_missing_artifact_overrides_clean_run(self):
        # claude reported success but no output file was written (0 bytes).
        r = m.parse_result(GOOD, artifact_bytes=0)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error_kind"], "missing-artifact")

    def test_missing_artifact_does_not_mask_real_error(self):
        # A 429 with no artifact stays a 429, not "missing-artifact".
        r = m.parse_result(API429, artifact_bytes=0)
        self.assertEqual(r["error_kind"], "api-429")

    def test_present_artifact_keeps_run_ok(self):
        r = m.parse_result(GOOD, artifact_bytes=4096)
        self.assertTrue(r["ok"])
        self.assertEqual(r["artifact_bytes"], 4096)

    def test_unchecked_artifact_is_not_missing(self):
        # artifact_bytes=None means "not checked" -- must not flag missing.
        r = m.parse_result(GOOD)
        self.assertTrue(r["ok"])
        self.assertIsNone(r["artifact_bytes"])


class TestModelUsage(unittest.TestCase):
    def test_parse_captures_per_model_split(self):
        mu = m.parse_result(GOOD)["model_usage"]
        self.assertIn("claude-sonnet-5", mu)
        self.assertAlmostEqual(mu["claude-sonnet-5"]["cost_usd"], 0.8752788)
        self.assertEqual(mu["claude-sonnet-5"]["output_tokens"], 21852)

    def test_recovers_tokens_usage_omits(self):
        # The per-model output (21852) exceeds the orchestrator-only usage
        # axis (5239) -- this split is the only place the rest surfaces.
        r = m.parse_result(GOOD)
        self.assertGreater(r["model_usage"]["claude-sonnet-5"]["output_tokens"],
                           r["output_tokens"])

    def test_missing_modelusage_is_empty_dict(self):
        self.assertEqual(m.parse_result({"total_cost_usd": 1.0})["model_usage"], {})

    def test_aggregate_means_per_model(self):
        agg = m.aggregate([m.parse_result(GOOD), m.parse_result(GOOD)])
        s5 = agg["model_usage"]["claude-sonnet-5"]
        self.assertEqual(s5["n"], 2)
        self.assertAlmostEqual(s5["cost_usd"]["mean"], 0.8752788)


class TestStats(unittest.TestCase):
    def test_known_distribution(self):
        s = m.stats([2, 4, 6])
        self.assertEqual(s["n"], 3)
        self.assertEqual(s["mean"], 4)
        self.assertEqual(s["min"], 2)
        self.assertEqual(s["max"], 6)
        self.assertAlmostEqual(s["stdev"], (8 / 3) ** 0.5)  # population stdev

    def test_empty_is_zeroed(self):
        s = m.stats([])
        self.assertEqual(s["n"], 0)
        self.assertEqual(s["stdev"], 0.0)


class TestAggregate(unittest.TestCase):
    def test_failed_reps_excluded(self):
        # Two good reps + one 429. The 429's $1.00 cost must not enter the mean.
        recs = [m.parse_result(GOOD), m.parse_result(GOOD), m.parse_result(API429)]
        agg = m.aggregate(recs)
        self.assertEqual(agg["n_total"], 3)
        self.assertEqual(agg["n_ok"], 2)
        self.assertEqual(agg["error_kinds"], {"api-429": 1})
        cost = agg["metrics"]["total_cost_usd"]
        self.assertEqual(cost["n"], 2)
        self.assertAlmostEqual(cost["mean"], GOOD["total_cost_usd"])

    def test_all_failed_yields_no_numeric_stats(self):
        agg = m.aggregate([m.parse_result(API429)])
        self.assertEqual(agg["n_ok"], 0)
        self.assertEqual(agg["metrics"]["total_cost_usd"]["n"], 0)


if __name__ == "__main__":
    unittest.main()
