"""#55: text-free style levers past ~48 house styles, and a distinguishability rule.

The issue's Done-when, one test group each:

* the house-style space supports at least the brand count #53's build needs
  (``test_the_space_supports_the_brands_the_deepened_catalog_needs``);
* the distinguishability rule is a test (the rule table, the book's pairs, the
  ink-to-paper contrast and the colour-vision-deficiency checks);
* the levers are drawn, text-free, and a brand that names none draws as before.
"""

from __future__ import annotations

import dataclasses
import functools
import itertools

import pytest

from synthetic_ecommerce_data.core import brands, emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.drawing import distinguish as dist
from synthetic_ecommerce_data.core.drawing import draw_sku, sheet, svg_problems
from synthetic_ecommerce_data.domains.industrial.generate import generate

MAX_DRAWING_BYTES = 8000  # tests/test_sku_drawings.py


@functools.cache
def _catalog():
    return generate(SMALL)


@functools.cache
def _sample() -> tuple[str, dict, bytes]:
    """A type, its record and its default drawing, for a brand of the book's first row.

    The first SKU whose drawing has interior lines (the ``stroke-opacity`` paths), so a
    dash lever has something to dash.
    """
    catalog = _catalog()
    for line, child in catalog.all_skus():
        record = emit.drawing_record(catalog, line, child)
        data, _ = draw_sku(line.type_key, brands.BRANDS[0], record)
        if b'stroke-opacity=".8"' in data:
            return line.type_key, record, data
    raise AssertionError("no drawing has interior lines")


def _draw(monkeypatch, brand: str, **levers) -> bytes:
    """``brand``'s drawing of the sample record with the book row's levers replaced."""
    type_key, record, _ = _sample()
    monkeypatch.setitem(
        brands.BY_NAME, brand, dataclasses.replace(brands.BY_NAME[brand], **levers)
    )
    return draw_sku(type_key, brand, record)[0]


# --- the capacity ---------------------------------------------------------------


def test_the_old_space_was_forty_eight_house_styles():
    """The premise: twelve inks and four frames, the (ink, frame) pairs."""
    assert len(brands.INKS) * len(brands.FRAMES) == 48


def test_the_space_supports_the_brands_the_deepened_catalog_needs():
    """Done-when, line one. The count is the greedy pack of ``dist.pack()``, built
    WITHOUT the mark (brands that would share one), so it does not lean on the 45
    marks, which are the other cap (``tests/test_brand_marks.py``)."""
    assert dist.BRANDS_NEEDED == 135
    assert dist.capacity() >= dist.BRANDS_NEEDED
    assert dist.capacity() > len(brands.INKS) * len(brands.FRAMES)


def test_the_pack_is_a_set_of_pairwise_visibly_different_styles():
    packed = dist.pack()
    assert len(packed) == dist.capacity()
    assert len(set(packed)) == len(packed)
    clashes = [
        (a, b)
        for a, b in itertools.combinations(packed, 2)
        if not dist.visibly_different(a, b)
    ]
    assert clashes == []


# --- the rule -------------------------------------------------------------------

_BASE = dist.Style(ink=0, paper=0, frame=0, mark="m", outline=0, dash=0, margin=0, texture=0)
#: (name, changes to _BASE, visibly different?)
RULE_TABLE = [
    ("identical", {}, False),
    ("one weak lever: paper", {"paper": 1}, False),
    ("one weak lever: outline", {"outline": 1}, False),
    ("two weak levers", {"outline": 1, "dash": 1}, False),
    ("three weak levers", {"outline": 1, "dash": 1, "texture": 1}, True),
    ("a safe ink alone", {"ink": 1}, True),
    ("a confusable ink alone", {"ink": 3}, False),
    ("a confusable ink and two weak levers", {"ink": 3, "paper": 1, "dash": 2}, True),
    ("the frame alone", {"frame": 1}, True),
    ("the chamfered frame alone", {"frame": 4}, True),
    ("the mark alone", {"mark": "n"}, True),
]


@pytest.mark.parametrize(
    ("changes", "expected"), [(c, e) for _, c, e in RULE_TABLE], ids=[n for n, _, _ in RULE_TABLE]
)
def test_the_distinguishability_rule(changes, expected):
    # Ink 0 (#1f6fb0) against ink 1 (#7a4a12) is safe; against ink 3 it is not (see below).
    other = _BASE._replace(**changes)
    assert dist.visibly_different(_BASE, other) is expected
    assert dist.visibly_different(other, _BASE) is expected


