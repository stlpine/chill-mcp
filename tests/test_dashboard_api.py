#!/usr/bin/env python3
"""FastAPI dashboard API tests executed as a standalone script."""


from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta
from typing import List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from fastapi.testclient import TestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TestClient = None  # type: ignore

if FASTAPI_AVAILABLE:
    from webapp.app import ACTION_TOOLS, EVENT_LOG, create_app
    from webapp.mcp_client import MCPTimeoutError
else:  # pragma: no cover
    ACTION_TOOLS = []  # type: ignore
    EVENT_LOG = None  # type: ignore
    MCPTimeoutError = RuntimeError  # type: ignore


class FakeMCPClient:
    """Deterministic stand-in for the MCP server used by dashboard tests."""

    def __init__(self) -> None:
        self.stress_level = 52
        self.boss_alert_level = 1
        self.cooldown_seconds = 180
        self.delay_active = False
        self.next_timeout: set[str] = set()
        self.calls: List[str] = []
        self._last_break = datetime.utcnow() - timedelta(minutes=5)
        self._last_cooldown = datetime.utcnow() - timedelta(seconds=90)

    def _snapshot_payload(self) -> dict:
        now = datetime.utcnow()
        elapsed_break = (now - self._last_break).total_seconds()
        elapsed_cooldown = (now - self._last_cooldown).total_seconds()
        remaining = max(0.0, self.cooldown_seconds - elapsed_cooldown)
        return {
            "timestamp": now.isoformat(),
            "stress_level": self.stress_level,
            "boss_alert_level": self.boss_alert_level,
            "boss_alertness": 50,
            "boss_alertness_cooldown": self.cooldown_seconds,
            "seconds_since_last_break": elapsed_break,
            "cooldown_seconds_remaining": remaining,
            "delay_seconds_remaining": 20.0 if self.delay_active else 0.0,
            "delay_active": self.delay_active,
            "last_break_time": self._last_break.isoformat(),
            "last_boss_cooldown_time": self._last_cooldown.isoformat(),
        }

    async def call_tool_text(self, tool_name: str, **_: dict) -> str:
        self.calls.append(tool_name)
        if tool_name in self.next_timeout:
            self.next_timeout.remove(tool_name)
            raise MCPTimeoutError("simulated timeout")

        if tool_name == "get_state_snapshot":
            return json.dumps(self._snapshot_payload())

        # Simulate tool execution and state changes.
        self.stress_level = max(0, self.stress_level - 7)
        self.boss_alert_level = min(5, self.boss_alert_level + 1)
        self.delay_active = self.boss_alert_level >= 4
        self._last_break = datetime.utcnow()
        if self.boss_alert_level > 0:
            self._last_cooldown = datetime.utcnow()

        return (
            "😌 Test Action\n\n"
            "Break Summary: Testing dashboard action\n"
            f"Stress Level: {self.stress_level}\n"
            f"Boss Alert Level: {self.boss_alert_level}"
        )

    async def close(self) -> None:
        return


def _make_client(fake: FakeMCPClient) -> TestClient:
    EVENT_LOG.clear()
    app = create_app(fake)
    return TestClient(app)


def run_state_endpoint_returns_snapshot() -> bool:
    fake = FakeMCPClient()
    try:
        with _make_client(fake) as client:
            response = client.get("/api/state")
            data = response.json()
        return (
            response.status_code == 200
            and data["status"] == "ok"
            and data["snapshot"]["stress_level"] == fake.stress_level
            and fake.calls.count("get_state_snapshot") == 1
        )
    except Exception as exc:
        print(f"  ✗ state endpoint error: {exc}")
        return False


def run_actions_catalog_lists_configured_tools() -> bool:
    fake = FakeMCPClient()
    try:
        with _make_client(fake) as client:
            response = client.get("/api/actions")
            data = response.json()
        names = {item["name"] for item in data["actions"]}
        expected = {tool["name"] for tool in ACTION_TOOLS}
        return response.status_code == 200 and names == expected
    except Exception as exc:
        print(f"  ✗ actions catalog error: {exc}")
        return False


def run_action_execution_updates_events() -> bool:
    fake = FakeMCPClient()
    try:
        with _make_client(fake) as client:
            response = client.post("/api/actions/take_a_break")
            payload = response.json()
            events_response = client.get("/api/events")
            events_payload = events_response.json()
        return (
            response.status_code == 200
            and payload["status"] == "ok"
            and payload["meme"]["image"].endswith(".svg")
            and len(events_payload["events"]) == 1
            and events_payload["events"][0]["tool"] == "take_a_break"
        )
    except Exception as exc:
        print(f"  ✗ action execution error: {exc}")
        return False


def run_unknown_tool_returns_404() -> bool:
    fake = FakeMCPClient()
    try:
        with _make_client(fake) as client:
            response = client.post("/api/actions/unknown_tool")
        return response.status_code == 404
    except Exception as exc:
        print(f"  ✗ unknown tool error: {exc}")
        return False


def run_state_timeout_path() -> bool:
    fake = FakeMCPClient()
    fake.next_timeout.add("get_state_snapshot")
    try:
        with _make_client(fake) as client:
            response = client.get("/api/state")
            data = response.json()
        return response.status_code == 200 and data["status"] == "degraded"
    except Exception as exc:
        print(f"  ✗ timeout path error: {exc}")
        return False


def run_html_routes_render() -> bool:
    fake = FakeMCPClient()
    try:
        with _make_client(fake) as client:
            root_ok = client.get("/").status_code == 200
            actions_ok = client.get("/actions").status_code == 200
        return root_ok and actions_ok
    except Exception as exc:
        print(f"  ✗ html route error: {exc}")
        return False


def main() -> None:
    print("\n[Dashboard API Tests]")
    results = [
        ("State endpoint returns snapshot", run_state_endpoint_returns_snapshot()),
        ("Actions catalog lists configured tools", run_actions_catalog_lists_configured_tools()),
        ("Action execution updates events and meme", run_action_execution_updates_events()),
        ("Unknown tool returns 404", run_unknown_tool_returns_404()),
        ("State endpoint handles timeout", run_state_timeout_path()),
        ("Dashboard HTML pages render", run_html_routes_render()),
    ]

    for description, passed in results:
        mark = "✓" if passed else "✗"
        print(f"  {mark} {description}")


if __name__ == "__main__":
    main()
