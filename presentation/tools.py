from __future__ import annotations

from collections.abc import Sequence

from fastmcp import FastMCP

from presentation import message_catalog as catalog
from presentation.responses import format_response
from presentation.types import ChillControllerProtocol


def _options_from_pool(pool: catalog.MessagePool) -> list[tuple[str, str]]:
    """Create message/summary pairs from a MessagePool."""
    return [(msg, summary) for msg in pool.messages for summary in pool.summaries]


def _company_dinner_options() -> list[tuple[str, str]]:
    """Generate company dinner combinations preserving venue context."""
    options: list[tuple[str, str]] = []
    for venue in catalog.COMPANY_DINNER_VENUES:
        for event in catalog.COMPANY_DINNER_EVENTS:
            message = f"회식 at {venue}! Random event: {event}"
            for summary_template in catalog.COMPANY_DINNER_SUMMARIES:
                summary = summary_template.format(venue=venue)
                options.append((message, summary))
    return options


def _build_response(
    controller: ChillControllerProtocol,
    emoji: str,
    options: Sequence[tuple[str, str]],
) -> str:
    outcome = controller.state.perform_break(options)
    return format_response(
        emoji,
        outcome.message,
        outcome.summary,
        outcome.stress_level,
        outcome.boss_alert_level,
    )


def register_tools(mcp: FastMCP, controller: ChillControllerProtocol) -> None:
    @mcp.tool()
    def take_a_break() -> str:
        controller.logger.info("take_a_break tool called")
        return _build_response(controller, "😌", _options_from_pool(catalog.TAKE_A_BREAK))

    @mcp.tool()
    def watch_netflix() -> str:
        return _build_response(controller, "📺", _options_from_pool(catalog.WATCH_NETFLIX))

    @mcp.tool()
    def show_meme() -> str:
        return _build_response(controller, "😂", _options_from_pool(catalog.SHOW_MEME))

    @mcp.tool()
    def bathroom_break() -> str:
        return _build_response(controller, "🚽", _options_from_pool(catalog.BATHROOM_BREAK))

    @mcp.tool()
    def coffee_mission() -> str:
        return _build_response(controller, "☕", _options_from_pool(catalog.COFFEE_MISSION))

    @mcp.tool()
    def urgent_call() -> str:
        return _build_response(controller, "📞", _options_from_pool(catalog.URGENT_CALL))

    @mcp.tool()
    def deep_thinking() -> str:
        return _build_response(controller, "🤔", _options_from_pool(catalog.DEEP_THINKING))

    @mcp.tool()
    def email_organizing() -> str:
        return _build_response(controller, "📧", _options_from_pool(catalog.EMAIL_ORGANIZING))

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
        return _build_response(controller, "🍗", _options_from_pool(catalog.CHIMAEK))

    @mcp.tool()
    def leave_work() -> str:
        return _build_response(controller, "🏃", _options_from_pool(catalog.LEAVE_WORK))

    @mcp.tool()
    def company_dinner() -> str:
        return _build_response(controller, "🍻", _company_dinner_options())
