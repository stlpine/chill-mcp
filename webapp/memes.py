"""Meme selection helpers for the ChillMCP dashboard."""

from __future__ import annotations

import os
import random
from typing import Any, Dict, Iterable

import requests

DISABLE_REMOTE = os.getenv("CHILL_MCP_DISABLE_MEME_FETCH", "").lower() in {"1", "true", "yes"}

FALLBACK_MEMES: Dict[str, Dict[str, str]] = {
    "boss_alert": {
        "id": "boss_alert",
        "image": "https://i.imgur.com/mE5oMDC.jpeg",
        "title": "Boss Alert!",
        "caption": "상사가 뒤에 있어요… 지금은 매우 조심!",
        "alt": "사무실에서 상사를 눈치보는 밈"
    },
    "burnout": {
        "id": "burnout",
        "image": "https://i.imgur.com/g9V6w5S.jpeg",
        "title": "Burnout Mode",
        "caption": "이대로는 머리에서 연기 나겠어요…",
        "alt": "불타는 쓰레기통 밈"
    },
    "coffee": {
        "id": "coffee",
        "image": "https://i.imgur.com/n8OYCzH.jpeg",
        "title": "Coffee Quest",
        "caption": "카페인 수혈 완료!",
        "alt": "커피를 들고 행복해하는 밈"
    },
    "celebration": {
        "id": "celebration",
        "image": "https://i.imgur.com/4hXKz7x.jpeg",
        "title": "Freedom Mode",
        "caption": "퇴근이다! 다같이 춤춰요!",
        "alt": "퇴근하며 춤추는 밈"
    },
    "chill": {
        "id": "chill",
        "image": "https://i.imgur.com/P6Hxg6V.jpeg",
        "title": "Zen Mode",
        "caption": "완벽한 힐링 타임…",
        "alt": "해먹에서 쉬는 개 밈"
    },
    "focus": {
        "id": "focus",
        "image": "https://i.imgur.com/Es7N8au.jpeg",
        "title": "Deep Thinking",
        "caption": "겉보기엔 진지하지만 속으론 휴식 생각뿐.",
        "alt": "생각하는 표정의 밈"
    },
}

SUBREDDIT_BUCKETS: Dict[str, Iterable[str]] = {
    "boss_alert": ("WorkMemes", "memeeconomy"),
    "burnout": ("me_irl", "wholesomememes"),
    "coffee": ("coffee", "wholesomememes"),
    "celebration": ("aww", "madeMeSmile"),
    "chill": ("wholesomememes", "relaxing"),
    "focus": ("ProgrammerHumor", "techsupportgore"),
}

DEFAULT_KEYS = ["chill", "focus"]


def _fetch_remote_meme(category: str) -> Dict[str, str]:
    if DISABLE_REMOTE:
        return FALLBACK_MEMES[category]

    subreddits = SUBREDDIT_BUCKETS.get(category, [])
    for subreddit in subreddits:
        try:
            response = requests.get(
                f"https://meme-api.com/gimme/{subreddit}",
                timeout=3,
            )
            if response.status_code != 200:
                continue
            payload = response.json()
            url = payload.get("url")
            if not url or not url.startswith("http"):
                continue
            title = payload.get("title") or "AI deserves a break"
            return {
                "id": category,
                "image": url,
                "title": title,
                "caption": title,
                "alt": title,
            }
        except Exception:
            continue
    return FALLBACK_MEMES[category]


def _choose(category: str) -> Dict[str, str]:
    if category not in FALLBACK_MEMES:
        category = random.choice(DEFAULT_KEYS)
    return _fetch_remote_meme(category)


def select_meme(tool_name: str, result: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, str]:
    """Pick a meme from the internet; fall back to curated picks if needed."""
    stress = result.get("stress_level")
    boss = result.get("boss_alert_level")
    delay_active = snapshot.get("delay_active")

    if boss is not None and boss >= 4:
        return _choose("boss_alert")
    if delay_active:
        return _choose("boss_alert")
    if stress is not None and stress >= 80:
        return _choose("burnout")
    if tool_name == "coffee_mission":
        return _choose("coffee")
    if tool_name in {"leave_work", "chimaek"}:
        return _choose("celebration")
    if tool_name == "deep_thinking":
        return _choose("focus")

    return _choose(random.choice(DEFAULT_KEYS))
