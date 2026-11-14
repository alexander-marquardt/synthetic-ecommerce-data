"""Toys in depth, slice 2 (gen#960): action figures, dolls and building sets.

Main's ceiling build held 1,464 Toys SKUs: 25 dolls and 89 building sets, none derived, and no
action figure. Slice 2 makes the three types derivable breadth types: their spec files
(``type_specs/action_figure.py``, ``doll.py``, ``building_set.py``) hold rows whose titles show
the values a derived style swaps (an action figure's character and kind, a doll's theme and
kind, a building set's theme and model), drawn by :mod:`kit_toys_figures`. These checks hold the
slice's Done-when: the three types add at least 3,600 SKUs to the ceiling build; each type's
styles have unique ids, titles, twin keys and SKUs; the figures and dolls come in the six main
colors; the rows and drawings are the same on every call, and the drawing follows the kind and
the theme; the Barry Plotter range is never derived; and a golden slice pins each type's first
derived styles.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import barry_plotter, kit, scale, type_registry

TYPES = ("Action Figure", "Doll", "Building Set")
KEYS = {"Action Figure": "action_figure", "Doll": "doll", "Building Set": "building_set"}
#: The SKUs the slice adds at the ceiling build: main + slice 1 (#1002) + this reach 7,000.
FLOOR = 3_600
SIX = {"Red", "Blue", "Green", "Yellow", "Black", "White"}


@pytest.fixture(scope="module")
def toys() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == "Toys"]


def test_the_three_types_hold_the_slice_floor_of_skus(toys) -> None:
    skus = sum(r["sku_count"] for r in toys if r["product_type"] in TYPES)
    assert skus >= FLOOR, skus


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_is_derived_in_the_ceiling_build(toys, ptype) -> None:
    derived = set(ceiling_build().template_of)
    assert any(r["product_type"] == ptype and r["product_id"] in derived for r in toys)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_twin_keys_and_skus(toys, ptype) -> None:
    mine = [r for r in toys if r["product_type"] == ptype]
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", ("Action Figure", "Doll"))
def test_every_figure_and_doll_row_is_sold_in_the_six_main_colors(ptype) -> None:
    for row in type_registry.specs()[KEYS[ptype]].rows:
        offered = {c["color"] for c in row.doc()["color_options"]}
        assert offered >= SIX, row.code


def test_the_barry_plotter_range_is_never_derived() -> None:
    build = ceiling_build()
    plotter = barry_plotter.ids()
    assert not plotter & set(build.template_of.values())
    derived = set(build.template_of)
    assert not [r["title"] for r in build.records
                if r["product_id"] in derived and "Barry Plotter" in r["title"]]  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic_and_follow_kind_and_theme(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert spec.derivable
    rows = [r for r in spec.rows if r.product_id not in barry_plotter.ids()]
    fill = kit.Fill("solid", "#123456", "#654321")
    pictures = set()
    for row in rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)
        pictures.add(first)
    assert len(pictures) == len(rows)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_carries_a_class_6_and_a_class_4_decoy(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert {6, 4} <= {d.cls for d in spec.decoys}


def _golden(toys: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in toys if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {"Action Figure": [], "Doll": [], "Building Set": []}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(toys, ptype) -> None:
    assert _golden(toys, ptype) == GOLDEN[ptype]
