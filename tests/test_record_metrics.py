#!/usr/bin/env python3
"""
Unit tests for the passive metrics collector. Deterministic, no network, no
Claude Code -- synthetic transcripts drive it. Covers the parts that matter:
step attribution via the invocation marker (mentions don't hijack it), uuid
dedup (idempotent hooks), dropping stepless messages, and token/cost aggregation.

Run:  python3 tests/test_record_metrics.py     (or: python3 -m unittest)
"""
import importlib.util
import json
import os
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_MOD = os.path.join(_HERE, "..", ".claude", "wtf-ms", "scripts", "record_metrics.py")
_spec = importlib.util.spec_from_file_location("record_metrics", _MOD)
rm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rm)


def _cmd(step):
    """A slash-command invocation as Claude Code records it (marker-wrapped)."""
    return {"type": "user", "uuid": "u-" + step,
            "message": {"content": f"<command-name>/wtfMS:{step}</command-name>"}}


def _u(text):
    """A plain user message (may mention commands, but is not an invocation)."""
    return {"type": "user", "uuid": "u-" + text[:8], "message": {"content": text}}


def _a(uuid, model="claude-sonnet-5", inp=10, out=100, cr=500, cw=50, sidechain=False):
    return {"type": "assistant", "uuid": uuid, "timestamp": "2026-07-23T00:00:00Z",
            "session_id": "sess", "isSidechain": sidechain,
            "message": {"model": model, "usage": {
                "input_tokens": inp, "output_tokens": out,
                "cache_read_input_tokens": cr, "cache_creation_input_tokens": cw}}}


def _write_transcript(objs):
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w") as fh:
        for o in objs:
            fh.write(json.dumps(o) + "\n")
    return path


class TestCollect(unittest.TestCase):
    def test_attributes_to_the_invoked_command(self):
        path = _write_transcript([_cmd("literature-review"), _a("a1")])
        recs = rm.collect(path)
        self.assertEqual(recs[0]["step"], "literature-review")
        os.remove(path)

    def test_a_mention_does_not_hijack_the_step(self):
        # The expanded command body / tool output mentions other commands; only
        # the invocation marker counts.
        path = _write_transcript([
            _cmd("literature-review"),
            _u("next you might run /wtfMS:progress or /wtfMS:define-research-tasks"),
            _a("a1")])
        self.assertEqual(rm.collect(path)[0]["step"], "literature-review")
        os.remove(path)

    def test_subagent_transcript_has_no_step(self):
        # A subagent transcript names no /wtfMS command -> step stays None.
        path = _write_transcript([_a("a1", model="claude-haiku-4-5", sidechain=True)])
        self.assertIsNone(rm.collect(path)[0]["step"])
        os.remove(path)

    def test_messages_without_usage_are_skipped(self):
        path = _write_transcript([{"type": "assistant", "uuid": "x",
                                   "message": {"model": "m"}}])
        self.assertEqual(rm.collect(path), [])
        os.remove(path)


class TestNewRecords(unittest.TestCase):
    def test_dedups_by_uuid(self):
        recs = [{"uuid": "a1", "step": "lit"}, {"uuid": "a2", "step": "lit"}]
        self.assertEqual(len(rm.new_records({"a1"}, recs)), 1)

    def test_drops_stepless(self):
        # Non-wtf-MS turns and subagent transcripts (no command) are dropped.
        recs = [{"uuid": "s1", "step": None}, {"uuid": "a1", "step": "lit"}]
        kept = rm.new_records(set(), recs)
        self.assertEqual([r["uuid"] for r in kept], ["a1"])


class TestCostAndReport(unittest.TestCase):
    def test_sonnet_cost_estimate(self):
        r = {"model": "claude-sonnet-5", "input": 1_000_000, "output": 0,
             "cache_read": 0, "cache_write": 0}
        self.assertAlmostEqual(rm.est_cost(r), 3.0)   # $3 / 1M input

    def test_report_sums_per_step(self):
        recs = [{"step": "lit", "model": "claude-sonnet-5", "input": 10, "output": 100,
                 "cache_read": 0, "cache_write": 0},
                {"step": "lit", "model": "claude-sonnet-5", "input": 10, "output": 100,
                 "cache_read": 0, "cache_write": 0}]
        txt = rm.report_text(recs)
        self.assertIn("lit", txt)
        self.assertIn("200", txt)     # summed output tokens
        self.assertIn("TOTAL", txt)

    def test_empty_report_is_graceful(self):
        self.assertIn("No wtf-MS metrics", rm.report_text([]))


class TestRunHook(unittest.TestCase):
    def setUp(self):
        self.cwd = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.cwd, ".research"))

    def _metrics(self):
        return rm._read_records(os.path.join(self.cwd, rm.METRICS_REL))

    def test_records_and_is_idempotent(self):
        path = _write_transcript([_cmd("literature-review"), _a("a1"), _a("a2")])
        rm.run_hook(self.cwd, {"transcript_path": path})
        rm.run_hook(self.cwd, {"transcript_path": path})   # second fire, no double-count
        recs = self._metrics()
        self.assertEqual(len(recs), 2)
        self.assertTrue(all(r["step"] == "literature-review" for r in recs))
        os.remove(path)

    def test_stepless_transcript_records_nothing(self):
        # A plain Stop on a transcript with no /wtfMS command contributes nothing.
        sub = _write_transcript([_a("s1", model="claude-haiku-4-5")])
        rm.run_hook(self.cwd, {"transcript_path": sub})
        self.assertEqual(self._metrics(), [])
        os.remove(sub)

    def test_no_research_dir_records_nothing(self):
        bare = tempfile.mkdtemp()             # no .research
        path = _write_transcript([_cmd("literature-review"), _a("a1")])
        rm.run_hook(bare, {"transcript_path": path})
        self.assertFalse(os.path.exists(os.path.join(bare, rm.METRICS_REL)))
        os.remove(path)

    def test_subagent_usage_charged_to_parent_step(self):
        # SubagentStop: the subagent's own transcript, charged to the parent's step.
        parent = _write_transcript([_cmd("execute-task"), _a("p1")])
        agent = _write_transcript([_a("g1", out=5000), _a("g2", out=6000)])
        rm.run_hook(self.cwd, {"transcript_path": parent})
        rm.run_hook(self.cwd, {"transcript_path": parent,
                               "agent_transcript_path": agent,
                               "agent_type": "wtfms-task-executor"})
        recs = self._metrics()
        self.assertTrue(all(r["step"] == "execute-task" for r in recs))
        subs = [r for r in recs if r.get("agent")]
        self.assertEqual({r["uuid"] for r in subs}, {"g1", "g2"})
        self.assertEqual(subs[0]["agent"], "wtfms-task-executor")
        os.remove(parent)
        os.remove(agent)

    def test_subagent_of_non_wtfms_command_is_skipped(self):
        parent = _write_transcript([_a("p1")])          # no /wtfMS command
        agent = _write_transcript([_a("g1", out=5000)])
        rm.run_hook(self.cwd, {"transcript_path": parent,
                               "agent_transcript_path": agent})
        self.assertEqual(self._metrics(), [])
        os.remove(parent)
        os.remove(agent)


if __name__ == "__main__":
    unittest.main()
