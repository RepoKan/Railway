"""Exercise synchronization against real local Git repositories."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sync-upstream.py"


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], text=True, stderr=subprocess.PIPE).strip()


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "source"
        self.dest = Path(self.tmp.name) / "destination.git"
        git("init", "-b", "main", self.source)
        git("-C", self.source, "config", "user.name", "Test")
        git("-C", self.source, "config", "user.email", "test@example.invalid")
        self.commit("first")
        git("init", "--bare", self.dest)

    def commit(self, message):
        git("-C", self.source, "commit", "--allow-empty", "-m", message)
        return git("-C", self.source, "rev-parse", "HEAD")

    def sync(self):
        spec = importlib.util.spec_from_file_location("sync_upstream", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.sync(str(self.source), str(self.dest))

    def refs(self):
        return dict(line.split(" ", 1)[::-1] for line in git("--git-dir", self.dest, "show-ref").splitlines())

    def test_imports_all_branches_tags_without_touching_main(self):
        git("-C", self.source, "branch", "release/example")
        git("-C", self.source, "tag", "v-example")
        self.sync()
        refs = self.refs()
        self.assertEqual(refs["refs/heads/upstream/main"], refs["refs/heads/release/example"])
        self.assertEqual(refs["refs/tags/v-example"], refs["refs/heads/upstream/main"])
        self.assertNotIn("refs/heads/main", refs)

    def test_fast_forward_and_idempotency(self):
        self.sync()
        new = self.commit("next")
        self.sync()
        self.sync()
        self.assertEqual(self.refs()["refs/heads/upstream/main"], new)

    def test_rewrite_rejects_entire_push(self):
        self.sync()
        before = self.refs()
        git("-C", self.source, "checkout", "--orphan", "rewritten")
        self.commit("unrelated history")
        git("-C", self.source, "branch", "-f", "main", "HEAD")
        with self.assertRaises(subprocess.CalledProcessError):
            self.sync()
        self.assertEqual(self.refs(), before)

    def test_moved_tag_is_rejected_and_old_tag_retained(self):
        git("-C", self.source, "tag", "v-example")
        self.sync()
        before = self.refs()
        self.commit("next")
        git("-C", self.source, "tag", "-f", "v-example")
        with self.assertRaises(subprocess.CalledProcessError):
            self.sync()
        self.assertEqual(self.refs(), before)

    def test_reserved_branch_rejected(self):
        git("-C", self.source, "branch", "repokan/workspace-setup")
        with self.assertRaisesRegex(ValueError, "reserved"):
            self.sync()


if __name__ == "__main__":
    unittest.main()
