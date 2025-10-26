from __future__ import annotations

import time

from presentation.types import ChillControllerProtocol


def format_response(emoji: str, message: str, break_summary: str,
                   stress: int, boss: int) -> str:
    return (
        f"{emoji} {message}\n\n"
        f"Break Summary: {break_summary}\n"
        f"Stress Level: {stress}\n"
        f"Boss Alert Level: {boss}"
    )


def take_break_and_format(
    controller: ChillControllerProtocol,
    emoji: str,
    message: str,
    break_summary: str,
) -> str:
    stress, boss, should_delay = controller.state.take_break()

    if should_delay:
        controller.logger.warning(
            "Applying 20-second delay due to boss alert level 5"
        )
        time.sleep(20)
        controller.logger.info("20-second delay completed")

    return format_response(emoji, message, break_summary, stress, boss)
