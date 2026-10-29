"""The legacy types move into one spec module each, family by family (gen#455, rest of gen#351).

A move changes no product: the rows leave the shared file and the legacy list, and the same
documents reach the build through the registry. These checks hold the first family, the seven
first-increment Sports & Outdoors types of gen#265 (tents to foam rollers), at the three places a
half-done move shows: the legacy list, the spec file and the shared file it left.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import (
    scale,
    sports_rows,
    type_registry,
)

DEPARTMENT = "Sports & Outdoors"
#: key -> (product type, the product ids of its styles): the ids are what the build had before
#: the move, so a lost or renamed style fails here.
MOVED = {
    "tent": ("Tent", {"TNTDOM", "TNTBPK", "TNTFAM", "TNTTRK"}),
    "sleeping_bag": ("Sleeping Bag", {"SLPMUM", "SLPWIN", "SLPRCT"}),
    "camping_chair": ("Camping Chair", {"CHRFLD", "CHRARM"}),
    "yoga_mat": ("Yoga Mat", {"YGMFLT", "YGMTRV"}),
    "dumbbell": ("Dumbbell", {"DMBHEX", "DMBNEO"}),
    "kettlebell": ("Kettlebell", {"KTBCST", "KTBVIN"}),
    "foam_roller": ("Foam Roller", {"FMRSMT", "FMRGRD"}),
}


def _codes(key: str) -> set[str]:
    return {r.code for r in type_registry.specs()[key].rows}


@pytest.mark.parametrize("key", sorted(MOVED))
def test_a_moved_type_is_a_spec_of_its_own_key(key: str) -> None:
    ptype, _ = MOVED[key]
    spec = type_registry.specs().get(key)
    assert spec is not None, f"type_specs/{key}.py is missing"
    assert (spec.department, spec.product_type) == (DEPARTMENT, ptype)


@pytest.mark.parametrize("key", sorted(MOVED))
def test_a_moved_type_keeps_every_style_it_had(key: str) -> None:
    _, codes = MOVED[key]
    assert key in type_registry.specs() and _codes(key) == codes


@pytest.mark.parametrize("key", sorted(MOVED))
def test_a_moved_type_owns_its_rows(key: str) -> None:
    ptype, _ = MOVED[key]
    spec = type_registry.specs()[key]
    assert (spec.department, spec.product_type) == (DEPARTMENT, ptype) and spec.rows


def test_no_sports_type_is_left_in_a_shared_module() -> None:
    held = {s.product_type for s in type_registry.specs().values()
            if s.department == DEPARTMENT and not s.rows}  # fmt: skip
    assert held == set()


def test_the_moved_styles_are_built_once_each_through_the_registry() -> None:
    wanted = {f"BRD-{c}" for _, codes in MOVED.values() for c in codes}
    built = [d["product_id"] for d in scale.templates() if d["product_id"] in wanted]
    assert sorted(built) == sorted(wanted)


def test_the_shared_sports_module_holds_no_rows_of_its_own() -> None:
    assert not hasattr(sports_rows, "docs"), "the build reads these rows through the registry"
    assert {r.department for r in sports_rows.ROWS} == {DEPARTMENT}
    assert {r.code for r in sports_rows.ROWS} >= {c for _, codes in MOVED.values() for c in codes}
