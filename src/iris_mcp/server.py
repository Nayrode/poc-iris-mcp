"""Assemble the FastMCP server from configuration and tool modules."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .client import IrisAtelierClient
from .config import Config
from .tools import register_all


def build_server(config: Config | None = None) -> FastMCP:
    """Build a configured FastMCP server.

    Exposed as a building block: a plugin can call ``build_server`` and then
    register additional tools on the returned instance before running it.
    """
    config = config or Config()
    mcp = FastMCP(
        "iris-mcp",
        host=config.host,
        port=config.port,
        streamable_http_path=config.mount_path,
    )
    client = IrisAtelierClient(config)
    register_all(mcp, client, config)
    return mcp


def run(config: Config | None = None) -> None:
    """Build and run the server over the Streamable HTTP transport."""
    build_server(config).run(transport="streamable-http")
