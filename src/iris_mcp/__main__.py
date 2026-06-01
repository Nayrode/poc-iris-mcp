"""Console entry point: ``iris-mcp`` / ``python -m iris_mcp``."""

from __future__ import annotations

from .config import Config
from .server import run


def main() -> None:
    config = Config()
    print(
        f"Starting iris-mcp -> IRIS {config.api_base} (namespace {config.namespace}, "
        f"read_only={config.read_only})\n"
        f"Serving Streamable HTTP on http://{config.host}:{config.port}{config.mount_path}"
    )
    run(config)


if __name__ == "__main__":
    main()
