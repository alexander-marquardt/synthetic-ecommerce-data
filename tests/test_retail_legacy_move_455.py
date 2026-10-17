"""The legacy types move into one spec module each, family by family (gen#455, rest of gen#351).

A move changes no product: the rows leave the shared file and the legacy list, and the same
documents reach the build through the registry. These checks hold the first family, the seven
first-increment Sports & Outdoors types of gen#265 (tents to foam rollers), at the three places a
half-done move shows: the legacy list, the spec file and the shared file it left.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402
import sports_rows  # noqa: E402
import type_registry  # noqa: E402

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
def test_a_moved_type_is_off_the_legacy_list(key: str) -> None:
    ptype, _ = MOVED[key]
    assert (DEPARTMENT, ptype) not in type_registry.legacy_types()


def test_no_sports_type_is_left_on_the_legacy_list() -> None:
    assert {p for d, p in type_registry.legacy_types() if d == DEPARTMENT} == set()


def test_the_moved_styles_are_built_once_each_through_the_registry() -> None:
    wanted = {f"BRD-{c}" for _, codes in MOVED.values() for c in codes}
    built = [d["product_id"] for d in scale.templates() if d["product_id"] in wanted]
    assert sorted(built) == sorted(wanted)


def test_the_shared_sports_module_holds_no_rows_of_its_own() -> None:
    assert sports_rows.docs() == []
    assert {r.code for r in sports_rows.ROWS} >= {c for _, codes in MOVED.values() for c in codes}
