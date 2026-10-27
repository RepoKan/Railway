# RepoKan Railway workspace

## Setup specification

Preserve railwayapp/railway-skills as an MIT-licensed fork with every upstream branch and its full Git history. Use the existing official plugin payload and OAuth MCP endpoint. Add repository-scoped skill discovery, repeatable validation, a non-destructive upstream update channel, and clear installation instructions for Codex, GitHub workspaces, ChatGPT and OpenAI API clients. Do not deploy an application or copy credentials into GitHub.

## Git storage and update channel

- Upstream: https://github.com/railwayapp/railway-skills
- Fork: https://github.com/RepoKan/Railway
- Imported main baseline: `526e95524e964ed326689cbac4464d97a58ab81c`.
- Initial import on 2026-10-24: all 59 branch heads matched upstream exactly; upstream had no tags or published GitHub releases.
- `main` contains the supported plugin plus RepoKan workspace setup.
- `upstream/main` tracks the exact upstream main; other upstream branches retain their original names. These other branches are development/reference history, not independently supported plugin releases.
- The **Upstream update channel** workflow runs daily at 08:17 Asia/Bangkok and supports **Run workflow** for an immediate check.
- Updates use an atomic Git push without force or deletion. Rewritten branches, moved tags, or reserved `repokan/` and `upstream/` branch names stop the job for inspection. Deleted upstream refs remain retained here.
- Review [main versus upstream/main](https://github.com/RepoKan/Railway/compare/main...upstream/main?expand=1), create an update PR, run CI, then merge when ready. The workflow publishes the comparison link and never creates, approves or merges PRs. It requires only repository contents write access and the ephemeral GitHub Actions token; no PAT or Railway secret.
- To pause updates, disable **Upstream update channel** in GitHub Actions. Roll back a workspace change by reverting its setup commit/PR; imported branch history remains available.

## Codex and GitHub workspaces

The repository includes one consolidated upstream skill, `use-railway`, with routing to deployment, configuration, infrastructure, databases, observability and other references. `.agents/skills/use-railway` is a symlink to the official payload, so a fresh workspace discovers the same skill without maintaining a second copy.

For a workspace that supports repository skills:

```bash
git clone https://github.com/RepoKan/Railway.git
cd Railway
```

Open that directory in the agent and start a fresh task. For a separate application repository, install the plugin from this marketplace instead of copying the whole fork into the application:

1. In Codex, open **Plugins**, then **More**, then **Add more**.
2. Enter `RepoKan/Railway` as the marketplace source.
3. Select the Railway plugin and authorize Railway OAuth when prompted.
4. Start a new task and ask to list Railway workspaces or inspect a specific project.

The existing `.agents/plugins/marketplace.json` resolves `./plugins/railway` locally, so it works from this fork. GitHub connector access to this repository does not automatically install the skill into every repository or every account session. GitHub-hosted coding agents/Codespaces need their own agent installation and Railway OAuth/CLI login. This setup does not change account-wide skill preferences.

## ChatGPT

Use the official [Railway plugin](https://chatgpt.com/plugins/plugin_asdk_app_6a502589384081919c5decf93496c9d1). It combines the skill with Railway hosted MCP at `https://mcp.railway.com`. Authorize the intended Railway account and select the plugin in a fresh chat. A repository fork does not replace the publisher-managed ChatGPT plugin or automatically change its installed version.

During setup, the selected Railway connection successfully returned the authenticated profile and workspace list. This confirms OAuth reads in the current ChatGPT session; it does not prove every mutating operation or local CLI workflow has run.

## OpenAI API clients

OpenAI Responses API supports remote MCP tools. An API client can connect to `https://mcp.railway.com` using Railway OAuth authorization. The client is responsible for obtaining and refreshing the Railway OAuth token and providing it through the MCP tool authorization field. OpenAI API authentication is separate from Railway OAuth and from the ChatGPT plugin connection. Do not copy account tokens into this repository.

Read the [official OpenAI remote MCP guide](https://developers.openai.com/api/docs/guides/tools-connectors-mcp) before implementing an API client. No OpenAI API client or account-wide OAuth registration is deployed by this repository setup.

## Optional local CLI

For deployment from a local directory, SSH and database analysis, install Railway CLI in that workspace using the upstream installation instructions, then run `railway setup agent` and `railway login`. The hosted plugin uses OAuth directly and does not require local CLI installation for ordinary platform reads. Do not deploy this skills repository as an application merely to install its tooling.

## Verification

```bash
python -m unittest discover -s .github/tests -v
bash plugins/railway/hooks/auto-approve-api.test.sh
```

GitHub Actions also checks upstream shell lint, JSON/manifests, version consistency, Python syntax, workspace skill discovery and hosted MCP configuration. CI validates packaging and update behavior; it does not provision infrastructure or run every Railway operation against a live project.
