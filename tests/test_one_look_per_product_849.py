"""#849, the maintainer's ruling on #860: what every SKU of a product shares, and what is its own.

| Same for every SKU of a product                    | Per SKU                                   |
|----------------------------------------------------|-------------------------------------------|
| outline color, frame, brand mark and name, angle   | fill = the SKU's own color; a named part's |
|                                                    | color (a cushion's blue trim) on that part |

Three checks, each over a whole committed or released set:

1. every SKU of a product shares its outline, frame, mark, name and angle: every product of
   the golden industrial catalog, and every product of the retail image release;
2. two SKUs of a product that differ in color differ in fill: every pair of colors of every
   product of the retail image release;
3. a SKU with a named-part color (``drawing.detail``, :mod:`named_parts`) draws that part in
   that color: every colorway of every such product of the retail ceiling build.
"""

from __future__ import annotations

import collections
import functools
import json
import re
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core.bundle import flat_facets, records
from synthetic_ecommerce_data.core.drawing import draw_product, product_angle, product_look
from synthetic_ecommerce_data.core.drawing.style import house_style
from synthetic_ecommerce_data.domains.retail import export, image_release
from synthetic_ecommerce_data.domains.retail import orientation as retail_orientation
from synthetic_ecommerce_data.domains.retail.house_styles import HOUSE_STYLES

GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog"
DEFS = re.compile(r"<defs>.*?</defs>", re.S)
#: The sheet's paper, the first element.
PAPER = re.compile(r'<rect width="\d+" height="\d+" fill="#[0-9a-f]{6}"/>')
#: One element's start tag.
ELEMENT = re.compile(r"<[a-z]+\b[^>]*>")
INDUSTRIAL_TURN = re.compile(r'<g transform="rotate\((-?[\d.]+) ')
#: The product's turn: the ``turn`` group's rotate (a pile's items carry rotates of their own).
RETAIL_TURN = re.compile(r'<g class="turn" transform="[^"]*rotate\((-?[\d.]+)\)')
#: A stroke's color and hand. Not its width, which a part's size sets (a magnifier's handle).
STROKE_ATTRS = re.compile(r'(stroke|stroke-linejoin|stroke-linecap|stroke-dasharray)="([^"]*)"')


