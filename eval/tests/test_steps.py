#!/usr/bin/env python3
"""
Unit tests for the step model in run_eval: prompt composition, step-schema
validation, and that the shipped step files under eval/steps/ load and validate.
Offline, no spend. Importing run_eval is safe -- nothing runs until main().

Run:  python3 eval/tests/test_steps.py     (or: python3 -m unittest)
"""
import importlib.util
import json
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "run_eval", os.path.join(_HERE, "..", "run_eval.py"))
re = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(re)

STEPS_DIR = os.path.join(_HERE, "..", "steps")


def _load_step(name):
    with open(os.path.join(STEPS_DIR, name)) as fh:
        return json.load(fh)


def _minimal():
    return {"name": "s", "state": {"reset": "backup", "paths": [".research"]},
            "measure": {"command": "/c", "prompt": "p", "timeout": 1}}


class TestComposePrompt(unittest.TestCase):
    def test_no_suffix_returns_base(self):
        self.assertEqual(re.compose_prompt("base", None), "base")

    def test_empty_suffix_returns_base(self):
        self.assertEqual(re.compose_prompt("base", ""), "base")

    def test_suffix_appended_with_blank_line(self):
        self.assertEqual(re.compose_prompt("base", "more"), "base\n\nmore")


class TestValidate(unittest.TestCase):
    def test_minimal_step_is_valid(self):
        re.validate(_minimal())  # no SystemExit

    def test_fixture_plus_seed_rejected(self):
        s = _minimal()
        s["fixture"] = "eval/fixtures/state/x"
        s["seed"] = {"command": "x", "prompt": "p", "timeout": 1}
        with self.assertRaises(SystemExit):
            re.validate(s)

    def test_resume_fork_without_seed_rejected(self):
        s = _minimal()
        s["session"] = "resume-fork"
        with self.assertRaises(SystemExit):
            re.validate(s)

    def test_check_needs_name_and_disable_suffix(self):
        s = _minimal()
        s["checks"] = [{"name": "citations"}]  # missing disable_suffix
        with self.assertRaises(SystemExit):
            re.validate(s)

    def test_bad_state_reset_rejected(self):
        s = _minimal()
        s["state"]["reset"] = "git"
        with self.assertRaises(SystemExit):
            re.validate(s)


class TestShippedSteps(unittest.TestCase):
    def test_all_steps_load_and_validate(self):
        names = [f for f in os.listdir(STEPS_DIR) if f.endswith(".json")]
        self.assertTrue(names, "no step files found")
        for name in names:
            re.validate(_load_step(name))

    def test_literature_review_is_isolated_with_a_check(self):
        s = _load_step("literature-review.json")
        self.assertEqual(s["fixture"], "eval/fixtures/state/after-identify")
        self.assertEqual(s.get("session"), "fresh")
        self.assertEqual(s["checks"][0]["name"], "citations")
        fixture = os.path.join(_HERE, "..", "..", s["fixture"])
        self.assertTrue(os.path.isdir(fixture), f"missing fixture {s['fixture']}")

    def test_identify_research_is_seedless(self):
        s = _load_step("identify-research.json")
        self.assertNotIn("fixture", s)
        self.assertNotIn("seed", s)


if __name__ == "__main__":
    unittest.main()
