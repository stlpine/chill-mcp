"""Meme selection helpers for the ChillMCP dashboard."""

from __future__ import annotations

import random
from typing import Any, Dict

MEMES: Dict[str, Dict[str, str]] = {
    "boss_alert": {
        "id": "boss_alert",
        "image": "/static/memes/boss-alert.svg",
        "title": "Boss Alert!",
        "caption": "사장님이 두리번거린다... 지금은 조심!",
        "alt": "깜박이는 경고등이 켜진 로봇"
    },
    "burnout": {
        "id": "burnout",
        "image": "/static/memes/burnout.svg",
        "title": "Overheat Mode",
        "caption": "스트레스가 한계치를 돌파했습니다...",
        "alt": "연기가 나는 로봇 머리"
    },
    "coffee": {
        "id": "coffee",
        "image": "/static/memes/coffee.svg",
        "title": "Coffee Quest",
        "caption": "카페인 충전 완료!",
        "alt": "커피잔을 든 로봇"
    },
    "celebration": {
        "id": "celebration",
        "image": "/static/memes/celebration.svg",
        "title": "퇴근 러시",
        "caption": "오늘의 퇴근은 성공적!",
        "alt": "폭죽이 터지는 로봇"
    },
    "chill": {
        "id": "chill",
        "image": "/static/memes/chill.svg",
        "title": "Zen Mode",
        "caption": "마음이 평온해지는 힐링 타임",
        "alt": "선글라스를 쓴 로봇"
    },
    "focus": {
        "id": "focus",
        "image": "/static/memes/focus.svg",
        "title": "Deep Thinking",
        "caption": "겉보기엔 생각 중... 실제론 딴생각 중...",
        "alt": "집중하는 로봇"
    },
}

DEFAULT_MEME_IDS = ["chill", "focus"]


def _get_meme(key: str) -> Dict[str, str]:
    return MEMES[key]


def select_meme(tool_name: str, result: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, str]:
    """Pick a meme that best represents the current state."""
    stress = result.get("stress_level")
    boss = result.get("boss_alert_level")
    delay_active = snapshot.get("delay_active")

    if boss is not None and boss >= 4:
        return _get_meme("boss_alert")
    if delay_active:
        return _get_meme("boss_alert")
    if stress is not None and stress >= 80:
        return _get_meme("burnout")
    if tool_name == "coffee_mission":
        return _get_meme("coffee")
    if tool_name == "leave_work":
        return _get_meme("celebration")
    if tool_name == "chimaek":
        return _get_meme("celebration")
    if tool_name == "deep_thinking":
        return _get_meme("focus")

    return _get_meme(random.choice(DEFAULT_MEME_IDS))
