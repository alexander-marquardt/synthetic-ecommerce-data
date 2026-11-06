"""#849: every drawing sits on one neutral paper, and each product's figure has its own angle.

The issue's Done-when, one test group each:

1. no colored background: every industrial brand and every retail brand draws on
   :data:`product_look.PAPER`, white (the maintainer's ruling on #860), with no texture
   behind the figure;
2. one angle per product: every SKU of a product is drawn at its product's angle, the
   angles spread over each orientation's set (not 0 degrees for most), two products of one
   type at two angles draw two pictures, and the turned figure stays inside its area;
3. every type names its orientation (#860): the 24 clock positions (``any``), +-36 degrees
   (``upright``), +-15 degrees (``slight``) or none (``level``, #884), every industrial type
   and every retail shape.
"""

from __future__ import annotations

import functools
import json
import re
from collections import Counter
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import brands, domain
from synthetic_ecommerce_data.core.bundle import flat_facets, records
from synthetic_ecommerce_data.core.drawing import draw_product, draw_sku, product_look, sheet
from synthetic_ecommerce_data.domains.industrial import orientation as industrial_orientation
from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail import kit, sheet_extent
from synthetic_ecommerce_data.domains.retail import orientation as retail_orientation
from synthetic_ecommerce_data.domains.retail.build_preview import drawing_svg
from synthetic_ecommerce_data.domains.retail.samples import records as retail_records

GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog"
SVG_OPEN = '<svg xmlns="http://www.w3.org/2000/svg">'
#: The first painted element of a sheet: the paper.
PAPER_RECT = re.compile(
    r'<svg[^>]*>(?:<defs>.*?</defs>)?<rect width="\d+" height="\d+" fill="(#[0-9a-f]{6})"/>'
)
#: A figure's turn: the group around its shapes (a hatch's own rotate is in the defs).
TURN = re.compile(r'<g transform="rotate\((-?[\d.]+) ')


