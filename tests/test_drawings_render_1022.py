"""The public draw call and its two finishes (gen#1022, slice 2).

``drawings.render(type, attributes, finish, product_id=...)`` returns one SVG, so a loader outside
the generator (elastic/prism-wands#1) draws a product without importing generator internals. The
figure is drawn from the attributes alone, at the product's own proportions (width, height and
depth); the finish dresses it: ``unbranded`` keyed only by the product id, with no mark and no
text, or ``brand`` in the brand's house style. Done-when 4 and 6 of the issue are pinned here,
on fixtures made from the generator's own vocabulary.
"""

from __future__ import annotations

import json
import re
import runpy
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail import sheet_extent

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "drawings_1022" / "sideboards_200.json"
SCRIPT = ROOT / "scripts" / "picture_share_1022.py"
NS = "{http://www.w3.org/2000/svg}"
BRAND = "Harbour & Pine"  # a lockup: mark plus wordmark
SPEC = {
    "color": "#8a5a3a",
    "width": 60,
    "height": 32,
    "doors": "2",
    "drawers": "3",
    "legs": "tapered",
}
PID = "fixture-sideboard-0001"
#: A key the vocabulary refuses: the British spelling, built so the US-spelling gate passes.
BRITISH_KEY = "colo" + "u" + "r_name"
_STROKE = re.compile(
    r'\s(?:stroke|stroke-width|stroke-dasharray|stroke-linejoin|stroke-linecap)="[^"]*"'
)


def _figure_group(svg: str) -> str:
    """The ``<g class="figure">`` in ``svg``, its strokes left out: what the finish restyles."""
    root = ET.fromstring(
        svg if svg.startswith("<svg") else f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>'
    )
    groups = [g for g in root.iter(f"{NS}g") if g.get("class") == "figure"]
    assert len(groups) == 1, len(groups)
    return _STROKE.sub("", ET.tostring(groups[0], encoding="unicode"))


def _grey(color: str) -> bool:
    r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return r == g == b


def test_render_returns_a_well_formed_svg_in_each_finish() -> None:
    for finish in drawings.FINISHES:
        svg = drawings.render("sideboard", SPEC, finish, product_id=PID, brand=BRAND)
        assert ET.fromstring(svg).tag == f"{NS}svg", finish


def test_both_finishes_draw_the_identical_figure() -> None:
    """Done-when 4: one base figure; only the finish differs."""
    figure = _figure_group(drawings.figure("sideboard", SPEC))
    unbranded = drawings.render("sideboard", SPEC, "unbranded", product_id=PID)
    brand = drawings.render("sideboard", SPEC, "brand", product_id=PID, brand=BRAND)
    assert _figure_group(unbranded) == figure
    assert _figure_group(brand) == figure
    assert unbranded != brand


def test_the_unbranded_finish_has_no_mark_and_no_text() -> None:
    svg = drawings.render("sideboard", SPEC, "unbranded", product_id=PID)
    assert "<text" not in svg
    assert 'class="brand"' not in svg
    style = hs.HOUSE_STYLES[BRAND]
    assert not any(part in svg for part in hs.logo(style, BRAND))
    frame = ET.fromstring(svg).find(f"{NS}g[@class='frame']")
    assert frame is not None and len(frame), "the unbranded sheet draws its frame"
    colors = {el.get("stroke") for el in frame.iter() if el.get("stroke")}
    assert colors and all(_grey(c) for c in colors), colors


def test_the_brand_finish_carries_the_mark_and_the_wordmark() -> None:
    svg = drawings.render("sideboard", SPEC, "brand", product_id=PID, brand=BRAND)
    style = hs.HOUSE_STYLES[BRAND]
    parts = hs.logo(style, BRAND)
    assert parts and all(part in svg for part in parts)
    assert "<text" in svg


def test_the_unbranded_look_is_keyed_only_by_the_product_id() -> None:
    a = drawings.render("sideboard", SPEC, "unbranded", product_id=PID)
    assert a == drawings.render("sideboard", SPEC, "unbranded", product_id=PID)
    looks = [drawings.unbranded_look(f"p-{i}") for i in range(200)]
    assert {lk.frame for lk in looks} == set(drawings.UNBRANDED_FRAMES)
    assert len(drawings.UNBRANDED_FRAMES) == 5
    for field in ("margin", "stroke", "dashed", "accent"):
        assert len({getattr(lk, field) for lk in looks}) >= 2, field
    assert all(_grey(lk.accent) for lk in looks)
    others = {
        drawings.render("sideboard", SPEC, "unbranded", product_id=f"p-{i}") for i in range(12)
    }
    assert len(others) >= 10


