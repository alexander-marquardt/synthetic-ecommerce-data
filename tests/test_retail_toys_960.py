"""Toys in depth, slice 1 (gen#960): board games, jigsaw puzzles and card games.

The Toys department held 1,464 SKUs at the ceiling build, 10 of them board games and 7 jigsaws,
because every game and puzzle row was a template only. Slice 1 makes the three types derivable
breadth types: their spec files (``type_specs/board_game.py``, ``jigsaw_puzzle.py``,
``card_game.py``) hold rows whose titles show the values a derived style swaps (a board game's
theme and kind, a jigsaw's theme, a card game's kind and theme). These checks hold the slice's
Done-when: the ceiling build has at least 3,000 SKUs under ``Toys``; each type's styles have
unique ids, titles and twin keys; the rows and their drawings are the same on every call; a
derived style keeps its template's age range, play time and finished size; and a golden slice
pins each type's first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

TYPES = ("Board Game", "Jigsaw Puzzle", "Card Game")
KEYS = {"Board Game": "board_game", "Jigsaw Puzzle": "jigsaw_puzzle", "Card Game": "card_game"}
#: The slice's floor at the ceiling build (the gate comment of gen#960).
FLOOR = 3_000
#: The entries a derived style keeps from its template: an age, a play time and a size follow
#: the piece count and the kind of game the template is, never a draw.
KEPT = ("age_range", "play_time", "finished_size")


@pytest.fixture(scope="module")
def toys() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == "Toys"]


def test_the_ceiling_build_holds_the_slice_floor_of_toys_skus(toys) -> None:
    skus = sum(r["sku_count"] for r in toys)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(toys) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in toys if r["product_id"] in derived}
    assert set(TYPES) <= kinds


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(toys, ptype) -> None:
    mine = [r for r in toys if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", TYPES)
def test_a_derived_style_keeps_its_templates_age_play_time_and_size(toys, ptype) -> None:
    build = ceiling_build()
    by_id = {r["product_id"]: r for r in build.records}

    def kept(rec: dict) -> dict[str, str]:
        return {a["key"]: str(a["value"]) for a in rec["attributes"] if a["key"] in KEPT}

    derived = [r for r in toys
               if r["product_type"] == ptype and r["product_id"] in build.template_of]  # fmt: skip
    assert derived
    moved = [r["product_id"] for r in derived
             if kept(r) != kept(by_id[build.template_of[r["product_id"]]])]  # fmt: skip
    assert moved == []


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert spec.derivable
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


def _golden(toys: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in toys if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {  # fmt: skip
    "Board Game": [
        ("BRD-00CDBC0B4318", "Pipwick Toys Imagine Farmyard Frolic Party Board Game", 3, 18.0),
        ("BRD-01E496529CE6", "Pipwick Toys Imagine Wildwood Forest Family Board Game", 3, 15.0),
        ("BRD-02096B1A91DE", "Lanternby Wonder Wizard Academy Family Board Game", 3, 23.0),
    ],
    "Jigsaw Puzzle": [
        (
            "BRD-033462830AF2",
            "Puddlecombe Toys Pretend World Map 1200 Piece Jigsaw Puzzle",
            1,
            16.0,
        ),
        ("BRD-0790FABADDDA", "Calderby & Lune Caper World Map 200 Piece Jigsaw Puzzle", 1, 11.5),
        ("BRD-0D31E4C3132C", "Lanternby Wobble Dinosaur 300 Piece Jigsaw Puzzle", 1, 12.5),
    ],
    "Card Game": [
        ("BRD-003AD9103AC0", "Pipwick Toys Imagine Garden Gnomes Party Card Game", 3, 11.5),
        ("BRD-022B945AAD59", "Pipwick Toys Imagine Racing Snails Strategy Card Game", 3, 7.0),
        ("BRD-02E397FE9A73", "Puddlecombe Toys Pretend Ninja Kittens Strategy Card Game", 3, 8.5),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(toys, ptype) -> None:
    assert _golden(toys, ptype) == GOLDEN[ptype]
