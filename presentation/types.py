from __future__ import annotations

from typing import Protocol, Sequence, Tuple

from domain.models import BreakOutcome


class ChillStateProtocol(Protocol):
    def take_break(self) -> Tuple[int, int, bool]:
        ...

    def perform_break(
        self,
        options: Sequence[Tuple[str, str]],
        apply_delay: bool = True,
    ) -> BreakOutcome:
        ...


class LoggerProtocol(Protocol):
    def info(self, msg: str, *args, **kwargs) -> None:
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        ...

    def error(self, msg: str, *args, **kwargs) -> None:
        ...


class ChillControllerProtocol(Protocol):
    state: ChillStateProtocol
    logger: LoggerProtocol