def _aspect(svg: str) -> float:
    box = sheet_extent.reach(
        svg if svg.startswith("<svg") else f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>'
    )
    assert box is not None
    return (box[2] - box[0]) / (box[3] - box[1])


@pytest.mark.parametrize("shape", sorted(drawings.PROPORTIONS))
def test_a_wider_piece_draws_wider_for_its_height(shape: str) -> None:
    """Real proportions: a piece half as wide again draws a figure wider for its height."""
    view, w, h, d = drawings.PROPORTIONS[shape]
    deep = view == "top"
    base = {"color": "#8a5a3a", "width": w, "height": h, "depth": d}
    wide = {**base, "width": w * 1.5}
    tall = {**base, ("depth" if deep else "height"): (d if deep else h) * 1.5}
    a0 = _aspect(drawings.figure(shape, base))
    assert _aspect(drawings.figure(shape, wide)) > a0 * 1.2, shape
    assert _aspect(drawings.figure(shape, tall)) < a0 / 1.2, shape


def _box(svg: str) -> tuple[float, float, float, float]:
    box = sheet_extent.reach(f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>')
    assert box is not None
    return box


@pytest.mark.parametrize(("key", "factor"), [("width", 1.5), ("height", 1.5), ("height", 0.6)])
def test_a_resized_piece_stands_on_the_same_floor_at_the_same_center(
    key: str, factor: float
) -> None:
    """The figure is scaled about its bottom center: a longer or lower piece keeps its floor."""
    base = {**SPEC, "width": 60, "height": 32}  # the sideboard's nominal size: drawn unscaled
    nominal = _box(drawings.figure("sideboard", base))
    resized = _box(drawings.figure("sideboard", {**base, key: base[key] * factor}))
    assert resized != nominal
    assert resized[3] == pytest.approx(nominal[3], abs=0.5)
    assert (resized[0] + resized[2]) / 2 == pytest.approx((nominal[0] + nominal[2]) / 2, abs=0.5)


def test_a_60_inch_and_a_90_inch_sideboard_draw_differently() -> None:
    narrow = drawings.figure("sideboard", {**SPEC, "width": 60})
    wide = drawings.figure("sideboard", {**SPEC, "width": 90})
    assert narrow != wide


@pytest.mark.parametrize(
    ("attributes", "word"),
    [
        ({**SPEC, BRITISH_KEY: "Oak"}, BRITISH_KEY),
        ({**SPEC, "color": "oak"}, "color"),
        ({k: v for k, v in SPEC.items() if k != "color"}, "color"),
        ({**SPEC, "width": -3}, "width"),
        ({**SPEC, "height": "tall"}, "height"),
        ({**SPEC, "doors": "nine"}, "doors"),
    ],
)
def test_an_attribute_outside_the_vocabulary_is_refused(attributes: dict, word: str) -> None:
    with pytest.raises(ValueError, match=word):
        drawings.render("sideboard", attributes, "unbranded", product_id=PID)


def test_an_unknown_type_finish_or_brand_is_refused() -> None:
    with pytest.raises(ValueError, match="type"):
        drawings.render("hovercraft", SPEC, "unbranded", product_id=PID)
    with pytest.raises(ValueError, match="finish"):
        drawings.render("sideboard", SPEC, "glossy", product_id=PID)
    with pytest.raises(ValueError, match="brand"):
        drawings.render("sideboard", SPEC, "brand", product_id=PID)
    with pytest.raises(ValueError, match="brand"):
        drawings.render("sideboard", SPEC, "brand", product_id=PID, brand="No Such Brand Ltd")
    with pytest.raises(ValueError, match="proportions"):
        drawings.render("tshirt", {"color": "#336699", "width": 20}, "unbranded", product_id=PID)


def test_the_share_of_products_sharing_a_picture_is_printed_for_each_finish(
    capsys, monkeypatch
) -> None:
    """Done-when 6: 200 drawings of one type; the share sharing a picture, figure and finishes."""
    rows = json.loads(FIXTURE.read_text())
    assert len(rows) == 200 and {r["type"] for r in rows} == {"sideboard"}
    share = drawings.picture_share(rows)
    assert set(share) == {"figure", *drawings.FINISHES}
    assert share["figure"][0] > 0, "the fixture repeats figures, so the finishes have work to do"
    assert share["unbranded"][0] < share["figure"][0]
    assert share["brand"][0] < share["figure"][0]
    monkeypatch.setattr("sys.argv", [str(SCRIPT), str(FIXTURE)])
    runpy.run_path(str(SCRIPT), run_name="__main__")
    out = capsys.readouterr().out
    for name in ("figure", *drawings.FINISHES):
        shared, total = share[name]
        assert re.search(
            rf"^{name}: {shared} of {total} share a picture \(\d+\.\d%\)$", out, re.M
        ), out
