"""Toys in depth, slice 3 (gen#960): arts and crafts kits, remote-control vehicles, learning toys.

Main's ceiling build held 1,464 Toys SKUs: 12 craft kits, all templates only, and no
remote-control vehicle or learning toy. Slice 3 makes the three types derivable breadth types:
their spec files (``type_specs/arts_and_crafts_kit.py``, ``remote_control_vehicle.py``,
``learning_toy.py``) hold rows whose titles show the values a derived style swaps (the theme and
the kind), drawn by :mod:`kit_toys_learning`. These checks hold the slice's Done-when: the three
types add at least 3,280 SKUs to the ceiling build, so main + slice 1 (#1002, +1,938) + slice 2
(#1007, +3,768) + this reach the issue's 10,450; each type's styles have unique ids, titles,
twin keys and SKUs; the vehicles and learning toys come in the six main colors; the rows and
drawings are the same on every call, and the drawing follows the kind and the theme; and a
golden slice pins each type's first derived styles.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

TYPES = ("Arts and Crafts Kit", "Remote-Control Vehicle", "Learning Toy")
KEYS = {
    "Arts and Crafts Kit": "arts_and_crafts_kit",
    "Remote-Control Vehicle": "remote_control_vehicle",
    "Learning Toy": "learning_toy",
}
#: The SKUs the three types hold at the ceiling build: 10,450 - 1,464 - 1,938 - 3,768.
FLOOR = 3_280
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


@pytest.mark.parametrize("ptype", ("Remote-Control Vehicle", "Learning Toy"))
def test_every_vehicle_and_learning_toy_row_is_sold_in_the_six_main_colors(ptype) -> None:
    for row in type_registry.specs()[KEYS[ptype]].rows:
        offered = {c["color"] for c in row.doc()["color_options"]}
        assert offered >= SIX, row.code


def test_a_craft_kit_is_colorless_and_sold_in_four_piece_counts() -> None:
    for row in type_registry.specs()["arts_and_crafts_kit"].rows:
        assert row.colorless, row.code
        assert [s for s, _ in row.sizes] == ["250", "500", "1000", "2000"], row.code


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic_and_follow_kind_and_theme(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert spec.derivable
    fill = kit.Fill("solid", "#123456", "#654321")
    pictures = set()
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)
        pictures.add(first)
    assert len(pictures) == len(spec.rows)
    kinds = {dict(row.params)["kind"] for row in spec.rows}
    shape, theme = spec.rows[0].shape, dict(spec.rows[0].params)["theme"]
    drawn = {kit.render(shape, fill, params={"kind": k, "theme": theme}) for k in kinds}
    assert len(drawn) == len(kinds) == 4


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
GOLDEN: dict[str, list[tuple]] = {
    "Arts and Crafts Kit": [
        ("BRD-015AC5D14340", "Thistle & Wren Frolic Butterfly Garden Pom-Pom Kit", 4, 8.5),
        ("BRD-025B57565EC0", "Calderby & Lune Bounce Polar Friends Gem Art Kit", 4, 8.0),
        ("BRD-033151BE2230", "Little Fernby Skip Candy Shop Gem Art Kit", 4, 12.0),
    ],
    "Remote-Control Vehicle": [
        (
            "BRD-0060ACD63ECA",
            "Puddlecombe Toys Whizz Lagoon Skipper Remote-Control Truck",
            2,
            32.0,
        ),
        (
            "BRD-008EDCE03A88",
            "Thistle & Wren Pretend Wave Dasher Remote-Control Helicopter",
            2,
            23.0,
        ),
        ("BRD-01584ABAA280", "Little Fernby Skip Track Blazer Remote-Control Boat", 2, 40.0),
    ],
    "Learning Toy": [
        ("BRD-00998F125497", "Lanternby Caper Clever Owl Shape Sorter", 2, 27.0),
        ("BRD-01D59194F9AC", "Puddlecombe Toys Imagine Dino Discovery Activity Cube", 6, 16.5),
        ("BRD-028B85676BFF", "Pipwick Toys Squeak Snail Trail Activity Cube", 6, 14.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(toys, ptype) -> None:
    assert _golden(toys, ptype) == GOLDEN[ptype]
