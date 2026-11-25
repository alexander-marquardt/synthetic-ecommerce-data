"""Every kit's shadow is drawn by the one shared step, level or turned (gen#1182, slice 2).

Slice 1 lifted the shadows labelled ``class="ground"`` out of a turned drawing and drew one flat
ellipse in their place (:mod:`ground_shadow`). The other kits drew their shadow unlabelled, a
translucent black ellipse from a ``_shadow`` helper or written inline, so it still turned with the
product; and a level picture kept whatever shadow its kit drew. These tests read every registered
shape: its kit labels each shadow it draws, and its picture, level or turned, in a house style or
on the plain sheet, shows only the step's shadow. A turned product of each newly labelled shape
then meets slice 1's checks (``test_flat_shadow_1182._check``).
"""

from __future__ import annotations

import functools
import re

import pytest

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail import kit, orientation, scale
from test_flat_shadow_1182 import _check

#: The shapes whose kit drew its shadow unlabelled and that the catalogue draws turned.
NEWLY_LABELLED = (
    "action_figure", "all_in_one", "baby_blanket", "bath_towel", "bed_pillow", "bikini_bottoms",
    "bikini_top", "board_game", "bowl", "boxers", "brick_box", "building_set", "casserole",
    "changing_robe", "chopping_board", "colander", "cover_up", "craft_kit", "craft_tub", "cushion",
    "doll", "doll_box", "dressing_gown", "drinking_glass", "frying_pan", "grill_press",
    "handheld_fan", "jigsaw", "kettle", "kids_swimsuit", "kitchen_knife", "kitchen_utensil",
    "knickers", "laundry_basket", "learning_toy", "mens_pants", "mop", "nappy_caddy", "plate",
    "puddlesuit", "role_play", "saucepan", "shapewear", "shoe", "sleepsuit", "slip", "snowsuit",
    "storage_box", "swim_bottoms", "swim_shorts", "swimsuit", "tankini", "vest", "wooden_toy",
)  # fmt: skip
#: Slice 1's shapes, which labelled their shadow already.
SLICE_1 = (
    "produce_pile", "punnet", "loaf", "chocolate_box", "hot_chocolate", "milk_carton", "milk_jug",
    "wine_bottle", "beer", "soft_drink",
)  # fmt: skip
#: A shadow as a kit draws one: an ellipse in a dark ink, laid on translucent.
_ELLIPSE = re.compile(r"<ellipse\b[^>]*>")
_DARK = ("#000000", "#000", "black", kit.INK)
_FILL = kit.Fill("solid", "#88aacc", "#335577")
#: The step's own shadow, painted with its gradient.
_STEP = re.compile(r'<ellipse class="ground" [^>]*fill="url\(#ground-[^"]+\)"/>')


def _unlabelled(svg: str) -> list[str]:
    """The ellipses in ``svg`` that are drawn as a shadow but carry no ``class="ground"``."""
    out = []
    for el in _ELLIPSE.findall(svg):
        fill = re.search(r'\bfill="([^"]+)"', el)
        alpha = re.search(r'\b(?:fill-)?opacity="([\d.]+)"', el)
        dark = fill is not None and fill.group(1).lower() in _DARK
        if dark and alpha and float(alpha.group(1)) < 0.5 and 'class="ground"' not in el:
            out.append(el)
    return out


def test_every_kit_labels_the_shadow_it_draws() -> None:
    found = {}
    for shape, draw in kit.shapes().items():
        drawn = "".join(kit._drawn(draw, _FILL.base, _FILL, None, None))
        if bad := _unlabelled(drawn):
            found[shape] = bad
    assert found == {}


def _brand() -> tuple[str, hs.HouseStyle]:
    """A brand whose house style has a logo, so its picture is placed clear of it."""
    return next((b, s) for b, s in hs.HOUSE_STYLES.items() if s.mark != hs.NO_MARK)


@pytest.mark.parametrize("angle", [0, 12, -90])
def test_no_kit_drawn_shadow_is_left_in_a_house_style_picture(angle: float) -> None:
    brand, style = _brand()
    found = {}
    for shape in kit.shapes():
        svg = kit.render(shape, _FILL, brand=brand, uid="u", style=style, angle=angle)
        grounds = svg.count('class="ground"')
        if _unlabelled(svg) or grounds > 1 or grounds != len(_STEP.findall(svg)):
            found[shape] = re.findall(r'<ellipse class="ground"[^>]*>', svg) + _unlabelled(svg)
    assert found == {}


def test_no_kit_drawn_shadow_is_left_on_the_plain_sheet() -> None:
    found = {}
    for shape in kit.shapes():
        svg = kit.render(shape, _FILL, brand="Plain", uid="u")
        grounds = svg.count('class="ground"')
        if _unlabelled(svg) or grounds > 1 or grounds != len(_STEP.findall(svg)):
            found[shape] = re.findall(r'<ellipse class="ground"[^>]*>', svg) + _unlabelled(svg)
    assert found == {}


def test_a_level_picture_stands_on_the_steps_shadow() -> None:
    """A level towel stack, whose kit drew its own shadow, stands on the one the step draws."""
    brand, style = _brand()
    svg = kit.render("bath_towel", _FILL, brand=brand, uid="u", style=style)
    assert len(_STEP.findall(svg)) == 1 and 'class="turn"' not in svg


@functools.cache
def _turned() -> dict[str, dict]:
    """The first product of each shape the catalogue draws turned."""
    out: dict[str, dict] = {}
    for rec in scale.templates():
        if orientation.drawn_angle(rec):
            out.setdefault(rec["drawing"]["shape"], rec)
    return out


def test_the_newly_labelled_shapes_are_every_turned_shape_with_a_shadow() -> None:
    """Every shape drawn turned whose kit draws a shadow is one of slice 1's or listed here."""
    shadowed = {
        shape
        for shape in _turned()
        if 'class="ground"'
        in "".join(kit._drawn(kit.shapes()[shape], _FILL.base, _FILL, None, None))
    }
    assert shadowed - set(SLICE_1) == set(NEWLY_LABELLED)


@pytest.mark.parametrize("shape", NEWLY_LABELLED)
def test_a_turned_product_of_each_newly_labelled_shape_stands_on_a_flat_shadow(shape: str) -> None:
    rec = _turned()[shape]
    _check(rec, rec["skus"][0])
