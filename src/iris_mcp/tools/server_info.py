"""Tools for inspecting the IRIS server and its namespaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from ..client import IrisAtelierClient
    from ..config import Config


def register(mcp: "FastMCP", client: "IrisAtelierClient", config: "Config") -> None:
    @mcp.tool()
    async def iris_server_info() -> dict:
        """Return IRIS server metadata: version, Atelier API level, and the
        list of available namespaces. Use this first to confirm connectivity."""
        return await client.server_info()

    @mcp.tool()
    async def iris_list_namespaces() -> list[str]:
        """List the namespaces available on the IRIS server."""
        return await client.list_namespaces()
