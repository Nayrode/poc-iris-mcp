"""Tools for viewing and editing IRIS documents (classes, routines, includes).

Split into ``register_read`` (always available) and ``register_write``
(skipped when the server runs read-only), so view and edit capabilities can be
enabled independently.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from ..client import IrisAtelierClient
    from ..config import Config


def register_read(mcp: "FastMCP", client: "IrisAtelierClient", config: "Config") -> None:
    @mcp.tool()
    async def iris_list_documents(
        namespace: str | None = None,
        category: str = "*",
        file_type: str = "*",
        filter_pattern: str = "",
        include_generated: bool = False,
    ) -> list[dict]:
        """List documents in a namespace.

        Args:
            namespace: Target namespace (defaults to the configured one).
            category: CLS (classes), RTN (routines), CSP, OTH, or * for all.
            file_type: Extension filter such as ``cls``, ``mac``, ``inc`` or ``*``.
            filter_pattern: SQL-LIKE pattern on the document name, e.g. ``MyApp.%``.
            include_generated: Include generated documents.
        """
        ns = config.resolve_namespace(namespace)
        return await client.list_documents(
            ns,
            category=category,
            file_type=file_type,
            generated=include_generated,
            filter_pattern=filter_pattern,
        )

    @mcp.tool()
    async def iris_read_document(name: str, namespace: str | None = None) -> str:
        """Read the source of an IRIS document.

        Args:
            name: Document name with extension, e.g. ``MyApp.Service.cls``,
                ``MyRoutine.mac`` or ``MyApp.Includes.inc``.
            namespace: Target namespace (defaults to the configured one).
        """
        ns = config.resolve_namespace(namespace)
        doc = await client.get_document(ns, name)
        lines = doc.get("content", [])
        return "\n".join(lines)


def register_write(mcp: "FastMCP", client: "IrisAtelierClient", config: "Config") -> None:
    @mcp.tool()
    async def iris_write_document(
        name: str, content: str, namespace: str | None = None
    ) -> str:
        """Create or overwrite an IRIS document with new source code.

        The full document body must be supplied. For a class, the first line is
        typically ``Class Package.Name Extends %RegisteredObject``. Save does not
        compile — call ``iris_compile_documents`` afterwards.

        Args:
            name: Document name with extension, e.g. ``MyApp.Service.cls``.
            content: Full source text (newline-separated).
            namespace: Target namespace (defaults to the configured one).
        """
        ns = config.resolve_namespace(namespace)
        lines = content.split("\n")
        result = await client.put_document(ns, name, lines)
        saved = result.get("name", name)
        return f"Saved {saved} in {ns}."

    @mcp.tool()
    async def iris_delete_document(name: str, namespace: str | None = None) -> str:
        """Delete an IRIS document.

        Args:
            name: Document name with extension, e.g. ``MyApp.Old.cls``.
            namespace: Target namespace (defaults to the configured one).
        """
        ns = config.resolve_namespace(namespace)
        await client.delete_document(ns, name)
        return f"Deleted {name} from {ns}."
