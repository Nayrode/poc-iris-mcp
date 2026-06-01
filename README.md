# iris-mcp

A modular, configurable **MCP server** for viewing and editing **InterSystems IRIS**
code. It talks to IRIS through the **Atelier REST API** (`/api/atelier/`) — the same
interface the VS Code ObjectScript extension uses — and exposes the operations as MCP
tools over the **Streamable HTTP** transport.

It is designed to be embedded: a plugin can import `build_server()`, reuse the
`IrisAtelierClient`, or register only the tool modules it needs.

## Tools

| Tool | Purpose | Mutating |
|------|---------|----------|
| `iris_server_info` | Server version, API level, namespaces | no |
| `iris_list_namespaces` | List available namespaces | no |
| `iris_list_documents` | List classes/routines/includes in a namespace | no |
| `iris_read_document` | Read a document's source | no |
| `iris_run_query` | Run an SQL query | no |
| `iris_write_document` | Create/overwrite a document | yes |
| `iris_delete_document` | Delete a document | yes |
| `iris_compile_documents` | Compile documents | yes |

When `IRIS_MCP_READ_ONLY=true`, the mutating tools are not registered.

## Layout

```
src/iris_mcp/
  config.py        # env/.env driven configuration (Config)
  client.py        # IrisAtelierClient — async Atelier API wrapper (no MCP deps)
  server.py        # build_server() / run() — assembles FastMCP
  __main__.py      # `iris-mcp` console entry point
  tools/
    __init__.py    # register_all(); READ_ONLY_MODULES / MUTATING_MODULES
    server_info.py
    documents.py   # register_read() + register_write()
    compile.py
    query.py
```

Each tool module exposes a `register(mcp, client, config)` function, so the tool set
is composable rather than monolithic.

## Configuration

All settings come from environment variables (prefix `IRIS_MCP_`) or a `.env` file.
See [`.env.example`](.env.example). Key ones:

| Variable | Default | Meaning |
|----------|---------|---------|
| `IRIS_MCP_BASE_URL` | `http://localhost:52773` | IRIS web/management URL |
| `IRIS_MCP_USERNAME` / `IRIS_MCP_PASSWORD` | `_SYSTEM` / `SYS` | IRIS credentials |
| `IRIS_MCP_NAMESPACE` | `USER` | Default namespace |
| `IRIS_MCP_ALLOWED_NAMESPACES` | *(empty)* | Comma-separated allowlist (empty = any) |
| `IRIS_MCP_READ_ONLY` | `false` | Disable mutating tools |
| `IRIS_MCP_HOST` / `IRIS_MCP_PORT` / `IRIS_MCP_MOUNT_PATH` | `127.0.0.1` / `8000` / `/mcp` | HTTP transport |

## Running

```bash
# 1. Start IRIS
docker compose up -d

# 2. Install and run the MCP server
uv venv
uv pip install -e .
cp .env.example .env   # edit as needed
uv run iris-mcp
```

The server listens on `http://127.0.0.1:8000/mcp`.

## Connecting a client

Point any Streamable HTTP MCP client at the mount URL. Example client config:

```json
{
  "mcpServers": {
    "iris": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

## Embedding in a plugin

```python
from iris_mcp import build_server, Config

mcp = build_server(Config(namespace="MYAPP", read_only=True))

@mcp.tool()
async def my_extra_tool() -> str:
    ...

mcp.run(transport="streamable-http")
```

## Claude Code plugin

A ready-made Claude Code plugin lives in [`plugin/`](plugin/README.md) and is
published via the marketplace manifest at `.claude-plugin/marketplace.json`. It
bundles this MCP server plus `/iris-explore`, `/iris-query`, `/iris-edit`
commands, an `iris-developer` agent, and an `iris-objectscript` skill.

```text
# with `uv run iris-mcp` already running:
/plugin marketplace add /home/dtetu/Documents/poc-iris-mcp
/plugin install iris-code@iris-tools
```

## Editor IntelliSense (InterSystems Language Server)

The MCP server/plugin cover programmatic view/edit/compile/query. For interactive
IntelliSense (hover, go-to-definition, completion) use the official **InterSystems
Language Server** in VS Code. This repo ships:

- `.vscode/extensions.json` — recommends `intersystems.language-server`,
  `intersystems-community.vscode-objectscript`, `intersystems-community.servermanager`.
- `.vscode/settings.json` — defines an `iris-local` server (port 52773, user
  `superuser`) and an active `USER` connection. The password is prompted on first
  connect and stored in the OS keychain, not in the file.

Open the project in VS Code, install the recommended extensions, and accept the
password prompt — the Language Server then reads class definitions from IRIS to
power IntelliSense.
