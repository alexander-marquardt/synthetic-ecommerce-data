"""Cleaning, slice 3 (gen#962): sponges and cloths, dishwasher tablets and laundry pods.

After slice 2's bags and wraps the Cleaning department held 6,462 SKUs at the ceiling build, with
no sponge, dishcloth, dishwasher tablet or laundry pod type, so a search for ``scrub sponge`` or
``dishwasher tablets`` found nothing. Slice 3 adds three types, each a spec of its own
(``type_specs/sponges_cloths.py``, ``dishwasher_tablets.py``, ``laundry_pods.py``) drawn by
:mod:`kit_cleaning_care`. These checks hold the issue's Done-when: the ceiling build has at least
8,550 SKUs under the department; each type's styles have unique ids, titles and twin keys; the
rows and their drawings are the same on every call; each drawn param changes the picture; and a
golden slice pins each type's first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    kit,
    paper_rows,
    scale,
    type_registry,
)

TYPES = ("Sponges & Cloths", "Dishwasher Tablets", "Laundry Pods")
KEYS = {"Sponges & Cloths": "sponges_cloths", "Dishwasher Tablets": "dishwasher_tablets",
        "Laundry Pods": "laundry_pods"}  # fmt: skip
#: The issue's floor at the ceiling build (95% of its 9,000 target): 6,462 before this slice.
FLOOR = 8_550


@pytest.fixture(scope="module")
def cleaning() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == paper_rows.ROOT]


def test_the_ceiling_build_holds_the_issue_floor_of_cleaning_skus(cleaning) -> None:
    skus = sum(r["sku_count"] for r in cleaning)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(cleaning) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in cleaning if r["product_id"] in derived}
    assert set(TYPES) <= kinds


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(cleaning, ptype) -> None:
    mine = [r for r in cleaning if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", ("Dishwasher Tablets", "Laundry Pods"))
def test_a_box_of_tablets_and_a_tub_of_pods_are_sold_without_a_color(cleaning, ptype) -> None:
    mine = [r for r in cleaning if r["product_type"] == ptype]
    assert [s for r in mine for s in r["skus"] if "color" in s] == []


def test_a_sponge_or_cloth_template_offers_the_six_main_colors() -> None:
    for row in type_registry.specs()["sponges_cloths"].rows:
        assert [c[0] for c in row.colors] == ["Red", "Blue", "Green", "Yellow", "Black", "White"]


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


#: The slice's three shapes, named here so the module collects before kit_cleaning_care exists.
SHAPES = ("sponge_cloth", "tablet_box", "pod_tub")


def _params() -> dict[str, dict[str, tuple]]:
    """Each shape's params and every value a row or a derived style may give it (gen#512)."""
    from synthetic_ecommerce_data.domains.retail import kit_cleaning_care as k

    return {
        "sponge_cloth": {"kind": tuple(k.SPONGE_KINDS)},
        "tablet_box": {"formula": tuple(k.TABLET_LAYERS), "scent": tuple(k.SCENTS),
                       "tablet_count": tuple(k.BOX_WIDTHS)},
        "pod_tub": {"formula": tuple(k.POD_FORMULAS), "scent": tuple(k.SCENTS),
                    "loads": tuple(k.TUB_HEIGHTS)},
    }  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_every_value_a_derived_style_may_take_is_one_its_shape_draws(cleaning, ptype) -> None:
    mine = [r for r in cleaning if r["product_type"] == ptype]
    shape = mine[0]["drawing"]["shape"]
    params = _params()[shape]
    drawn = {p: {r["drawing"]["params"][p] for r in mine} for p in params}
    assert all(drawn[p] <= set(params[p]) for p in drawn), drawn


@pytest.mark.parametrize("shape", SHAPES)
def test_each_param_value_changes_the_drawing(shape) -> None:
    fill = kit.Fill("solid", "#ffffff", "#2a2a2e")
    for param, values in _params()[shape].items():
        pictures = {kit.render(shape, fill, params={param: v}) for v in values}
        assert len(pictures) == len(values), param


def _golden(cleaning: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in cleaning
                   if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Sponges & Cloths": [],
    "Dishwasher Tablets": [],
    "Laundry Pods": [],
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(cleaning, ptype) -> None:
    assert _golden(cleaning, ptype) == GOLDEN[ptype]
