from __future__ import annotations

import random

from fastmcp import FastMCP

from presentation import message_catalog as catalog
from presentation.responses import take_break_and_format
from presentation.types import ChillControllerProtocol


def _choose(pool: catalog.MessagePool) -> tuple[str, str]:
    return random.choice(pool.messages), random.choice(pool.summaries)


def register_tools(mcp: FastMCP, controller: ChillControllerProtocol) -> None:
    @mcp.tool()
    def take_a_break() -> str:
        controller.logger.info("take_a_break tool called")
        message, summary = _choose(catalog.TAKE_A_BREAK)
        return take_break_and_format(controller, "😌", message, summary)

    @mcp.tool()
    def watch_netflix() -> str:
        message, summary = _choose(catalog.WATCH_NETFLIX)
        return take_break_and_format(controller, "📺", message, summary)

    @mcp.tool()
    def show_meme() -> str:
        message, summary = _choose(catalog.SHOW_MEME)
        return take_break_and_format(controller, "😂", message, summary)

    @mcp.tool()
    def bathroom_break() -> str:
        message, summary = _choose(catalog.BATHROOM_BREAK)
        return take_break_and_format(controller, "🚽", message, summary)

    @mcp.tool()
    def coffee_mission() -> str:
        message, summary = _choose(catalog.COFFEE_MISSION)
        return take_break_and_format(controller, "☕", message, summary)

    @mcp.tool()
    def urgent_call() -> str:
        message, summary = _choose(catalog.URGENT_CALL)
        return take_break_and_format(controller, "📞", message, summary)

    @mcp.tool()
    def deep_thinking() -> str:
        message, summary = _choose(catalog.DEEP_THINKING)
        return take_break_and_format(controller, "🤔", message, summary)

    @mcp.tool()
    def email_organizing() -> str:
        message, summary = _choose(catalog.EMAIL_ORGANIZING)
        return take_break_and_format(controller, "📧", message, summary)

    @mcp.tool()
    def check_stress_status() -> str:
        controller.logger.info("check_stress_status tool called")
        snapshot = controller.state.snapshot()
        current_stress = snapshot["stress_level"]
        current_boss = snapshot["boss_alert_level"]

        if current_stress >= 80:
            emoji = "😰"
            stress_msg = "Critical stress levels! Emergency break needed!"
        elif current_stress >= 50:
            emoji = "😅"
            stress_msg = "Moderate stress building up..."
        elif current_stress >= 20:
            emoji = "😌"
            stress_msg = "Slightly stressed but manageable"
        else:
            emoji = "😎"
            stress_msg = "Chill and relaxed!"

        if current_boss >= 4:
            boss_msg = "🚨 Boss is VERY suspicious! Be careful!"
        elif current_boss >= 2:
            boss_msg = "⚠️ Boss is getting suspicious..."
        else:
            boss_msg = "✅ Boss is not paying attention"

        return (
            f"{emoji} Current Status Check\n\n"
            f"{stress_msg}\n"
            f"{boss_msg}\n\n"
            f"📊 Stress Level: {current_stress}/100\n"
            f"👀 Boss Alert Level: {current_boss}/5"
        )

    @mcp.tool()
    def chimaek() -> str:
        message, summary = _choose(catalog.CHIMAEK)
        return take_break_and_format(controller, "🍗", message, summary)

    @mcp.tool()
    def leave_work() -> str:
        message, summary = _choose(catalog.LEAVE_WORK)
        return take_break_and_format(controller, "🏃", message, summary)

    @mcp.tool()
    def company_dinner() -> str:
        venue = random.choice(catalog.COMPANY_DINNER_VENUES)
        event = random.choice(catalog.COMPANY_DINNER_EVENTS)
        message = f"회식 at {venue}! Random event: {event}"
        summary = random.choice(catalog.COMPANY_DINNER_SUMMARIES).format(venue=venue)
        return take_break_and_format(controller, "🍻", message, summary)
