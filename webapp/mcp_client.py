"""Async MCP client that talks to the ChillMCP server over stdio."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

LOGGER = logging.getLogger(__name__)


class MCPError(RuntimeError):
    """Base error for MCP communication failures."""


class MCPTimeoutError(MCPError):
    """Raised when the MCP server does not answer within the expected time."""


class MCPProcessError(MCPError):
    """Raised when the MCP server process stops unexpectedly."""


class MCPClient:
    """Manage a single MCP server process and issue JSON-RPC requests."""

    def __init__(
        self,
        command: Optional[list[str]] = None,
        init_timeout: float = 5.0,
        call_timeout: float = 10.0,
    ) -> None:
        self._init_timeout = init_timeout
        self._call_timeout = call_timeout
        self._command = command or self._default_command()
        self._process: Optional[subprocess.Popen[str]] = None
        self._lock = asyncio.Lock()
        self._initialized = False
        self._request_id = 0

    @staticmethod
    def _default_command() -> list[str]:
        """Build the default command to launch the local ChillMCP server."""
        env_override = os.getenv("CHILL_MCP_COMMAND")
        if env_override:
            return shlex.split(env_override)

        project_root = Path(__file__).resolve().parent.parent
        script = project_root / "main.py"

        boss_alertness = os.getenv("CHILL_MCP_BOSS_ALERTNESS", "50")
        cooldown = os.getenv("CHILL_MCP_BOSS_ALERTNESS_COOLDOWN", "300")

        return [
            sys.executable,
            str(script),
            "--boss_alertness",
            str(boss_alertness),
            "--boss_alertness_cooldown",
            str(cooldown),
        ]

    async def _ensure_process(self) -> None:
        """Start the MCP server process if needed."""
        if self._process and self._process.poll() is None:
            return

        LOGGER.info("Starting MCP server: %s", " ".join(self._command))
        self._process = subprocess.Popen(
            self._command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._initialized = False
        self._request_id = 0

    async def _ensure_initialized(self) -> None:
        await self._ensure_process()
        if self._initialized:
            return

        assert self._process is not None and self._process.stdin and self._process.stdout

        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "chill-web", "version": "1.0.0"},
            },
        }

        response = await self._send_request(init_request, timeout=self._init_timeout)
        if not response or "result" not in response:
            raise MCPError("Failed to initialize MCP server")

        await self._send_notification({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self._initialized = True
        self._request_id = 1
        LOGGER.info("MCP server initialized")

    async def _send_notification(self, message: Dict[str, Any]) -> None:
        assert self._process is not None and self._process.stdin

        loop = asyncio.get_running_loop()

        def _write() -> None:
            if self._process is None or self._process.stdin is None:
                raise MCPProcessError("MCP process stdin is not available")
            self._process.stdin.write(json.dumps(message) + "\n")
            self._process.stdin.flush()

        await loop.run_in_executor(None, _write)

    async def _send_request(self, request: Dict[str, Any], timeout: float) -> Dict[str, Any]:
        assert self._process is not None and self._process.stdin and self._process.stdout

        loop = asyncio.get_running_loop()

        def _write_and_read() -> Dict[str, Any]:
            if self._process is None or self._process.stdin is None or self._process.stdout is None:
                raise MCPProcessError("MCP process pipes closed")

            if self._process.poll() is not None:
                raise MCPProcessError("MCP process exited unexpectedly")

            self._process.stdin.write(json.dumps(request) + "\n")
            self._process.stdin.flush()

            line = self._process.stdout.readline()
            if not line:
                raise MCPTimeoutError("No response from MCP server")
            return json.loads(line)

        try:
            return await asyncio.wait_for(loop.run_in_executor(None, _write_and_read), timeout=timeout)
        except json.JSONDecodeError as exc:
            raise MCPError(f"Invalid JSON from MCP server: {exc}") from exc
        except asyncio.TimeoutError as exc:
            raise MCPTimeoutError("Timed out waiting for MCP response") from exc

    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        async with self._lock:
            await self._ensure_initialized()

            assert self._process is not None
            self._request_id += 1
            request_id = self._request_id
            call_request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments or {}},
            }

            response = await self._send_request(call_request, timeout=timeout or self._call_timeout)
            return response

    async def call_tool_text(self, name: str, **kwargs: Any) -> str:
        response = await self.call_tool(name, **kwargs)
        result = response.get("result", {})
        contents = result.get("content", [])
        if contents and isinstance(contents, list):
            first = contents[0]
            if isinstance(first, dict) and first.get("type") == "text":
                return first.get("text", "")
        raise MCPError(f"Unexpected MCP tool response structure: {response}")

    async def close(self) -> None:
        if self._process and self._process.poll() is None:
            LOGGER.info("Terminating MCP server process")
            self._process.terminate()
            try:
                await asyncio.wait_for(asyncio.get_running_loop().run_in_executor(None, self._process.wait), timeout=5)
            except asyncio.TimeoutError:
                LOGGER.warning("Force-killing MCP server process")
                self._process.kill()
        self._process = None
        self._initialized = False
        self._request_id = 0


async def get_state_snapshot(client: MCPClient) -> Dict[str, Any]:
    """Helper to fetch and decode the JSON state snapshot."""
    text = await client.call_tool_text("get_state_snapshot")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise MCPError(f"Invalid JSON payload from get_state_snapshot: {exc}") from exc
