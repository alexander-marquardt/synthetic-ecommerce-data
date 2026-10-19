"""Stub: the pins the tests read from ``tests/data/golden_pins.json`` (#50). Not yet measured."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "golden-catalog"
PINS_PATH = ROOT / "tests" / "data" / "golden_pins.json"
REGENERATE = (
    "uv run ecom-generate build --out golden-catalog && uv run python scripts/measure_pins.py"
)


class PinRuleError(Exception):
    pass


@dataclass(frozen=True)
class SkuRule:
    key: str
    statement: str
    product_type: str
    attribute: tuple[str, str] | None
    handle_less: bool


SKU_RULES: tuple[SkuRule, ...] = (
    SkuRule("screw", "a socket head cap screw", "screw_socket_head", None, True),
    SkuRule("drill", 'a 5/64" jobber drill', "drill_jobber", ("size", "5/64"), True),
    SkuRule("hairline_drill", 'a 1/16" jobber drill', "drill_jobber", ("size", "1/16"), False),
)


def pick_sku(rule: SkuRule, candidates: Iterable[tuple[dict, dict, bool]]) -> str | None:
    return None


def find_anchor(nested_lines: Iterable[str]) -> dict:
    return {}


def anchor_needles(anchor: dict) -> list[tuple[str, str]]:
    return []


def check_anchor(anchor: dict, texts: dict[str, str]) -> None:
    return None


def measure_anchor(golden: Path = GOLDEN) -> dict:
    return {}


def prose_patterns(pins: dict) -> dict[str, str]:
    return {}


MEASURES: dict[str, Callable[[], dict]] = {"anchor": measure_anchor}


def measure_all() -> dict:
    return {}


def load() -> dict:
    return json.loads(PINS_PATH.read_text("utf-8"))


def dump(pins: dict) -> str:
    return json.dumps(pins, indent=2, sort_keys=True) + "\n"
