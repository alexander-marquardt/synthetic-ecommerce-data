"""A beer is drawn as its real can, bottle or 4-pack (gen#1127, slice 3).

Before gen#1127 a lager, sour or alcohol free beer (BLG, BSO, BAF) drew the generic ``tin`` and a
pale ale or fruit beer (BPA, BFR) the generic ``bottle``, each shrunk by :mod:`pack_scale`, and a
4-pack was four copies of that drawing. ``beer`` (:mod:`kit_beer`) draws a crown-capped glass
bottle, a ring-pull can, or 4 cans or 4 bottles from the SKU's own pack. Cover and height span
are measured as the soft drinks test measures them (:mod:`test_soft_drinks_1127`).

The floors are the rethink's on gen#1127, under the 2026-11-15 ruling that the figure draws the
product's real proportions: a bottle is judged on its height span and an area floor its real
outline holds; a 330ml can and a 4-pack on half the product area. A 440ml can is a real can
too, slimmer, so it spans the full height and covers what its outline holds (0.39).
"""

# ruff: noqa: E501 -- one drawing call per line reads better whole than wrapped.

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    grocery,
    kit,
    kit_beer,
    pack_copies,
    pack_scale,
)
from synthetic_ecommerce_data.domains.retail.kit import Fill
from test_soft_drinks_1127 import SVG, _classes, _cover, _span, _svg

#: The beer families: whether the line sells cans or bottles.
LINES = {
    "BLG": "can",
    "BSO": "can",
    "BAF": "can",
    "BPA": "bottle",
    "BFR": "bottle",
}
#: Each single's cover on main 6f3d0518 (the generic tin or bottle at its pack_scale factor).
BEFORE = {
    ("can", "330ml"): 0.020,
    ("can", "440ml"): 0.022,
    ("BPA", "330ml"): 0.093,
    ("BPA", "500ml"): 0.104,
}
#: A 330ml can and a 4-pack paint at least half the product area.
HALF = 0.50
#: A 440ml can (66 x 148 mm) at the full height paints what its outline holds.
TALL_CAN = 0.38
#: A single beer bottle at real proportions paints at least this share of the area. A fruit
#: beer's 500ml covered 0.269 on main as the generic bottle, half again as wide as a real one.
BOTTLE = 0.20
#: The line's largest single bottle spans this share of the area's height, a smaller one this
#: share of it; a can spans the full share wherever it is sold (the wine and soft drink floors).
FULL, STEP = 0.95, 0.8


def _family(rec: dict) -> str:
    return rec["skus"][0]["sku"].split("-")[1]


@pytest.fixture(scope="module")
def beers() -> list[tuple[dict, dict]]:
    rows = [
        (rec, sku)
        for rec in grocery.build(grocery.TARGET)
        if rec["product_type"] == "Beer"
        for sku in rec["skus"]
    ]
    assert rows, "no beer in the grocery build"
    return rows


def _form(rec: dict, sku: dict) -> tuple[str, int, float]:
    return kit_beer.container(sku["pack_size"], LINES[_family(rec)])


def test_every_beer_draws_the_beer_shape_and_spirits_keep_the_bottle(
    beers: list[tuple[dict, dict]],
) -> None:
    assert {rec["drawing"]["shape"] for rec, _ in beers} == {"beer"}
    assert {_family(rec) for rec, _ in beers} == set(LINES)
    for rec, _ in beers:
        assert rec["drawing"]["params"]["line"] == LINES[_family(rec)]
    spirits = {
        rec["drawing"]["shape"]
        for rec in grocery.build(grocery.TARGET)
        if rec["product_type"] in ("Whisky", "Gin", "Vodka", "Rum", "Tequila")
    }
    assert spirits == {"bottle"}


def test_every_pack_fills_its_floor_and_no_single_less_than_before(
    beers: list[tuple[dict, dict]],
) -> None:
    low = []
    for rec, sku in beers:
        form, n, ml = _form(rec, sku)
        share = _cover(_svg(rec, sku))
        if n > 1 or (form == "can" and ml <= 330):
            floor = HALF
        else:
            floor = TALL_CAN if form == "can" else BOTTLE
        before = BEFORE.get((form if form == "can" else _family(rec), sku["pack_size"]), 0.0)
        if share < max(floor, before):
            low.append(
                f"{rec['product_id']} {sku['pack_size']}: {share:.3f} < {max(floor, before)}"
            )
    assert not low, "\n".join(low)


