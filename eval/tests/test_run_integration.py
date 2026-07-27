#!/usr/bin/env python3
"""
Offline integration test for the runner's live orchestration. Stubs run_claude
(no `claude`, no network, no spend) and drives main() end-to-end on a seedless
step with a priced check, then asserts the results shape and that state was
restored. This covers the parts unit tests can't: the rep loop, the check-pricing
loop, aggregation, and the state backup/restore in the finally block.

Run:  python3 eval/tests/test_run_integration.py     (or: python3 -m unittest)
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "run_eval", os.path.join(_HERE, "..", "run_eval.py"))
re = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(re)

STATE_REL = "_tmp_eval_int_state"          # REPO-relative throwaway state path
LIVE_STATE = os.path.join(re.REPO, STATE_REL)


FIXTURE_DIR = os.path.join(re.REPO, "eval", "fixtures", "state", "_tmp_int_fixture")


def _fake_run_claude(prompt, session_id, model, timeout, max_usd,
                     resume=False, fork=False):
    """Canned success. Writes a marker into the state dir (simulating the
    command's output, for --save-fixture). The check-disabled rep (suffix
    present) is cheaper, so the citation increment comes out positive."""
    os.makedirs(LIVE_STATE, exist_ok=True)
    with open(os.path.join(LIVE_STATE, "out.txt"), "w") as fh:
        fh.write("output")
    cost = 0.50 if "DISABLE-CHECK" in prompt else 1.00
    res = {"type": "result", "is_error": False, "api_error_status": None,
           "total_cost_usd": cost, "num_turns": 3,
           "duration_ms": 1000, "duration_api_ms": 900,
           "usage": {"input_tokens": 1, "output_tokens": 100,
                     "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0,
                     "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0}},
           "modelUsage": {"claude-sonnet-5": {"costUSD": cost, "outputTokens": 100,
                                              "inputTokens": 1, "cacheReadInputTokens": 0,
                                              "cacheCreationInputTokens": 0}}}
    return res, json.dumps(res)


class TestLiveOrchestration(unittest.TestCase):
    def setUp(self):
        self.tmp_results = tempfile.mkdtemp()
        self.step_file = os.path.join(self.tmp_results, "step.json")
        with open(self.step_file, "w") as fh:
            json.dump({
                "name": "int-step",
                "state": {"reset": "backup", "paths": [STATE_REL]},
                "session": "fresh",
                "measure": {"command": "/c", "prompt": "MEASURE", "timeout": 5},
                "checks": [{"name": "citations", "disable_suffix": "DISABLE-CHECK"}],
            }, fh)
        # Save what we monkeypatch / mutate.
        self._saved = (re.RESULTS_DIR, re.run_claude, re.shutil.which, sys.argv)
        re.RESULTS_DIR = self.tmp_results
        re.run_claude = _fake_run_claude
        re.shutil.which = lambda _name: "/usr/bin/claude"
        if os.path.exists(LIVE_STATE):
            shutil.rmtree(LIVE_STATE)

    def tearDown(self):
        re.RESULTS_DIR, re.run_claude, re.shutil.which, sys.argv = self._saved
        shutil.rmtree(self.tmp_results, ignore_errors=True)
        if os.path.exists(LIVE_STATE):
            shutil.rmtree(LIVE_STATE)
        shutil.rmtree(FIXTURE_DIR, ignore_errors=True)

    def _results(self):
        f = [x for x in os.listdir(self.tmp_results)
             if x.endswith(".json") and x != "step.json"]
        self.assertEqual(len(f), 1, "expected exactly one results file")
        with open(os.path.join(self.tmp_results, f[0])) as fh:
            return json.load(fh)

    def test_run_records_reps_check_and_restores_state(self):
        sys.argv = ["run_eval.py", self.step_file, "--live", "--price-checks",
                    "--reps", "2"]
        re.main()

        rec = self._results()
        self.assertEqual(len(rec["cells"]), 2)                       # 2 baseline reps
        self.assertAlmostEqual(rec["aggregate"]["metrics"]["total_cost_usd"]["mean"], 1.00)
        self.assertEqual(len(rec["checks"]["citations"]["cells"]), 2)  # 2 disabled reps
        self.assertAlmostEqual(rec["checks"]["citations"]["increment_usd"], 0.50)
        # seedless step must leave no state behind (restored to absent).
        self.assertFalse(os.path.exists(LIVE_STATE))

    def test_plan_only_without_live_spends_nothing(self):
        sys.argv = ["run_eval.py", self.step_file]      # no --live
        re.main()
        # No results file should have been written.
        self.assertEqual([x for x in os.listdir(self.tmp_results) if x != "step.json"], [])

    def test_save_fixture_captures_output_state(self):
        sys.argv = ["run_eval.py", self.step_file, "--live", "--reps", "1",
                    "--save-fixture", "_tmp_int_fixture"]
        re.main()
        # The command's output (out.txt) is frozen under the fixture dir, mirroring
        # the state path's basename -- ready to seed the next step.
        saved = os.path.join(FIXTURE_DIR, STATE_REL, "out.txt")
        self.assertTrue(os.path.exists(saved), f"fixture not saved at {saved}")
        # And the user's live state is still restored (not left behind).
        self.assertFalse(os.path.exists(LIVE_STATE))


if __name__ == "__main__":
    unittest.main()
