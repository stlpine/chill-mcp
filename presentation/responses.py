from __future__ import annotations


def format_response(
    emoji: str,
    message: str,
    break_summary: str,
    stress: int,
    boss: int,
) -> str:
    return (
        f"{emoji} {message}\n\n"
        f"Break Summary: {break_summary}\n"
        f"Stress Level: {stress}\n"
        f"Boss Alert Level: {boss}"
    )
