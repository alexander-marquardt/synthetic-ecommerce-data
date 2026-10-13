"""Toy vehicles and ride-ons come in a full color range, bikes in sizes (gen#271).

A toy car, a scooter, a trike or a ride-on whose paint is a free choice is sold in about
ten colors, each its own SKU with its own drawing. A product whose color IS what it is
(the police car's livery, the London taxi, a red fire engine, unpainted wood) keeps one
color and says why in the row's ``fixed_color`` field, so it is never a silent omission.
A bike is sold in sizes: its wheel size is a SKU axis, and the drawing scales with it.
"""

from __future__ import annotations

import dataclasses
import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import breadth_rows  # noqa: E402
import colorwords  # noqa: E402
import export  # noqa: E402
import toys_rows  # noqa: E402

#: The leaves the issue names: toy cars and every ride-on (bikes, scooters, trikes).
LEAVES = {"Toy Vehicles", "Ride-On Toys"}
MIN_COLORS = 8
MIN_BIKE_SIZES = 3

#: The styles whose color is what the product is. A hand-kept census: a style joins it
#: with a reason on its row, and this list says so in review.
FIXED = {"CARPOL", "CARBMB", "CARTIN", "RIDWDB", "RIDSC2"}


def vehicle_rows() -> list:
    return [r for r in (*breadth_rows.TOYS, *toys_rows.RIDE_ONS) if r.path[-1] in LEAVES]


def _bike(row) -> bool:
    return any(a[0] == "toy_type" and "Bike" in a[2] for a in row.attrs)


def short_of_colors(rows) -> list[str]:
    """The free-paint styles with fewer than :data:`MIN_COLORS` colors."""
    return sorted(r.code for r in rows if not r.fixed_color and len(r.colors) < MIN_COLORS)


def short_of_sizes(rows) -> list[str]:
    """The bike styles with fewer than :data:`MIN_BIKE_SIZES` sizes on the size axis."""
    return sorted(r.code for r in rows if _bike(r) and len(r.sizes) < MIN_BIKE_SIZES)


def test_the_census_covers_the_toy_vehicles_and_the_ride_ons() -> None:
    rows = vehicle_rows()
    assert {r.path[-1] for r in rows} == LEAVES
    assert {r.code for r in rows if r.fixed_color} == FIXED
    assert len(rows) > len(FIXED) + 6


def test_every_free_paint_style_has_at_least_eight_colors() -> None:
    assert short_of_colors(vehicle_rows()) == []


def test_every_free_paint_style_sells_each_color_as_its_own_sku() -> None:
    for row in vehicle_rows():
        if row.fixed_color:
            continue
        colors = [s["color"] for s in row.skus()]
        assert len(set(colors)) >= MIN_COLORS, row.code
        names = [c[0] for c in row.colors]
        assert len(names) == len(set(names)), row.code


def test_a_fixed_color_style_keeps_one_color_and_says_why() -> None:
    wrong = {
        r.code: (len(r.colors), r.fixed_color)
        for r in vehicle_rows()
        if r.fixed_color and (len(r.colors) != 1 or len(r.fixed_color) < 10)
    }
    assert wrong == {}


def test_a_style_cut_to_three_colors_is_caught() -> None:
    """The hand mutant of the acceptance: one style down to 3 colors reds the guard."""
    rows = vehicle_rows()
    target = next(r for r in rows if not r.fixed_color)
    mutant = [dataclasses.replace(target, colors=target.colors[:3]) if r is target else r
              for r in rows]
    assert short_of_colors(mutant) == [target.code]


def test_every_bike_style_has_at_least_three_sizes() -> None:
    bikes = [r for r in vehicle_rows() if _bike(r)]
    assert len(bikes) >= 2
    assert short_of_sizes(vehicle_rows()) == []


def test_a_bike_collapsed_to_one_size_is_caught() -> None:
    rows = vehicle_rows()
    target = next(r for r in rows if _bike(r))
    mutant = [dataclasses.replace(target, sizes=target.sizes[:1]) if r is target else r
              for r in rows]
    assert short_of_sizes(mutant) == [target.code]


def test_a_bike_size_is_a_wheel_size_not_the_garment_size() -> None:
    for row in vehicle_rows():
        if not _bike(row):
            continue
        assert row.size_key == "wheel_size_in", row.code
        doc = export.standard_document(row.doc())
        product_keys = {e["key"] for e in doc["attributes"]}
        assert "wheel_size" not in product_keys, row.code
        for variant in doc["variants"]:
            keys = [e["key"] for e in variant["attributes"]]
            assert "wheel_size" in keys and "size" not in keys, row.code


def test_a_trike_takes_a_wheel_size_too() -> None:
    trike = next(r for r in toys_rows.RIDE_ONS if dict(r.params).get("kind") == "trike")
    assert trike.size_key == "wheel_size_in"
    assert len(trike.sizes) >= 2


def test_every_color_and_size_is_its_own_drawing() -> None:
    for row in vehicle_rows():
        rec = row.doc()
        images = [export.image_id(rec, sku) for sku in rec["skus"]]
        assert len(images) == len(set(images)), row.code


def test_the_drawing_scales_with_the_wheel_size() -> None:
    rec = next(r for r in toys_rows.RIDE_ONS if _bike(r) and len(r.colors) > 1).doc()
    one_color = [s for s in rec["skus"] if s["color"] == rec["skus"][0]["color"]]
    specs = {s.get("wheel_size_in"): export.drawing_spec(rec, s) for s in one_color}
    assert None not in specs
    assert len(specs) >= MIN_BIKE_SIZES
    assert len({repr(v) for v in specs.values()}) == len(specs)


def test_every_color_name_is_a_shared_vocabulary_word_with_one_spelling() -> None:
    names: dict[str, set[str]] = {}
    for row in vehicle_rows():
        for color in row.colors:
            assert colorwords.is_plain(color[0]), (row.code, color[0])
            names.setdefault(color[0].casefold(), set()).add(color[0])
    assert {k: v for k, v in names.items() if len(v) > 1} == {}


def test_no_title_or_description_names_a_color_the_style_does_not_sell() -> None:
    words = {w for w in colorwords.COLOR_WORDS}
    wrong = {}
    for row in vehicle_rows():
        sold = {w for c in row.colors for w in re.findall(r"[A-Za-z]+", c[0])}
        text = f"{row.title} {row.description}"
        named = {w for w in re.findall(r"[A-Za-z]+", text) if w in words}
        if named - sold - {"Natural"}:
            wrong[row.code] = sorted(named - sold)
    assert wrong == {}


@pytest.mark.parametrize("code", sorted(FIXED))
def test_each_fixed_color_style_is_a_real_row(code: str) -> None:
    assert code in {r.code for r in vehicle_rows()}
