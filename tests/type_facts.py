"""The facts each modelled type's records are held to, by type key (#61).

A type declared in its own module states them on its ``TypeSpec``:
``may_claim`` (every standard a record may claim), ``key_attributes`` (the
key dimension every title names).
Its size in the default build is read from ``stats.json``. Adding a type edits nothing here.

The rows below are the types still declared in the shared tables
(``taxonomy``, ``vocab``, ``newtypes``). A row for a type that has a module
is refused, so moving a type into its module moves its rows with it, and the
rows only shrink. The facts tests (``test_catalog_facts``) and the size pins
(``catalog_size``) read the merged tables through the functions below, at
call time, so a type module is covered from its first build.

``may_claim`` is not ``claims``: the build never reads it, so a claim rule
that returns a standard the type's records may not carry still reds.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.domains.industrial.generate import all_type_keys

STATS = Path(__file__).resolve().parents[1] / "golden-catalog" / "stats.json"
_V = TypeVar("_V")


class TypeFactsError(Exception):
    """A type's facts are missing, or declared in two places."""


#: The standards a record of each shared-table type may claim.
SHARED_MAY_CLAIM: dict[str, frozenset[str]] = {
    "screw_flat_head": frozenset({"ASME B18.3", "ISO 10642", "ISO 3506-1", "ISO 898-1"}),
    "screw_button_head": frozenset({"ASME B18.3", "ISO 3506-1", "ISO 7380-1", "ISO 898-1"}),
    "screw_low_head": frozenset({"ASME B18.3", "DIN 7984", "ISO 3506-1", "ISO 898-1"}),
    "bolt_hex": frozenset(
        {
            "ASME B18.2.1",
            "DIN 933",
            "DIN 961",
            "ISO 4014",
            "ISO 4017",
            "ISO 8676",
            "ISO 8765",
            "ISO 898-1",
            "SAE J429",
        }
    ),
    "nut_hex": frozenset(
        {"ASME B18.2.2", "ISO 4032", "ISO 4035", "ISO 8673", "ISO 8675", "ISO 898-2", "SAE J995"}
    ),
    "end_mill_square": frozenset({"ANSI B94.19", "DIN 6527", "ISO 1641"}),
    "end_mill_ball": frozenset({"ANSI B94.19", "DIN 6527", "ISO 1641"}),
    "tap_spiral_point": frozenset({"ASME B94.9", "ISO 529"}),
    "hex_key": frozenset({"ASME B18.3", "ISO 2936"}),
    "hammer_ball_pein": frozenset({"ASME B107.400"}),
    "abrasive_flap_disc": frozenset({"EN 13743", "oSa Certified"}),
    "wheel_depressed_center": frozenset({"ANSI B7.1", "EN 12413", "oSa Certified"}),
    "bearing_radial_ball": frozenset({"ABMA 20", "ISO 15", "ISO 492"}),
    "kit_assortment": frozenset(),
}

#: The key dimension every title of each shared-table type names.
SHARED_TITLE_KEY: dict[str, tuple[str, ...]] = {
    "end_mill_square": ("Milling Dia.",),
    "end_mill_ball": ("Milling Dia.",),
    "tap_spiral_point": ("Thread Size",),
    "screw_flat_head": ("Dia./Thread Size",),
    "screw_button_head": ("Dia./Thread Size",),
    "screw_low_head": ("Dia./Thread Size",),
    "bolt_hex": ("Dia./Thread Size",),
    "nut_hex": ("Thread Size",),
    "hex_key": ("Size",),
    "bearing_radial_ball": ("Bearing Number", "Bore Dia."),
    "wheel_depressed_center": ("Wheel Dia.",),
    "abrasive_flap_disc": ("Diameter",),
    "hammer_ball_pein": ("Head Weight",),
    "kit_assortment": ("Number of Pieces",),
}


def _merged(
    shared: dict[str, _V], read: Callable[[typespec.TypeSpec], _V | None], fields: str
) -> dict[str, _V]:
    """``shared`` plus every type module's own value, refusing a module that
    declares none and a type declared in both places."""
    merged = dict(shared)
    for key, spec in typespec.modelled().items():
        if key in shared:
            raise TypeFactsError(
                f"{key} is declared by its module {spec.module} and by a row of "
                "tests/type_facts.py; delete the row"
            )
        value = read(spec)
        if value is None:
            raise TypeFactsError(f"type module {spec.module} declares no {fields}")
        merged[key] = value
    return merged


def may_claim() -> dict[str, frozenset[str]]:
    """Every modelled type's claimable standards."""
    return _merged(SHARED_MAY_CLAIM, lambda spec: spec.may_claim, "may_claim")


def title_key() -> dict[str, tuple[str, ...]]:
    """Every modelled type's title key: its key dimension, or the attribute
    its module names in place of it (``title_attributes``)."""
    return _merged(
        SHARED_TITLE_KEY,
        lambda spec: spec.title_attributes or spec.key_attributes or None,
        "key_attributes",
    )


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
