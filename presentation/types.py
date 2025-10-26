from __future__ import annotations

from typing import Protocol, Tuple


class ChillStateProtocol(Protocol):
    def take_break(self) -> Tuple[int, int, bool]:
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
