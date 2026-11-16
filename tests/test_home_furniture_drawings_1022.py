"""The home-furniture types the generator could not draw (gen#1022, slice 1).

Bar stools, desks, office chairs, TV stands and kitchen islands each get a kit shape of their
own, drawn from the attributes a record states: a bar-height stool is taller than a counter
stool, a desk with three drawers draws three drawer fronts, a TV stand draws one door per door.
Each param value draws a picture of its own, a value outside the shape's table is refused, and
a White piece reads white (the gen#226 rule for the rest of the furniture range).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import kit, kit_home_furniture, orientation
from test_retail_furniture_drawings_226 import BASE, _lum, _rgb, _structure_luminances

TYPES = ("bar_stool", "desk", "office_chair", "tv_stand", "kitchen_island")
WOOD = kit.Fill("solid", "#8a5a3a", "#333333", "#f2d14b")


def _svg(shape: str, **params: str) -> str:
    return kit.render(shape, WOOD, params=params or None)


def _count(svg: str, cls: str) -> int:
    return len(re.findall(rf'class="{cls}"', svg))


def test_the_five_types_are_registered_with_their_param_tables() -> None:
    kit.register_all()
    assert set(kit_home_furniture.PARAMS) == set(TYPES)
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
    [(s, k) for s in TYPES for k in kit_home_furniture.PARAMS[s]],
)
def test_every_value_of_a_param_draws_a_picture_of_its_own(shape: str, key: str) -> None:
    values = kit_home_furniture.PARAMS[shape][key]
    assert len(values) >= 2, (shape, key)
    pictures = {_svg(shape, **{key: v}) for v in values}
    assert len(pictures) == len(values), (shape, key)


@pytest.mark.parametrize("shape", TYPES)
def test_a_value_outside_the_table_is_refused(shape: str) -> None:
    for key in kit_home_furniture.PARAMS[shape]:
        with pytest.raises(ValueError, match=key):
            _svg(shape, **{key: "seventeen"})


@pytest.mark.parametrize(
    ("shape", "key", "cls"),
    [
        ("desk", "drawers", "drawer"),
        ("tv_stand", "doors", "door"),
        ("tv_stand", "shelves", "shelf"),
        ("kitchen_island", "doors", "door"),
        ("kitchen_island", "drawers", "drawer"),
    ],
)
def test_the_drawn_count_is_the_stated_count(shape: str, key: str, cls: str) -> None:
    for value in kit_home_furniture.PARAMS[shape][key]:
        assert _count(_svg(shape, **{key: value}), cls) == int(value), (shape, key, value)


def test_a_bar_stool_stands_taller_than_a_counter_stool() -> None:
    def seat_y(height: str) -> float:
        m = re.search(r'<[^>]*class="seat"[^>]*\by="([\d.]+)"', _svg("bar_stool", height=height))
        assert m, height
        return float(m[1])

    assert seat_y("bar") < seat_y("counter") - 20


def test_an_office_chair_has_arms_only_when_it_says_so() -> None:
    assert _count(_svg("office_chair", arms="yes"), "arm") == 2
    assert _count(_svg("office_chair", arms="no"), "arm") == 0


def test_an_l_shaped_desk_draws_its_return() -> None:
    assert _count(_svg("desk", outline="l_shaped"), "return") == 1
    assert _count(_svg("desk", outline="rectangular"), "return") == 0


@pytest.mark.parametrize("shape", TYPES)
def test_a_white_piece_reads_white(shape: str) -> None:
    """At least 80% of the body's painted area keeps 80% of White's own lightness."""
    white = _lum(_rgb(BASE))
    fill = kit.Fill("solid", BASE, "#333333", "#f2d14b")
    lums = _structure_luminances(kit.render(shape, fill))
    assert lums, shape
    light = sum(1 for v in lums if v >= 0.8 * white) / len(lums)
    assert light >= 0.8, (shape, light)
