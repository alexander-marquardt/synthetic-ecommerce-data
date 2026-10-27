"""The facts each modelled type's records are held to, by type key (#61).

A type declared in its own module states them on its ``TypeSpec``:
``may_claim`` (every standard a record may claim), ``key_attributes`` (the
key dimension every title names).
Its size in the default build is read from ``stats.json``. Adding a type edits nothing here.

The facts tests (``test_catalog_facts``) and the size pins (``catalog_size``)
read them through the functions below, at call time, so a type module is
covered from its first build and there is no table here to edit.

``may_claim`` is not ``claims``: the build never reads it, so a claim rule
that returns a standard the type's records may not carry still reds.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.domains.industrial.generate import all_type_keys

STATS = Path(__file__).resolve().parents[1] / "golden-catalog" / "stats.json"
_V = TypeVar("_V")


class TypeFactsError(Exception):
    """A type's facts are missing."""


def _specs() -> list[tuple[str, typespec.TypeSpec]]:
    return list(typespec.modelled().items())


def _declared(spec: typespec.TypeSpec, value: _V | None, fields: str) -> _V:
    """A type module's own value, refusing a module that declares none."""
    if value is None:
        raise TypeFactsError(f"type module {spec.module} declares no {fields}")
    return value


def may_claim() -> dict[str, frozenset[str]]:
    """Every modelled type's claimable standards."""
    return {key: _declared(spec, spec.may_claim, "may_claim") for key, spec in _specs()}


def title_key() -> dict[str, tuple[str, ...]]:
    """Every modelled type's title key: its key dimension, or the attribute
    its module names in place of it (``title_attributes``)."""
    return {
        key: _declared(spec, spec.title_attributes or spec.key_attributes or None, "key_attributes")
        for key, spec in _specs()
    }


def default_size() -> dict[str, tuple[int, int]]:
    """Every modelled type's (product lines, SKUs) in the default build.

    Read from ``golden-catalog/stats.json``, which the build writes, so a
    type's size is never typed by hand and a type PR does not edit it (#103).
    """
    stats = json.loads(STATS.read_text("utf-8"))
    return {
        key: (stats["lines_by_type"][key], stats["skus_by_type"][key])
        for key in (*all_type_keys("modelled"), *all_type_keys("new"))
    }
