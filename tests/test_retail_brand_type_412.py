"""Retail's brand marks sit on the shared core (#412, split from #132).

The retail prototype used to estimate a wordmark's width from a per-font average
advance and set every name at 15-21 units on a 400-unit sheet, which the Studio
tile (180 px tall, 0.45 px a unit) shows at 4-6 px. These tests hold what the move
onto ``core/drawing`` promises: one width model (the core's), every wordmark
pinned to it, every name's capitals at least 10 px at the tile (#133's rule), real
brands drawing no logo, and no two brands drawn alike.
"""

from __future__ import annotations

import re
import sys
from html import unescape
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import house_styles as hs  # noqa: E402

from synthetic_ecommerce_data.core.drawing import brand_mark, brand_type, sheet  # noqa: E402

TILE_PX = 180.0
PX_PER_UNIT = TILE_PX / hs.SIZE
_TEXT = re.compile(r"<text\b([^>]*)>([^<]*)</text>")
_ATTR = re.compile(r'([\w:-]+)="([^"]*)"')


def _texts(fragments: list[str]) -> list[tuple[dict[str, str], str]]:
    found = _TEXT.finditer("".join(fragments))
    return [(dict(_ATTR.findall(m.group(1))), m.group(2)) for m in found]


def _marked() -> dict[str, hs.HouseStyle]:
    return {b: s for b, s in hs.HOUSE_STYLES.items() if s.mark != hs.NO_MARK}


def _family_of(attrs: dict[str, str]) -> str:
    stack = attrs["font-family"]
    return next(k for k, f in brand_type.FAMILIES.items() if f.stack == stack)


def test_retail_keeps_no_second_text_width_table() -> None:
    """The core measures a wordmark; retail has no advance table or width estimate of its own."""
    assert not hasattr(hs, "ADVANCE")
    assert not hasattr(hs, "text_width")
    assert not hasattr(hs, "name_size")


def test_every_retail_wordmark_is_pinned_to_a_width() -> None:
    """A viewer with another face squeezes the glyphs instead of overflowing the box."""
    bare = [
        brand
        for brand, style in _marked().items()
        for attrs, _ in _texts(hs.logo(style, brand))
        if "textLength" not in attrs
    ]
    assert bare == []


def test_no_retail_wordmark_renders_under_10px_at_the_studio_tile() -> None:
    """The capitals of every line of every name stand at least 10 px tall at the tile."""
    small = []
    for brand, style in _marked().items():
        for attrs, _ in _texts(hs.logo(style, brand)):
            cap = brand_type.FAMILIES[_family_of(attrs)].cap_height
            cap_px = float(attrs["font-size"]) * cap * PX_PER_UNIT
            if cap_px < sheet.MIN_NAME_PX - 1e-9:
                small.append((brand, round(cap_px, 2)))
    assert small == []


@pytest.mark.parametrize("brand", ["Apple", "Nike"])
def test_a_real_brand_draws_no_logo(brand: str) -> None:
    style = hs.HOUSE_STYLES[brand]
    assert style.mark == hs.NO_MARK
    assert hs.logo(style, brand) == []


def test_any_two_retail_logos_differ_in_geometry() -> None:
    """Two brands' logos are not the same drawing in other colours or other words."""
    seen: dict[str, str] = {}
    twins = []
    for brand, style in _marked().items():
        svg = "".join(hs.logo(style, brand))
        svg = re.sub(r"#[0-9a-fA-F]{3,8}", "#", svg)
        svg = _TEXT.sub("<text/>", svg)
        if svg in seen:
            twins.append((seen[svg], brand))
        seen[svg] = brand
    assert twins == []


def test_the_smallest_glyph_of_every_wordmark_is_10px_at_the_tile() -> None:
    """A small-caps lowercase is drawn at 0.8 of a capital: that glyph is held to 10 px."""
    small = []
    for brand, style in _marked().items():
        for attrs, _ in _texts(hs.logo(style, brand)):
            px = float(attrs["font-size"]) * brand_type.cap_height(style) * PX_PER_UNIT
            if px < sheet.MIN_NAME_PX - 1e-9:
                small.append((brand, round(px, 2)))
    assert small == []


