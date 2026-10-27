# Railway Workspace Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Preserve all upstream Git history and make Railway skills discoverable, validated and updateable in RepoKan/Railway.

**Architecture:** Keep the official plugin payload unchanged. Add repository-scoped skill discovery and a credential-free upstream synchronization workflow that publishes a compare link; changes to the supported skill enter main through reviewed pull requests.

**Tech Stack:** Git, Python standard library, GitHub Actions, Railway OAuth MCP.

**Spec:** [Workspace setup specification](../../repokan-workspace.md).

## Global Constraints

- Preserve upstream MIT attribution, all original branch heads and Git history.
- No credentials, account profiles, project data or deployment creation in this public repository.
- One consolidated use-railway skill; no account-wide skill activation.
- No force pushes or branch/tag deletion during updates.

## Review Focus

- Rewritten upstream refs must fail atomically without overwriting destination history.
- Reserved branch names must not overwrite workspace configuration.
- Existing tags must survive upstream changes.
- OAuth and CLI requirements must be distinguished from repository installation.
- Scheduled updates must never automatically merge or approve pull requests.

### Task 1: Verify import

- [x] Create all-branch fork and compare all 59 branch names and SHAs with upstream.
- [x] Confirm source has no tags or GitHub releases.

### Task 2: Workspace and update channel

Files: `.agents/skills/use-railway`, `.github/scripts/sync-upstream.py`, `.github/tests/test_sync_upstream.py`, `.github/workflows/upstream-sync.yml`, `.github/workflows/repokan-validate.yml`, `docs/repokan-workspace.md`, `README.md`.

- [x] Add meaningful local Git integration tests; observe failure before implementation.
- [x] Implement atomic, non-forced branch/tag import and verify tests.
- [x] Add skill symlink, setup instructions, credential-free daily synchronization and validation workflows.
- [ ] Run upstream shell regression suite, JSON/version/MCP checks and Python syntax checks.

### Task 3: Publish and verify

- [ ] Commit on isolated feature branch, inspect changed-file scope, open setup PR.
- [ ] Verify CI for exact candidate; review branch, merge and verify main CI.
- [ ] Enable and dispatch upstream workflow; verify its result and imported refs.
- [ ] Recheck GitHub connector read/write visibility and Railway OAuth read.

## Decisions

Use a comparison link rather than automatic PR creation: the GitHub setting for bot PR creation also permits automated review approval. Keep that setting disabled; the connected GitHub tools can create an update PR when requested.
