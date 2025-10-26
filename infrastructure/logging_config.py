from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(logs_dir: Optional[Path] = None) -> logging.Logger:
    """Configure application logging and return the root ChillMCP logger."""
    if logs_dir is None:
        project_root = Path(__file__).resolve().parent.parent
        logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_filename = logs_dir / f"chill-mcp-{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
        ],
    )

    logger = logging.getLogger("ChillMCP")
    return logger
