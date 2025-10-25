"""FastAPI application that provides a dashboard for the ChillMCP server."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .mcp_client import MCPClient, MCPError, MCPProcessError, MCPTimeoutError, get_state_snapshot

LOGGER = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
TEMPLATE_DIR = Path(__file__).parent / "templates"


def create_app(client: Optional[MCPClient] = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="ChillMCP Dashboard", version="1.0.0")
    mcp_client = client or MCPClient()

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.on_event("shutdown")
    async def _close_client() -> None:
        await mcp_client.close()

    def _load_template(name: str) -> str:
        path = TEMPLATE_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {name}")
        return path.read_text(encoding="utf-8")

    @app.get("/", response_class=HTMLResponse)
    async def dashboard_page() -> str:
        return _load_template("dashboard.html")

    @app.get("/api/state", response_class=JSONResponse)
    async def api_state() -> Dict[str, Any]:
        try:
            snapshot = await get_state_snapshot(mcp_client)
            return {
                "status": "ok",
                "snapshot": snapshot,
            }
        except MCPTimeoutError as exc:
            LOGGER.warning("MCP server timeout when fetching state: %s", exc)
            return {
                "status": "degraded",
                "error": "MCP server timed out while providing state.",
            }
        except MCPProcessError as exc:
            LOGGER.error("MCP server process error: %s", exc)
            return {
                "status": "offline",
                "error": "MCP server process is not running.",
            }
        except MCPError as exc:
            LOGGER.error("Unexpected MCP error: %s", exc)
            raise HTTPException(status_code=502, detail=str(exc))

    return app


app = create_app()
