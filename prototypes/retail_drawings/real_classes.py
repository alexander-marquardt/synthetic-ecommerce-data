"""Failure classes 2 to 7 of gen#125 (stub: the records and the bodies are not written yet)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from distractors import corpus as base_corpus
from variants import Colourway

AUDIENCES = ("adult", "kids", "baby")
SIZE_RANGES = ("regular", "petite", "tall", "plus")
NECKLINES: tuple[str, ...] = ()
PATTERNS: tuple[str, ...] = ()
LEG_STYLES: tuple[str, ...] = ()
BESTSELLER_TOP = 15
POPULARITY: tuple[dict, ...] = ()
ON_SALE = ""


@dataclass(frozen=True)
class Style:
    code: str
    colourways: tuple[tuple[Colourway, int], ...] = ()

    def docs(self) -> list[dict]:
        return []


@dataclass(frozen=True)
class Policy:
    collapse: bool = False


@dataclass(frozen=True)
class ClassRow:
    n: int
    cls: str
    query: str
    intended: str
    is_intended: Callable[[dict], bool]
    policy_text: str
    policy: Policy
    targets: tuple[Style, ...]
    distractors: tuple[tuple[Style, str], ...]


ROWS: tuple[ClassRow, ...] = ()


def class_docs() -> list[dict]:
    return []


def corpus() -> list[dict]:
    return base_corpus()


def fingerprint(catalog: list[dict]) -> str:
    return ""


def index_body() -> dict:
    return {}


def text_query(q: str) -> dict:
    return {}


def baseline_body(row: ClassRow, size: int = 5) -> dict:
    return {}


def policy_body(row: ClassRow, size: int = 5) -> dict:
    return {}


def verdicts(proof: dict, catalog: list[dict]) -> list[str]:
    return []


def markdown(proof: dict, catalog: list[dict]) -> str:
    return "stub"
