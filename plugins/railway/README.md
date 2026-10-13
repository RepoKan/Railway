# Railway

Deploy, configure, monitor, and troubleshoot apps and infrastructure on
[Railway](https://railway.com) from your coding agent.

## What's included

- **`use-railway` skill**: routes Railway requests to the right workflow:
  creating projects and services, deploying code, configuring environments,
  variables, and domains, provisioning databases and buckets, reading logs and
  metrics, and debugging failed builds or deployments.
- **Railway MCP server**: Railway's hosted MCP server at
  `https://mcp.railway.com`, authenticated with your Railway account over
  OAuth.

## Getting started

1. Install the plugin.
2. Connect your Railway account when prompted. If you don't have one, sign-in
   creates it.
3. Try a starter prompt:
   - "Deploy this app to Railway"
   - "Check the Railway status for this project"
   - "Debug my latest failed Railway deployment"

## Optional: Railway CLI

The hosted MCP server covers most platform operations without any local
install. For workflows that need your local machine, such as deploying the
current directory, SSH, or database analysis scripts, install the
[Railway CLI](https://docs.railway.com/cli):

```bash
curl -fsSL agents.railway.com | sh
```

The database analysis scripts also require `python3`.

## Links

- [Railway agent docs](https://docs.railway.com/agents)
- [Source](https://github.com/railwayapp/railway-skills)
- [Privacy policy](https://railway.com/legal/privacy)
- [Terms of service](https://railway.com/legal/terms)
