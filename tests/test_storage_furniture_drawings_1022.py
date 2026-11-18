"""The storage furniture the generator could not draw (gen#1022, slice 2).

Sideboards, bar cabinets, office storage cabinets, shoe storage and wall shelves each get a kit
shape of their own, drawn from the attributes a record states, with slice 1's promises: each
param value draws a picture of its own, the drawn count of doors, drawers, shelves, tiers and
stools is the stated count, a value outside the shape's table is refused, and a White piece
reads white (the gen#226 rule for the rest of the furniture range).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import kit, kit_storage_furniture, orientation
from test_retail_furniture_drawings_226 import BASE, _lum, _rgb, _structure_luminances

TYPES = ("sideboard", "bar_cabinet", "storage_cabinet", "shoe_storage", "wall_shelf")
WOOD = kit.Fill("solid", "#8a5a3a", "#333333", "#f2d14b")


def _svg(shape: str, **params: str) -> str:
    return kit.render(shape, WOOD, params=params or None)


def _count(svg: str, cls: str) -> int:
    return len(re.findall(rf'class="{cls}"', svg))


def test_the_five_types_are_registered_with_their_param_tables() -> None:
    kit.register_all()
    assert set(kit_storage_furniture.PARAMS) == set(TYPES)
    assert set(TYPES) <= set(kit.SHAPES)
    for shape in TYPES:
        assert orientation.of(shape) == "upright", shape


@pytest.mark.parametrize("shape", TYPES)
def test_each_type_draws_a_well_formed_svg_with_a_body(shape: str) -> None:
    svg = _svg(shape)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert len(re.findall(r"<(?:rect|path|circle|ellipse)\b", svg)) >= 8, shape
    assert WOOD.base in svg, f"{shape} does not paint the record's color"


@pytest.mark.parametrize(
    ("shape", "key"),
    [(s, k) for s in TYPES for k in kit_storage_furniture.PARAMS[s]],
)
def test_every_value_of_a_param_draws_a_picture_of_its_own(shape: str, key: str) -> None:
    values = kit_storage_furniture.PARAMS[shape][key]
    assert len(values) >= 2, (shape, key)
    pictures = {_svg(shape, **{key: v}) for v in values}
    for svg in pictures:
        ET.fromstring(svg)  # every variant is a well-formed document, not only the default
    assert len(pictures) == len(values), (shape, key)


@pytest.mark.parametrize("shape", TYPES)
def test_a_value_outside_the_table_is_refused(shape: str) -> None:
    for key in kit_storage_furniture.PARAMS[shape]:
        with pytest.raises(ValueError, match=key):
            _svg(shape, **{key: "seventeen"})


@pytest.mark.parametrize(
    ("shape", "key", "cls"),
    [
        ("sideboard", "doors", "door"),
        ("sideboard", "drawers", "drawer"),
        ("bar_cabinet", "doors", "door"),
        ("bar_cabinet", "stools", "stool"),
        ("storage_cabinet", "shelves", "shelf"),
        ("storage_cabinet", "drawers", "drawer"),
        ("shoe_storage", "tiers", "tier"),
        ("wall_shelf", "shelves", "shelf"),
    ],
)
def test_the_drawn_count_is_the_stated_count(shape: str, key: str, cls: str) -> None:
    for value in kit_storage_furniture.PARAMS[shape][key]:
        assert _count(_svg(shape, **{key: value}), cls) == int(value), (shape, key, value)


def test_a_bracket_shelf_draws_two_brackets_per_shelf_and_a_floating_one_none() -> None:
    for n in kit_storage_furniture.PARAMS["wall_shelf"]["shelves"]:
        assert _count(_svg("wall_shelf", shelves=n, mount="bracket"), "bracket") == 2 * int(n)
        assert _count(_svg("wall_shelf", shelves=n, mount="floating"), "bracket") == 0


def test_a_shoe_bench_has_a_seat_and_a_rack_has_none() -> None:
    assert _count(_svg("shoe_storage", form="bench"), "seat") == 1
    assert _count(_svg("shoe_storage", form="rack"), "seat") == 0


def test_a_glass_front_shows_its_shelves_through_the_glass() -> None:
    assert _count(_svg("storage_cabinet", front="glass"), "glass") >= 1
    assert _count(_svg("storage_cabinet", front="open"), "glass") == 0


def test_a_lock_is_drawn_only_when_the_cabinet_locks() -> None:
    assert _count(_svg("storage_cabinet", lock="yes"), "lock") == 1
    assert _count(_svg("storage_cabinet", lock="no"), "lock") == 0


def test_a_bar_cabinet_hangs_glasses_only_from_a_glass_rack() -> None:
    assert _count(_svg("bar_cabinet", glass_rack="yes"), "wine_glass") >= 2
    assert _count(_svg("bar_cabinet", glass_rack="no"), "wine_glass") == 0


@pytest.mark.parametrize("shape", TYPES)
def test_a_white_piece_reads_white(shape: str) -> None:
    """At least 80% of the body's painted area keeps 80% of White's own lightness."""
    white = _lum(_rgb(BASE))
    fill = kit.Fill("solid", BASE, "#333333", "#f2d14b")
    lums = _structure_luminances(kit.render(shape, fill))
    assert lums, shape
    light = sum(1 for v in lums if v >= 0.8 * white) / len(lums)
    assert light >= 0.8, (shape, light)
