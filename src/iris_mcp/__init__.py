"""Modular MCP server for InterSystems IRIS code via the Atelier REST API."""

from .client import IrisAtelierClient, IrisError
from .config import Config
from .server import build_server, run

__all__ = ["Config", "IrisAtelierClient", "IrisError", "build_server", "run"]
__version__ = "0.1.0"
