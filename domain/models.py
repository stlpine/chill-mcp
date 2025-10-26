from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeConfig:
    boss_alertness: int
    boss_alertness_cooldown: int


@dataclass(frozen=True)
class BreakOutcome:
    message: str
    summary: str
    stress_level: int
    boss_alert_level: int
    delay_applied: bool
