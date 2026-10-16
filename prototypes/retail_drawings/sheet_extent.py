"""How far a drawing reaches on its sheet: the bounding box of the SVG a shape draws (gen#242).

:func:`reach` reads the ``<path>``, ``<rect>``, ``<circle>`` and ``<ellipse>`` of one SVG, through
every ``translate``, ``rotate`` and ``scale`` of the groups around them, and returns the box
they cover.
A curve is measured at its true extremes, not at its control points, so a curve that bows
inside the sheet is not flagged for a control point outside it. Stroke width is not counted:
the guard is about the geometry a drawing places, as the issue words it. ``<text>`` is not
measured either: a label is skipped, not read.

Anything else outside this vocabulary (another element that paints, a path command, a transform,
a nested ``<svg>``, a ``style`` transform, a ``<clipPath>`` transform or ``clipPathUnits``)
raises ``ValueError`` instead of being skipped, so a drawing that starts to use one is not
measured as a smaller box than it has.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator

NS = "{http://www.w3.org/2000/svg}"

#: ``(a, b, c, d, e, f)``: the SVG matrix, x' = a x + c y + e and y' = b x + d y + f.
Matrix = tuple[float, float, float, float, float, float]
Point = tuple[float, float]
Box = tuple[float, float, float, float]  # x0, y0, x1, y1

IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

#: Elements that paint nothing a viewer sees as the drawing, or are read elsewhere in this module.
_NOT_DRAWN = {"title", "desc", "text", "svg", "g"}
#: Elements whose children are a definition (a tile, a clip, a mask, a gradient), not a drawing.
_DEFINITIONS = ("defs", "clipPath", "pattern", "mask", "linearGradient", "radialGradient")
_ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
_NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_TRANSFORM = re.compile(r"([A-Za-z]+)\(([^)]*)\)")


def _mul(m: Matrix, n: Matrix) -> Matrix:
    """``m`` applied after ``n`` (the transform of a child inside its parent's)."""
    a, b, c, d, e, f = m
    p, q, r, s, t, u = n
    return (a * p + c * q, b * p + d * q, a * r + c * s, b * r + d * s,
            a * t + c * u + e, b * t + d * u + f)  # fmt: skip


def _transform(text: str | None) -> Matrix:
    """The matrix of a ``transform`` attribute: ``translate(x y)``, ``rotate(deg [cx cy])``,
    ``scale(s [sy])`` and ``matrix(...)``."""
    out = IDENTITY
    for name, args in _TRANSFORM.findall(text or ""):
        v = [float(x) for x in _NUMBER.findall(args)]
        if name == "translate" and len(v) in (1, 2):
            step: Matrix = (1.0, 0.0, 0.0, 1.0, v[0], v[1] if len(v) == 2 else 0.0)
        elif name == "rotate" and len(v) in (1, 3):
            cos, sin = math.cos(math.radians(v[0])), math.sin(math.radians(v[0]))
            cx, cy = (v[1], v[2]) if len(v) == 3 else (0.0, 0.0)
            step = (cos, sin, -sin, cos, cx - cos * cx + sin * cy, cy - sin * cx - cos * cy)
        elif name == "scale" and len(v) in (1, 2):
            step = (v[0], 0.0, 0.0, v[-1], 0.0, 0.0)
        elif name == "matrix" and len(v) == 6:
            step = (v[0], v[1], v[2], v[3], v[4], v[5])
        else:
            raise ValueError(f"transform {name}({args}) is not read by sheet_extent")
        out = _mul(out, step)
    return out


def _apply(m: Matrix, p: Point) -> Point:
    return (m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5])


def _bezier_extremes(pts: list[Point]) -> Iterator[Point]:
    """The points of a quadratic or cubic Bezier where x or y is at its extreme (and its ends)."""
    yield pts[0]
    yield pts[-1]
    for axis in (0, 1):
        v = [p[axis] for p in pts]
        if len(v) == 3:  # quadratic: derivative is linear
            den = v[0] - 2 * v[1] + v[2]
            ts = [(v[0] - v[1]) / den] if den else []
        else:  # cubic: derivative is a quadratic in t
            a = -v[0] + 3 * v[1] - 3 * v[2] + v[3]
            b = 2 * (v[0] - 2 * v[1] + v[2])
            c = v[1] - v[0]
            ts = _quadratic_roots(a, b, c)
        for t in ts:
            if 0.0 < t < 1.0:
                yield _bezier_at(pts, t)


