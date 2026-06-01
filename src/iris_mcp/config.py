"""Configuration for the IRIS MCP server.

All settings are read from environment variables (prefixed ``IRIS_MCP_``) or a
local ``.env`` file. Instantiating :class:`Config` with explicit keyword
arguments is also supported, which is handy when a plugin embeds the server.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Config(BaseSettings):
    """Runtime configuration for the IRIS MCP server."""

    model_config = SettingsConfigDict(
        env_prefix="IRIS_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- IRIS connection ---
    base_url: str = Field(
        default="http://localhost:52773",
        description="Base URL of the IRIS web server (management port).",
    )
    api_path: str = Field(
        default="/api/atelier",
        description="Path prefix of the Atelier REST API.",
    )
    username: str = Field(default="superuser")
    password: str = Field(default="SYS")
    namespace: str = Field(
        default="USER",
        description="Default namespace used when a tool omits one.",
    )
    # NoDecode: don't let pydantic-settings JSON-parse this; the validator
    # below splits a plain comma-separated env string instead.
    allowed_namespaces: Annotated[list[str], NoDecode] = Field(
        default_factory=list,
        description="Allowlist of namespaces (empty = any namespace permitted).",
    )
    verify_ssl: bool = Field(default=False)
    timeout: float = Field(default=30.0)

    # --- Safety ---
    read_only: bool = Field(
        default=False,
        description="When true, mutating tools (save/delete/compile) are not registered.",
    )

    # --- MCP transport (Streamable HTTP) ---
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    mount_path: str = Field(default="/mcp")

    @field_validator("allowed_namespaces", mode="before")
    @classmethod
    def _split_namespaces(cls, value: object) -> object:
        """Accept a comma-separated string from the environment."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def api_base(self) -> str:
        """Fully-qualified Atelier API base, e.g. ``http://host:52773/api/atelier``."""
        return f"{self.base_url.rstrip('/')}{self.api_path}"

    def resolve_namespace(self, namespace: str | None) -> str:
        """Return a usable namespace, validating it against the allowlist."""
        ns = (namespace or self.namespace).strip()
        if self.allowed_namespaces and ns.upper() not in {
            n.upper() for n in self.allowed_namespaces
        }:
            allowed = ", ".join(self.allowed_namespaces)
            raise ValueError(
                f"Namespace {ns!r} is not allowed. Permitted: {allowed}"
            )
        return ns
