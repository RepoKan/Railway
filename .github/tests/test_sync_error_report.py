"""Regression coverage for non-destructive upstream conflict diagnostics."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sync-upstream.py"


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], text=True, stderr=subprocess.PIPE).strip()


def sync(source, destination):
    spec = importlib.util.spec_from_file_location("sync_upstream_diagnostics", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.sync(str(source), str(destination))


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "upstream"
        self.dest = Path(self.temp.name) / "destination.git"
        git("init", "-b", "main", self.source)
        git("-C", self.source, "config", "user.name", "Test")
        git("-C", self.source, "config", "user.email", "test@example.invalid")
        self.commit("first")
        git("init", "--bare", self.dest)

    def commit(self, message):
        git("-C", self.source, "commit", "--allow-empty", "-m", message)
        return git("-C", self.source, "rev-parse", "HEAD")

    def refs(self):
        return {name: sha for sha, name in (line.split(" ", 1) for line in
                git("--git-dir", self.dest, "show-ref").splitlines())}

    def test_diverged_branch_shows_ref_sha_and_no_partial_writes(self):
        git("-C", self.source, "branch", "paulo/example")
        sync(self.source, self.dest)
        before = self.refs()
        git("-C", self.source, "checkout", "paulo/example")
        self.commit("upstream change")
        git("-C", self.source, "checkout", "--orphan", "rewritten")
        self.commit("independent history")
        git("-C", self.source, "branch", "-f", "paulo/example", "HEAD")
        summary = Path(self.temp.name) / "summary.md"
        with patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}):
            with self.assertRaises(subprocess.CalledProcessError) as ctx:
                sync(self.source, self.dest)
        self.assertIn("non-fast-forward branch", str(ctx.exception))
        self.assertIn("refs/heads/paulo/example", str(ctx.exception))
        self.assertIn(before["refs/heads/paulo/example"], str(ctx.exception))
        self.assertIn("No refs were pushed", summary.read_text())
        self.assertEqual(self.refs(), before)

    def test_moved_tag_shows_specific_ref_and_preserves_destination(self):
        git("-C", self.source, "tag", "v1")
        sync(self.source, self.dest)
        before = self.refs()
        self.commit("next")
        git("-C", self.source, "tag", "-f", "v1")
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            sync(self.source, self.dest)
        self.assertIn("moved tag: refs/tags/v1", str(ctx.exception))
        self.assertEqual(self.refs(), before)

    def test_fast_forward_and_idempotency_still_work(self):
        sync(self.source, self.dest)
        expected = self.commit("next")
        sync(self.source, self.dest)
        sync(self.source, self.dest)
        self.assertEqual(self.refs()["refs/heads/upstream/main"], expected)


if __name__ == "__main__":
    unittest.main()