def _quadratic_roots(a: float, b: float, c: float) -> list[float]:
    if abs(a) < 1e-12:
        return [-c / b] if abs(b) > 1e-12 else []
    disc = b * b - 4 * a * c
    if disc < 0:
        return []
    root = math.sqrt(disc)
    return [(-b + root) / (2 * a), (-b - root) / (2 * a)]


def _bezier_at(pts: list[Point], t: float) -> Point:
    while len(pts) > 1:
        pts = [((1 - t) * p[0] + t * q[0], (1 - t) * p[1] + t * q[1])
               for p, q in zip(pts, pts[1:], strict=False)]  # fmt: skip
    return pts[0]


def _arc_points(
    p0: Point, rx: float, ry: float, rot: float, large: int, sweep: int, p1: Point
) -> list[Point]:
    """Points along an SVG elliptical arc, dense enough that the box between them is the arc's
    to within a hundredth of a unit (the endpoint-to-center conversion of the SVG spec, F.6.5)."""
    if rx == 0 or ry == 0 or p0 == p1:
        return [p0, p1]
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(rot)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1, y1 = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    coef = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cx1, cy1 = coef * rx * y1 / ry, -coef * ry * x1 / rx
    cx = cp * cx1 - sp * cy1 + (p0[0] + p1[0]) / 2
    cy = sp * cx1 + cp * cy1 + (p0[1] + p1[1]) / 2
    t0 = math.atan2((y1 - cy1) / ry, (x1 - cx1) / rx)
    t1 = math.atan2((-y1 - cy1) / ry, (-x1 - cx1) / rx)
    sweep_angle = t1 - t0
    if sweep and sweep_angle < 0:
        sweep_angle += 2 * math.pi
    elif not sweep and sweep_angle > 0:
        sweep_angle -= 2 * math.pi
    steps = 96
    pts = []
    for i in range(steps + 1):
        t = t0 + sweep_angle * i / steps
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        pts.append((cp * ex - sp * ey + cx, sp * ex + cp * ey + cy))
    return pts


def _path_points(d: str) -> Iterator[Point]:
    """Every point a path's ``d`` reaches: its vertices and the extremes of its curves."""
    cur = start = (0.0, 0.0)
    last: Point | None = None  # the previous curve's last control point, which S and T mirror
    kind = ""
    for cmd, body in re.findall(r"([A-Za-z])([^A-Za-z]*)", d):
        up = cmd.upper()
        if up not in _ARGS:
            raise ValueError(f"path command {cmd!r} is not read by sheet_extent")
        nums = [float(x) for x in _NUMBER.findall(body)]
        width = _ARGS[up]
        if width == 0:
            cur = start
            continue
        if len(nums) % width or not nums:
            raise ValueError(f"path {cmd}{body!r}: {len(nums)} numbers do not fit {width} each")
        rel = cmd.islower()
        for i in range(0, len(nums), width):
            n = nums[i : i + width]
            ox, oy = cur if rel else (0.0, 0.0)
            if up == "H":
                end = (n[0] + ox, cur[1])
            elif up == "V":
                end = (cur[0], n[0] + oy)
            elif up == "A":
                end = (n[5] + ox, n[6] + oy)
            else:
                end = (n[-2] + ox, n[-1] + oy)
            if up == "M":
                start = end
                yield end
            elif up in "LHV":
                yield end
            elif up == "A":
                yield from _arc_points(cur, n[0], n[1], n[2], int(n[3]), int(n[4]), end)
            else:
                ctrl = [(n[j] + ox, n[j + 1] + oy) for j in range(0, len(n) - 2, 2)]
                if up in "ST":  # the first control point is the previous one, mirrored
                    same = kind == ("C" if up == "S" else "Q") and last is not None
                    mirror = (2 * cur[0] - last[0], 2 * cur[1] - last[1]) if same else cur
                    ctrl = [mirror, *ctrl]
                yield from _bezier_extremes([cur, *ctrl, end])
                last = ctrl[-1]
            kind = "C" if up in "CS" else "Q" if up in "QT" else ""
            cur = end
            if up == "M":
                up = "L"  # further pairs after a move are implicit lines
                width = 2


