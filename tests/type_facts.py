"""The facts each modelled type's records are held to, by type key (#61).

A type declared in its own module states them on its ``TypeSpec``:
``may_claim`` (every standard a record may claim), ``key_attributes`` (the
key dimension every title names) and ``default_lines`` / ``default_skus``
(its size in the default build). Adding a type edits nothing here.

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

from collections.abc import Callable
from typing import TypeVar

from synthetic_industrial_products.catalog import typespec

_V = TypeVar("_V")


class TypeFactsError(Exception):
    """A type's facts are missing, or declared in two places."""


#: The standards a record of each shared-table type may claim.
SHARED_MAY_CLAIM: dict[str, frozenset[str]] = {
    "screw_flat_head": frozenset({"ISO 10642", "ASME B18.3", "ISO 898-1", "ISO 3506-1"}),
    "screw_button_head": frozenset({"ISO 7380-1", "ASME B18.3", "ISO 898-1", "ISO 3506-1"}),
    "screw_low_head": frozenset({"DIN 7984", "ASME B18.3", "ISO 898-1", "ISO 3506-1"}),
    "bolt_hex": frozenset({"ASME B18.2.1", "ISO 4014", "ISO 4017", "DIN 933", "ISO 8765",
                           "ISO 8676", "DIN 961", "SAE J429", "ISO 898-1"}),
    "nut_hex": frozenset({"ISO 4032", "ISO 4035", "ISO 8673", "ISO 8675", "ASME B18.2.2",
                          "SAE J995", "ISO 898-2"}),
    "washer_flat": frozenset({"ISO 7089", "DIN 125-A"}),
    "end_mill_square": frozenset({"ISO 1641", "DIN 6527", "ANSI B94.19"}),
    "end_mill_ball": frozenset({"ISO 1641", "DIN 6527", "ANSI B94.19"}),
    "drill_jobber": frozenset({"DIN 338", "ASME B94.11M"}),
    "tap_spiral_point": frozenset({"ISO 529", "ASME B94.9"}),
    "hex_key": frozenset({"ISO 2936", "ASME B18.3"}),
    "hammer_ball_pein": frozenset({"ASME B107.400"}),
    "abrasive_flap_disc": frozenset({"EN 13743", "oSa Certified"}),
    "wheel_depressed_center": frozenset({"ANSI B7.1", "EN 12413", "oSa Certified"}),
    "bearing_radial_ball": frozenset({"ISO 15", "ISO 492", "ABMA 20"}),
    "kit_assortment": frozenset(),
}  # fmt: skip

#: The key dimension every title of each shared-table type names.
SHARED_TITLE_KEY: dict[str, tuple[str, ...]] = {
    "end_mill_square": ("Milling Dia.",), "end_mill_ball": ("Milling Dia.",),
    "drill_jobber": ("Size",), "tap_spiral_point": ("Thread Size",),
    "screw_flat_head": ("Dia./Thread Size",), "screw_button_head": ("Dia./Thread Size",),
    "screw_low_head": ("Dia./Thread Size",), "bolt_hex": ("Dia./Thread Size",),
    "washer_flat": ("Size",), "nut_hex": ("Thread Size",),
    "hex_key": ("Size",), "bearing_radial_ball": ("Bearing Number", "Bore Dia."),
    "wheel_depressed_center": ("Wheel Dia.",), "abrasive_flap_disc": ("Diameter",),
    "hammer_ball_pein": ("Head Weight",), "kit_assortment": ("Number of Pieces",),
}  # fmt: skip

#: Each shared-table type's (product lines, SKUs) in the default build,
#: counted from a fresh build's documents whose ``spec_quality`` is not the
#: breadth one. Restated when a change moves a type's count.
SHARED_SIZE: dict[str, tuple[int, int]] = {
    "abrasive_flap_disc": (129, 232), "bearing_radial_ball": (679, 1182),
    "bolt_hex": (235, 487), "drill_jobber": (286, 530), "end_mill_ball": (286, 568),
    "end_mill_square": (498, 918), "hammer_ball_pein": (98, 184), "hex_key": (630, 1120),
    "kit_assortment": (59, 59), "nut_hex": (662, 1264), "screw_button_head": (130, 251),
    "screw_flat_head": (180, 337), "screw_low_head": (104, 190),
    "tap_spiral_point": (179, 329), "washer_flat": (135, 225),
    "wheel_depressed_center": (670, 1212),
}  # fmt: skip


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
    """Every modelled type's (product lines, SKUs) in the default build."""

    def read(spec: typespec.TypeSpec) -> tuple[int, int] | None:
        if spec.default_lines <= 0:
            raise TypeFactsError(f"type module {spec.module} declares no default_lines")
        if spec.default_skus <= 0:
            raise TypeFactsError(f"type module {spec.module} declares no default_skus")
        return (spec.default_lines, spec.default_skus)

    return _merged(SHARED_SIZE, read, "default_lines")
