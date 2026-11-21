"""The bath and kitchen types the generator could not draw (gen#1022, slice 4).

Floor and wall tile, bathroom vanities, cabinet and drawer pulls, bathroom sink faucets,
bathroom storage and kitchen canisters each get a kit shape of their own, drawn from the
attributes a record states, with slice 1's promises: each param value draws a picture of its
own, the drawn count of sinks, doors, drawers, handles, shelves and canisters is the stated count,
a value outside the shape's table is refused, a White piece reads white (gen#226), and each
shape names one orientation (#849). Each draws through ``drawings.render`` in both finishes, at
the width, height and depth a product states.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data.domains.retail import kit, kit_bath_kitchen, orientation
from test_retail_furniture_drawings_226 import BASE, _lum, _rgb, _structure_luminances

TYPES = ("tile", "vanity", "cabinet_pull", "sink_faucet", "bath_storage", "canister")
ORIENTATIONS = {
    "tile": "level",  # fixed to a wall, not held (#1101)
    "vanity": "level",  # stands on the floor, not held (#1101)
    "cabinet_pull": "upright",
    "sink_faucet": "level",  # fixed to the plumbing, not held (#1101)
    "bath_storage": "level",  # stands on the floor, not held (#1101)
    "canister": "level",  # a set drawn as several items (#884)
}
WOOD = kit.Fill("solid", "#8a5a3a", "#333333", "#f2d14b")
BRAND = "Harbour & Pine"


def _svg(shape: str, **params: str) -> str:
    return kit.render(shape, WOOD, params=params or None)


def _count(svg: str, cls: str) -> int:
    return len(re.findall(rf'class="{cls}"', svg))


def test_the_six_types_are_registered_with_their_param_tables() -> None:
    kit.register_all()
    assert set(kit_bath_kitchen.PARAMS) == set(TYPES)
    assert set(TYPES) <= set(kit.SHAPES)
    for shape in TYPES:
        assert orientation.of(shape) == ORIENTATIONS[shape], shape


@pytest.mark.parametrize("shape", TYPES)
def test_each_type_draws_a_well_formed_svg_with_a_body(shape: str) -> None:
    svg = _svg(shape)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert len(re.findall(r"<(?:rect|path|circle|ellipse)\b", svg)) >= 8, shape
    assert WOOD.base in svg, f"{shape} does not paint the record's color"


@pytest.mark.parametrize(
    ("shape", "key"),
    [(s, k) for s in TYPES for k in kit_bath_kitchen.PARAMS.get(s, {})],
)
def test_every_value_of_a_param_draws_a_picture_of_its_own(shape: str, key: str) -> None:
    values = kit_bath_kitchen.PARAMS[shape][key]
    assert len(values) >= 2, (shape, key)
    pictures = {_svg(shape, **{key: v}) for v in values}
    for svg in pictures:
        ET.fromstring(svg)  # every variant is a well-formed document, not only the default
    assert len(pictures) == len(values), (shape, key)


@pytest.mark.parametrize("shape", TYPES)
def test_a_value_outside_the_table_is_refused(shape: str) -> None:
    for key in kit_bath_kitchen.PARAMS[shape]:
        with pytest.raises(ValueError, match=key):
            _svg(shape, **{key: "seventeen"})


@pytest.mark.parametrize(
    ("shape", "key", "cls"),
    [
        ("vanity", "sinks", "basin"),
        ("vanity", "doors", "door"),
        ("vanity", "drawers", "drawer"),
        ("sink_faucet", "handles", "handle"),
        ("bath_storage", "shelves", "shelf"),
        ("canister", "count", "canister"),
    ],
)
def test_the_drawn_count_is_the_stated_count(shape: str, key: str, cls: str) -> None:
    for value in kit_bath_kitchen.PARAMS[shape][key]:
        assert _count(_svg(shape, **{key: value}), cls) == int(value), (shape, key, value)


def test_a_vanity_with_neither_doors_nor_drawers_shows_an_open_shelf() -> None:
    assert _count(_svg("vanity", doors="0", drawers="0"), "open_shelf") == 1
    assert _count(_svg("vanity"), "open_shelf") == 0


def test_a_tile_panel_draws_its_tiles_and_a_gloss_tile_its_highlights() -> None:
    for form in kit_bath_kitchen.PARAMS["tile"]["form"]:
        assert _count(_svg("tile", form=form), "tile") >= 9, form
    tiles = _count(_svg("tile"), "tile")
    assert _count(_svg("tile", surface="gloss"), "gloss") == tiles
    assert _count(_svg("tile", surface="matte"), "gloss") == 0


def test_a_pull_draws_its_backplate_only_when_it_has_one() -> None:
    for style in kit_bath_kitchen.PARAMS["cabinet_pull"]["style"]:
        assert _count(_svg("cabinet_pull", style=style, backplate="yes"), "backplate") == 1, style
        assert _count(_svg("cabinet_pull", style=style, backplate="no"), "backplate") == 0, style


def test_a_cabinet_has_a_mirror_only_when_it_says_so() -> None:
    assert _count(_svg("bath_storage", cabinet="mirror"), "mirror") == 1
    assert _count(_svg("bath_storage", cabinet="door"), "mirror") == 0
    assert _count(_svg("bath_storage", cabinet="door"), "door") == 1
    assert _count(_svg("bath_storage", cabinet="none"), "door") == 0


def test_a_glass_canister_shows_what_it_holds() -> None:
    assert _count(_svg("canister", body="glass"), "contents") == 3
    assert _count(_svg("canister", body="ceramic"), "contents") == 0


@pytest.mark.parametrize("shape", TYPES)
def test_a_white_piece_reads_white(shape: str) -> None:
    """At least 80% of the body's painted area keeps 80% of White's own lightness."""
    white = _lum(_rgb(BASE))
    fill = kit.Fill("solid", BASE, "#333333", "#f2d14b")
    lums = _structure_luminances(kit.render(shape, fill))
    assert lums, shape
    light = sum(1 for v in lums if v >= 0.8 * white) / len(lums)
    assert light >= 0.8, (shape, light)


@pytest.mark.parametrize("shape", TYPES)
def test_each_type_draws_through_render_in_both_finishes(shape: str) -> None:
    """The public call draws each type at the dimensions a product states, in either finish."""
    _, w, h, d = drawings.PROPORTIONS[shape]
    spec = {"color": "#8a5a3a", "width": w * 1.5, "height": h, "depth": d}
    for finish in drawings.FINISHES:
        svg = drawings.render(shape, spec, finish, product_id=f"fixture-{shape}-1", brand=BRAND)
        ET.fromstring(svg)
        assert "#8a5a3a" in svg, (shape, finish)
