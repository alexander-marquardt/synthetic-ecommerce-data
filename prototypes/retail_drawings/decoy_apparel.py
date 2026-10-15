"""Text-match decoys on every clothing, footwear and lingerie type (gen#311).

Stub: the plan is empty, so no type carries a decoy yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Spec:
    product_type: str
    per_class: int = 3


@dataclass(frozen=True)
class Row:
    pid: str
    product_type: str
    cls: int
    word: str
    query: str
    policy: str
    doc: dict


TYPES: tuple[Spec, ...] = ()
EXEMPT: dict[str, str] = {}
IDS: frozenset[str] = frozenset()


def build(body: list[dict]) -> list[Row]:
    return []


def docs(body: list[dict]) -> list[dict]:
    return [r.doc for r in build(body)]


def table_markdown(rows: list[Row]) -> str:
    return ""
