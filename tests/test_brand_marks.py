"""Every industrial drawing carries its brand's mark and name (#132).

The plate under the figure (:mod:`...core.drawing.sheet`) sets the brand's mark
(:mod:`...domains.industrial.drawing.brand_marks`) beside its wordmark, both
drawn by the shared core (:mod:`...core.drawing.brand_mark`). These tests hold
the four promises the plate makes: every brand's mark differs visibly from
every other's at the Studio grid tile; the name is legible there; nothing the
figure draws reaches the plate; and the only text a drawing carries is its own
brand's wordmark.
"""

from __future__ import annotations

import functools
import itertools
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import brands, bundle
from synthetic_ecommerce_data.core.drawing import (
    FIGURES,
    brand_mark,
    draw_sku,
    product_scale_for,
    sheet,
    svg,
    svg_problems,
)
from synthetic_ecommerce_data.domains.industrial.drawing import brand_marks

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"

#: THE STUDIO GRID TILE: the 200 x 300 sheet shown 180 px tall, 0.6 px a unit.
#: Stated here, not read from the code under test, so the code cannot move it.
TILE_PX_PER_UNIT = 180 / svg.HEIGHT
#: The legibility ruling (#132): no brand name renders under 10 px at the tile.
MIN_NAME_PX = 10.0
#: The distinguishability ruling (#55, #132): two marks differ in at least this
#: many pixels at the tile. The code's own floor may be stricter, never looser.
RULED_DIFFERING_PIXELS = 24
#: Float noise allowed at a box edge (a width summed from advances).
EPS = 1e-9


@functools.cache
def _golden_parents() -> list[dict]:
    return [json.loads(line) for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()]


@functools.cache
def _facets() -> dict[str, dict]:
    return bundle.flat_facets(GOLDEN)


def _wordmark(brand: str) -> str:
    """The words the plate sets for ``brand``, as the drawing's ``<text>`` joins them."""
    return " ".join(sheet.plate_lockup(brand).lines)


def _texts(data: bytes) -> list[str]:
    return [e.text or "" for e in ET.fromstring(data).iter() if e.tag.endswith("}text")]


# --- the mark ----------------------------------------------------------------


def test_every_brand_has_a_declared_mark_and_no_two_share_one():
    assert set(brands.MOTIFS) == set(brand_marks.MOTIFS)
    assert set(brands.ENCLOSURES) == set(brand_mark.ENCLOSURES)
    pairs = {(brands.motif_of(b), brands.enclosure_of(b)) for b in brands.BY_NAME}
    assert len(pairs) == len(brands.BY_NAME)
    assert all(m in brand_marks.MOTIFS and e in brand_mark.ENCLOSURES for m, e in pairs)


def test_the_tile_mark_size_is_the_plate_mark_at_the_tile():
    assert int(sheet.PLATE_MARK * TILE_PX_PER_UNIT) == brand_marks.TILE_MARK_PX


def test_any_two_brands_marks_differ_visibly():
    """Every pair of the brand book's marks, rasterised at the tile, differs in enough pixels."""
    assert brand_marks.MIN_DIFFERING_PIXELS >= RULED_DIFFERING_PIXELS
    marks = {b: brand_marks.mark_of(b) for b in brands.BY_NAME}
    closest = min(
        (brand_mark.differing_pixels(marks[a], marks[b], brand_marks.TILE_MARK_PX), a, b)
        for a, b in itertools.combinations(sorted(marks), 2)
    )
    assert closest[0] >= brand_marks.MIN_DIFFERING_PIXELS, closest


def test_differing_pixels_counts_the_pixels_only_one_mark_inks():
    """A disc against nothing differs in every pixel the disc inks; against itself in none."""
    disc = (brand_mark.Disc(0, 0, 1.0),)
    inked = int(brand_mark.mark_bitmap(disc, 19).sum())
    assert brand_mark.differing_pixels(disc, (), 19) == inked
    assert brand_mark.differing_pixels(disc, disc, 19) == 0


# --- the name ----------------------------------------------------------------


def test_every_brands_name_renders_at_least_10px_on_the_tile():
    small = {b: round(sheet.plate_lockup(b).size * TILE_PX_PER_UNIT, 2) for b in brands.BY_NAME}
    assert {b: px for b, px in small.items() if px < MIN_NAME_PX} == {}


