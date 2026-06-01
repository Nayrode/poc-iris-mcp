"""Tool for running SQL queries against a namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from ..client import IrisAtelierClient
    from ..config import Config


def register(mcp: "FastMCP", client: "IrisAtelierClient", config: "Config") -> None:
    @mcp.tool()
    async def iris_run_query(
        query: str,
        parameters: list | None = None,
        namespace: str | None = None,
    ) -> list[dict]:
        """Run an SQL query in a namespace and return the resulting rows.

        Useful for exploring class definitions and data, e.g.
        ``SELECT Name FROM %Dictionary.ClassDefinition WHERE Name %STARTSWITH 'MyApp.'``.

        Args:
            query: SQL statement. Use ``?`` placeholders for parameters.
            parameters: Values bound to the ``?`` placeholders, in order.
            namespace: Target namespace (defaults to the configured one).
        """
        ns = config.resolve_namespace(namespace)
        return await client.run_query(ns, query, parameters)
