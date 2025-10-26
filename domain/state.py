from __future__ import annotations

import logging
import random
import threading
import time
from datetime import datetime
from typing import Optional, Sequence, Tuple

from domain.models import BreakOutcome

class AgentStressState:
    """Represents the AI agent의 스트레스 상태."""

    def __init__(self, logger: logging.Logger) -> None:
        self.level = 0
        self.last_break_time = datetime.now()
        self._logger = logger

    def apply_elapsed_time(self) -> None:
        now = datetime.now()
        elapsed_minutes = (now - self.last_break_time).total_seconds() / 60.0
        increase = int(elapsed_minutes)
        if increase > 0:
            old_level = self.level
            self.level = min(100, self.level + increase)
            if self.level != old_level:
                self._logger.info(
                    "Stress auto-increased: %s -> %s (+%s, elapsed: %.1fmin)",
                    old_level,
                    self.level,
                    increase,
                    elapsed_minutes,
                )

    def reduce_for_break(self) -> int:
        reduction = random.randint(1, 100)
        old_level = self.level
        self.level = max(0, self.level - reduction)
        self.last_break_time = datetime.now()
        self._logger.info(
            "Break taken - Stress: %s -> %s (-%s)",
            old_level,
            self.level,
            reduction,
        )
        return reduction

    def snapshot(self) -> dict:
        return {
            "stress_level": self.level,
            "last_break_time": self.last_break_time.isoformat(),
        }


class BossAlertState:
    """Boss의 의심 수준과 쿨다운 로직을 관리."""

    def __init__(
        self,
        alertness_probability: int,
        cooldown_seconds: int,
        logger: logging.Logger,
    ) -> None:
        self.level = 0
        self.alertness_probability = alertness_probability
        self.cooldown_seconds = cooldown_seconds
        self.last_cooldown_time = datetime.now()
        self._logger = logger

    def register_break(self) -> Optional[Tuple[int, int]]:
        probability = self.alertness_probability
        if probability <= 0:
            return None
        if random.randint(1, 100) <= probability:
            old_level = self.level
            self.level = min(5, self.level + 1)
            if self.level != old_level:
                self.last_cooldown_time = datetime.now()
            return old_level, self.level
        return None

    def cooldown_step(
        self,
        reference_time: datetime,
    ) -> Optional[Tuple[int, int, float]]:
        elapsed = (reference_time - self.last_cooldown_time).total_seconds()
        if elapsed >= self.cooldown_seconds and self.level > 0:
            old_level = self.level
            self.level = max(0, self.level - 1)
            self.last_cooldown_time = reference_time
            return old_level, self.level, elapsed
        return None

    def snapshot(self) -> dict:
        return {
            "boss_alert_level": self.level,
            "boss_alertness": self.alertness_probability,
            "boss_alertness_cooldown": self.cooldown_seconds,
            "last_boss_cooldown_time": self.last_cooldown_time.isoformat(),
        }


class ChillState:
    """AI Agent의 스트레스와 Boss 의심 상태를 조율하는 서비스."""

    def __init__(
        self,
        boss_alertness: int,
        boss_alertness_cooldown: int,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.agent = AgentStressState(self.logger)
        self.boss = BossAlertState(
            alertness_probability=boss_alertness,
            cooldown_seconds=boss_alertness_cooldown,
            logger=self.logger,
        )
        self.lock = threading.Lock()

        self.logger.info(
            "ChillState initialized - Boss alertness: %s%%, Cooldown: %ss",
            boss_alertness,
            boss_alertness_cooldown,
        )

        threading.Thread(
            target=self._cooldown_worker,
            daemon=True,
            name="boss-alert-cooldown",
        ).start()
        self.logger.info("Boss alert cooldown thread started")

    # ------------------------------------------------------------------
    # Background worker
    # ------------------------------------------------------------------
    def _cooldown_worker(self) -> None:
        while True:
            time.sleep(1)
            with self.lock:
                result = self.boss.cooldown_step(datetime.now())
                if result:
                    old_level, new_level, elapsed = result
                    self.logger.info(
                        "Boss alert cooldown: %s -> %s (elapsed: %.1fs)",
                        old_level,
                        new_level,
                        elapsed,
                    )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def take_break(self) -> Tuple[int, int, bool]:
        """휴식을 적용하고 (스트레스, 보스레벨, 지연여부)를 반환."""
        with self.lock:
            self.agent.apply_elapsed_time()
            self.agent.reduce_for_break()
            boss_result = self.boss.register_break()

            if boss_result:
                old_level, new_level = boss_result
                self.logger.warning(
                    "Boss alert increased: %s -> %s",
                    old_level,
                    new_level,
                )
            should_delay = self.boss.level == 5
            if should_delay:
                self.logger.warning(
                    "Boss alert level 5 reached! 20-second delay will be applied"
                )

            return self.agent.level, self.boss.level, should_delay

    def perform_break(
        self,
        options: Sequence[Tuple[str, str]],
        apply_delay: bool = True,
    ) -> BreakOutcome:
        if not options:
            raise ValueError("Break options must not be empty")

        message, summary = random.choice(options)
        stress, boss, should_delay = self.take_break()

        delay_applied = False
        if should_delay and apply_delay:
            delay_applied = True
            self.logger.warning(
                "Applying 20-second delay due to boss alert level 5"
            )
            time.sleep(20)
            self.logger.info("20-second delay completed")

        return BreakOutcome(
            message=message,
            summary=summary,
            stress_level=stress,
            boss_alert_level=boss,
            delay_applied=delay_applied,
        )

    def snapshot(self) -> dict:
        with self.lock:
            self.agent.apply_elapsed_time()
            data = {
                "timestamp": datetime.now().isoformat(),
            }
            data.update(self.agent.snapshot())
            data.update(self.boss.snapshot())
            return data

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------
    @property
    def boss_alert_level(self) -> int:
        return self.boss.level

    @property
    def boss_alertness(self) -> int:
        return self.boss.alertness_probability

    @property
    def boss_alertness_cooldown(self) -> int:
        return self.boss.cooldown_seconds
