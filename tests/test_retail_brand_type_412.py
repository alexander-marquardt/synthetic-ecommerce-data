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
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import house_styles as hs  # noqa: E402

from synthetic_ecommerce_data.core.drawing import brand_type, sheet  # noqa: E402

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
