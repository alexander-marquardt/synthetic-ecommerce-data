"""How much of an area a drawing covers: the share of a box its filled shapes paint (gen#1111).

:func:`cover` reads the same SVG vocabulary as :mod:`sheet_extent` (``<path>``, ``<rect>``,
``<circle>``, ``<ellipse>``, through every ``translate``, ``rotate`` and ``scale`` of the groups
around them) and fills each shape whose ``fill`` is not ``none`` on a grid of sample points with
the nonzero rule, the SVG default. A ``clip-path`` cuts its shape. A curve is flattened into short
lines. Strokes are not counted (an outline, a gloss line or a net's mesh sits on or beside a fill),
and neither is ``<text>``, so a figure counts as the area its fills cover.

It is the measure behind the produce kit's fill floor: before gen#1111, a pack of lemons covered
about a tenth of its picture and nothing noticed. It needs only numpy, so the test runs anywhere
the suite does, with no rasteriser installed.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

import numpy as np

from synthetic_ecommerce_data.domains.retail.sheet_extent import (
    _ARGS,
    _DEFINITIONS,
    _NUMBER,
    IDENTITY,
    NS,
    Box,
    Matrix,
    Point,
    _apply,
    _bezier_at,
    _mul,
    _transform,
)

#: Points per flattened curve, and per ellipse.
CURVE_STEPS, ROUND_STEPS = 12, 48


def _subpaths(d: str) -> list[list[Point]]:
    """A path's ``d`` as closed polygons, one per subpath (a fill closes an open subpath)."""
    out: list[list[Point]] = []
    cur = start = (0.0, 0.0)
    last: Point | None = None
    kind = ""
    for cmd, body in re.findall(r"([A-Za-z])([^A-Za-z]*)", d):
        up = cmd.upper()
        if up not in _ARGS or up == "A":
            raise ValueError(f"path command {cmd!r} is not read by sheet_cover")
        width = _ARGS[up]
        nums = [float(x) for x in _NUMBER.findall(body)]
        if width == 0:
            cur = start
            kind = ""
            continue
        rel = cmd.islower()
        for i in range(0, len(nums), width):
            n = nums[i : i + width]
            ox, oy = cur if rel else (0.0, 0.0)
            if up == "H":
                end = (n[0] + ox, cur[1])
            elif up == "V":
                end = (cur[0], n[0] + oy)
            else:
                end = (n[-2] + ox, n[-1] + oy)
            if up == "M":
                out.append([end])
                start = end
                up, width = "L", 2  # further pairs after a move are implicit lines
            elif up in "LHV":
                out[-1].append(end)
            else:
                ctrl = [(n[j] + ox, n[j + 1] + oy) for j in range(0, len(n) - 2, 2)]
                if up in "ST":
                    same = kind == ("C" if up == "S" else "Q") and last is not None
                    mirror = (2 * cur[0] - last[0], 2 * cur[1] - last[1]) if same else cur
                    ctrl = [mirror, *ctrl]
                pts = [cur, *ctrl, end]
                out[-1] += [_bezier_at(pts, k / CURVE_STEPS) for k in range(1, CURVE_STEPS + 1)]
                last = ctrl[-1]
            kind = "C" if up in "CS" else "Q" if up in "QT" else ""
            cur = end
    return [p for p in out if len(p) > 2]


def _ellipse(cx: float, cy: float, rx: float, ry: float) -> list[Point]:
    turns = [2 * math.pi * k / ROUND_STEPS for k in range(ROUND_STEPS)]
    return [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in turns]


def _num(el: ET.Element, name: str) -> float:
    return float(el.get(name, 0.0))


def _polygons(el: ET.Element, tag: str) -> list[list[Point]]:
    if tag == "path":
        return _subpaths(el.get("d", ""))
    if tag == "rect":
        x, y, w, h = (_num(el, k) for k in ("x", "y", "width", "height"))
        return [[(x, y), (x + w, y), (x + w, y + h), (x, y + h)]]
    if tag == "circle":
        r = _num(el, "r")
        return [_ellipse(_num(el, "cx"), _num(el, "cy"), r, r)]
    if tag == "ellipse":
        return [_ellipse(_num(el, "cx"), _num(el, "cy"), _num(el, "rx"), _num(el, "ry"))]
    return []