def test_every_wordmark_is_the_whole_brand_name() -> None:
    """Two lines join back to the name: nothing is cut to fit."""
    cut = []
    for brand, style in _marked().items():
        shown = unescape(" ".join(t for _, t in _texts(hs.logo(style, brand))))
        if shown != brand_type.cased(style, brand):
            cut.append(brand)
    assert cut == []


def test_the_product_clears_every_logo() -> None:
    """The product (y 28..362 of the sheet) stays inside what the logo's text leaves free."""
    crowded = []
    for brand, style in _marked().items():
        top, bottom = hs.reach(style, brand)
        pattern = r"translate\(([-\d.]+) ([-\d.]+)\) scale\(([\d.]+)\)"
        m = re.fullmatch(pattern, hs.product_transform(style, brand))
        assert m, brand
        ty, s = float(m.group(2)), float(m.group(3))
        y0, y1 = ty + 28 * s, ty + 362 * s
        if y0 < top - 1e-6 or y1 > hs.SIZE - bottom + 1e-6:
            crowded.append((brand, round(y0), round(y1), top, bottom))
    assert crowded == []


class _Style:
    weight = 700
    case = "title"
    spacing = 0.0
    italic = False

    def __init__(self, font: str = "sans", **kw: object) -> None:
        self.font = font
        self.__dict__.update(kw)


def test_a_sans_bold_name_is_measured_by_the_core() -> None:
    width = brand_type.width(_Style(), "Harbour", 20)
    assert width == pytest.approx(brand_mark.text_width("Harbour", 20))


def test_a_lighter_weight_is_narrower_and_a_fixed_pitch_face_is_its_pitch() -> None:
    bold, light = _Style(), _Style(weight=400)
    assert brand_type.width(light, "Harbour", 20) < brand_type.width(bold, "Harbour", 20)
    assert brand_type.width(_Style("mono"), "abcde", 10) == pytest.approx(5 * 0.6 * 10)


def test_letter_spacing_adds_to_every_character() -> None:
    plain, spaced = _Style(), _Style(spacing=2.0)
    extra = brand_type.width(spaced, "Nest", 10) - brand_type.width(plain, "Nest", 10)
    assert extra == pytest.approx(8)


def test_a_name_that_fits_one_line_stays_on_one_line() -> None:
    block = brand_type.set_lines(_Style(), "Nest", 300, 40.0, PX_PER_UNIT)
    assert block.lines == ("Nest",)
    assert block.size == 40.0


def test_a_long_name_breaks_at_its_space_rather_than_shrinking() -> None:
    style = _Style()
    block = brand_type.set_lines(style, "Harbour Pine Outfitters", 300, 40.0, PX_PER_UNIT)
    assert len(block.lines) == 2
    assert " ".join(block.lines) == "Harbour Pine Outfitters"
    assert block.size >= brand_type.min_size(style, PX_PER_UNIT)
    assert block.width <= 300 + 1e-9


def test_a_name_that_fits_no_layout_is_refused_not_shrunk() -> None:
    with pytest.raises(ValueError, match="fits 120 units"):
        brand_type.set_lines(_Style(), "Harbourpineoutfitters", 120, 40.0, PX_PER_UNIT)


def test_a_small_caps_name_is_held_to_its_smaller_glyph() -> None:
    caps, small = _Style(), _Style(case="smallcaps")
    assert brand_type.cap_height(small) == pytest.approx(0.8 * brand_type.cap_height(caps))
    assert brand_type.min_size(small, PX_PER_UNIT) > brand_type.min_size(caps, PX_PER_UNIT)


def test_a_line_is_written_with_its_width_pinned_and_escaped() -> None:
    svg = brand_type.text(_Style(), "Thistle & Wren", 10, 20, 18, "#123456")
    assert "&amp;" in svg
    assert 'lengthAdjust="spacingAndGlyphs"' in svg
    assert 'textLength="' in svg
