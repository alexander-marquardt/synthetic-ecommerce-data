"""The last of a shoe: its colors, its :class:`Kind` and its outline (:mod:`kit_footwear`)."""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import re
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.kit import _shade, _tint

#: The heel's back edge, the toe tip and the ground, in sheet coordinates.
XB, XT, G = 62.0, 350.0, 330.0
LINING = "#d9c4a0"
GUM = "#c99a5b"
FOAM = "#f3f1ea"
RUBBER = "#2c2d31"
TREAD = "#5d6068"
METAL = "#c9ccd1"
BRASS = "#c9a24a"
AMBER = "#e0a526"
WOOD = "#b98a56"
CORK = "#c9a77c"
ROPE = "#d8c08a"


def _f(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def _pt(x: float, y: float) -> str:
    return f"{_f(x)},{_f(y)}"


def _dark(color: str) -> bool:
    r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b < 110


def _detail(base: str) -> str:
    """A seam or stitch color that shows on ``base``: lighter on a dark upper, darker on a light one."""
    return _tint(base, 0.45) if _dark(base) else _shade(base, 0.4)


def _trim(base: str, t: float = 0.2) -> str:
    """An overlay a shade off ``base`` that still shows on it (lighter on near-black)."""
    return _tint(base, t) if _dark(base) else _shade(base, t)


# --------------------------------------------------------------------------
# Sampling a path: where the outline's edge is at a given x or y
# --------------------------------------------------------------------------

_TOKEN = re.compile(r"([MLCQZ])|(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)")


def _points(d: str, n: int = 48) -> list[tuple[float, float]]:
    """Points along ``d`` (absolute M, L, C, Q and Z only, the commands this module writes)."""
    out: list[tuple[float, float]] = []
    cmd, args, cur, start = "", [], (0.0, 0.0), (0.0, 0.0)
    need = {"M": 1, "L": 1, "Q": 2, "C": 3}
    for m in _TOKEN.finditer(d):
        if m.group(1):
            cmd, args = m.group(1), []
            if cmd == "Z":
                out.append(start)
                cur = start
            continue
        args.append((float(m.group(2)), float(m.group(3))))
        if len(args) < need[cmd]:
            continue
        if cmd == "M":
            cur = start = args[0]
            out.append(cur)
        elif cmd == "L":
            (x0, y0), (x1, y1) = cur, args[0]
            out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(1, n + 1)]
            cur = args[0]
        else:
            ctrl = [cur, *args]
            for i in range(1, n + 1):
                t = i / n
                pts = list(ctrl)
                while len(pts) > 1:  # de Casteljau
                    pts = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(pts, pts[1:], strict=False)]
                out.append(pts[0])
            cur = args[-1]
        args = []
    return out


def _crossings(d: str, v: float, axis: int) -> list[float]:
    """Where the outline crosses the line ``axis`` = ``v`` (0: x, 1: y): the other coordinate."""
    pts = _points(d)
    out = []
    for a, b in zip(pts, pts[1:], strict=False):
        lo, hi = sorted((a[axis], b[axis]))
        if lo <= v <= hi and hi > lo:
            t = (v - a[axis]) / (b[axis] - a[axis])
            out.append(a[1 - axis] + t * (b[1 - axis] - a[1 - axis]))
    return out


def _top_at(d: str, x: float) -> float:
    """The outline's highest point (smallest y) over ``x``."""
    return min(_crossings(d, x, 0))


def _front_at(d: str, y: float) -> float:
    """The outline's frontmost point (largest x) at height ``y``."""
    return max(_crossings(d, y, 1))


# --------------------------------------------------------------------------
# The kinds
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Kind:
    """One kind of shoe: its last, its sole unit and its cut.

    ``top`` is the collar's back top, ``instep`` where the vamp starts down to
    the toe (a pump's throat, a lace-up's tongue, a boot's ankle front).
    ``cut`` is ``pump`` (the topline dips to the throat), ``lace`` (it dips,
    then rises to the tongue) or ``boot`` (across the shaft top to ``front``,
    then down the shin). ``heel`` is how far the heel seat sits above the
    forefoot (a heel's height, or a sole unit's drop), ``sole`` the sole's
    thickness under the ball and ``spring`` how far the toe tip lifts.
    """

    top: float
    instep: tuple[float, float]
    cut: str
    heel: float
    heel_style: str  # stiletto | kitten | block | stacked | low | none
    sole: float
    sole_style: str  # leather | cup | midsole | lug | crepe | welly | soft | footbed
    toe: str  # point | almond | round | cap
    spring: float = 4.0
    front: float = 0.0  # a boot's shaft top front x


