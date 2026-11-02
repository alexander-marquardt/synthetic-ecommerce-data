"""Every product drawing is original and drawn by code (#803).

The C-clamp was the one exception: a copied Wikimedia Commons file, loaded through a normaliser
and a licence manifest (#102). It is now drawn in code like the other breadth shapes, and no
image file ships under ``src/``, so a copied drawing cannot come back unnoticed.
"""

from __future__ import annotations

import re
from pathlib import Path

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.drawing import draw_sku, svg_problems
from synthetic_ecommerce_data.core.drawing.model import Lines, Poly
from synthetic_ecommerce_data.domains.industrial import breadth
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_shapes import BREADTH_SHAPES

SRC = Path(__file__).resolve().parents[1] / "src"


def test_no_svg_file_is_committed_under_src():
    """Test fixtures live under ``tests/``; under ``src/`` a drawing is code, never a file."""
    found = sorted(str(p.relative_to(SRC)) for p in SRC.rglob("*") if p.suffix.lower() == ".svg")
    assert found == [], f"an image file under src/, where every drawing is code: {found}"


def _clamp():
    return BREADTH_SHAPES["c_clamp"]


def _area(points) -> float:
    pairs = zip(points, points[1:] + points[:1], strict=True)
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in pairs)) / 2


def test_the_c_clamps_row_draws_the_clamp():
    row = next(r for r in breadth.rows() if r.key == "c_clamps")
    assert row.shape == "c_clamp"


def test_the_clamp_is_a_frame_a_screw_and_a_pad():
    fn, _ = _clamp()
    fig = fn({"Size": "3 in"}).figure
    x0, y0, x1, y1 = fig.bounds()
    polys = [s for s in fig.shapes if isinstance(s, Poly)]
    # The frame: the biggest part, a C open on one side, so it covers well under its own box.
    frame = max(polys, key=lambda p: _area(list(p.points)))
    fx = [p[0] for p in frame.points]
    fy = [p[1] for p in frame.points]
    box = (max(fx) - min(fx)) * (max(fy) - min(fy))
    assert max(fy) - min(fy) >= 0.6 * (y1 - y0), "the frame spans the clamp's height"
    assert _area(list(frame.points)) <= 0.6 * box, "the frame is a C, open at the throat"
    # The screw: a narrow upright part with its thread drawn as line work.
    assert any(isinstance(s, Lines) and len(s.segments) >= 6 for s in fig.shapes), "no thread"
    # The pad: a part clear of both arms, in the throat between them.
    pads = [
        p
        for p in polys
        if p is not frame
        and p.role == "part"
        and min(q[1] for q in p.points) > min(fy) + 0.3
        and max(q[1] for q in p.points) < max(fy) - 0.3
    ]
    assert pads, "no swivel pad in the throat"
    # The handle: a bar below the frame, wider than the screw it turns.
    handles = [
        p
        for p in polys
        if min(q[1] for q in p.points) > max(fy)
        and max(q[0] for q in p.points) - min(q[0] for q in p.points) >= 0.5
    ]
    assert handles, "no T-handle below the frame"


def test_the_clamp_fills_its_declared_extent():
    fn, extent = _clamp()
    x0, y0, x1, y1 = fn({"Size": "3 in"}).figure.bounds()
    assert (round(x1 - x0, 9), round(y1 - y0, 9)) == extent


def test_the_clamp_does_not_read_the_record():
    fn, _ = _clamp()
    assert fn({"Size": "2 in"}).figure == fn({"Size": "6 in"}).figure


def test_a_c_clamps_sheet_passes_the_svg_gate():
    data, _ = draw_sku("c_clamps", brands.BRANDS[0], {"Material": "Steel", "Size": "3 in"})
    assert svg_problems(data) == []
    assert len(re.findall(rb"<path ", data)) >= 5, "a clamp of several parts, not one outline"
