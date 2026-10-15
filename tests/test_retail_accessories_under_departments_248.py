"""Every retail accessory sits under a department Accessories node (gen#248).

The shape is ``<Department> > Accessories > <leaf>``.
Bags, purses and umbrellas once sat under a top-level ``Accessories`` root beside
``Mens > Accessories > Belts`` and ``Beauty > Accessories > Wash Bags``. A root shows as a
separate department in the store's department filter, so there is none: the three leaves sit
under ``Womens > Accessories``. An umbrella (and a backpack or a tote) is unisex, which the
``audience`` facet states; the path does not, and a product sits in one place only.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import accessory_rows  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402

LEAVES = {
    "Handbags": ("Womens", "Accessories", "Bags", "Handbags"),
    "Backpacks": ("Womens", "Accessories", "Bags", "Backpacks"),
    "Tote Bags": ("Womens", "Accessories", "Bags", "Tote Bags"),
    "Purses": ("Womens", "Accessories", "Purses & Wallets", "Purses"),
    "Umbrellas": ("Womens", "Accessories", "Umbrellas"),
}


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    return scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)


def _paths(rows: list[Any]) -> set[tuple[str, ...]]:
    return {tuple(r["category_path"]) for r in rows}


def test_no_template_has_a_top_level_accessories_root() -> None:
    assert [p for p in _paths(scale.templates()) if p[0] == "Accessories"] == []


def test_no_build_record_has_a_top_level_accessories_root(built: scale.Scaled) -> None:
    assert [p for p in _paths(built.records) if p[0] == "Accessories"] == []


def test_the_authored_export_has_no_top_level_accessories_root() -> None:
    assert [p for p in _paths(export.documents()) if p[0] == "Accessories"] == []


@pytest.mark.parametrize("leaf", sorted(LEAVES))
def test_each_accessory_leaf_sits_under_its_department(leaf: str) -> None:
    paths = {tuple(d["category_path"]) for d in accessory_rows.docs()}
    assert LEAVES[leaf] in paths


def test_every_accessory_style_sits_under_a_department_accessories_node() -> None:
    bad = [p for p in _paths(accessory_rows.docs()) if "Bags" in p or "Umbrellas" in p]
    assert [p for p in bad if p[1] != "Accessories" or p[0] != "Womens"] == []
