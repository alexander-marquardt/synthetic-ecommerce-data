"""Measure every retail product type's picture for fill and flatness, worst first (gen#1129).

A stub: the red commit's readers return nothing yet.
"""

from __future__ import annotations

from dataclasses import dataclass

EMPTY_FLOOR = 0.35
FLAT_SHARE = 0.5


@dataclass(frozen=True)
class Measure:
    cover: float
    solid: float
    highlight: bool
    shadow: bool

    @property
    def flat(self) -> bool:
        return False


def measure(
    svg: str | bytes, box: tuple = (), skip: tuple = (), only: str | None = None
) -> Measure:
    return Measure(0.0, 0.0, False, False)


def tone(color: str, of: str) -> str | None:
    return None


def pack_size(key: tuple) -> float:
    return 0.0


def chosen_packs(keys: list[tuple]) -> list[tuple[str, tuple]]:
    return []


def scaled_keys(param_keys: set[str], source: str) -> list[str]:
    return []


def type_rows(renders: list[dict], served: dict) -> list[dict]:
    return []


def kit_rows(types: list[dict]) -> list[dict]:
    return []


def type_table(rows: list[dict]) -> str:
    return ""


def kit_table(rows: list[dict], unserved: list[str]) -> str:
    return ""


def cost(seconds: list[float], skus: int, vcpus: int) -> dict:
    return {
        "median_s": 0.0,
        "p95_s": 0.0,
        "mean_s": 0.0,
        "skus": skus,
        "vcpus": vcpus,
        "wall_s": 0.0,
    }
