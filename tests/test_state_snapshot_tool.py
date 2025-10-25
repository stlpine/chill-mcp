#!/usr/bin/env python3
"""Tests for the get_state_snapshot MCP tool."""

import json
import os
import subprocess
import sys
import time
from typing import Any, Dict

try:
    import fastmcp  # noqa: F401

    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PATH = sys.executable
MAIN_PATH = os.path.join(PROJECT_ROOT, "main.py")


def send_mcp_request(process: subprocess.Popen[str], request: Dict[str, Any]) -> Dict[str, Any]:
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    while True:
        response_line = process.stdout.readline()
        if not response_line:
            return {}
        response_line = response_line.strip()
        if response_line:
            return json.loads(response_line)


def initialize_mcp_session(process: subprocess.Popen[str]) -> None:
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "snapshot-test", "version": "1.0.0"},
        },
    }
    send_mcp_request(process, init_request)
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()


def call_tool(process: subprocess.Popen[str], tool_name: str, request_id: int = 2) -> str:
    call_request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": {}},
    }
    response = send_mcp_request(process, call_request)
    contents = response.get("result", {}).get("content", [])
    if contents and contents[0].get("type") == "text":
        return contents[0]["text"]
    raise AssertionError(f"Unexpected tool response payload: {response}")


def test_get_state_snapshot_returns_valid_json() -> bool:
    process = subprocess.Popen(
        [
            PYTHON_PATH,
            MAIN_PATH,
            "--boss_alertness",
            "0",
            "--boss_alertness_cooldown",
            "60",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,
    )

    time.sleep(1)

    try:
        initialize_mcp_session(process)
        snapshot_text = call_tool(process, "get_state_snapshot")
        snapshot = json.loads(snapshot_text)

        checks = [
            snapshot["stress_level"] >= 0,
            0 <= snapshot["boss_alert_level"] <= 5,
            "cooldown_seconds_remaining" in snapshot,
            isinstance(snapshot["delay_active"], bool),
            "last_break_time" in snapshot,
            "timestamp" in snapshot,
        ]
        return all(checks)
    except Exception as exc:  # pragma: no cover - debugging aid
        print(f"  ✗ Error: {exc}")
        if process.poll() is not None and process.stderr is not None:
            stderr_output = process.stderr.read()
            if stderr_output:
                print(stderr_output.strip())
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> None:
    if not FASTMCP_AVAILABLE:
        print("\n[State Snapshot Tool]")
        print("  ⚠️ Skipped: fastmcp is not installed.")
        print("  Install dependencies with `pip install -r requirements.txt` to run this test.")
        return

    print("\n[State Snapshot Tool]")
    if test_get_state_snapshot_returns_valid_json():
        print("  ✓ PASS: get_state_snapshot returns structured JSON")
    else:
        print("  ✗ FAIL: get_state_snapshot did not return expected payload")


if __name__ == "__main__":
    main()
