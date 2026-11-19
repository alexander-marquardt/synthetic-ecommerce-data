"""The décor types the generator could not draw (gen#1022, slice 6).

Wall art, decorative objects, garden statues, faux florals and fountains each get a kit shape of
their own, drawn from the attributes a record states, with slice 1's promises: each param value
draws a picture of its own, the drawn count of panels, pieces and basins is the stated count, a
value outside the shape's table is refused, a White piece reads white (gen#226), and each shape
names one orientation (#849). Each draws through ``drawings.render`` in both finishes, at the
width, height and depth a product states.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data.domains.retail import kit, kit_decor_pieces, orientation
from test_retail_furniture_drawings_226 import BASE, _lum, _rgb, _structure_luminances

TYPES = ("wall_art", "decor_object", "garden_statue", "faux_floral", "fountain")
ORIENTATIONS = {
    "wall_art": "level",  # hung level; a set of panels is drawn as several items (#884)
    "decor_object": "level",  # a set of pieces is drawn as several items (#884)
    "garden_statue": "upright",
    "faux_floral": "upright",
    "fountain": "upright",
}
WOOD = kit.Fill("solid", "#8a5a3a", "#333333", "#f2d14b")
BRAND = "Harbour & Pine"


def _svg(shape: str, **params: str) -> str:
    return kit.render(shape, WOOD, params=params or None)


def _count(svg: str, cls: str) -> int:
    return len(re.findall(rf'class="{cls}"', svg))


def test_the_five_types_are_registered_with_their_param_tables() -> None:
    kit.register_all()
    assert set(kit_decor_pieces.PARAMS) == set(TYPES)
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
    [(s, k) for s in TYPES for k in kit_decor_pieces.PARAMS.get(s, {})],
)
def test_every_value_of_a_param_draws_a_picture_of_its_own(shape: str, key: str) -> None:
    values = kit_decor_pieces.PARAMS[shape][key]
    assert len(values) >= 2, (shape, key)
    pictures = {_svg(shape, **{key: v}) for v in values}
    for svg in pictures:
        ET.fromstring(svg)  # every variant is a well-formed document, not only the default
    assert len(pictures) == len(values), (shape, key)


def test_every_form_draws_each_of_its_other_values_apart() -> None:
    """A param draws its own picture on every form, not only on the default one."""
    for shape, params in kit_decor_pieces.PARAMS.items():
        if "form" not in params:
            continue
        for form in params["form"]:
            for key, values in params.items():
                if key == "form":
                    continue
                pictures = {_svg(shape, form=form, **{key: v}) for v in values}
                assert len(pictures) == len(values), (shape, form, key)


@pytest.mark.parametrize("shape", TYPES)
def test_a_value_outside_the_table_is_refused(shape: str) -> None:
    for key in kit_decor_pieces.PARAMS[shape]:
        with pytest.raises(ValueError, match=key):
            _svg(shape, **{key: "seventeen"})


@pytest.mark.parametrize(
    ("shape", "key", "cls"),
    [
        ("wall_art", "panels", "panel"),
        ("decor_object", "pieces", "piece"),
        ("fountain", "basins", "basin"),
    ],
)
def test_the_drawn_count_is_the_stated_count(shape: str, key: str, cls: str) -> None:
    forms = kit_decor_pieces.PARAMS[shape].get("form", (None,))
    for form in forms:
        extra = {"form": form} if form else {}
        for value in kit_decor_pieces.PARAMS[shape][key]:
            svg = _svg(shape, **extra, **{key: value})
            assert _count(svg, cls) == int(value), (shape, form, key, value)


def test_framed_wall_art_draws_a_frame_round_each_panel_and_a_canvas_none() -> None:
    for panels in kit_decor_pieces.PARAMS["wall_art"]["panels"]:
        for frame in ("thin", "wide"):
            assert _count(_svg("wall_art", panels=panels, frame=frame), "frame") == int(panels)
        assert _count(_svg("wall_art", panels=panels, frame="canvas"), "frame") == 0
    assert _count(_svg("wall_art", panels="3", frame="wide"), "mat") == 3
    assert _count(_svg("wall_art", panels="3", frame="thin"), "mat") == 0


def test_a_statue_stands_on_a_plinth_only_when_it_says_so() -> None:
    for form in kit_decor_pieces.PARAMS["garden_statue"]["form"]:
        assert _count(_svg("garden_statue", form=form, base="plinth"), "plinth") == 1, form
        assert _count(_svg("garden_statue", form=form, base="none"), "plinth") == 0, form


def test_the_material_shows_as_its_own_texture() -> None:
    """Stone is speckled, metal and resin catch a sheen, wood shows its grain, glass is clear."""
    assert _count(_svg("garden_statue", material="stone"), "speckle") >= 6
    assert _count(_svg("garden_statue", material="metal"), "speckle") == 0
    assert _count(_svg("fountain", material="stone"), "speckle") >= 6
    assert _count(_svg("fountain", material="resin"), "speckle") == 0
    assert _count(_svg("decor_object", material="wood"), "grain") == 1
    assert _count(_svg("decor_object", material="ceramic"), "grain") == 0
    assert 'fill-opacity=".35"' in _svg("decor_object", material="glass")
    assert 'fill-opacity=".35"' not in _svg("decor_object", material="metal")


def test_a_wreath_hangs_with_a_bow_and_the_other_florals_stand_in_a_pot() -> None:
    assert _count(_svg("faux_floral", form="wreath"), "pot") == 0
    assert _count(_svg("faux_floral", form="wreath"), "bow") == 1
    for form in ("arrangement", "topiary", "tree"):
        assert _count(_svg("faux_floral", form=form), "pot") == 1, form
    assert _count(_svg("faux_floral", bloom="flower"), "flower") >= 3
    assert _count(_svg("faux_floral", bloom="berry"), "berry") >= 3
    leaves = _svg("faux_floral", bloom="leaf")
    assert _count(leaves, "flower") + _count(leaves, "berry") == 0


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