def _sy(k: Kind) -> tuple[float, float]:
    """(underside of the upper at the ball, at the heel seat)."""
    return G - k.sole, G - k.sole - k.heel


def _tip(k: Kind) -> tuple[float, float]:
    fy, _ = _sy(k)
    return XT, fy - k.spring - 2


def _under(k: Kind, dy: float = 0.0) -> str:
    """The upper's underside from the toe tip back to the heel (``dy`` lowers it)."""
    fy, by = _sy(k)
    fy, by = fy + dy, by + dy
    _, t = _tip(k)
    cmds = f"C{_pt(XT + 2, t + 6 + dy)} {_pt(XT - 40, fy)} {_pt(XT - 110, fy)}"
    if k.heel > 0:
        return f"{cmds} C{_pt(XB + 150, fy)} {_pt(XB + 110, by)} {_pt(XB + 52, by)} L{_pt(XB, by)}"
    return f"{cmds} L{_pt(XB + 18, fy)} Q{_pt(XB, fy)} {_pt(XB - 1, fy - 8)}"


def _vamp(k: Kind) -> str:
    """The vamp from the instep down to the toe tip, shaped by ``k.toe``."""
    xi, yi = k.instep
    x, t = _tip(k)
    span = x - xi
    if k.toe == "point":
        return f"C{_pt(xi + 0.45 * span, yi + 0.18 * (t - yi))} {_pt(x - 34, t - 12)} {_pt(x + 10, t)}"
    # the toe box: how tall the toe stands, which the vamp slopes down to
    box = t - {"almond": 30.0, "cap": 50.0, "wide": 52.0}.get(k.toe, 40.0)
    sink = max(0.0, box - yi)
    if k.toe == "almond":
        return f"C{_pt(xi + 0.45 * span, yi + 0.5 * sink)} {_pt(x - 40, box)} {_pt(x - 12, box + 6)} C{_pt(x + 2, box + 10)} {_pt(x + 5, t - 6)} {_pt(x, t)}"
    if k.toe == "cap":
        return f"C{_pt(xi + 0.3 * span, yi + 0.4 * sink)} {_pt(x - 50, box - 2)} {_pt(x - 18, box + 4)} C{_pt(x + 4, box + 12)} {_pt(x + 8, t - 10)} {_pt(x, t)}"
    return f"C{_pt(xi + 0.4 * span, yi + 0.55 * sink)} {_pt(x - 44, box)} {_pt(x - 16, box + 5)} C{_pt(x + 2, box + 10)} {_pt(x + 5, t - 8)} {_pt(x, t)}"


def _collar(k: Kind) -> str:
    """The collar line from the back top to the instep, by ``k.cut``."""
    xi, yi = k.instep
    if k.cut == "pump":
        return f"C{_pt(XB + 40, k.top + 12)} {_pt(xi - 50, yi + 6)} {_pt(xi, yi)}"
    if k.cut == "lace":
        dip = k.top + 14
        return f"C{_pt(XB + 30, dip)} {_pt(xi - 40, dip + 4)} {_pt(xi - 12, yi + 18)} Q{_pt(xi - 6, yi)} {_pt(xi, yi)}"
    return f"L{_pt(k.front, k.top + 2)} C{_pt(k.front - 2, k.top + (yi - k.top) * 0.55)} {_pt(xi - 30, yi - 20)} {_pt(xi, yi)}"


def _outline(k: Kind) -> str:
    """The whole upper: collar, vamp, underside, back of the heel."""
    _, by = _sy(k)
    rise = by - k.top
    xb = XB + 2
    back = (
        f"C{_pt(XB - 10, by - rise * 0.3)} {_pt(XB + 8, by - rise * 0.6)} {_pt(xb, k.top)}"
        if rise > 120
        else f"C{_pt(XB - 9, by - rise * 0.35)} {_pt(XB - 3, k.top + rise * 0.2)} {_pt(xb, k.top)}"
    )
    return f"M{_pt(xb, k.top)} {_collar(k)} {_vamp(k)} {_under(k)} {back} Z"
