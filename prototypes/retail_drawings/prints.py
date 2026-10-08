"""The print range (gen#125): stub for the red commit."""

from __future__ import annotations

from dataclasses import dataclass

MAX_PRINT_SHARE = 0.25


@dataclass(frozen=True)
class Print:
    motif: str
    placement: str
    scale: float
    spacing: float = 0


@dataclass(frozen=True)
class Line:
    code: str
    group: str
    audience: str
    range_: str
    shape: str
    plains: tuple = ()
    prints: tuple[Print, ...] = ()


LINES: tuple[Line, ...] = ()


def style_key(line: Line, p: Print) -> tuple:
    return (line.code,)


def check_range(lines: tuple[Line, ...] = LINES) -> None:
    return None


def docs() -> list[dict]:
    return []


def is_print(doc: dict) -> bool:
    return False


def print_share(catalog: list[dict]) -> dict[tuple[str, ...], float]:
    return {}


def check_share(catalog: list[dict]) -> None:
    return None
