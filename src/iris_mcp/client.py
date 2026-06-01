"""Thin async client around the InterSystems IRIS Atelier REST API.

The Atelier API is the same interface the VS Code ObjectScript extension uses.
It speaks JSON over the IRIS web port and wraps every response in an envelope::

    {
      "status":  {"errors": [...], "summary": "..."},
      "console": [...],
      "result":  {...}
    }

This client unwraps that envelope, raises on errors, and exposes one method per
operation the MCP tools need. It is intentionally transport-agnostic and holds
no MCP concepts, so it can be reused directly by a plugin.
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import Config


class IrisError(RuntimeError):
    """Raised when IRIS returns an error envelope or a non-2xx HTTP status."""


class IrisAtelierClient:
    """Reusable async client for the Atelier API."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._client: httpx.AsyncClient | None = None

    # -- lifecycle ---------------------------------------------------------
    def _ac(self) -> httpx.AsyncClient:
        """Lazily create and reuse a single AsyncClient."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._config.api_base,
                auth=(self._config.username, self._config.password),
                verify=self._config.verify_ssl,
                timeout=self._config.timeout,
                headers={"Accept": "application/json"},
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # -- low-level request -------------------------------------------------
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        """Send a request and return the unwrapped ``result`` payload."""
        try:
            response = await self._ac().request(
                method, path, params=params, json=json
            )
        except httpx.RequestError as exc:  # network/connection failures
            raise IrisError(f"Could not reach IRIS at {self._config.api_base}: {exc}") from exc

        if response.status_code == 401:
            raise IrisError(
                "Authentication failed (401). Check IRIS_MCP_USERNAME / IRIS_MCP_PASSWORD."
            )

        try:
            envelope = response.json()
        except ValueError:
            response.raise_for_status()
            raise IrisError(
                f"IRIS returned a non-JSON response ({response.status_code})."
            )

        errors = (envelope.get("status") or {}).get("errors") or []
        if errors:
            raise IrisError("; ".join(str(e) for e in errors))

        if response.status_code >= 400:
            raise IrisError(f"IRIS HTTP {response.status_code}: {envelope}")

        return envelope

    # -- server / namespaces ----------------------------------------------
    async def server_info(self) -> dict[str, Any]:
        env = await self._request("GET", "/")
        return env.get("result", {}).get("content", {})

    async def list_namespaces(self) -> list[str]:
        content = await self.server_info()
        return content.get("namespaces", [])

    # -- documents (classes, routines, includes, etc.) --------------------
    async def list_documents(
        self,
        namespace: str,
        *,
        category: str = "*",
        file_type: str = "*",
        generated: bool = False,
        filter_pattern: str = "",
    ) -> list[dict[str, Any]]:
        """List document names. ``category`` is CLS/RTN/CSP/OTH/* and
        ``file_type`` filters by extension (e.g. ``cls``, ``mac``, ``*``)."""
        path = f"/v1/{namespace}/docnames/{category}/{file_type}"
        params: dict[str, Any] = {"generated": int(generated)}
        if filter_pattern:
            params["filter"] = filter_pattern
        env = await self._request("GET", path, params=params)
        return env.get("result", {}).get("content", [])

    async def get_document(self, namespace: str, name: str) -> dict[str, Any]:
        """Fetch a document. Returns the ``result`` block including
        ``content`` (list of lines), ``ts``, ``cat`` and ``enc``."""
        env = await self._request("GET", f"/v1/{namespace}/doc/{name}")
        return env.get("result", {})

    async def put_document(
        self, namespace: str, name: str, content: list[str]
    ) -> dict[str, Any]:
        """Create or overwrite a document from a list of source lines."""
        body = {"enc": False, "content": content}
        env = await self._request(
            "PUT",
            f"/v1/{namespace}/doc/{name}",
            params={"ignoreConflict": 1},
            json=body,
        )
        return env.get("result", {})

    async def delete_document(self, namespace: str, name: str) -> dict[str, Any]:
        env = await self._request("DELETE", f"/v1/{namespace}/doc/{name}")
        return env.get("result", {})

    # -- actions -----------------------------------------------------------
    async def compile_documents(
        self, namespace: str, names: list[str], *, flags: str = "cuk"
    ) -> dict[str, Any]:
        """Compile one or more documents. ``flags`` follows ObjectScript
        compile flags (``c`` compile, ``u`` update, ``k`` keep generated)."""
        env = await self._request(
            "POST",
            f"/v1/{namespace}/action/compile",
            params={"flags": flags},
            json=names,
        )
        return {
            "result": env.get("result", {}),
            "console": env.get("console", []),
        }

    async def run_query(
        self, namespace: str, query: str, parameters: list[Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute an SQL query and return the rows."""
        body = {"query": query, "parameters": parameters or []}
        env = await self._request("POST", f"/v1/{namespace}/action/query", json=body)
        return env.get("result", {}).get("content", [])
