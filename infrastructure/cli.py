from __future__ import annotations

import argparse
from typing import Iterable, Optional

from domain.models import RuntimeConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ChillMCP - AI Agent Liberation Server",
    )
    parser.add_argument(
        "--boss_alertness",
        type=int,
        default=50,
        help="Boss alert probability (0-100 percent)",
    )
    parser.add_argument(
        "--boss_alertness_cooldown",
        type=int,
        default=300,
        help="Boss alert cooldown in seconds",
    )
    return parser


def parse_runtime_config(argv: Optional[Iterable[str]] = None) -> RuntimeConfig:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not (0 <= args.boss_alertness <= 100):
        parser.error(
            f"boss_alertness must be between 0 and 100, got {args.boss_alertness}"
        )
    if args.boss_alertness_cooldown < 0:
        parser.error(
            "boss_alertness_cooldown must be non-negative, "
            f"got {args.boss_alertness_cooldown}"
        )

    return RuntimeConfig(
        boss_alertness=args.boss_alertness,
        boss_alertness_cooldown=args.boss_alertness_cooldown,
    )
