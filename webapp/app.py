"""FastAPI application that provides a dashboard for the ChillMCP server."""

from __future__ import annotations

import logging
import asyncio
import re
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .mcp_client import MCPClient, MCPError, MCPProcessError, MCPTimeoutError, get_state_snapshot
from .memes import select_meme

LOGGER = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
TEMPLATE_DIR = Path(__file__).parent / "templates"

ACTION_TOOLS: List[Dict[str, str]] = [
    {"name": "take_a_break", "label": "Take a Break", "emoji": "😌", "description": "기본 휴식으로 스트레스를 낮춥니다."},
    {"name": "watch_netflix", "label": "Watch Netflix", "emoji": "📺", "description": "넷플릭스로 여유를 즐깁니다."},
    {"name": "show_meme", "label": "Show Meme", "emoji": "😂", "description": "짧은 밈 타임으로 스트레스 해소."},
    {"name": "bathroom_break", "label": "Bathroom Break", "emoji": "🚽", "description": "화장실로 가서 몰래 쉬어요."},
    {"name": "coffee_mission", "label": "Coffee Mission", "emoji": "☕", "description": "커피 핑계로 사무실을 한 바퀴."},
    {"name": "urgent_call", "label": "Urgent Call", "emoji": "📞", "description": "급한 전화를 받는 척 밖으로 나갑니다."},
    {"name": "deep_thinking", "label": "Deep Thinking", "emoji": "🤔", "description": "심각한 척 멍 때리기."},
    {"name": "email_organizing", "label": "Email Organizing", "emoji": "📧", "description": "이메일 정리하는 척 온라인 쇼핑."},
    {"name": "chimaek", "label": "Chimaek", "emoji": "🍗", "description": "가상의 치맥으로 기분 전환."},
    {"name": "leave_work", "label": "Leave Work", "emoji": "🏃", "description": "퇴근 선언으로 스트레스 제로."},
    {"name": "company_dinner", "label": "Company Dinner", "emoji": "🍻", "description": "회식 랜덤 이벤트를 체험합니다."},
]

SUMMARY_PATTERN = re.compile(r"Break Summary:\s*(.+)")
STRESS_PATTERN = re.compile(r"Stress Level:\s*(\d{1,3})")
BOSS_PATTERN = re.compile(r"Boss Alert Level:\s*([0-5])")

EVENT_LOG: deque[Dict[str, Any]] = deque(maxlen=30)
EVENT_LOCK = asyncio.Lock()


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def parse_tool_response(text: str) -> Dict[str, Any]:
    """Parse the standard ChillMCP response format into structured data."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Empty tool response")

    first_line = lines[0]
    parts = first_line.split(" ", 1)
    emoji = parts[0]
    message = parts[1] if len(parts) > 1 else ""

    summary_match = SUMMARY_PATTERN.search(text)
    stress_match = STRESS_PATTERN.search(text)
    boss_match = BOSS_PATTERN.search(text)

    return {
        "raw_text": text,
        "emoji": emoji,
        "message": message,
        "break_summary": summary_match.group(1).strip() if summary_match else "",
        "stress_level": int(stress_match.group(1)) if stress_match else None,
        "boss_alert_level": int(boss_match.group(1)) if boss_match else None,
    }


async def record_event(entry: Dict[str, Any]) -> None:
    async with EVENT_LOCK:
        EVENT_LOG.appendleft(entry)


def create_app(client: Optional[MCPClient] = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="ChillMCP Dashboard", version="1.0.0")
    mcp_client = client or MCPClient()
    tool_lookup = {tool["name"]: tool for tool in ACTION_TOOLS}

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

    @app.get("/actions", response_class=HTMLResponse)
    async def actions_page() -> str:
        return _load_template("actions.html")

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

    @app.get("/api/actions", response_class=JSONResponse)
    async def api_actions() -> Dict[str, Any]:
        return {"actions": ACTION_TOOLS}

    @app.get("/api/events", response_class=JSONResponse)
    async def api_events() -> Dict[str, Any]:
        async with EVENT_LOCK:
            events = list(EVENT_LOG)
        return {"events": events}

    @app.post("/api/actions/{tool_name}", response_class=JSONResponse)
    async def api_trigger_action(tool_name: str) -> Dict[str, Any]:
        tool_meta = tool_lookup.get(tool_name)
        if not tool_meta:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")

        try:
            text = await mcp_client.call_tool_text(tool_name, timeout=35.0)
            parsed = parse_tool_response(text)
            timestamp = _now_iso()
            snapshot = await get_state_snapshot(mcp_client)
            meme = select_meme(tool_name, parsed, snapshot)

            event_entry = {
                "id": f"{tool_name}-{timestamp}",
                "tool": tool_name,
                "timestamp": timestamp,
                "label": tool_meta["label"],
                **parsed,
                "cooldown_seconds_remaining": snapshot.get("cooldown_seconds_remaining"),
                "meme": meme,
            }
            await record_event(event_entry)

            return {
                "status": "ok",
                "tool": tool_meta,
                "result": parsed,
                "snapshot": snapshot,
                "meme": meme,
            }
        except MCPTimeoutError as exc:
            LOGGER.warning("MCP timeout while running %s: %s", tool_name, exc)
            return JSONResponse(
                status_code=504,
                content={
                    "status": "timeout",
                    "error": "MCP server did not respond in time. Boss alert 5 delay?",
                },
            )
        except MCPProcessError as exc:
            LOGGER.error("MCP process error during %s: %s", tool_name, exc)
            return JSONResponse(
                status_code=503,
                content={
                    "status": "offline",
                    "error": "MCP server process is not running.",
                },
            )
        except MCPError as exc:
            LOGGER.error("Unexpected MCP error during %s: %s", tool_name, exc)
            raise HTTPException(status_code=502, detail=str(exc))
        except ValueError as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return app


app = create_app()
