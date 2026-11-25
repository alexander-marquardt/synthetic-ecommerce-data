"""A turned product's shadow lies flat on the ground (gen#1182).

The maintainer saw a tilted pile of oranges whose shadow was turned with it, so the pile looked as
if it sat on a slope. Each test renders a product as it is served (``image_release.render``), finds
its ``class="ground"`` element, and reads where every transform above it puts the ellipse: the major
axis is horizontal, and the ellipse sits under the lowest point of the turned drawing. The lowest
point is measured here on its own, from the drawing without its shadow, not by the code under test.
"""

from __future__ import annotations

import functools
import math
import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import (
    ground_shadow,
    image_release,
    kit,
    orientation,
    scale,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail import house_styles as hs

#: A picture of each shape that stands on a labelled shadow and is drawn turned: shape -> its kit.
SHAPES = {
    "produce_pile": "produce",
    "punnet": "punnet",
    "loaf": "bread",
    "chocolate_box": "chocolate",
    "hot_chocolate": "chocolate",
    "milk_carton": "dairy",
    "milk_jug": "dairy",
    "wine_bottle": "drinks",
    "beer": "drinks",
    "soft_drink": "soft drinks",
}
#: Sheet units between the shadow's center line and the drawing's lowest point.
SLACK = 1.0


@functools.cache
def _turned() -> dict[str, tuple[dict, ...]]:
    """Each shape's products that are drawn turned, at most two, at two angles where it has them."""
    out: dict[str, dict[int, dict]] = {}
    for rec in scale.templates():
        shape = rec["drawing"]["shape"]
        angle = orientation.drawn_angle(rec)
        if shape in SHAPES and angle and len(out.setdefault(shape, {})) < 2:
            out[shape].setdefault(angle, rec)
    return {shape: tuple(found.values()) for shape, found in out.items()}


@functools.cache
def _oranges() -> dict:
    """The Blood Oranges of the maintainer's report, drawn at 12 degrees."""
    (rec,) = [r for r in scale.templates() if r["product_id"] == "PLT-ORBLOD"]
    assert orientation.drawn_angle(rec) == 12
    return rec


def _parts(svg: str) -> tuple[ET.Element, list[tuple[ET.Element, list[str]]]]:
    """The drawn SVG's root, and its ground ellipses with the transforms above each."""
    root = ET.fromstring(svg)
    found: list[tuple[ET.Element, list[str]]] = []

    def walk(el: ET.Element, above: list[str]) -> None:
        here = [*above, el.get("transform", "")]
        if el.get("class") == "ground":
            found.append((el, here))
        for child in el:
            walk(child, here)

    walk(root, [])
    return root, found


def _axis(el: ET.Element, above: list[str]) -> tuple[float, float, float]:
    """The ellipse's center and its major axis's angle from horizontal, in degrees, on the sheet."""
    m = sheet_extent.IDENTITY
    for t in above:
        m = sheet_extent._mul(m, sheet_extent._transform(t or None))
    cx, cy = float(el.get("cx", 0)), float(el.get("cy", 0))
    x0, y0 = sheet_extent._apply(m, (cx, cy))
    x1, y1 = sheet_extent._apply(m, (cx + float(el.get("rx", 0)), cy))
    return x0, y0, math.degrees(math.atan2(y1 - y0, x1 - x0))


def _without_shadow(svg: str) -> str:
    """The product's own drawing on the sheet: no paper, logo or shadow."""
    svg = re.sub(r'<ellipse class="ground"[^>]*/>', "", svg)
    product = svg[svg.index('<g class="product"') : svg.index('<g class="brand">')]
    defs = re.search(r"<defs>.*?</defs>", svg, re.S)
    return (defs.group(0) if defs else "") + product


def _lowest(drawing: str) -> tuple[float, float, sheet_extent.Box]:
    """The drawing's lowest point (x, y), and the box it covers. Leaning the sheet one degree either
    way moves the lowest edge by its x: the mean of the two is the point's x."""

    def box(degrees: float) -> sheet_extent.Box:
        found = sheet_extent.reach(
            '<svg xmlns="http://www.w3.org/2000/svg">'
            f'<g transform="rotate({degrees})">{drawing}</g></svg>'
        )
        assert found is not None
        return found

    flat = box(0)
    lean = 1.0
    x = (box(lean)[3] - box(-lean)[3]) / (2 * math.sin(math.radians(lean)))
    return x, flat[3], flat


def _check(rec: dict, sku: dict) -> None:
    svg = image_release.render(rec, sku).decode()
    _check_svg(svg, (rec["product_id"], sku["sku"], orientation.drawn_angle(rec)))


def _check_svg(svg: str, name: tuple) -> None:
    _, found = _parts(svg)
    assert len(found) == 1, name
    el, above = found[0]
    x, y, axis = _axis(el, above)
    assert float(el.get("rx", 0)) > float(el.get("ry", 0)) > 0, name
    assert abs(axis) <= 1.0, (name, axis)
    low_x, low_y, (x0, _, x1, _) = _lowest(_without_shadow(svg))
    k = math.prod(
        float(n) for t in above for n in re.findall(r"scale\(([\d.]+)\)", t)
    )  # the sheet's scale of the drawing's units
    half = float(el.get("rx", 0)) * k
    assert abs(y - low_y) <= SLACK, (name, y, low_y)
    assert x - half <= low_x <= x + half, (name, x, half, low_x)
    assert 2 * half <= (x1 - x0) + 2 * ground_shadow.PAD + SLACK, (name, half, x0, x1)


def test_the_blood_oranges_of_the_report_stand_on_a_flat_shadow() -> None:
    rec = _oranges()
    for sku in rec["skus"]:
        _check(rec, sku)


def test_every_shape_that_stands_on_a_labelled_shadow_is_drawn_turned_somewhere() -> None:
    assert set(_turned()) == set(SHAPES)


@pytest.mark.parametrize("shape", SHAPES)
def test_a_turned_product_of_each_shadow_kit_stands_on_a_flat_shadow(shape: str) -> None:
    for rec in _turned()[shape]:
        _check(rec, rec["skus"][0])


def test_a_drawing_with_no_shadow_gets_none() -> None:
    drawing = '<path d="M10,10 L90,10 L90,90 Z"/>'
    assert ground_shadow.turned(drawing, "", "rotate(20)", "u") == ("", drawing)


def test_the_shadow_falls_away_from_the_one_light() -> None:
    """The light is up and to the left, so the shadow's center is right of its footprint's."""
    assert ground_shadow.LIGHT[0] < 0 and ground_shadow.LIGHT[1] < 0
    figure = '<path d="M100,100 L300,100 L300,300 L100,300 Z"/>'
    ground = '<ellipse class="ground" cx="200" cy="300" rx="100" ry="10" fill="#000000"/>'
    shadow, rest = ground_shadow.turned(ground + figure, "", "", "u")
    assert rest == figure
    el = ET.fromstring(f"<g>{shadow}</g>").find("ellipse")
    assert el is not None
    shift = float(el.get("cx", 0)) - 200
    assert 0 < shift < ground_shadow.PAD
    assert float(el.get("rx", 0)) == pytest.approx(100 + ground_shadow.PAD, abs=3)


def _pile(style: hs.HouseStyle, brand: str, angle: float, shrink: float = 1.0) -> str:
    fill = kit.Fill("solid", "#e8872b", "#8a4a10")
    params = {"fruit": "orange", "count": 5, "seed": "x", "pack": "loose"}
    return kit.render(
        "produce_pile", fill, brand=brand, uid="u", params=params, style=style,
        shrink=shrink, angle=angle,
    )  # fmt: skip


def test_a_smaller_pack_stands_on_its_own_shadow_not_the_largest_ones() -> None:
    brand = _oranges()["brand"]
    style = hs.HOUSE_STYLES[brand]
    for angle in (12, -36, 90):
        small, whole = _pile(style, brand, angle, 0.6), _pile(style, brand, angle)
        _check_svg(small, ("shrunk", angle))
        (_, _, (a0, _, a1, _)), (_, _, (b0, _, b1, _)) = (
            _lowest(_without_shadow(svg)) for svg in (small, whole)
        )
        assert (a1 - a0) < 0.75 * (b1 - b0), angle


def test_the_shadow_is_clear_of_a_logo_at_the_foot() -> None:
    """Placed by the rows the drawing covers with its shadow, so the shadow keeps the logo's air."""
    styles = [
        (brand, style)
        for brand, style in list(hs.HOUSE_STYLES.items())
        if style.mark != hs.NO_MARK and hs.reach(style, brand)[1]
    ][:6]
    assert len(styles) == 6
    for brand, style in styles:
        for angle in (90, 180):  # the turned pile reaches the foot of its room
            svg = _pile(style, brand, angle)
            product = svg[svg.index('<g class="product"') : svg.index('<g class="brand">')]
            box = sheet_extent.reach(f'<svg xmlns="http://www.w3.org/2000/svg">{product}</svg>')
            assert box is not None
            foot = hs.SIZE - hs.reach(style, brand)[1] - hs.AIR
            assert box[3] <= foot + 0.5, (brand, angle, box)


def test_the_shadow_is_as_wide_as_the_part_near_the_ground_not_the_whole_drawing() -> None:
    """A square on its corner touches the ground at a point: its shadow is the width of its lowest
    12%, 2 x 0.12 of its height, where the whole drawing is 283 wide."""
    ground = '<ellipse class="ground" cx="200" cy="300" rx="100" ry="10" fill="#000000"/>'
    square = '<path d="M100,100 L300,100 L300,300 L100,300 Z"/>'
    shadow, _ = ground_shadow.turned(ground + square, "", "rotate(45 200 200)", "u")
    el = ET.fromstring(f"<g>{shadow}</g>").find("ellipse")
    assert el is not None
    tall = 200 * math.sqrt(2)
    assert float(el.get("cy", 0)) == pytest.approx(200 + tall / 2, abs=0.1)
    assert float(el.get("rx", 0)) == pytest.approx(0.12 * tall + ground_shadow.PAD, abs=0.5)
