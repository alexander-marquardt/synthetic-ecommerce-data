"""Footwear styles of gen#125 (stub)."""

from __future__ import annotations

from dataclasses import dataclass

import distractors as dz

MATERIALS: tuple[str, ...] = ()
CLOSURES: tuple[str, ...] = ()
WOMEN: dict[str, tuple[str, str, str]] = {}
MEN: dict[str, tuple[str, str, str]] = {}
KIDS: dict[str, tuple[str, str, str]] = {}
SLIPPERS_WOMEN: dict[str, tuple[str, str, str]] = {}
CHARTS: dict[str, dict[str, tuple[str, str, str]]] = {}


@dataclass(frozen=True)
class FootwearStyle:
    code: str


FOOTWEAR: tuple[FootwearStyle, ...] = ()


def sh(name: str, hex_: str, family: str, material: str) -> tuple:
    return (name, hex_, family, material)


def chart_of(doc: dict) -> str:
    return ""


def docs() -> list[dict]:
    return []


BOOTS = dz.Row("", "boots", "", lambda d: False, "", ())


def catalog() -> list[dict]:
    return dz.corpus()