def test_every_brands_lockup_stays_inside_the_plate():
    x0, y0, x1, y1 = sheet.PLATE_BOX
    for brand in brands.BY_NAME:
        placed = sheet.plate_lockup(brand)
        for box in (placed.mark, placed.name):
            assert x0 - EPS <= box[0] and y0 - EPS <= box[1], (brand, box)
            assert box[2] <= x1 + EPS and box[3] <= y1 + EPS, (brand, box)
        assert placed.name[0] >= placed.mark[2], brand


def test_a_name_too_long_for_one_line_is_set_on_two():
    placed = sheet.plate_lockup("Harrowgate Precision Works")
    assert placed.lines == ("Harrowgate", "Precision Works")
    assert placed.size * TILE_PX_PER_UNIT >= MIN_NAME_PX


def test_a_name_too_long_for_two_lines_is_set_as_its_first_word():
    """Two lines would set it under 10 px at the tile: the wordmark is its first word."""
    placed = sheet.plate_lockup("Saltmarsh Meadowland Works")
    assert placed.lines == ("Saltmarsh",)
    assert placed.size * TILE_PX_PER_UNIT >= MIN_NAME_PX


def test_a_name_whose_first_word_does_not_fit_is_refused():
    with pytest.raises(ValueError, match="fits"):
        sheet.plate_lockup("Brackenthorpefabricationsworks Limited")


# --- the figure keeps out of the plate ---------------------------------------


def test_no_golden_figure_reaches_the_plate():
    """Every committed SKU, at its product's one scale: part and lens end above the plate."""
    reaching = []
    for parent in _golden_parents():
        records = bundle.records(parent, _facets())
        scale = product_scale_for(parent["product_type"], records)
        figure_fn, _ = FIGURES[parent["product_type"]]
        for record in records:
            for box in sheet.figure_boxes(figure_fn(dict(record)).figure, scale):
                if box[3] > sheet.PLATE_BOX[1]:
                    reaching.append((parent["product_id"], box))
    assert reaching == []


# --- the only text is the brand's wordmark -----------------------------------


@functools.cache
def _one_drawing_per_type_and_brand() -> dict[tuple[str, str], bytes]:
    drawings: dict[tuple[str, str], bytes] = {}
    for parent in _golden_parents():
        key = (parent["product_type"], parent["brand"])
        if key not in drawings:
            record = bundle.records(parent, _facets())[0]
            drawings[key] = draw_sku(parent["product_type"], parent["brand"], record)[0]
    return drawings


def test_each_drawings_text_is_its_own_brands_wordmark():
    drawings = _one_drawing_per_type_and_brand()
    assert {brand for _, brand in drawings} == set(brands.BY_NAME)
    wrong = {
        key: _texts(data)
        for key, data in drawings.items()
        if " ".join(_texts(data)) != _wordmark(key[1]) or svg_problems(data)
    }
    assert wrong == {}


def _drawing_of(brand: str) -> bytes:
    return next(d for (_, b), d in _one_drawing_per_type_and_brand().items() if b == brand)


#: Each plant is made in a REAL drawing of the named brand, so the planted
#: change is the only difference from a clean one.
PLANTS = {
    "a name not in the brand book": ("Dravenholt", b">Dravenholt<", b">Hollisdane Tools<"),
    "a size in the wordmark": ("Dravenholt", b">Dravenholt<", b">M8 x 1.25<"),
    "half of a two-word name": ("Iron Heron", b">Iron Heron<", b">Iron<"),
    "a font attribute on a path": ("Dravenholt", b"<path ", b'<path font-size="12" '),
    "a text length on a circle": ("Dravenholt", b"<circle ", b'<circle textLength="9" '),
    "a character reference for the ampersand": ("Lark & Lathe", b"&amp;", b"&#38;"),
    "a child element in the text": ("Dravenholt", b">Dravenholt<", b"><g/>Dravenholt<"),
}


@pytest.mark.parametrize("name", sorted(PLANTS))
def test_the_gate_refuses_text_that_is_not_the_wordmark(name):
    brand, old, new = PLANTS[name]
    clean = _drawing_of(brand)
    assert svg_problems(clean) == [], "the control drawing must be clean"
    assert old in clean
    assert svg_problems(clean.replace(old, new, 1)), name
