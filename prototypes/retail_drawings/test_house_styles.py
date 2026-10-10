"""The prototype's own tests: house styles, logos and round 2's weak shapes.

Run: ``uv run pytest prototypes/retail_drawings/test_house_styles.py``.
"""

from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from itertools import combinations
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_preview  # noqa: E402
import house_styles as hs  # noqa: E402
import kit_garments as kg  # noqa: E402
from samples import records  # noqa: E402

RECS = records()
BRANDS = Counter(r["brand"] for r in RECS)


def test_every_brand_on_a_record_has_a_declared_style_row() -> None:
    missing = sorted(set(BRANDS) - set(hs.HOUSE_STYLES))
    assert missing == []


def test_a_brand_with_no_row_is_refused_at_render() -> None:
    rec = dict(RECS[0], brand="Nobody Ltd")
    with pytest.raises(KeyError):
        build_preview.drawing_svg(rec)


def test_no_two_brands_share_a_style_row() -> None:
    rows = Counter(hs.HOUSE_STYLES.values())
    assert [r for r, n in rows.items() if n > 1] == []


def test_no_two_brands_share_a_mark() -> None:
    marks = Counter(s.mark for s in hs.HOUSE_STYLES.values())
    assert {m: n for m, n in marks.items() if n > 1} == {}


def test_no_two_brands_share_a_lockup_arrangement_and_wordmark() -> None:
    keys = Counter(hs.lockup_key(s) for s in hs.HOUSE_STYLES.values())
    assert {k: n for k, n in keys.items() if n > 1} == {}


def test_any_two_brands_differ_in_at_least_five_levers() -> None:
    close = [
        (a, b, hs.differing(sa, sb))
        for (a, sa), (b, sb) in combinations(hs.HOUSE_STYLES.items(), 2)
        if hs.differing(sa, sb) < 5
    ]
    assert close == []


def test_about_half_the_brands_use_a_full_lockup() -> None:
    lockups = sum(s.layout != "mark_only" for s in hs.HOUSE_STYLES.values())
    assert lockups == 28
    assert len(hs.HOUSE_STYLES) == 59


def test_marks_are_large_enough_to_see_and_within_the_cap() -> None:
    for size in (hs.MARK_ONLY_SIZE, hs.LOCKUP_MARK_SIZE):
        assert 0.12 * hs.SIZE <= size <= 0.15 * hs.SIZE


def test_every_mark_in_the_table_exists_and_draws() -> None:
    for s in hs.HOUSE_STYLES.values():
        svg = hs.mark_svg(s.mark, 0, 0, 50, s.color)
        ET.fromstring(svg)
        assert s.color in svg


def test_at_least_twelve_brands_each_carry_three_or_more_products() -> None:
    assert len([b for b, n in BRANDS.items() if n >= 3]) == 13
    assert len(RECS) == 70


def test_every_drawing_is_well_formed_xml() -> None:
    for r in RECS:
        ET.fromstring(build_preview.drawing_svg(r))


def _product_fills(svg: str) -> list[str]:
    product = svg.split('<g class="product"', 1)[1].split('<g class="brand">', 1)[0]
    return re.findall(r'fill="([^"]*)"', product)


def test_the_brand_never_changes_the_products_own_fill_or_pattern() -> None:
    rec = next(r for r in RECS if r["product_id"] == "APP-PEEK-0045")
    a = build_preview.drawing_svg(dict(rec, brand="Stridewell"))
    b = build_preview.drawing_svg(dict(rec, brand="Wrenfield"))
    assert _product_fills(a) == _product_fills(b)
    assert a != b


def test_two_brands_restyle_the_same_outline_differently() -> None:
    frag = (
        '<path d="M0,0 L9,9" fill="#123456" stroke="#2b3440" stroke-width="3.0" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    knit = hs.restyle(frag, hs.HOUSE_STYLES["Hollinwray Knits"])
    sport = hs.restyle(frag, hs.HOUSE_STYLES["Stridewell"])
    assert 'stroke-dasharray="9 4"' in knit and "stroke-dasharray" not in sport
    assert 'stroke-width="4.05"' in sport and 'stroke-linejoin="miter"' in sport
    assert 'fill="#123456"' in knit and 'fill="#123456"' in sport


# --------------------------------------------------------------------------
# Round 2's weak shapes
# --------------------------------------------------------------------------


def _widths(fit: str) -> list[float]:
    """Leg width at the thigh, knee, calf and hem."""
    return [i - o for o, i in kg.FITS[fit]["legs"]]


def test_bootcut_has_no_knee_pinch() -> None:
    thigh, knee, calf, hem = _widths("bootcut")
    assert knee >= 0.9 * thigh
    assert hem > knee + 10


def test_skinny_and_slim_are_far_apart() -> None:
    assert _widths("slim")[-1] - _widths("skinny")[-1] >= 25
    assert _widths("slim")[1] - _widths("skinny")[1] >= 20


def test_carrot_leaves_the_waistband_without_a_sharp_step() -> None:
    for rise in kg.RISES:
        outer, _ = kg._leg_outline("carrot", rise)
        (x0, y0), (x1, y1) = outer[0], outer[1]
        assert math.degrees(math.atan2(x0 - x1, y1 - y0)) < 15


def test_square_neck_has_a_solid_binding_on_a_print() -> None:
    from kit import Fill

    parts = kg.top("url(#p)", Fill("polka", "#2a2a2e", "#ffffff"), None, neckline="square")
    assert any('fill="#ffffff"' in p and "L146,142" in p for p in parts)