class _Grid:
    """Sample points at the centres of ``step``-unit cells over ``box``."""

    def __init__(self, box: Box, step: float) -> None:
        self.box = box
        xs = np.arange(box[0] + step / 2, box[2], step)
        ys = np.arange(box[1] + step / 2, box[3], step)
        self.x, self.y = np.meshgrid(xs, ys)
        self.mask = np.zeros(self.x.shape, dtype=bool)

    def fill(self, polys: list[list[Point]]) -> np.ndarray:
        """The points inside ``polys`` by the nonzero rule (only the polygons' box is tested)."""
        out = np.zeros(self.x.shape, dtype=bool)
        pts = [p for poly in polys for p in poly]
        if not pts:
            return out
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
        cols = np.nonzero((self.x[0] >= x0) & (self.x[0] <= x1))[0]
        rows = np.nonzero((self.y[:, 0] >= y0) & (self.y[:, 0] <= y1))[0]
        if not len(cols) or not len(rows):
            return out
        px = self.x[np.ix_(rows, cols)]
        py = self.y[np.ix_(rows, cols)]
        wind = np.zeros(px.shape, dtype=int)
        for poly in polys:
            a = np.array(poly)
            b = np.roll(a, -1, axis=0)
            for (ax, ay), (bx, by) in zip(a, b, strict=True):
                if ay == by:
                    continue
                side = (bx - ax) * (py - ay) - (px - ax) * (by - ay)
                up = (ay <= py) & (by > py) & (side > 0)
                down = (by <= py) & (ay > py) & (side < 0)
                wind += up.astype(int) - down.astype(int)
        out[np.ix_(rows, cols)] = wind != 0
        return out


def _painted(el: ET.Element, inherited: str | None) -> bool:
    fill = el.get("fill", inherited or "#000")
    if fill == "none":
        return False
    return all(float(el.get(key, 1.0)) > 0 for key in ("fill-opacity", "opacity"))


def _walk(
    el: ET.Element, m: Matrix, grid: _Grid, named: dict[str, ET.Element], skip: set[str],
    fill: str | None,
) -> None:  # fmt: skip
    tag = el.tag.removeprefix(NS)
    if tag in _DEFINITIONS or skip & set((el.get("class") or "").split()):
        return
    if float(el.get("opacity", 1.0)) <= 0:
        return
    here = _mul(m, _transform(el.get("transform")))
    fill = el.get("fill", fill)
    if tag in ("path", "rect", "circle", "ellipse") and _painted(el, fill):
        inside = grid.fill([[_apply(here, p) for p in poly] for poly in _polygons(el, tag)])
        ref = el.get("clip-path")
        if ref is not None:
            found = re.fullmatch(r"url\(#([^)]+)\)", ref)
            if not found or found.group(1) not in named:
                raise ValueError(f"clip-path {ref!r} names no clipPath in the SVG")
            clip = np.zeros(inside.shape, dtype=bool)
            for child in named[found.group(1)]:
                polys = _polygons(child, child.tag.removeprefix(NS))
                clip |= grid.fill([[_apply(here, p) for p in poly] for poly in polys])
            inside &= clip
        grid.mask |= inside
    for child in el:
        _walk(child, here, grid, named, skip, fill)


def cover(svg: str | bytes, box: Box, step: float = 2.0, skip: tuple[str, ...] = ()) -> float:
    """The share (0..1) of ``box`` the SVG's filled shapes paint, sampled every ``step`` units.
    An element whose ``class`` names one of ``skip`` (a ground shadow) is not counted."""
    root = ET.fromstring(svg)
    named = {el.get("id", ""): el for el in root.iter()}
    grid = _Grid(box, step)
    _walk(root, IDENTITY, grid, named, set(skip), None)
    return float(grid.mask.mean())
