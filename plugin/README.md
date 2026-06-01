# iris-code (Claude Code plugin)

A Claude Code plugin that brings InterSystems IRIS code editing into Claude. It
bundles the [`iris-mcp`](../README.md) server and adds commands, an agent, and a
skill for working with ObjectScript on a live IRIS instance.

## What's inside

| Component | Name | Purpose |
|-----------|------|---------|
| MCP server | `iris` | view/edit/compile/query IRIS code (declared in `.mcp.json`) |
| Command | `/iris-explore` | browse namespaces, classes, routines, source |
| Command | `/iris-query` | run an SQL query against a namespace |
| Command | `/iris-edit` | edit/create a document and compile it |
| Agent | `iris-developer` | specialist subagent for IRIS/ObjectScript work |
| Skill | `iris-objectscript` | conventions + read→edit→compile→verify workflow |

## Prerequisites

1. IRIS running (`docker compose up -d` in the project root).
2. The `iris-mcp` server running and reachable over HTTP:
   ```bash
   uv run iris-mcp        # serves http://127.0.0.1:8000/mcp
   ```
   Override the URL the plugin connects to with `IRIS_MCP_URL` if needed.

## Install

From the project root (which contains the marketplace manifest):

```text
/plugin marketplace add /home/dtetu/Documents/poc-iris-mcp
/plugin install iris-code@iris-tools
```

Then verify the MCP server is connected with `/mcp` and try `/iris-explore`.

## Configuration

The plugin connects to the MCP server's HTTP URL (`.mcp.json`):

```json
{ "mcpServers": { "iris": { "type": "http", "url": "${IRIS_MCP_URL:-http://127.0.0.1:8000/mcp}" } } }
```

All IRIS-side configuration (credentials, default namespace, read-only mode,
namespace allowlist) lives with the `iris-mcp` server — see the project
[`.env.example`](../.env.example). Running the server with
`IRIS_MCP_READ_ONLY=true` makes the plugin view-only.

## Editor IntelliSense (InterSystems Language Server)

This plugin handles programmatic view/edit/compile/query. For interactive editing
with hover, go-to-definition and completion, use the official **InterSystems
Language Server** in VS Code. The repository ships `.vscode/extensions.json`
(recommended extensions) and `.vscode/settings.json` (a `iris-local` server
connection on port 52773). Open the project in VS Code, install the recommended
extensions, and accept the password prompt on first connect.
