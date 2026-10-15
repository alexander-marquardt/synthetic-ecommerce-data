"""Stub (red): the registry of retail type specs (gen#351)."""

from __future__ import annotations

from dataclasses import dataclass


class SpecError(ValueError):
    """A malformed spec."""


@dataclass(frozen=True)
class Decoy:
    cls: int
    query: str
    policy: str
    row: object


@dataclass(frozen=True)
class TypeSpec:
    key: str
    department: str
    product_type: str
    rows: tuple = ()
    decoys: tuple = ()
    derivable: bool = False

    def docs(self) -> list[dict]:
        return []


def specs() -> dict[str, TypeSpec]:
    return {}


def validate(spec: TypeSpec) -> None:
    return None


def legacy_types() -> frozenset[tuple[str, str]]:
    return frozenset()


def ids_of(spec: TypeSpec) -> frozenset[str]:
    return frozenset()


def decoy_ids_of(spec: TypeSpec) -> frozenset[str]:
    return frozenset()
