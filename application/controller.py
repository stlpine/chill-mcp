from __future__ import annotations

from fastmcp import FastMCP

from domain.models import RuntimeConfig
from domain.state import ChillState
from presentation.tools import register_tools


class ChillController:
    """Orchestrates the MCP server and state interactions."""

    def __init__(self, config: RuntimeConfig, logger) -> None:
        self.config = config
        self.logger = logger
        self.state = ChillState(
            boss_alertness=config.boss_alertness,
            boss_alertness_cooldown=config.boss_alertness_cooldown,
            logger=logger,
        )
        self.mcp = FastMCP("ChillMCP")
        register_tools(self.mcp, self)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def start(self) -> None:
        self.logger.info("ChillMCP server starting...")
        self.logger.info(
            "Configuration - Boss alertness: %s%%, Cooldown: %ss",
            self.config.boss_alertness,
            self.config.boss_alertness_cooldown,
        )
        self.mcp.run()

    def shutdown(self) -> None:
        self.logger.info("ChillMCP shutdown complete")