def _ellipse_box(cx: float, cy: float, rx: float, ry: float, m: Matrix) -> Box:
    """An ellipse under ``m``: its center moves and its half-extents are the norms of the matrix
    rows applied to the radii."""
    x, y = _apply(m, (cx, cy))
    hx = math.hypot(m[0] * rx, m[2] * ry)
    hy = math.hypot(m[1] * rx, m[3] * ry)
    return (x - hx, y - hy, x + hx, y + hy)


def _num(el: ET.Element, name: str, default: float = 0.0) -> float:
    return float(el.get(name, default))


def _boxes(el: ET.Element, m: Matrix, clips: dict[str, ET.Element]) -> Iterator[Box]:
    tag = el.tag.removeprefix(NS)
    if "transform" in el.get("style", ""):
        raise ValueError(f"<{tag}> style transform is not read by sheet_extent")
    here = _mul(m, _transform(el.get("transform")))
    if tag in _DEFINITIONS:
        return  # a definition paints nothing until something uses it
    if tag == "path":
        pts = [_apply(here, p) for p in _path_points(el.get("d", ""))]
        if pts:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            yield _clipped((min(xs), min(ys), max(xs), max(ys)), el, here, clips)
    elif tag == "rect":
        x, y, w, h = (_num(el, k) for k in ("x", "y", "width", "height"))
        pts = [_apply(here, p) for p in ((x, y), (x + w, y), (x, y + h), (x + w, y + h))]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        yield _clipped((min(xs), min(ys), max(xs), max(ys)), el, here, clips)
    elif tag == "circle":
        r = _num(el, "r")
        box = _ellipse_box(_num(el, "cx"), _num(el, "cy"), r, r, here)
        yield _clipped(box, el, here, clips)
    elif tag == "ellipse":
        box = _ellipse_box(_num(el, "cx"), _num(el, "cy"), _num(el, "rx"), _num(el, "ry"), here)
        yield _clipped(box, el, here, clips)
    elif tag not in _NOT_DRAWN:
        raise ValueError(f"<{tag}> is not read by sheet_extent")
    if tag in ("g", "svg"):
        for child in el:
            yield from _boxes(child, here, clips)


def _clipped(box: Box, el: ET.Element, m: Matrix, clips: dict[str, ET.Element]) -> Box:
    """``box`` cut to the box of the ``clip-path`` the element names, if it names one: a net
    that is drawn far wider than the bag it is clipped to is only as wide as the bag."""
    ref = el.get("clip-path")
    if ref is None:
        return box
    found = re.fullmatch(r"url\(#([^)]+)\)", ref)
    if not found or found.group(1) not in clips:
        raise ValueError(f"clip-path {ref!r} names no clipPath in the SVG")
    cut = [b for child in clips[found.group(1)] for b in _boxes(child, m, clips)]
    if not cut:
        return (0.0, 0.0, 0.0, 0.0)
    x0, y0 = min(b[0] for b in cut), min(b[1] for b in cut)
    x1, y1 = max(b[2] for b in cut), max(b[3] for b in cut)
    return (max(box[0], x0), max(box[1], y0), min(box[2], x1), min(box[3], y1))


def reach(svg: str | bytes) -> Box | None:
    """``(x0, y0, x1, y1)``: the box the SVG's drawn elements cover, or ``None`` when none is."""
    root = ET.fromstring(svg)
    if any(el is not root for el in root.iter(f"{NS}svg")):
        raise ValueError("a nested <svg> (its x, y and viewBox) is not read by sheet_extent")
    clips = {el.get("id", ""): el for el in root.iter(f"{NS}clipPath")}
    for clip in clips.values():
        if clip.get("transform") or clip.get("clipPathUnits"):
            raise ValueError("a <clipPath> transform or clipPathUnits is not read by sheet_extent")
    boxes = list(_boxes(root, IDENTITY, clips))
    if not boxes:
        return None
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))  # fmt: skip


def overrun(svg: str | bytes, sheet: float = 400.0, slack: float = 0.5) -> float:
    """How far past the ``sheet`` x ``sheet`` square the drawing reaches, in units (0 when it
    stays inside, within ``slack`` for rounding in the drawing's own numbers)."""
    box = reach(svg)
    if box is None:
        return 0.0
    past = max(-box[0], -box[1], box[2] - sheet, box[3] - sheet)
    return past if past > slack else 0.0
