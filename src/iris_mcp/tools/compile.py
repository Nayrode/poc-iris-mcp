"""Tool for compiling IRIS documents (mutating)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from ..client import IrisAtelierClient
    from ..config import Config


def register(mcp: "FastMCP", client: "IrisAtelierClient", config: "Config") -> None:
    @mcp.tool()
    async def iris_compile_documents(
        names: list[str],
        namespace: str | None = None,
        flags: str = "cuk",
    ) -> dict:
        """Compile one or more IRIS documents and return the compiler output.

        Args:
            names: Document names with extension, e.g. ``["MyApp.Service.cls"]``.
            namespace: Target namespace (defaults to the configured one).
            flags: ObjectScript compile flags (default ``cuk``: compile, update,
                keep generated source).
        """
        ns = config.resolve_namespace(namespace)
        outcome = await client.compile_documents(ns, names, flags=flags)
        return {
            "namespace": ns,
            "compiled": names,
            "console": outcome.get("console", []),
        }