def test_ink_zero_and_ink_three_are_the_confusable_pair_the_table_uses():
    """The table's "confusable" row needs a real pair: blue #1f6fb0 and green #1e7a3c
    fall to 13.2 under tritanopia, under the 15 floor."""
    assert dist.ink_delta_e(brands.INKS[0], brands.INKS[3]) < dist.MIN_INK_DELTA_E
    assert dist.ink_delta_e(brands.INKS[0], brands.INKS[1]) >= dist.MIN_INK_DELTA_E


def test_every_pair_of_brands_in_the_book_is_visibly_different():
    """The way the (ink, paper, frame) uniqueness was tested: every pair of the book."""
    styles = {name: dist.style_of(name) for name in brands.BRANDS}
    clashes = [
        (a, b)
        for a, b in itertools.combinations(styles, 2)
        if not dist.visibly_different(styles[a], styles[b])
    ]
    assert clashes == []


def test_the_rule_is_not_vacuous_on_the_book():
    """Strip each brand's mark and 936 of the book's 990 pairs (94.5%, measured) still
    differ: the book is not distinct only because every brand owns a mark."""
    styles = [dist.style_of(name)._replace(mark=None) for name in brands.BRANDS]
    strong_or_weak = sum(
        1 for a, b in itertools.combinations(styles, 2) if dist.visibly_different(a, b)
    )
    pairs = len(styles) * (len(styles) - 1) // 2
    # (ink, frame) was unique per brand, so most pairs differ by frame or a safe ink.
    assert strong_or_weak > 0.9 * pairs


# --- colours --------------------------------------------------------------------


def _luminance(hex_color: str) -> float:
    def lin(c: int) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(int(hex_color[i : i + 2], 16)) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def test_every_ink_holds_three_to_one_on_every_paper():
    """The existing floor, held for every ink against EVERY paper tint, so a lever
    that re-pairs a brand's ink and paper cannot drop under it."""
    worst = min(
        (
            (_luminance(max(i, p, key=_luminance)) + 0.05)
            / (_luminance(min(i, p, key=_luminance)) + 0.05),
            i,
            p,
        )
        for i in brands.INKS
        for p in brands.PAPERS
    )
    assert worst[0] >= 3.0, worst


def test_inks_the_rule_calls_distinct_stay_apart_under_every_deficiency():
    """Normal vision, protanopia, deuteranopia and tritanopia: a pair counts as an
    ink difference only if it is at least MIN_INK_DELTA_E apart under all four."""
    safe = [
        (a, b)
        for a, b in itertools.combinations(brands.INKS, 2)
        if dist.inks_are_safe(a, b)
    ]
    assert safe, "no safe pair"
    for a, b in safe:
        for kind in dist.VISION:
            assert dist.ink_delta_e(a, b, vision=(kind,)) >= dist.MIN_INK_DELTA_E


def test_olive_and_orange_collapse_under_protanopia_and_are_not_a_safe_pair():
    """Measured (CIE76 on Machado 2009 severity 1.0): #4d6b00 and #a85a00 are 53 apart
    for a normal eye and 0.2 for a protanope."""
    olive, orange = brands.INKS[6], brands.INKS[9]
    assert dist.ink_delta_e(olive, orange, vision=("none",)) > 50
    assert dist.ink_delta_e(olive, orange, vision=("prot",)) < 1
    assert not dist.inks_are_safe(olive, orange)


def test_red_and_green_are_confusable_to_a_protanope_alone():
    """#c0392b and #1e7a3c are 95 apart for a normal eye and 21 for a deuteranope, so
    only protanopia (10.8) takes them under the floor: the pair a rule that left out
    one kind of vision would call safe."""
    red, green = brands.INKS[2], brands.INKS[3]
    assert dist.ink_delta_e(red, green, vision=("none", "deut", "trit")) >= dist.MIN_INK_DELTA_E
    assert dist.ink_delta_e(red, green, vision=("prot",)) < dist.MIN_INK_DELTA_E
    assert not dist.inks_are_safe(red, green)


# --- the levers are drawn -------------------------------------------------------


def test_the_levers_default_to_the_original_look():
    assert brands.WEIGHTS[0] == sheet.MIN_STROKE
    assert brands.DASHES[0] == ""
    assert brands.MARGINS[0] == 6.0
    assert brands.TEXTURES[0] == "plain"
    _, _, data = _sample()
    for marker in (b"stroke-dasharray", b"tgrid", b"tdot"):
        assert marker not in data