@functools.cache
def _golden() -> list[dict]:
    lines = (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()
    return [json.loads(line) for line in lines if line]


@functools.cache
def _facets():
    return flat_facets(GOLDEN)


def _one_per_type() -> list[dict]:
    """The first product of each industrial type in the committed catalog."""
    seen: dict[str, dict] = {}
    for parent in _golden():
        seen.setdefault(parent["product_type"], parent)
    return list(seen.values())


def _figure_groups(svg: bytes) -> str:
    """The turned figure(s) of an industrial drawing, with its defs, as an SVG to measure."""
    text = svg.decode()
    defs = re.search(r"<defs>.*?</defs>", text)
    groups = re.findall(r'<g transform="rotate\([^"]*\)">.*?</g>', text)
    return SVG_OPEN + (defs.group(0) if defs else "") + "".join(groups) + "</svg>"


# --- 1. one paper, no texture ----------------------------------------------------------


def test_the_paper_is_white():
    assert product_look.PAPER == "#ffffff"


@pytest.mark.parametrize("brand", brands.BRANDS)
def test_every_industrial_brand_draws_on_the_one_paper_with_no_texture(brand):
    parent = _one_per_type()[0]
    data, _ = draw_sku(
        parent["product_type"], brand, records(parent, _facets())[0], parent["product_id"]
    )
    text = data.decode()
    assert PAPER_RECT.match(text).group(1) == product_look.PAPER
    assert "url(#t" not in text and 'id="t' not in text


def test_every_retail_brand_draws_on_the_one_paper_with_no_texture():
    rec = retail_records()[0]
    for brand in hs.HOUSE_STYLES:
        text = drawing_svg(dict(rec, brand=brand))
        assert PAPER_RECT.match(text).group(1) == product_look.PAPER, brand
        assert "tex-" not in text, brand
        assert text.count(product_look.PAPER) >= 1, brand


# --- 2. one angle per product ----------------------------------------------------------


def _angle(product_id: str, product_type: str) -> int:
    return product_look.angle_of(product_id, domain.orientation(product_type))


def test_the_four_orientations_are_the_clock_two_narrow_fans_and_level():
    assert product_look.ORIENTATIONS == {
        "any": (0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165,
                180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345),
        "upright": (-36, -24, -12, 0, 12, 24, 36),
        "slight": (-15, -10, -5, 0, 5, 10, 15),
        "level": (0,),
    }  # fmt: skip
    assert product_look.angle_of("ABC-1", "any") == product_look.angle_of("ABC-1", "any")


@pytest.mark.parametrize("name", ["any", "upright"])
def test_the_angles_spread_over_each_set_and_most_products_are_turned(name):
    """Over the committed catalog's products of each orientation, every angle of its set is
    used and none takes more than twice its share: 0 degrees is one in 24 or one in seven,
    not most."""
    angles = product_look.ORIENTATIONS[name]
    counts = Counter(
        product_look.angle_of(p["product_id"], name)
        for p in _golden()
        if domain.orientation(p["product_type"]) == name
    )
    total = sum(counts.values())
    assert total > 50 * len(angles)
    assert set(counts) == set(angles)
    assert max(counts.values()) / total < 2 / len(angles), counts


def test_every_sku_of_a_product_is_drawn_at_its_products_angle():
    checked = 0
    for parent in _golden():
        if len(parent["variants"]) < 3 or checked >= 12:
            continue
        angle = _angle(parent["product_id"], parent["product_type"])
        drawn = draw_product(
            parent["product_type"],
            parent["brand"],
            records(parent, _facets()),
            parent["product_id"],
        )
        for data, _ in drawn:
            turns = {float(a) for a in TURN.findall(data.decode())}
            assert turns == ({float(angle)} if angle else set()), parent["product_id"]
        checked += 1
    assert checked == 12


def test_two_products_of_one_type_at_two_angles_draw_two_pictures():
    parent = _one_per_type()[0]
    record = records(parent, _facets())[0]
    name = domain.orientation(parent["product_type"])
    ids = {}
    for n in range(200):
        ids.setdefault(product_look.angle_of(f"P-{n}", name), f"P-{n}")
    a, b = sorted(ids.values())[:2]
    one, _ = draw_sku(parent["product_type"], parent["brand"], record, a)
    two, _ = draw_sku(parent["product_type"], parent["brand"], record, b)
    assert one != two


#: Every angle some orientation turns a figure by.
EVERY_ANGLE = sorted({a for angles in product_look.ORIENTATIONS.values() for a in angles})


@pytest.mark.parametrize("angle", EVERY_ANGLE)
def test_a_turned_industrial_figure_stays_inside_the_figure_area(angle, monkeypatch):
    """Every type's first product, drawn at each angle of its orientation: the turned figure,
    measured through its rotation (strokes not counted), stays inside the area above the
    brand plate."""
    monkeypatch.setattr(product_look, "angle_of", lambda *_: angle)
    outside = []
    for parent in _one_per_type():
        if angle not in product_look.ORIENTATIONS[domain.orientation(parent["product_type"])]:
            continue
        for data, _ in draw_product(
            parent["product_type"], parent["brand"], records(parent, _facets()), "any"
        ):
            box = sheet_extent.reach(_figure_groups(data))
            if box is None:  # 0 degrees draws no group
                continue
            x0, y0, x1, y1 = box
            slack = 0.5
            if x0 < -slack or y0 < -slack or x1 > 200 + slack or y1 > sheet.FIGURE_HEIGHT + slack:
                outside.append((parent["product_id"], box))
    assert outside == []


def _product(text: str) -> tuple[str, str]:
    """(defs, the product group) of a styled retail drawing."""
    defs = re.search(r"<defs>.*?</defs>", text)
    group = text[text.index('<g class="product"') : text.index('<g class="brand">')]
    return (defs.group(0) if defs else ""), group


def _reach(text: str) -> tuple[float, float, float, float]:
    defs, group = _product(text)
    return sheet_extent.reach(SVG_OPEN + defs + group + "</svg>")


def test_a_turned_retail_product_stays_inside_the_room_its_logo_leaves(monkeypatch):
    """Every authored style, at its own angle: the product's reach is inside the turn area
    (mapped onto the sheet by the brand's product transform), or inside its own upright
    reach where that is larger, so it never runs into the logo or off the sheet."""
    bad = []
    turned = 0
    every = retail_records()
    for rec in every:
        shape = rec["drawing"]["shape"]
        angle = product_look.angle_of(rec["product_id"], retail_orientation.of(shape))
        if angle == 0:
            continue
        turned += 1
        text = drawing_svg(rec)
        with monkeypatch.context() as m:
            m.setattr(product_look, "angle_of", lambda *_: 0)
            upright = _reach(drawing_svg(rec))
        box = _reach(text)
        _, group = _product(text)
        tx, ty, s = (
            float(v)
            for v in re.match(
                r'<g class="product" transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([\d.]+)\)',
                group,
            ).groups()
        )
        area = (
            min(upright[0], tx + hs.TURN_AREA[0] * s),
            min(upright[1], ty + hs.TURN_AREA[1] * s),
            max(upright[2], tx + hs.TURN_AREA[2] * s),
            max(upright[3], ty + hs.TURN_AREA[3] * s),
        )
        slack = 0.5
        if (box[0] < area[0] - slack or box[1] < area[1] - slack
                or box[2] > area[2] + slack or box[3] > area[3] + slack):  # fmt: skip
            bad.append((rec["product_id"], angle, box, area))
    assert turned > len(every) // 2  # 0 degrees is one product in seven at most
    assert bad == []


# --- 3. every type names its orientation (#860) ------------------------------------------


def _drawn_industrial_types() -> set[str]:
    return {t for d in domain.domains() for t in d.figures()}


def _retail_shapes() -> set[str]:
    kit.register_all()
    return set(kit.SHAPES)


@pytest.mark.parametrize(
    ("table", "every"),
    [
        (industrial_orientation, _drawn_industrial_types),
        (retail_orientation, _retail_shapes),
    ],
    ids=["industrial type", "retail shape"],
)
def test_every_type_names_one_orientation(table, every):
    """A drawn type missing from its domain's table, or named twice, fails here, so a new
    type cannot forget its orientation."""
    named = [*table.ANY, *table.UPRIGHT, *table.SLIGHT, *table.LEVEL]
    assert len(named) == len(set(named)), Counter(named).most_common(3)
    assert sorted(every() - set(named)) == []
    assert sorted(set(named) - every()) == []
    assert set(table.ORIENTATION.values()) <= set(product_look.ORIENTATIONS)


def test_gloves_turn_any_way_and_clothing_only_slightly():
    """The maintainer's rulings on #860: gloves read at any angle; a garment or a shoe turned
    past 15 degrees reads as falling over; a screw has no up; a sink or a bottle does; a
    cutlery set is not turned at all (#884)."""
    assert domain.orientation("cut_resistant_gloves") == "any"
    assert retail_orientation.of("gloves") == "any"
    for shape in ("tshirt", "top", "blouse", "trousers", "jeans_straight", "dress", "skirt",
                  "coat", "bra", "knickers", "pyjamas", "swimsuit", "socks", "tights", "shoe",
                  "trainer"):  # fmt: skip
        assert retail_orientation.of(shape) == "slight", shape
    assert domain.orientation("screw_socket_head") == "any"
    assert domain.orientation("bench_vises") == "upright"
    assert retail_orientation.of("bottle") == "upright"
    assert retail_orientation.of("cutlery_set") == "level"
