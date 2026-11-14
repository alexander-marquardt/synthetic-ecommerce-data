"""Cleaning, slice 1 (gen#962): paper goods, with toilet paper, paper towels and facial tissues.

The Cleaning department held 835 SKUs at the ceiling build, nearly all sprays and detergents, so
a search for ``paper towels`` or ``toilet paper`` found nothing. Slice 1 adds three types under
``Cleaning > Paper Goods``, each a spec of its own (``type_specs/toilet_paper.py``,
``paper_towels.py``, ``facial_tissues.py``) drawn by :mod:`kit_paper`. These checks hold the
slice's Done-when: the ceiling build has at least 2,800 SKUs under the department; each type's
styles have unique ids, titles and twin keys; the rows and their drawings are the same on every
call; each drawn param changes the picture; and a golden slice pins each type's first derived
styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, kit_paper, paper_rows, scale, type_registry

TYPES = ("Toilet Paper", "Paper Towels", "Facial Tissues")
KEYS = {"Toilet Paper": "toilet_paper", "Paper Towels": "paper_towels",
        "Facial Tissues": "facial_tissues"}  # fmt: skip
#: The slice's floor at the ceiling build (the gate comment of gen#962): 835 before it.
FLOOR = 2_800


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


@pytest.mark.parametrize("ptype", ("Toilet Paper", "Paper Towels"))
def test_a_roll_of_white_paper_is_sold_without_a_color(cleaning, ptype) -> None:
    mine = [r for r in cleaning if r["product_type"] == ptype]
    assert [s for r in mine for s in r["skus"] if "color" in s] == []


def test_a_tissue_template_offers_its_box_in_the_six_main_colors() -> None:
    for row in type_registry.specs()["facial_tissues"].rows:
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
    "toilet_roll": {"roll_size": tuple(kit_paper.TOILET_SIZES), "ply": tuple(kit_paper.PLIES),
                    "finish": ("ultra soft", "quilted", "ultra strong", "recycled")},
    "paper_towel_roll": {"roll_size": tuple(kit_paper.TOWEL_SIZES),
                         "sheet": ("full sheet", "half sheet"),
                         "finish": ("extra absorbent", "ultra strong", "embossed", "recycled")},
    "tissue_box": {"box": ("cube", "flat"), "ply": ("2-ply", "3-ply")},
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
        if shape == "toilet_roll" and param == "finish":
            # Ultra Soft and Ultra Strong are a feel, not a look: quilted and recycled draw.
            assert len(pictures) == 3, param
        elif shape == "paper_towel_roll" and param == "finish":
            assert len(pictures) == 3, param
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
    "Toilet Paper": [
        ("BRD-00253D010CDE", "Salcroft Ultra Strong 3-Ply Toilet Paper, Mega Rolls", 6, 3.55),
        ("BRD-00EF506C9697", "Wykefell Ultra Strong 4-Ply Toilet Paper, Mega Rolls", 6, 3.25),
        ("BRD-033E1D3D791A", "Denington Ultra Soft 4-Ply Toilet Paper, Mega Rolls", 6, 3.05),
    ],
    "Paper Towels": [
        ("BRD-0410EECB425D", "Mordale Embossed Paper Towels, Half Sheet, Triple Rolls", 5, 3.3),
        ("BRD-046AAA078A64", "Ellerborough Recycled Paper Towels, Full Sheet, Double Rolls", 5,
         4.25),
        ("BRD-04B2FA3C12AA", "Lamstead Ultra Strong Paper Towels, Half Sheet, Regular Rolls", 5,
         2.65),
    ],
    "Facial Tissues": [
        ("BRD-001DED332822", "Glenwood Lotion 3-Ply Facial Tissues, Flat Box", 16, 2.6),
        ("BRD-02B93040D771", "Rosridge Menthol 2-Ply Facial Tissues, Cube Box", 8, 1.75),
        ("BRD-0D593922307B", "Rudness Menthol 3-Ply Facial Tissues, Flat Box", 20, 1.65),
    ],
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(cleaning, ptype) -> None:
    assert _golden(cleaning, ptype) == GOLDEN[ptype]
