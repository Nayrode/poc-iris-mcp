"""Tool registry.

Every tool module exposes ``register(mcp, client, config)``. ``register_all``
wires them onto a FastMCP instance. Modules are intentionally independent so a
plugin can import and register only the subset it needs, or append its own.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from . import compile as compile_tools
from . import documents, query, server_info

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from ..client import IrisAtelierClient
    from ..config import Config

# Read-only modules are always registered; mutating modules are skipped when
# the server is configured ``read_only``.
READ_ONLY_MODULES: list[Callable] = [server_info.register, documents.register_read, query.register]
MUTATING_MODULES: list[Callable] = [documents.register_write, compile_tools.register]


def register_all(mcp: "FastMCP", client: "IrisAtelierClient", config: "Config") -> None:
    for register in READ_ONLY_MODULES:
        register(mcp, client, config)
    if not config.read_only:
        for register in MUTATING_MODULES:
            register(mcp, client, config)


__all__ = ["register_all", "READ_ONLY_MODULES", "MUTATING_MODULES"]
