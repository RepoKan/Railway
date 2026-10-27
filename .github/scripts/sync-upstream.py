"""Copy upstream branches/tags without deleting or rewriting destination refs."""
import argparse
import subprocess
import tempfile


def sync(source, destination):
    with tempfile.TemporaryDirectory(prefix="railway-sync-") as directory:
        def git(*args):
            return subprocess.check_output(
                ["git", "-C", directory, *args], text=True, stderr=subprocess.PIPE
            ).strip()

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
