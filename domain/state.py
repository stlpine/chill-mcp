from __future__ import annotations

import logging
import random
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple


class ChillState:
    """Manages the stress and boss alert levels for the AI agent."""

    def __init__(
        self,
        boss_alertness: int,
        boss_alertness_cooldown: int,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.stress_level = 0
        self.boss_alert_level = 0
        self.boss_alertness = boss_alertness
        self.boss_alertness_cooldown = boss_alertness_cooldown
        self.last_break_time = datetime.now()
        self.last_boss_cooldown_time = datetime.now()
        self.lock = threading.Lock()

        self.logger.info(
            "ChillState initialized - Boss alertness: %s%%, Cooldown: %ss",
            boss_alertness,
            boss_alertness_cooldown,
        )

        self._cooldown_thread = threading.Thread(
            target=self._cooldown_worker,
            daemon=True,
            name="boss-alert-cooldown",
        )
        self._cooldown_thread.start()
        self.logger.info("Boss alert cooldown thread started")

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _cooldown_worker(self) -> None:
        while True:
            time.sleep(1)
            with self.lock:
                now = datetime.now()
                elapsed = (now - self.last_boss_cooldown_time).total_seconds()
                if elapsed >= self.boss_alertness_cooldown and self.boss_alert_level > 0:
                    old_level = self.boss_alert_level
                    self.boss_alert_level = max(0, self.boss_alert_level - 1)
                    self.last_boss_cooldown_time = now
                    self.logger.info(
                        "Boss alert cooldown: %s -> %s (elapsed: %.1fs)",
                        old_level,
                        self.boss_alert_level,
                        elapsed,
                    )

    def _update_stress(self) -> None:
        """Auto-increment stress based on time elapsed since last break."""
        now = datetime.now()
        elapsed_minutes = (now - self.last_break_time).total_seconds() / 60.0

        stress_increase = int(elapsed_minutes)
        if stress_increase > 0:
            old_stress = self.stress_level
            self.stress_level = min(100, self.stress_level + stress_increase)
            if old_stress != self.stress_level:
                self.logger.info(
                    "Stress auto-increased: %s -> %s (+%s, elapsed: %.1fmin)",
                    old_stress,
                    self.stress_level,
                    stress_increase,
                    elapsed_minutes,
                )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def take_break(self) -> Tuple[int, int, bool]:
        """Apply a break and return (stress_level, boss_alert_level, delay_required)."""
        with self.lock:
            self._update_stress()

            initial_stress = self.stress_level
            initial_boss = self.boss_alert_level

            stress_reduction = random.randint(1, 100)
            self.stress_level = max(0, self.stress_level - stress_reduction)

            boss_alert_increased = False
            if random.randint(0, 100) <= self.boss_alertness:
                self.boss_alert_level = min(5, self.boss_alert_level + 1)
                boss_alert_increased = True
                self.last_boss_cooldown_time = datetime.now()

            self.last_break_time = datetime.now()
            should_delay = self.boss_alert_level == 5

            self.logger.info(
                "Break taken - Stress: %s -> %s (-%s)",
                initial_stress,
                self.stress_level,
                stress_reduction,
            )
            if boss_alert_increased:
                self.logger.warning(
                    "Boss alert increased: %s -> %s",
                    initial_boss,
                    self.boss_alert_level,
                )
            if should_delay:
                self.logger.warning(
                    "Boss alert level 5 reached! 20-second delay will be applied"
                )

            return self.stress_level, self.boss_alert_level, should_delay

    def snapshot(self) -> dict:
        """Return a JSON-serialisable snapshot of the current state."""
        with self.lock:
            self._update_stress()
            return {
                "timestamp": datetime.now().isoformat(),
                "stress_level": self.stress_level,
                "boss_alert_level": self.boss_alert_level,
                "boss_alertness": self.boss_alertness,
                "boss_alertness_cooldown": self.boss_alertness_cooldown,
                "last_break_time": self.last_break_time.isoformat(),
                "last_boss_cooldown_time": self.last_boss_cooldown_time.isoformat(),
            }
