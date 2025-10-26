from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeConfig:
    boss_alertness: int
    boss_alertness_cooldown: int
