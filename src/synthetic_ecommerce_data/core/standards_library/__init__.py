"""Stub: the shared standards library (#73). The real loader follows the red commit."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


class StandardsTableError(KeyError):
    """A table is missing, uncited or duplicated."""


@dataclass(frozen=True)
class Table:
    name: str = ""
    standards: tuple[str, ...] = ()
    edition: str = ""
    source: str = ""
    kind: str = ""
    data: dict = field(default_factory=dict)
    values: list = field(default_factory=list)
    rows: list = field(default_factory=list)

    def select(self, keys, *, by="size") -> list:
        return []


class Library:
    def __init__(self, *extra_roots: Path) -> None:
        self.extra_roots = extra_roots

    def names(self) -> tuple[str, ...]:
        return ()

    def table(self, name: str) -> Table:
        return Table(name="")


DEFAULT = Library()


def names() -> tuple[str, ...]:
    return DEFAULT.names()


def table(name: str) -> Table:
    return DEFAULT.table(name)
