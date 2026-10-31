"""A White bicycle's frame shows on every bicycle brand's sheet (gen#746).

``kit_sports.bicycle`` strokes the frame tubes in the colorway's base color, and White's base sits
on the brands' pale sheets at about 1:1, so at 120 px a White bike read as two wheels, a saddle and
a bar. A frame that pale now carries an ink outline under its paint. The outline is the house
style's ink, so it is held on each brand's sheet, in that brand's ink and stroke weight. A colored
frame stays bare: the outline would darken its color at a thumbnail.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import bicycle_model_numbers as bmn
from synthetic_ecommerce_data.domains.retail import image_release, kit, kit_sports, scale
from synthetic_ecommerce_data.domains.retail.build_preview import drawing_svg
from synthetic_ecommerce_data.domains.retail.house_styles import HOUSE_STYLES

STYLES = ("road", "mountain", "electric", "kids")
#: What a frame's outline shows each side of its paint, in the drawing's units, at the least.
MIN_EDGE = 1.0
#: The least contrast of the outline against a brand's sheet: the battery's bar, gen#718.
MIN_CONTRAST = 3.0


def _bikes() -> list[dict]:
    return [rec for rec in scale.templates() if rec["product_type"] == "Bicycle"]


BIKES = _bikes()
WHITE = next(c["hex"] for rec in BIKES for c in rec["color_options"] if c["color"] == "White")
COLORS = sorted({c["hex"] for rec in BIKES for c in rec["color_options"]} - {WHITE})


def _elements(svg: str) -> list[ET.Element]:
    return list(ET.fromstring(svg).iter())


def _drawn(style: str, color: str) -> list[ET.Element]:
    parts = kit_sports.bicycle(color, kit.Fill(base=color), None, style=style)
    return _elements(f'<svg xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>')


def _on_sheet(brand: str) -> list[ET.Element]:
    """The brand's first bike painted White, on the brand's sheet: its first SKU, the smallest
    size, is the image on its card. Two brands sell no White bike, so the paint is set here."""
    rec = next(r for r in BIKES if r["brand"] == brand)
    drawing = image_release.colorway_drawing(rec, rec["skus"][0]) | {"base": WHITE}
    return _elements(drawing_svg(rec | {"drawing": drawing}))


def _outlines(found: list[ET.Element]) -> list[ET.Element]:
    return [el for el in found if el.get("class") == "tube-outline"]


def _paint(found: list[ET.Element], color: str) -> list[ET.Element]:
    return [el for el in found if el.get("stroke") == color]


def _luminance(color: str) -> float:
    def channel(i: int) -> float:
        c = int(color[i : i + 2], 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(1) + 0.7152 * channel(3) + 0.0722 * channel(5)


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_the_brands_cover_the_ten_that_sell_bicycles():
    assert {rec["brand"] for rec in BIKES} == set(bmn.SERIES)
    assert len(bmn.SERIES) == 10


@pytest.mark.parametrize("style", STYLES)
def test_every_white_tube_has_an_outline_under_all_the_paint(style):
    found = _drawn(style, WHITE)
    paint, outlines = _paint(found, WHITE), _outlines(found)
    assert len(paint) == (3 if style == "mountain" else 4), "a mountain bike's fork is steel"
    assert {el.get("d") for el in paint} <= {el.get("d") for el in outlines}
    last_outline = max(found.index(el) for el in outlines)
    assert last_outline < min(found.index(el) for el in paint), "an outline runs over the paint"


@pytest.mark.parametrize("brand", list(bmn.SERIES))
def test_a_white_frame_shows_on_the_brands_sheet(brand):
    found = _on_sheet(brand)
    style = HOUSE_STYLES[brand]
    paint = {el.get("d"): float(el.get("stroke-width", "0")) for el in _paint(found, WHITE)}
    outlines = _outlines(found)
    assert outlines, f"{brand}: the frame has no outline"
    for el in outlines:
        assert _contrast(el.get("stroke", "#ffffff"), style.paper) >= MIN_CONTRAST
        d = el.get("d")
        if d in paint:  # the mountain fork is steel, not the frame's paint
            edge = (float(el.get("stroke-width", "0")) - paint[d]) / 2
            assert edge >= MIN_EDGE, f"{brand}: {edge:.2f} of outline shows beside the paint"


def test_the_sold_white_is_the_one_outlined():
    rec = next(r for r in BIKES if any(s["color"] == "White" for s in r["skus"]))
    sku = next(s for s in rec["skus"] if s["color"] == "White")
    assert _outlines(_elements(image_release.render(rec, sku).decode()))


@pytest.mark.parametrize("color", COLORS)
def test_a_colored_frame_stays_bare(color):
    for style in STYLES:
        assert _outlines(_drawn(style, color)) == [], f"{style} {color}"
