"""Knitwear depth (gen#309): data only. Stub; the rows follow."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Decoy:
    code: str
    root: str
    ptype: str
    klass: int
    word: str
    color: str
    query: str
    policy: str


ROWS: tuple = ()
TABLE: tuple[Decoy, ...] = ()


def docs() -> list[dict]:
    return []


def decoy_ids() -> frozenset[str]:
    return frozenset()


def product_ids() -> frozenset[str]:
    return frozenset()
