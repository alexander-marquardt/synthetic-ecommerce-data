"""#849: every drawing sits on one neutral paper, and each product's figure has its own angle.

The issue's Done-when, one test group each:

1. no colored background: every industrial brand and every retail brand draws on
   :data:`product_look.PAPER`, with no texture behind the figure;
2. one angle per product: every SKU of a product is drawn at its product's angle, the
   angles spread over the set (not 0 degrees for most), two products of one type at two
   angles draw two pictures, and the turned figure stays inside its area.
"""

from __future__ import annotations

import functools
import json
import re
from collections import Counter
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.bundle import flat_facets, records
from synthetic_ecommerce_data.core.drawing import draw_product, draw_sku, product_look, sheet
from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail import sheet_extent
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


def test_the_paper_is_one_light_neutral():
    r, g, b = (int(product_look.PAPER[i : i + 2], 16) for i in (1, 3, 5))
    assert min(r, g, b) >= 0xF0
    assert max(r, g, b) - min(r, g, b) <= 4  # a neutral, not a tint


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


def test_an_angle_is_a_multiple_of_twelve_within_thirty_six():
    assert product_look.ANGLES == (-36, -24, -12, 0, 12, 24, 36)
    assert product_look.angle_of("ABC-1") == product_look.angle_of("ABC-1")


def test_the_angles_spread_over_the_set_and_most_products_are_turned():
    """Over the committed catalog's products, every angle is used and none takes more than
    a fifth: 0 degrees is one in seven, not most."""
    counts = Counter(product_look.angle_of(p["product_id"]) for p in _golden())
    total = sum(counts.values())
    assert set(counts) == set(product_look.ANGLES)
    assert max(counts.values()) / total < 0.2, counts
    assert counts[0] / total < 0.2


def test_every_sku_of_a_product_is_drawn_at_its_products_angle():
    checked = 0
    for parent in _golden():
        if len(parent["variants"]) < 3 or checked >= 12:
            continue
        angle = product_look.angle_of(parent["product_id"])
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
    ids = {}
    for n in range(100):
        ids.setdefault(product_look.angle_of(f"P-{n}"), f"P-{n}")
    a, b = ids[-24], ids[24]
    one, _ = draw_sku(parent["product_type"], parent["brand"], record, a)
    two, _ = draw_sku(parent["product_type"], parent["brand"], record, b)
    assert one != two


@pytest.mark.parametrize("angle", product_look.ANGLES)
def test_a_turned_industrial_figure_stays_inside_the_figure_area(angle, monkeypatch):
    """Every type's first product, drawn at each angle: the turned figure, measured through
    its rotation (strokes not counted), stays inside the area above the brand plate."""
    monkeypatch.setattr(product_look, "angle_of", lambda _id: angle)
    outside = []
    for parent in _one_per_type():
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
        angle = product_look.angle_of(rec["product_id"])
        if angle == 0:
            continue
        turned += 1
        text = drawing_svg(rec)
        with monkeypatch.context() as m:
            m.setattr(product_look, "angle_of", lambda _id: 0)
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
    assert turned > len(every) // 2  # 0 degrees is one product in seven
    assert bad == []
