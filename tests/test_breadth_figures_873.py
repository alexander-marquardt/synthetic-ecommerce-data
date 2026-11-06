"""Four breadth types draw their own figure, not the generic box, and the glove is rounded (#873).

The maintainer, on the #860 contact sheet: the glove and ball valve images "are a bit too
square". The ball valve, bench vise, thread pitch gauge and T-slot nut drew the
generic ``block``; each now has a shape of its own, drawn in code like the C-clamp (#803).
``bar_stock_square`` is a block and keeps it. The glove's palm, thumb and fingers were
rectangles; it is now one curved outline, still in its shell's knit hatch and the brand's ink.
Every new figure sits on the white paper at its product's angle (#849/#860).
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import brands, domain
from synthetic_ecommerce_data.core.bundle import flat_facets, records
from synthetic_ecommerce_data.core.drawing import draw_product, draw_sku, product_look, svg_problems
from synthetic_ecommerce_data.core.drawing.model import Disc, Lines, Poly
from synthetic_ecommerce_data.core.drawing.style import house_style
from synthetic_ecommerce_data.domains.industrial import breadth
from synthetic_ecommerce_data.domains.industrial.drawing import breadth_shapes
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_shapes import BREADTH_SHAPES

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"

#: Each type that drew the box, and the shape it draws now.
OWN_SHAPES = {
    "ball_valves": "ball_valve",
    "bench_vises": "bench_vise",
    "thread_pitch_gages": "pitch_gage",
    "t_slot_nuts": "t_slot_nut",
}
TURN = re.compile(r'<g transform="rotate\((-?[\d.]+) ')
PAPER = re.compile(
    r'<svg[^>]*>(?:<defs>.*?</defs>)?<rect width="\d+" height="\d+" fill="(#[0-9a-f]{6})"/>'
)


def _shape(name: str):
    assert name in BREADTH_SHAPES, f"no breadth shape {name!r}"
    return BREADTH_SHAPES[name]


def _figure(name: str):
    fn, _ = _shape(name)
    return fn({"Size": "1/2 in"}).figure


def _polys(fig, role: str | None = None) -> list[Poly]:
    return [s for s in fig.shapes if isinstance(s, Poly) and role in (None, s.role)]


def _width(poly: Poly) -> float:
    xs = [p[0] for p in poly.points]
    return max(xs) - min(xs)


def _height(poly: Poly) -> float:
    ys = [p[1] for p in poly.points]
    return max(ys) - min(ys)


# --- every type draws its own shape -----------------------------------------------------


@pytest.mark.parametrize(("key", "shape"), sorted(OWN_SHAPES.items()))
def test_the_type_draws_its_own_shape_not_the_box(key, shape):
    assert breadth.row_for(key).shape == shape
    assert domain.figure(key)[0] is not breadth_shapes.block


def test_square_bar_stock_keeps_the_box():
    assert breadth.row_for("bar_stock_square").shape == "block"


def test_roller_chain_already_draws_its_own_chain():
    """Roller chain is a deep type (#98) with its own figure: the box never drew it."""
    assert domain.figure("roller_chain")[0] is not breadth_shapes.block


@pytest.mark.parametrize("shape", sorted(OWN_SHAPES.values()))
def test_the_shape_is_fixed_fills_its_extent_and_passes_the_svg_gate(shape):
    fn, (ex, ey) = _shape(shape)
    fig = fn({"Size": "1/2 in"}).figure
    assert fig == fn({"Size": "2 in"}).figure, "a breadth shape does not read the record"
    x0, y0, x1, y1 = fig.bounds()
    assert x1 - x0 <= ex + 1e-9 and y1 - y0 <= ey + 1e-9
    assert x1 - x0 >= 0.95 * ex and y1 - y0 >= 0.95 * ey, "the extent is the figure's own"
    key = next(k for k, s in OWN_SHAPES.items() if s == shape)
    data, source = draw_sku(key, brands.BRANDS[0], {"Material": "Steel", "Size": "1/2 in"})
    assert source == "nominal"
    assert svg_problems(data) == []
    assert len(re.findall(rb"<path ", data)) >= 4, "a part of several pieces, not one outline"


# --- what each shape draws ----------------------------------------------------------------


def test_the_ball_valve_is_a_round_body_two_pipe_ends_and_a_lever():
    fig = _figure("ball_valve")
    bodies = [s for s in fig.shapes if isinstance(s, Disc) and s.role == "part"]
    assert bodies, "no round body"
    body = max(bodies, key=lambda d: d.radius)
    cx, cy = body.centre
    # The pipe ends: one each side of the body, level with its centre.
    ends = [
        p
        for p in _polys(fig, "part")
        if min(q[1] for q in p.points) < cy < max(q[1] for q in p.points)
    ]
    assert any(max(q[0] for q in p.points) < cx for p in ends), "no left pipe end"
    assert any(min(q[0] for q in p.points) > cx for p in ends), "no right pipe end"
    assert any(isinstance(s, Lines) for s in fig.shapes), "the pipe ends carry no thread"
    # The lever: above the body, longer than the body is wide, with its grip.
    top = cy - body.radius
    levers = [
        p for p in _polys(fig) if max(q[1] for q in p.points) < top and _width(p) > 2 * body.radius
    ]
    assert levers, "no lever handle over the body"
    assert _polys(fig, "grip"), "the lever has no grip"


def test_the_bench_vise_has_two_jaws_a_throat_a_screw_and_a_handle():
    fig = _figure("bench_vise")
    x0, y0, x1, y1 = fig.bounds()
    jaws = [p for p in _polys(fig, "dark") if min(q[1] for q in p.points) <= y0 + 0.1]
    assert len(jaws) == 2, "two jaw plates at the top"
    (a, b) = sorted(jaws, key=lambda p: min(q[0] for q in p.points))
    gap = min(q[0] for q in b.points) - max(q[0] for q in a.points)
    assert gap > 0.2, "the jaws stand apart: a throat between them"
    handles = [p for p in _polys(fig, "plain") if _height(p) > 0.4 * (y1 - y0) and _width(p) < 0.15]
    assert handles, "no handle bar through the screw"
    bases = [
        p
        for p in _polys(fig)
        if max(q[1] for q in p.points) >= y1 - 1e-9 and _width(p) > 0.6 * (x1 - x0)
    ]
    assert bases, "no base under the vise"


def test_the_pitch_gage_fans_toothed_leaves_from_one_pivot():
    fig = _figure("pitch_gage")
    leaves = [p for p in _polys(fig, "plain") if len(p.points) >= 20]
    assert len(leaves) >= 3, "several leaves"
    angles = set()
    for leaf in leaves:
        (ax, ay), (bx, by) = leaf.points[0], leaf.points[len(leaf.points) // 2]
        angles.add(round(math.degrees(math.atan2(by - ay, bx - ax))))
    assert len(angles) == len(leaves), "the leaves fan out, each at its own angle"
    assert _polys(fig, "part"), "no case the leaves fold into"


def test_the_t_slot_nut_is_a_t_with_a_tapped_hole():
    fig = _figure("t_slot_nut")
    faces = [p for p in _polys(fig, "part") if len(p.points) == 8]
    assert faces, "no T-shaped front face"
    (face,) = faces
    ys = sorted({q[1] for q in face.points})
    assert len(ys) == 3, "a T: the neck's top, the shoulder and the flange's bottom"
    neck = [q[0] for q in face.points if q[1] == ys[0]]
    flange = [q[0] for q in face.points if q[1] == ys[2]]
    assert max(neck) - min(neck) < max(flange) - min(flange), "the neck is narrower than the flange"
    assert _polys(fig, "hole"), "no tapped hole"


# --- the glove ----------------------------------------------------------------------------


def _glove(size: str = "Medium"):
    fn, extent = domain.figure("cut_resistant_gloves")
    return fn({"Size": size}).figure, extent


def test_the_glove_has_no_rectangle():
    fig, _ = _glove()
    boxes = [p for p in _polys(fig) if len(p.points) == 4]
    assert boxes == [], "the palm, thumb or a finger is still a rectangle"


def test_the_glove_is_one_rounded_outline_that_narrows_to_its_cuff():
    fig, _ = _glove()
    parts = _polys(fig, "part")
    assert len(parts) == 1, "the cuff, palm, thumb and fingers are one outline"
    points = parts[0].points
    assert len(points) >= 60, "rounded fingertips and thumb take many points"
    tip_y = min(q[1] for q in points)
    tips = [q for q in points if q[1] <= tip_y + 0.05]
    assert len(tips) >= 3, "the longest fingertip is a curve, not a corner"

    def width_at(y: float) -> float:
        xs = []
        for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1], strict=True):
            if (ay - y) * (by - y) < 0:
                xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
        return max(xs) - min(xs)

    cuff_edge = max(q[1] for q in points)
    palm = width_at(cuff_edge - 0.4 * (cuff_edge - tip_y))
    assert width_at(cuff_edge - 0.05) < 0.9 * palm, "the palm narrows to the cuff"