def test_a_bottle_spans_the_area_against_its_largest_and_a_can_the_full_height(
    beers: list[tuple[dict, dict]],
) -> None:
    short = []
    for rec, sku in beers:
        form, n, _ = _form(rec, sku)
        if n > 1:
            continue
        span = _span(_svg(rec, sku))
        largest = rec["drawing"]["params"]["largest"]
        floor = FULL if form == "can" or sku["pack_size"] == largest else FULL * STEP
        if span < floor:
            short.append(
                f"{rec['product_id']} {sku['pack_size']} ({form}) of {largest}: {span:.3f}"
            )
    assert not short, "\n".join(short)


def test_a_four_pack_draws_its_count_and_no_copies(beers: list[tuple[dict, dict]]) -> None:
    packs = [(rec, sku) for rec, sku in beers if _form(rec, sku)[1] > 1]
    assert {_form(rec, sku)[0] for rec, sku in packs} == {"can", "bottle"}
    for rec, sku in packs:
        form, n, _ = _form(rec, sku)
        svg = _svg(rec, sku)
        assert n == sku["units_per_pack"] == 4
        assert len(_classes(svg, form)) == n, (rec["product_id"], sku["pack_size"])
        assert len(_classes(svg, "ring-pull" if form == "can" else "cap")) == n
        assert len(_classes(svg, "carrier")) == 1
        assert "pack_count" not in export.drawing_spec(rec, sku)
        assert pack_copies.copies(rec, sku) == 1


def test_a_bottle_line_sells_a_440ml_as_a_can_and_its_bottles_carry_a_crown_cap(
    beers: list[tuple[dict, dict]],
) -> None:
    assert kit_beer.container("440ml", "bottle") == ("can", 1, 440.0)
    assert kit_beer.container("500ml", "bottle") == ("bottle", 1, 500.0)
    assert kit_beer.container("330ml", "can") == ("can", 1, 330.0)
    for rec, sku in beers:
        form, n, _ = _form(rec, sku)
        if n == 1:
            svg = _svg(rec, sku)
            assert len(_classes(svg, form)) == 1
            assert len(_classes(svg, "ring-pull" if form == "can" else "cap")) == 1


def test_each_beer_shows_its_own_color_through_its_glass_or_on_its_can(
    beers: list[tuple[dict, dict]],
) -> None:
    glass = {"BPA": "brown", "BFR": "clear"}
    seen: dict[str, set[str]] = {"bottle": set(), "can": set()}
    for rec, sku in beers:
        form, n, _ = _form(rec, sku)
        if n > 1:
            continue
        svg = _svg(rec, sku)
        color = rec["drawing"]["base"]
        if form == "bottle":
            assert rec["drawing"]["params"]["glass"] == glass[_family(rec)]
            (drink,) = _classes(svg, "drink")
            assert drink.get("fill") == kit_beer.through(color, glass[_family(rec)])
            seen["bottle"].add(drink.get("fill") or "")
        else:
            (livery,) = _classes(svg, "livery")
            assert livery.get("fill") == color
            seen["can"].add(color)
    assert len(seen["bottle"]) > 1 and len(seen["can"]) > 1


def test_brown_glass_hides_more_of_the_beer_than_clear_glass() -> None:
    fill = Fill("solid", "#e8b04a", "#ffffff")
    drinks = {}
    for glass in ("brown", "clear"):
        svg = SVG.format("".join(kit_beer.beer("#e8b04a", fill, "Ale", pack_size="500ml", line="bottle", glass=glass)))  # fmt: skip
        (drink,) = _classes(svg, "drink")
        drinks[glass] = drink.get("fill")
    assert drinks["brown"] != drinks["clear"]
    assert drinks["clear"] == kit_beer.through("#e8b04a", "clear")
    with pytest.raises(ValueError):
        kit_beer.beer("#e8b04a", fill, "Ale", line="keg")


def test_a_beer_takes_no_pack_scale_factor_and_draws_its_own_pack(
    beers: list[tuple[dict, dict]],
) -> None:
    assert "beer" in pack_scale.SELF_SIZED
    assert all(pack_scale.factor(rec, sku) is None for rec, sku in beers)
    rec, _ = beers[0]
    assert pack_copies.self_drawn(rec, 4)
    assert kit.SHAPES["beer"] is kit_beer.beer
