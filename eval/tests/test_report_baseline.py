#!/usr/bin/env python3
"""
Unit tests for the pure report + baseline layers. Offline, deterministic, no
spend. Uses eval/fixtures/results_sample.json: the literature-review step with
2 ok baseline reps (mean $1.05) + one api-429, and a priced `citations` check
(+$0.05).

Run:  python3 eval/tests/test_report_baseline.py     (or: python3 -m unittest)
"""
import importlib.util
import json
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, "..", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


report = _load("report")
baseline = _load("baseline")
metrics = _load("metrics")

with open(os.path.join(_HERE, "..", "fixtures", "results_sample.json")) as fh:
    SAMPLE = json.load(fh)


class TestReport(unittest.TestCase):
    def test_render_has_step_and_cost(self):
        md = report.render(SAMPLE)
        self.assertIn("# eval step: literature-review", md)
        self.assertIn("$1.0500", md)     # step mean cost
        self.assertIn("2/3", md)         # ok reps

    def test_render_shows_error_kinds(self):
        self.assertIn("api-429×1", report.render(SAMPLE))

    def test_render_shows_check_increment(self):
        md = report.render(SAMPLE)
        self.assertIn("citations: +$0.0500", md)

    def test_empty_cells_is_graceful(self):
        md = report.render({"step": "x", "command": "/c", "model": "opus",
                            "run_id": "r", "reps": 0, "cells": []})
        self.assertIn("no reps recorded", md)

    def test_per_model_split_shown_only_when_multi_model(self):
        self.assertNotIn("per-model cost", report.render(SAMPLE))  # sample is single-model
        rec = metrics.parse_result({"total_cost_usd": 1.2, "num_turns": 3,
            "modelUsage": {"claude-sonnet-5": {"costUSD": 1.0, "outputTokens": 100},
                           "claude-haiku-4-5": {"costUSD": 0.2, "outputTokens": 50}}},
            artifact_bytes=10)
        md = report.render({"step": "s", "command": "/c", "model": "sonnet",
                            "run_id": "r", "reps": 1,
                            "cells": [{"tag": "r1", "rep": 1, "attempts": 1, "record": rec}]})
        self.assertIn("per-model cost", md)
        self.assertIn("claude-haiku-4-5", md)


class TestBaseline(unittest.TestCase):
    def test_build_captures_mean(self):
        bl = baseline.build_baseline(SAMPLE, band=0.2)
        self.assertAlmostEqual(bl["metrics"]["total_cost_usd"]["mean"], 1.05)
        self.assertEqual(bl["band"], 0.2)

    def test_build_captures_check_increment(self):
        bl = baseline.build_baseline(SAMPLE)
        self.assertAlmostEqual(bl["checks"]["citations"]["increment_usd"], 0.05)

    def test_same_run_has_nothing_notable(self):
        bl = baseline.build_baseline(SAMPLE)
        self.assertEqual(baseline.notable(baseline.compare(bl, SAMPLE)), [])

    def test_cost_rise_beyond_band_is_notable(self):
        bl = baseline.build_baseline(SAMPLE, band=0.10)
        infl = json.loads(json.dumps(SAMPLE))
        for c in infl["cells"]:
            c["record"]["total_cost_usd"] *= 1.5   # +50%, well outside 10%
        moved = baseline.notable(baseline.compare(bl, infl))
        self.assertTrue(any(f["metric"] == "total_cost_usd" and f["pct"] > 0
                            for f in moved))

    def test_cost_drop_is_also_notable(self):
        # Both directions are recorded -- a big drop is worth knowing about too.
        bl = baseline.build_baseline(SAMPLE, band=0.10)
        cheaper = json.loads(json.dumps(SAMPLE))
        for c in cheaper["cells"]:
            c["record"]["total_cost_usd"] *= 0.5
        moved = baseline.notable(baseline.compare(bl, cheaper))
        self.assertTrue(any(f["metric"] == "total_cost_usd" and f["pct"] < 0
                            for f in moved))

    def test_missing_data_is_notable(self):
        bl = baseline.build_baseline(SAMPLE)
        empty = json.loads(json.dumps(SAMPLE))
        empty["cells"] = []
        moved = baseline.notable(baseline.compare(bl, empty))
        self.assertTrue(any(f["metric"] == "total_cost_usd" and not f["has_data"]
                            for f in moved))


if __name__ == "__main__":
    unittest.main()
