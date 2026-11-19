"""Cleaning, slice 2 (gen#962): bags and wraps, with trash bags, food storage bags and food wrap.

After slice 1's paper goods the Cleaning department held 3,679 SKUs at the ceiling build, with no
trash bags, zip bags, foil or plastic wrap, so a search for ``trash bags`` or ``aluminum foil``
found nothing. Slice 2 adds three types under ``Cleaning > Bags & Wraps``, each a spec of its own
(``type_specs/trash_bags.py``, ``food_storage_bags.py``, ``food_wrap.py``) drawn by
:mod:`kit_bags_wrap`. These checks hold the slice's Done-when: the ceiling build has at least
5,600 SKUs under the department; each type's styles have unique ids, titles and twin keys; the
rows and their drawings are the same on every call; each drawn param changes the picture; and a
golden slice pins each type's first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    kit,
    kit_bags_wrap,
    paper_rows,
    scale,
    type_registry,
)

TYPES = ("Trash Bags", "Food Storage Bags", "Food Wrap")
KEYS = {"Trash Bags": "trash_bags", "Food Storage Bags": "food_storage_bags",
        "Food Wrap": "food_wrap"}  # fmt: skip
#: The slice's floor at the ceiling build (the gate comments of gen#962): 3,679 before it.
FLOOR = 5_600


@pytest.fixture(scope="module")
def cleaning() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == paper_rows.ROOT]


def test_the_ceiling_build_holds_the_slice_floor_of_cleaning_skus(cleaning) -> None:
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


@pytest.mark.parametrize("ptype", ("Food Storage Bags", "Food Wrap"))
def test_a_clear_bag_and_a_roll_of_wrap_are_sold_without_a_color(cleaning, ptype) -> None:
    mine = [r for r in cleaning if r["product_type"] == ptype]
    assert [s for r in mine for s in r["skus"] if "color" in s] == []


def test_a_trash_bag_template_offers_the_six_main_colors() -> None:
    for row in type_registry.specs()["trash_bags"].rows:
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


#: Each shape's params and every value a row or a derived style may give it (gen#512).
PARAMS = {
    "trash_bag": {"closure": ("drawstring", "tie handle", "flap tie"),
                  "use": tuple(kit_bags_wrap.TRASH_SIZES)},
    "zip_bag": {"closure": ("zip seal", "slider", "fold top"),
                "kind": ("freezer", "sandwich", "snack"),
                "bag_size": tuple(kit_bags_wrap.BAG_SIZES)},
    "wrap_box": {"material": tuple(kit_bags_wrap.MATERIALS),
                 "roll": tuple(kit_bags_wrap.ROLL_LENGTHS),
                 "grade": ("everyday", "heavy duty", "extra wide")},
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_every_value_a_derived_style_may_take_is_one_its_shape_draws(cleaning, ptype) -> None:
    mine = [r for r in cleaning if r["product_type"] == ptype]
    shape = mine[0]["drawing"]["shape"]
    drawn = {p: {r["drawing"]["params"][p] for r in mine} for p in PARAMS[shape]}
    assert all(drawn[p] <= set(PARAMS[shape][p]) for p in drawn), drawn


@pytest.mark.parametrize("shape", tuple(PARAMS))
def test_each_param_value_changes_the_drawing(shape) -> None:
    fill = kit.Fill("solid", "#ffffff", "#2a2a2e")
    for param, values in PARAMS[shape].items():
        pictures = {kit.render(shape, fill, params={param: v}) for v in values}
        if shape == "wrap_box" and param == "grade":
            # Everyday and Heavy Duty are a feel, not a look: an extra wide roll draws a deeper box.
            assert len(pictures) == 2, param
        else:
            assert len(pictures) == len(values), param


def _golden(cleaning: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in cleaning
                   if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Trash Bags": [
        ("BRD-024E4FD4E4D7", "Mildale Tear Resistant Drawstring Kitchen Trash Bags", 6, 6.5),
        ("BRD-03AE1649B8D3", "Lonworth Heavy Duty Tie Handle Bathroom Trash Bags", 12, 4.55),
        ("BRD-05E73AFE5533", "Zenworth Tear Resistant Drawstring Bathroom Trash Bags", 15, 3.95),
    ],
    "Food Storage Bags": [
        ("BRD-0093A797EFD0", "Horwyke Fold Top Snack Bags, Large", 5, 2.85),
        ("BRD-03222E9A5BDC", "Horhill Slider Snack Bags, Medium", 5, 2.15),
        ("BRD-089DDEE0A793", "Stokestone Fold Top Snack Bags, Small", 5, 2.75),
    ],
    "Food Wrap": [
        ("BRD-00772D88C5D5", "Barcliffe Heavy Duty Plastic Wrap, Large Roll", 3, 4.35),
        ("BRD-02585D96E700", "Kelley Everyday Plastic Wrap, Jumbo Roll", 3, 3.6),
        ("BRD-06F48834B63E", "Ryworth Heavy Duty Wax Paper, Large Roll", 3, 2.75),
    ],
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(cleaning, ptype) -> None:
    assert _golden(cleaning, ptype) == GOLDEN[ptype]