@pytest.mark.parametrize("size", ["X-Small", "Medium", "XX-Large"])
def test_the_glove_fits_its_declared_extent(size):
    fig, (ex, ey) = _glove(size)
    x0, y0, x1, y1 = fig.bounds()
    assert x1 - x0 <= ex and y1 - y0 <= ey


def test_the_glove_keeps_its_knit_hatch_and_the_brand_outline():
    brand = brands.BRANDS[0]
    data, _ = draw_sku("cut_resistant_gloves", brand, {"Size": "Medium", "Material": "HPPE Blend"})
    text = data.decode()
    assert svg_problems(data) == []
    assert re.search(r'<pattern id="h45', text), "no knit hatch for the HPPE shell"
    assert re.search(r'<path [^>]*fill="url\(#h45', text), "the glove is not filled with its knit"
    assert f'stroke="{house_style(brand).ink}"' in text, "no brand outline"


# --- the #849/#860 conventions ------------------------------------------------------------


def _products(key: str) -> list[dict]:
    lines = (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()
    return [p for p in map(json.loads, filter(None, lines)) if p["product_type"] == key][:3]


@pytest.mark.parametrize("key", [*sorted(OWN_SHAPES), "cut_resistant_gloves"])
def test_every_sku_of_a_product_shares_its_angle_and_look_on_white_paper(key):
    facets = flat_facets(GOLDEN)
    products = _products(key)
    assert products, key
    for parent in products:
        pid = parent["product_id"]
        angle = product_look.angle_of(pid, domain.orientation(key))
        drawn = draw_product(key, parent["brand"], records(parent, facets), pid)
        looks = set()
        for data, _ in drawn:
            text = data.decode()
            assert PAPER.match(text).group(1) == product_look.PAPER == "#ffffff", pid
            assert {float(a) for a in TURN.findall(text)} == ({float(angle)} if angle else set()), (
                pid
            )
            plate = text[text.rindex("<g fill=") :]
            strokes = frozenset(re.findall(r'stroke="(#[0-9a-f]{6})"', text))
            looks.add((plate, strokes))
        assert len(looks) == 1, f"{pid}: its SKUs differ in plate or outline"
    assert domain.figure(key)[0] is not breadth_shapes.block