@pytest.mark.parametrize(
    ("lever", "value", "marker"),
    [
        pytest.param("outline", 1, b'stroke-width="3"', id="outline-medium"),
        pytest.param("outline", 2, b'stroke-width="3.7"', id="outline-heavy"),
        pytest.param("dash", 1, b'stroke-dasharray="3 2"', id="dash-dashed"),
        pytest.param("dash", 2, b'stroke-dasharray="6 2 1 2"', id="dash-chain"),
        pytest.param("texture", 1, b'fill="url(#tgrid', id="texture-grid"),
        pytest.param("texture", 2, b'fill="url(#tdot', id="texture-dot"),
    ],
)
def test_each_lever_changes_the_drawing_and_stays_text_free(lever, value, marker, monkeypatch):
    brand = brands.BRANDS[0]
    _, _, default = _sample()
    drawn = _draw(monkeypatch, brand, **{lever: value})
    assert drawn != default
    assert drawn.count(marker) > default.count(marker)
    assert svg_problems(drawn) == []
    assert len(drawn) < MAX_DRAWING_BYTES


def test_a_dash_leaves_the_outline_solid(monkeypatch):
    """Only the interior lines (flutes, threads, centre lines) dash: an outline is
    the part's edge, and a dashed edge would read as a hidden one."""
    drawn = _draw(monkeypatch, brands.BRANDS[0], dash=1).decode()
    for element in drawn.split("<")[1:]:
        if "stroke-dasharray" in element:
            assert 'stroke-opacity=".8"' in element


@pytest.mark.parametrize("frame", range(len(brands.ALL_FRAMES)))
def test_a_margin_moves_every_frame_but_none(frame, monkeypatch):
    brand = brands.BRANDS[0]
    far = _draw(monkeypatch, brand, frame=frame, margin=0)
    near = _draw(monkeypatch, brand, frame=frame, margin=1)
    assert svg_problems(far) == svg_problems(near) == []
    assert (far == near) is (brands.ALL_FRAMES[frame] == "none")


def test_the_chamfer_frame_is_a_closed_polygon_that_keeps_clear_of_the_plate():
    """The plate's bottom corners sit inside the cut corners by at least 1.5 units, at
    every margin."""
    x0, _, x1, y1 = sheet.PLATE_BOX
    for margin in brands.MARGINS:
        pts = sheet.chamfer_points(margin)
        assert len(pts) == 8
        assert pts[0] != pts[-1]
        # The bottom-left cut runs from pts[5] to pts[6]; the bottom-right from pts[3] to pts[4].
        centre = (sheet.svg.WIDTH / 2, sheet.svg.HEIGHT / 2)
        for corner, (a, b) in (((x0, y1), (pts[5], pts[6])), ((x1, y1), (pts[3], pts[4]))):

            def side(p, a=a, b=b):
                length = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
                return ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / length

            inside = side(corner) * (1 if side(centre) > 0 else -1)
            assert inside >= 1.5, (margin, corner, inside)


def test_a_nearer_margin_leaves_the_lens_and_the_plate_more_room():
    """Margins only move the frame OUT: the handle-less lens (8 in, its ring 1 clear of
    a frame at 6) and the plate (14 in) keep their clearance at every margin."""
    assert max(brands.MARGINS) == 6.0
    assert max(brands.MARGINS) + 1.0 + 1.0 <= sheet.LENS_MARGIN
    assert sheet.PLATE_BOX[0] >= max(brands.MARGINS) + 2.0


def test_the_heaviest_outline_still_clears_the_plate():
    assert (
        sheet.FIGURE_HEIGHT - sheet.MARGIN + max(brands.WEIGHTS) / 2 <= sheet.PLATE_BOX[1]
    )


def test_weights_are_above_the_floor_and_a_visible_step_apart_at_the_tile():
    steps = [b - a for a, b in itertools.pairwise(brands.WEIGHTS)]
    assert brands.WEIGHTS[0] == 2.3
    assert all(step * sheet.TILE_PX_PER_UNIT >= 0.4 for step in steps), steps


# --- the allow-list -------------------------------------------------------------


@pytest.mark.parametrize(
    "planted",
    [
        '<path d="M0 0L1 1" stroke-dasharray="A 2"/>',
        '<path d="M0 0L1 1" stroke-dasharray="3 2 7"/>',
        '<path d="M0 0L1 1" fill="url(#tgridzzzzzz)"/>',
        '<path d="M0 0L1 1" fill="url(#tspiral1f6fb0)"/>',
    ],
)
def test_the_allow_list_refuses_a_dash_or_texture_it_does_not_declare(planted):
    _, _, clean = _sample()
    assert svg_problems(clean) == []
    assert svg_problems(clean.replace(b"</svg>", planted.encode() + b"</svg>"))
