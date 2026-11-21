"""Copy upstream branches/tags without deleting or rewriting destination refs."""
import argparse
import os
import subprocess
import tempfile
from pathlib import Path


class SyncError(subprocess.CalledProcessError):
    """A Git failure with safe, actionable details visible in Actions logs."""

    def __str__(self):
        return f"Upstream synchronization blocked (exit {self.returncode}):\n{self.stderr or 'Git did not provide an error message.'}"


def _append_summary(blocked):
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return
    with Path(summary_file).open("a", encoding="utf-8") as summary:
        summary.write("## Upstream synchronization blocked\n\n")
        summary.write("No refs were pushed. Rewritten upstream refs require manual review; no force-push, pruning, or deletion is permitted.\n\n")
        for ref, reason, old, new in blocked:
            summary.write(f"- `{ref}`: **{reason}**, destination `{old}`, upstream `{new}`\n")


def sync(source, destination):
    with tempfile.TemporaryDirectory(prefix="railway-sync-") as directory:
        def git(*args):
            try:
                return subprocess.check_output(
                    ["git", "-C", directory, *args], text=True, stderr=subprocess.PIPE
                ).strip()
            except subprocess.CalledProcessError as exc:
                # Do not display full Git arguments, which could contain authentication URLs.
                raise SyncError(exc.returncode, ["git", args[0]], output=exc.output,
                                stderr=(exc.stderr or "").strip()) from None

        git("init", "--bare")
        git("fetch", "--no-tags", source, "refs/heads/*:refs/heads/*", "refs/tags/*:refs/tags/*")
        refs = git("for-each-ref", "--format=%(refname)", "refs/heads/", "refs/tags/").splitlines()
        if "refs/heads/main" not in refs:
            raise ValueError("Upstream must have a main branch")
        specs = []
        for ref in refs:
            target = ref
            if ref.startswith("refs/heads/"):
                branch = ref.removeprefix("refs/heads/")
                if branch.startswith(("repokan/", "upstream/")):
                    raise ValueError(f"Upstream uses reserved workspace branch: {branch}")
                if branch == "main":
                    target = "refs/heads/upstream/main"
            specs.append(f"{ref}:{target}")

        # Fetch destination refs into a private namespace so the source refs stay intact.
        # This provides the current destination SHA for a reproducible failure report.
        git("fetch", "--no-tags", destination,
            "refs/heads/*:refs/sync-destination/heads/*",
            "refs/tags/*:refs/sync-destination/tags/*")
        blocked = []
        for spec in specs:
            ref, target = spec.split(":", 1)
            destination_ref = target.replace("refs/heads/", "refs/sync-destination/heads/", 1) \
                if target.startswith("refs/heads/") else target.replace("refs/tags/", "refs/sync-destination/tags/", 1)
            if subprocess.run(["git", "-C", directory, "show-ref", "--verify", "--quiet", destination_ref],
                              check=False).returncode != 0:
                continue
            old, new = git("rev-parse", destination_ref), git("rev-parse", ref)
            if old == new:
                continue
            if target.startswith("refs/tags/"):
                blocked.append((target, "moved tag", old, new))
                continue
            result = subprocess.run(["git", "-C", directory, "merge-base", "--is-ancestor", old, new],
                                    check=False, capture_output=True, text=True)
            if result.returncode == 1:
                blocked.append((target, "non-fast-forward branch", old, new))
            elif result.returncode != 0:
                raise SyncError(result.returncode, ["git", "merge-base"], stderr=result.stderr.strip())
        if blocked:
            _append_summary(blocked)
            details = "\n".join(f"- {reason}: {ref} (destination {old}, upstream {new})"
                                for ref, reason, old, new in blocked)
            raise SyncError(1, ["git", "push", "--atomic"], stderr=(
                f"{len(blocked)} rewritten refs detected; atomic push cancelled before writing anything.\n"
                f"{details}\nReview upstream history and decide how to handle each ref; no force update was performed."))

        # Atomic push: one rewritten branch or tag rejects the entire update.
        # No --force, leading '+', --mirror, --prune or deletion refspecs.
        git("push", "--atomic", destination, *specs)
        return {"branches": sum(r.startswith("refs/heads/") for r in refs),
                "tags": sum(r.startswith("refs/tags/") for r in refs),
                "upstream_main": git("rev-parse", "refs/heads/main")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="https://github.com/railwayapp/railway-skills.git")
    parser.add_argument("--destination", default="https://github.com/RepoKan/Railway.git")
    args = parser.parse_args()
    print(sync(args.source, args.destination))
