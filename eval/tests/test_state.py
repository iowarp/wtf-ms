#!/usr/bin/env python3
"""
Unit tests for run_eval's state backup/restore -- the logic whose earlier
git-based version could DELETE untracked runtime state (.research) instead of
restoring it. These are pure filesystem operations, so they run offline with
no `claude` and no spend. Importing run_eval is safe: it only defines
functions at module load; nothing runs until main() under __main__.

Run:  python3 eval/tests/test_state.py     (or: python3 -m unittest)
"""
import importlib.util
import os
import shutil
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_MOD = os.path.join(_HERE, "..", "run_eval.py")
_spec = importlib.util.spec_from_file_location("run_eval", _MOD)
re = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(re)

REL = "_tmp_state_test"          # a REPO-relative state path, _tmp_ per convention
LIVE = os.path.join(re.REPO, REL)


def _write(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def _read(path):
    with open(path) as fh:
        return fh.read()


class TestBackupRestore(unittest.TestCase):
    def setUp(self):
        self.backup = tempfile.mkdtemp()
        if os.path.exists(LIVE):
            shutil.rmtree(LIVE)

    def tearDown(self):
        shutil.rmtree(self.backup, ignore_errors=True)
        if os.path.exists(LIVE):
            shutil.rmtree(LIVE)

    def test_restore_recovers_original_content(self):
        os.makedirs(LIVE)
        _write(os.path.join(LIVE, "a.txt"), "orig")
        re.snapshot_state([REL], self.backup)

        # Simulate a run mutating the state: change a file, add another.
        _write(os.path.join(LIVE, "a.txt"), "changed")
        _write(os.path.join(LIVE, "b.txt"), "new")

        re.restore_state([REL], self.backup)
        self.assertEqual(_read(os.path.join(LIVE, "a.txt")), "orig")
        # restore rmtrees live then copies the backup back, so the added file is gone.
        self.assertFalse(os.path.exists(os.path.join(LIVE, "b.txt")))

    def test_restore_removes_state_that_did_not_exist_originally(self):
        # This is exactly the incident: no .research to begin with, the seed
        # creates one, and cleanup must return to "absent" -- not leave the
        # seeded state behind, and (unlike git clean) not error.
        re.snapshot_state([REL], self.backup)      # nothing to back up
        os.makedirs(LIVE)                          # seed creates state
        _write(os.path.join(LIVE, "seeded.txt"), "x")

        re.restore_state([REL], self.backup)
        self.assertFalse(os.path.exists(LIVE))

    def test_restore_with_none_source_clears_state(self):
        # A seedless step resets to empty before each rep (src=None).
        os.makedirs(LIVE)
        _write(os.path.join(LIVE, "a.txt"), "x")
        re.restore_state([REL], None)
        self.assertFalse(os.path.exists(LIVE))

    def test_snapshot_then_restore_is_idempotent(self):
        os.makedirs(os.path.join(LIVE, "sub"))
        _write(os.path.join(LIVE, "sub", "c.txt"), "deep")
        re.snapshot_state([REL], self.backup)
        re.restore_state([REL], self.backup)       # no mutation between
        self.assertEqual(_read(os.path.join(LIVE, "sub", "c.txt")), "deep")


if __name__ == "__main__":
    unittest.main()
