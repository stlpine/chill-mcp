#!/usr/bin/env python3
"""Entry point for the ChillMCP server."""

from __future__ import annotations

import sys

from infrastructure.cli import parse_runtime_config
from infrastructure.logging_config import setup_logging


def main(argv: list[str] | None = None) -> int:
    config = parse_runtime_config(argv)
    logger = setup_logging()

    from application.controller import ChillController  # Lazy import

    controller = ChillController(config=config, logger=logger)

    try:
        controller.start()
    except KeyboardInterrupt:
        logger.info("ChillMCP server stopped by user")
    except Exception as exc:  # pragma: no cover - top-level guard
        logger.error("ChillMCP server error: %s", exc)
        raise
    finally:
        controller.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