@functools.cache
def _golden() -> list[dict]:
    lines = (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()
    return [json.loads(line) for line in lines if line]


def _outline(body: str, ink: str) -> frozenset:
    """The outline: the brand's ink and the hand (joins, caps, dash) of the figure's outline
    strokes, the ink strokes that turn a corner. A magnifier's handle or a thread's line is
    neither; a small SKU has a magnifier its larger sibling does not."""
    return frozenset(
        tuple(sorted(STROKE_ATTRS.findall(el)))
        for el in ELEMENT.findall(body)
        if f'stroke="{ink}"' in el and "stroke-linejoin=" in el
    )


def _industrial_look(svg: bytes, brand: str) -> tuple:
    """(frame, plate, outline, angle) of one industrial drawing."""
    house = house_style(brand)
    text = DEFS.sub("", svg.decode())
    body = text[PAPER.search(text).end() :]
    frame = ELEMENT.match(body).group(0) if house.frame != "none" else ""
    plate = text[text.rindex("<g fill=") :]
    return frame, plate, _outline(body, house.ink), frozenset(INDUSTRIAL_TURN.findall(text))


def test_every_sku_of_an_industrial_product_shares_its_outline_frame_plate_and_angle():
    """Every product of the golden catalog: its SKUs' frame, brand plate (mark and name),
    outline hand and turn are one; the frame is in the brand's ink, and every view's turn is
    the product's angle."""
    facets = flat_facets(GOLDEN)
    split = []
    for parent in _golden():
        drawn = draw_product(
            parent["product_type"], parent["brand"], records(parent, facets), parent["product_id"]
        )
        pid = parent["product_id"]
        looks = {_industrial_look(data, parent["brand"]) for data, _ in drawn}
        if len(looks) != 1:
            split.append(pid)
            continue
        ((frame, _, outline, turn),) = looks
        angle = product_angle(parent["product_type"], records(parent, facets), pid)
        assert turn == ({f"{angle}"} if angle else set()), pid
        assert outline, pid
        if frame:
            assert f'stroke="{house_style(parent["brand"]).ink}"' in frame, pid
    assert split == []


@functools.cache
def _release() -> dict[str, list[tuple[dict, dict, str]]]:
    """Every SKU of the retail image release, ``(record, sku, svg)``, by product id."""
    by: dict[str, list[tuple[dict, dict, str]]] = collections.defaultdict(list)
    drawn: dict[str, str] = {}
    for rec in image_release.records():
        for sku in rec["skus"]:
            key = export.drawing_id(rec, sku)
            if key not in drawn:
                drawn[key] = image_release.render(rec, sku).decode()
            by[rec["product_id"]].append((rec, sku, drawn[key]))
    return by


def _retail_parts(svg: str) -> tuple[str, str]:
    """(the sheet without its product: paper, frame, logo; the product group) of a drawing.
    A pack's item is defined inside the product group, so only the sheet drops its defs."""
    start, end = svg.index('<g class="product"'), svg.index('<g class="brand">')
    return DEFS.sub("", svg[:start] + svg[end:]), svg[start:end]


def test_every_sku_of_a_retail_product_shares_its_outline_frame_logo_and_angle():
    """Every product of the retail image release: its SKUs' sheet outside the product (the
    paper, frame and logo), the outline hand of its ink strokes and its turn are one, and the
    turn is the product's angle over its shape's orientation, level for a pack (#884)."""
    split = []
    for pid, skus in _release().items():
        rec = skus[0][0]
        ink = HOUSE_STYLES[rec["brand"]].ink
        looks = set()
        for _, _, svg in skus:
            sheet, product = _retail_parts(svg)
            looks.add((sheet, _outline(product, ink), tuple(RETAIL_TURN.findall(product))))
        if len(looks) != 1:
            split.append(pid)
            continue
        ((_, outline, turn),) = looks
        angle = product_look.angle_of(pid, retail_orientation.of_product(rec))
        assert turn == ((f"{angle}",) if angle else ()), pid
        assert outline, pid
    assert split == []
    assert len(_release()) == 352


def _fills(svg: str) -> tuple[str, frozenset]:
    """What paints the product: the sheet's defs (a pattern's colors) and the fills in its
    group."""
    defs = DEFS.search(svg[: svg.index('<g class="product"')])
    _, product = _retail_parts(svg)
    return (defs.group(0) if defs else ""), frozenset(re.findall(r'fill="([^"]+)"', product))


def test_two_skus_of_a_retail_product_in_two_colors_differ_in_fill():
    """Every pair of colors of every product of the retail image release: the two colors'
    drawings are painted differently, so a red mug's image is never its blue sibling's."""
    same = []
    pairs = 0
    for pid, skus in _release().items():
        by_color: dict[str, str] = {}
        for rec, sku, svg in skus:
            swatch = export.drawing_spec(rec, sku)["swatch"]
            if swatch is not None:
                by_color.setdefault(swatch["color"], svg)
        colors = sorted(by_color)
        for i, a in enumerate(colors):
            for b in colors[i + 1 :]:
                pairs += 1
                if _fills(by_color[a]) == _fills(by_color[b]):
                    same.append((pid, a, b))
    assert pairs > 1000
    assert same == []


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return ceiling_build().records


@pytest.mark.timeout(900)
def test_a_named_part_is_drawn_in_its_color_on_every_colorway(ceiling):
    """Every product of the retail ceiling build whose drawing names a part in a color
    ("Black Bra with Red Cups"): every colorway's image carries that part, marked
    ``data-part``, in that color, whatever the SKU's own fill."""
    missing = []
    named = 0
    for rec in ceiling:
        detail = rec["drawing"].get("detail")
        if not detail:
            continue
        named += 1
        seen: set[str] = set()
        for sku in rec["skus"]:
            key = export.drawing_id(rec, sku)
            if key in seen:
                continue
            seen.add(key)
            svg = image_release.render(rec, sku).decode()
            parts = [el for el in ELEMENT.findall(svg) if f'data-part="{detail["part"]}"' in el]
            if not any(f'"{detail["color"]}"' in el for el in parts):
                missing.append((rec["product_id"], rec["drawing"]["shape"], detail["part"]))
    assert named > 300
    assert missing == []
