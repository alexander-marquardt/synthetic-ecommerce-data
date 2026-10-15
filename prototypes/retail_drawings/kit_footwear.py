"""Side-view footwear drawings: ``shoe`` (seventeen kinds) and ``boot_sock`` (prototype for #125).

``shoe(paint, fill, label, kind, material, closure)`` draws one shoe from its
outer side, toe to the right, on the kit's 400 x 400 sheet. The record says
what to draw (:mod:`footwear_rows` puts all three in ``drawing.params``):

* ``kind`` is a key of :data:`KINDS`: the last (heel height, toe shape, shaft
  height and cut), the sole unit and the kind's own marks (a Chelsea boot's
  elastic gusset, a brogue's punching, a safety boot's toe cap). An unknown
  kind is a ``KeyError``, never a fallback drawing.
* ``material`` is one of :data:`footwear_rows.MATERIALS`. Its texture is drawn
  over the upper inside ``<g class="tex-<material>">``: suede and nubuck a
  matte nap, patent a hard gloss, canvas a weave, mesh open holes, leather,
  synthetic and rubber a soft sheen.
* ``closure`` is the record's closure attribute: laces, a zip, a buckle strap,
  hook-and-loop straps, an ankle strap, a slingback or a pull tab.

A heel block carries ``class="heel"`` (a flat or a sole unit has none), and
:func:`top` is the y of the collar's back top edge before the drawing is
centred, so a test can tell a shoe from an ankle boot from a knee boot
without parsing paths. Nothing is painted in the paper's color: a house style
changes the paper, so a gap is left as a gap.

Adding a kind: add a :class:`Kind` row to :data:`KINDS` (its ``cut`` picks the
collar line, see :func:`_outline`), draw its own marks in a ``_marks_<name>``
function listed in :data:`MARKS`, and point a column-4 entry of
:data:`footwear_rows.TYPES` at it. ``test_footwear.py`` draws every kind in
every material.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _mix, _path, _shade, _tint, register

__all__ = ["KINDS", "Fill", "Kind", "boot_sock", "shoe", "top"]

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
    box = t - {"almond": 30.0, "cap": 50.0}.get(k.toe, 40.0)
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


def top(kind: str) -> float:
    """The y of the collar's back top edge: smaller is a taller shaft."""
    return KINDS[kind].top


# --------------------------------------------------------------------------
# Soles and heels
# --------------------------------------------------------------------------


def _leather_sole(k: Kind, base: str) -> list[str]:
    """A dress sole: a thin welt-edged strip that follows the shank up to the heel seat."""
    x, t = _tip(k)
    edge = "#3b2f27" if _dark(base) else "#6e4a30"
    d = f"M{_pt(x + 1, t)} {_under(k)} L{_pt(XB - 1, _sy(k)[1] + k.sole)} {_reverse_under(k, k.sole)} Z"
    return [_path(d, edge, LW_DETAIL + 0.4)]


def _reverse_under(k: Kind, dy: float) -> str:
    """:func:`_under` lowered by ``dy`` and walked from the heel back to the toe."""
    fy, by = _sy(k)
    fy, by = fy + dy, by + dy
    x, t = _tip(k)
    toe = f"C{_pt(XT - 40, fy)} {_pt(XT + 6, t + 6)} {_pt(x + 1, t)}"
    if k.heel > 0:
        return f"L{_pt(XB + 52, by)} C{_pt(XB + 110, by)} {_pt(XB + 150, fy)} {_pt(XT - 110, fy)} {toe}"
    return f"L{_pt(XB + 18, fy)} L{_pt(XT - 110, fy)} {toe}"


def _unit_sole(k: Kind, base: str) -> list[str]:
    """A sole unit: it fills from the upper's underside to the ground and wraps the toe."""
    fy, by = _sy(k)
    x, t = _tip(k)
    color = {
        "cup": FOAM,
        "midsole": FOAM,
        "lug": RUBBER,
        "crepe": GUM,
        "welly": _shade(base, 0.45) if not _dark(base) else RUBBER,
        "soft": "#6f6156",
        "footbed": "#3a3330",
    }[k.sole_style]
    w = {"cup": 9, "midsole": 6, "lug": 8, "welly": 6}.get(k.sole_style, 3)
    d = (
        f"M{_pt(x + 4, t - w)} Q{_pt(x - 6, t - w + 4)} {_pt(x - 40, fy - w * 0.5)} "
        f"C{_pt(x - 110, fy - w * 0.4)} {_pt(XB + 150, by - w * 0.3)} {_pt(XB + 70, by - w)} "
        f"L{_pt(XB - 5, by - w)} L{_pt(XB - 5, G - 6)} Q{_pt(XB - 4, G)} {_pt(XB + 8, G)} "
        f"L{_pt(x - 80, G)} C{_pt(x - 30, G)} {_pt(x + 10, t + 6)} {_pt(x + 4, t - w)} Z"
    )
    out = [_path(d, color, LW)]
    s = k.sole_style
    if s == "cup":
        out += [
            _line(f"M{_pt(XB - 4, G - 11)} L{_pt(x - 70, G - 11)} Q{_pt(x - 24, G - 11)} {_pt(x + 4, t + 2)}", 1.3),
            _line(f"M{_pt(XB - 1, by - w + 6)} L{_pt(XB + 70, by - w + 6)} C{_pt(XB + 150, by - 1)} {_pt(x - 110, fy - 1)} {_pt(x - 40, fy - 1)}", 1.4, ' stroke-dasharray="1.5 3.5"', "#8f8a80"),
        ]
    elif s == "midsole":
        unit = f"M{_pt(XB + 6, G - 32)} Q{_pt(XB + 6, G - 44)} {_pt(XB + 20, G - 44)} L{_pt(XB + 84, G - 42)} Q{_pt(XB + 96, G - 41)} {_pt(XB + 96, G - 30)} L{_pt(XB + 96, G - 20)} L{_pt(XB + 6, G - 20)} Z"
        ribs = " ".join(f"M{_pt(XB + 18 + 12 * i, G - 41)} L{_pt(XB + 18 + 12 * i, G - 22)}" for i in range(7))
        tread = " ".join(f"M{_pt(XB + 6 + 20 * i, G - 1)} L{_pt(XB + 15 + 20 * i, G - 8)}" for i in range(12))
        out += [
            _path(f"M{_pt(XB - 4, G - 10)} L{_pt(x - 80, G - 10)} C{_pt(x - 40, G - 10)} {_pt(x - 6, t + 4)} {_pt(x + 6, t)} C{_pt(x + 10, t + 10)} {_pt(x - 30, G)} {_pt(x - 80, G)} L{_pt(XB + 8, G)} Q{_pt(XB - 4, G)} {_pt(XB - 4, G - 10)} Z", "#3b3d44", LW_DETAIL),
            _line(tread, 1.2, "", "#7a7d86"),
            _path(unit, "#cfe0ee", LW_DETAIL),
            _line(ribs, 2.2, "", "#8fb0cc"),
            _line(f"M{_pt(XB + 110, by - 3)} C{_pt(XB + 170, fy - 22)} {_pt(x - 120, fy + 2)} {_pt(x - 60, fy - 2)}", 1.4),
        ]
    elif s in ("lug", "welly"):
        lugs = " ".join(f"M{_pt(px, G)} L{_pt(px, G - 8)} L{_pt(px + 12, G - 8)} L{_pt(px + 12, G)}" for px in range(int(XB + 4), int(x - 70), 20))
        out.append(_line(lugs, 1.6, "", TREAD))
        if s == "lug":
            band = AMBER if k.toe == "cap" else "#9a9da4"
            mid = (
                f"M{_pt(XB - 5, by - w + 2)} L{_pt(XB + 70, by - w + 2)} C{_pt(XB + 150, by - w * 0.3 + 2)} {_pt(x - 110, fy - w * 0.4 + 2)} {_pt(x - 40, fy - w * 0.5 + 2)} "
                f"Q{_pt(x - 6, t - w + 6)} {_pt(x + 5, t - w + 3)} L{_pt(x + 7, t + 4)} Q{_pt(x - 6, t + 8)} {_pt(x - 40, fy + 7)} "
                f"C{_pt(x - 110, fy + 8)} {_pt(XB + 150, by + 8)} {_pt(XB + 70, by + 6)} L{_pt(XB - 5, by + 6)} Z"
            )
            out.append(_path(mid, band, LW_DETAIL))
    elif s == "crepe":
        specks = " ".join(f"M{_pt(XB + 6 + 9 * i, G - 3 - (i * 7) % 10)} l1,0" for i in range(31))
        out.append(_line(specks, 2.2, "", "#a77a42"))
    elif s == "soft":
        out.append(_line(f"M{_pt(XB + 2, by - 1)} L{_pt(x - 40, fy - 1)}", 1.4, ' stroke-dasharray="4 3"', "#d8cfc4"))
    return out


def _sole(k: Kind, base: str) -> list[str]:
    return _leather_sole(k, base) if k.sole_style == "leather" else _unit_sole(k, base)


def _heel(k: Kind, paint: str, base: str) -> list[str]:
    """The heel block under the seat (``class="heel"``), or nothing for a flat or a sole unit."""
    _, by = _sy(k)
    seat = by + k.sole - 1
    style = k.heel_style
    if style == "none":
        return []
    fill = paint
    if style == "stiletto":
        d = f"M{_pt(XB - 1, seat)} C{_pt(XB + 6, seat + 40)} {_pt(XB + 18, G - 30)} {_pt(XB + 19, G - 5)} L{_pt(XB + 29, G - 5)} C{_pt(XB + 29, G - 34)} {_pt(XB + 32, seat + 22)} {_pt(XB + 50, seat)} Z"
        lift = f"M{_pt(XB + 19, G - 5)} L{_pt(XB + 19, G)} L{_pt(XB + 29, G)} L{_pt(XB + 29, G - 5)} Z"
    elif style == "kitten":
        d = f"M{_pt(XB, seat)} C{_pt(XB + 4, seat + 14)} {_pt(XB + 16, G - 14)} {_pt(XB + 14, G - 4)} L{_pt(XB + 25, G - 4)} C{_pt(XB + 25, G - 16)} {_pt(XB + 30, seat + 8)} {_pt(XB + 46, seat)} Z"
        lift = f"M{_pt(XB + 14, G - 4)} L{_pt(XB + 14, G)} L{_pt(XB + 25, G)} L{_pt(XB + 25, G - 4)} Z"
    elif style == "block":
        d = f"M{_pt(XB - 1, seat)} L{_pt(XB + 6, G - 6)} L{_pt(XB + 44, G - 6)} L{_pt(XB + 51, seat)} Z"
        lift = f"M{_pt(XB + 6, G - 6)} L{_pt(XB + 6, G)} L{_pt(XB + 44, G)} L{_pt(XB + 44, G - 6)} Z"
    else:  # stacked, low: a leather stack with its layers showing
        fill = "#6b4a33" if style == "stacked" else ("#3b2f27" if _dark(base) else "#6e4a30")
        d = f"M{_pt(XB - 2, seat)} L{_pt(XB + 1, G - 5)} L{_pt(XB + 47, G - 5)} L{_pt(XB + 51, seat)} Z"
        lift = f"M{_pt(XB + 1, G - 5)} L{_pt(XB + 1, G)} L{_pt(XB + 47, G)} L{_pt(XB + 47, G - 5)} Z"
        n = max(1, int((G - 5 - seat) // 8))
        layers = " ".join(f"M{_pt(XB + 1, seat + (G - 5 - seat) * i / (n + 1))} L{_pt(XB + 48, seat + (G - 5 - seat) * i / (n + 1))}" for i in range(1, n + 1))
        return [f'<g class="heel">{_path(d, fill, LW)}{_line(layers, 1.1, "", _tint(fill, 0.35))}{_path(lift, RUBBER, LW_DETAIL)}</g>']
    return [f'<g class="heel">{_path(d, fill, LW)}{_path(lift, RUBBER, LW_DETAIL)}</g>']


# --------------------------------------------------------------------------
# Textures: what the upper is made of
# --------------------------------------------------------------------------


def _sheen(k: Kind) -> str:
    """A highlight line along the toe box, just inside the vamp."""
    xi, yi = k.instep
    x, t = _tip(k)
    return f"M{_pt(xi + 0.35 * (x - xi), yi + 0.2 * (t - yi) + 8)} C{_pt(xi + 0.6 * (x - xi), yi + 0.28 * (t - yi) + 8)} {_pt(x - 24, yi + 0.45 * (t - yi) + 4)} {_pt(x - 10, yi + 0.66 * (t - yi))}"


def _texture(material: str, area: str, base: str, k: Kind, uid: str) -> list[str]:
    """The material's surface over ``area``, in ``<g class="tex-<material>">``."""
    pid = f"tex-{uid}"
    defs = ""
    body: list[str] = []
    light, dark = _tint(base, 0.6), _shade(base, 0.5)
    if material in ("suede", "nubuck"):
        # a nap of specks, light and dark, scattered over a 7 px tile so no grid shows
        r, op = (0.75, 0.55) if material == "suede" else (0.45, 0.4)
        specks = ((0.8, 1.2, dark), (4.6, 0.6, light), (2.9, 3.4, dark), (6.1, 4.2, light), (1.6, 5.8, light), (5.0, 6.4, dark))
        defs = (
            f'<pattern id="{pid}" width="7" height="7" patternUnits="userSpaceOnUse">'
            + "".join(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r}" fill="{c}" opacity="{op}"/>' for cx, cy, c in specks)
            + "</pattern>"
        )
        body.append(f'<path d="{area}" fill="url(#{pid})" stroke="none"/>')
    elif material == "canvas":
        defs = (
            f'<pattern id="{pid}" width="4" height="4" patternUnits="userSpaceOnUse">'
            f'<path d="M0,1 L4,1" stroke="{dark}" stroke-width="1" opacity=".3"/>'
            f'<path d="M3,0 L3,4" stroke="{dark}" stroke-width="1" opacity=".25"/>'
            "</pattern>"
        )
        body.append(f'<path d="{area}" fill="url(#{pid})" stroke="none"/>')
    elif material == "mesh":
        hole = _tint(base, 0.35) if _dark(base) else _shade(base, 0.35)
        defs = (
            f'<pattern id="{pid}" width="7" height="6" patternUnits="userSpaceOnUse">'
            f'<ellipse cx="1.8" cy="1.6" rx="1.5" ry="1.2" fill="{hole}"/>'
            f'<ellipse cx="5.3" cy="4.6" rx="1.5" ry="1.2" fill="{hole}"/>'
            "</pattern>"
        )
        body.append(f'<path d="{area}" fill="url(#{pid})" stroke="none"/>')
    elif material == "patent":
        xi, yi = k.instep
        body += [
            _highlight(_sheen(k), 6, 0.9),
            _highlight(f"M{_pt(XB + 10, k.top + 14)} C{_pt(XB + 6, k.top + 30)} {_pt(XB + 10, _sy(k)[1] - 14)} {_pt(XB + 24, _sy(k)[1] - 8)}", 3.5, 0.7),
            _highlight(f"M{_pt(xi - 70, yi + 2)} Q{_pt(xi - 40, yi + 10)} {_pt(xi - 10, yi + 14)}", 2.5, 0.6),
        ]
    elif material == "rubber":
        body += [
            _highlight(f"M{_pt(XB + 20, k.top + 18)} C{_pt(XB + 16, k.top + 90)} {_pt(XB + 20, _sy(k)[1] - 60)} {_pt(XB + 28, _sy(k)[1] - 34)}", 9, 0.3),
            _highlight(_sheen(k), 6, 0.35),
        ]
    else:  # leather, synthetic: a soft sheen on the toe
        body.append(_highlight(_sheen(k), 4, 0.4 if material == "leather" else 0.25))
    head = f"<defs>{defs}</defs>" if defs else ""
    return [f'<g class="tex-{material}">{head}{"".join(body)}</g>']


# --------------------------------------------------------------------------
# Closures
# --------------------------------------------------------------------------


#: The lace colour a record names (its ``lace`` drawing param), set while one shoe is drawn
#: (gen#326: "Dress for Success Oxford, red laces" shows red laces on a black shoe).
_LACE_OVERRIDE: list[str] = [""]


def _laces(eyelets: list[tuple[float, float]], lace: str, reach: tuple[float, float] = (10, -9)) -> list[str]:
    """Eyelets and the lace bars that cross from each one to the far side."""
    lace = _LACE_OVERRIDE[0] or lace
    dx, dy = reach
    bars = " ".join(f"M{_pt(x, y)} L{_pt(x + dx, y + dy)}" for x, y in eyelets)
    holes = "".join(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="3" fill="{METAL}" stroke="{INK}" stroke-width="1"/>' for x, y in eyelets)
    return [_line(bars, 5.5), _line(bars, 3, "", lace), holes]


def _bow(x: float, y: float, lace: str) -> list[str]:
    lace = _LACE_OVERRIDE[0] or lace
    d = f"M{_pt(x, y)} C{_pt(x - 14, y - 16)} {_pt(x - 24, y - 2)} {_pt(x, y)} C{_pt(x + 12, y - 20)} {_pt(x + 24, y - 6)} {_pt(x, y)} M{_pt(x, y)} Q{_pt(x - 10, y + 10)} {_pt(x - 6, y + 22)} M{_pt(x, y)} Q{_pt(x + 8, y + 12)} {_pt(x + 8, y + 22)}"
    return [_line(d, 5), _line(d, 2.6, "", lace)]


def _stitch(d: str, base: str) -> str:
    return _line(d, 1.2, ' stroke-dasharray="3 2.5"', _detail(base))


def _tab(x: float, y: float, color: str, h: float = 18) -> str:
    """A pull loop standing up from the collar."""
    return _path(f"M{_pt(x - 6, y + 8)} L{_pt(x - 6, y - h)} Q{_pt(x + 2, y - h - 9)} {_pt(x + 10, y - h)} L{_pt(x + 10, y + 8)}", color, LW_DETAIL)


def _velcro(x0: float, y0: float, x1: float, y1: float, base: str) -> list[str]:
    """A hook-and-loop strap across the instep, its tab end showing."""
    d = f"M{_pt(x0, y0)} L{_pt(x1, y1)} Q{_pt(x1 + 8, y1 + 8)} {_pt(x1 + 2, y1 + 17)} L{_pt(x0 + 2, y0 + 16)} Z"
    return [_path(d, _trim(base, 0.3), LW_DETAIL), _stitch(f"M{_pt(x0 + 5, y0 + 4)} L{_pt(x1 - 2, y1 + 4)} L{_pt(x1 - 1, y1 + 12)} L{_pt(x0 + 5, y0 + 12)} Z", _trim(base, 0.3))]


def _lining(k: Kind, end: tuple[float, float], lift: float = 8.0) -> str:
    """The far side's collar seen over the near one: a sliver of lining above the topline."""
    x0, y0 = XB + 2, k.top
    x1, y1 = end
    d = f"M{_pt(x0, y0)} C{_pt(x0 + 40, y0 - lift)} {_pt(x1 - 40, y1 - lift)} {_pt(x1, y1)} C{_pt(x1 - 40, y1 - 2)} {_pt(x0 + 40, y0 + 6)} {_pt(x0, y0)} Z"
    return _path(d, LINING, LW_DETAIL)


# --------------------------------------------------------------------------
# Each kind's own marks
# --------------------------------------------------------------------------


def _marks_pump(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    out: list[str] = []
    if closure == "Ankle Strap":
        ay = k.top - 30
        out += [
            _path(f"M{_pt(XB + 2, k.top + 6)} L{_pt(XB + 2, ay + 4)} L{_pt(XB + 15, ay + 4)} L{_pt(XB + 15, k.top + 6)} Z", paint, LW_DETAIL),
            _path(f"M{_pt(XB - 8, ay)} C{_pt(XB + 40, ay - 8)} {_pt(XB + 90, ay - 6)} {_pt(XB + 124, ay + 6)} L{_pt(XB + 122, ay + 17)} C{_pt(XB + 90, ay + 6)} {_pt(XB + 40, ay + 4)} {_pt(XB - 8, ay + 12)} Z", paint, LW_DETAIL),
            f'<rect x="{_f(XB + 92)}" y="{_f(ay - 5)}" width="14" height="21" rx="2" fill="none" stroke="{BRASS}" stroke-width="3"/>',
        ]
    return out


def _marks_ballet(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    xi, yi = k.instep
    trim = _tint(base, 0.55) if _dark(base) else _shade(base, 0.35)
    x, y = xi - 8, yi + 2
    return [
        _line(f"M{_pt(XB + 4, k.top + 3)} C{_pt(XB + 40, k.top + 15)} {_pt(xi - 50, yi + 9)} {_pt(xi, yi + 3)}", 3, "", trim),
        _path(f"M{_pt(x, y)} C{_pt(x - 26, y - 22)} {_pt(x - 34, y + 14)} {_pt(x, y)} C{_pt(x + 26, y - 22)} {_pt(x + 34, y + 14)} {_pt(x, y)} Z", trim, LW_DETAIL),
        _path(f"M{_pt(x - 3, y + 2)} L{_pt(x - 12, y + 20)} L{_pt(x - 5, y + 18)} Z M{_pt(x + 3, y + 2)} L{_pt(x + 13, y + 19)} L{_pt(x + 6, y + 18)} Z", trim, LW_DETAIL),
        f'<circle cx="{_f(x)}" cy="{_f(y)}" r="4.5" fill="{trim}" stroke="{INK}" stroke-width="1.2"/>',
    ]


def _marks_loafer(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    xi, yi = k.instep
    fy, _ = _sy(k)
    det = _detail(base)
    apron = f"M{_pt(xi - 22, yi + 6)} C{_pt(xi - 6, yi + 22)} {_pt(xi + 50, yi + 26)} {_pt(XT - 36, fy - 38)}"
    sx = xi - 30
    saddle = f"M{_pt(sx, _top_at(outline, sx) - 1)} L{_pt(sx + 34, _top_at(outline, sx + 34) - 1)} L{_pt(sx + 28, fy - 26)} L{_pt(sx - 4, fy - 30)} Z"
    return [
        _path(saddle, _trim(base, 0.25), LW_DETAIL),
        f'<path d="M{_pt(sx + 6, fy - 46)} Q{_pt(sx + 15, fy - 54)} {_pt(sx + 24, fy - 46)} Q{_pt(sx + 15, fy - 40)} {_pt(sx + 6, fy - 46)} Z" fill="{_shade(base, 0.5)}" stroke="{det}" stroke-width="1.2"/>',
        _line(apron, 2, "", det),
        _stitch(f"M{_pt(xi - 14, yi + 6)} C{_pt(xi + 2, yi + 16)} {_pt(xi + 50, yi + 18)} {_pt(XT - 40, fy - 44)}", base),
    ]


def _marks_brogue(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    xi, yi = k.instep
    fy, _ = _sy(k)
    det = _detail(base)
    cap_top = _top_at(outline, XT - 92)
    wing = f"M{_pt(XT - 92, cap_top + 2)} C{_pt(XT - 120, fy - 30)} {_pt(XB + 150, fy - 20)} {_pt(XB + 110, fy - 2)}"
    toecap = f"M{_pt(XT - 92, cap_top + 2)} C{_pt(XT - 70, cap_top + 20)} {_pt(XT - 40, cap_top + 30)} {_pt(XT - 34, fy - 2)}"
    quarter = f"M{_pt(xi + 6, yi + 6)} C{_pt(xi + 2, fy - 50)} {_pt(XB + 50, fy - 34)} {_pt(XB + 34, fy - 2)}"
    holes = _tint(base, 0.6) if _dark(base) else _shade(base, 0.6)
    dots = " ".join(f"M{_pt(px, py + 4)} l0.1,0" for px, py in _every(_points(wing) + _points(toecap) + _points(quarter), 6))
    out = [_line(wing, 2, "", det), _line(toecap, 2, "", det), _line(quarter, 2, "", det), _line(dots, 2.8, "", holes)]
    medallion = " ".join(f"M{_pt(XT - 30 + 7 * dx, fy - 22 + 6 * dy)} l0.1,0" for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)))
    out.append(_line(medallion, 2.6, "", holes))
    if closure == "Hook & Loop":
        out += _velcro(xi - 20, _top_at(outline, xi - 20) - 2, xi + 40, _top_at(outline, xi + 40) - 1, base)
    else:
        eye = [(xi + 4 + 11 * i, _top_at(outline, xi + 4 + 11 * i) + 9) for i in range(4)]
        out += _laces(eye, "#e8e2d6" if _dark(base) else "#3b2f27", (8, -8))
    return out


def _marks_sport(k: Kind, outline: str, paint: str, base: str, closure: str, running: bool) -> list[str]:
    xi, yi = k.instep
    fy, by = _sy(k)
    x0 = xi + 2
    xs = [x0 + 16 * i for i in range(5)]
    stay = [(px, _top_at(outline, px)) for px in range(int(x0 - 4), int(xs[-1] + 18), 4)]
    edge = " ".join(f"{'M' if i == 0 else 'L'}{_pt(px, py)}" for i, (px, py) in enumerate(stay))
    back = " ".join(f"L{_pt(px, py + 22)}" for px, py in reversed(stay))
    out = [_path(f"{edge} {back} Z", _trim(base, 0.18) if not running else _tint(base, 0.3), LW_DETAIL)]
    if running:
        sweep = f"M{_pt(XB + 24, fy - 4)} C{_pt(XB + 90, fy - 16)} {_pt(xi - 10, yi + 50)} {_pt(xs[-1] + 4, _top_at(outline, xs[-1] + 4) + 24)} L{_pt(xs[-1] + 8, _top_at(outline, xs[-1] + 8) + 36)} C{_pt(xi + 10, yi + 66)} {_pt(XB + 110, fy - 6)} {_pt(XB + 40, fy + 2)} Z"
        out += [
            _path(sweep, _tint(base, 0.7) if _dark(base) else _shade(base, 0.45), LW_DETAIL),
            _path(f"M{_pt(XB - 6, by - 26)} Q{_pt(XB + 32, by - 38)} {_pt(XB + 56, by - 8)} L{_pt(XB - 6, by - 6)} Z", _shade(base, 0.3), LW_DETAIL),
            _tab(XB + 6, k.top + 2, "#e25b2a", 14),
        ]
    else:
        out += [
            _path(f"M{_pt(XT - 58, fy + 2)} C{_pt(XT - 58, fy - 28)} {_pt(XT - 20, fy - 34)} {_pt(XT + 3, fy - 16)} L{_pt(XT + 3, fy + 2)} Z", FOAM, LW_DETAIL),
            _tab(XB + 6, k.top + 2, _trim(base, 0.25), 12),
            _stitch(f"M{_pt(XB + 4, fy - 14)} C{_pt(XB + 60, fy - 16)} {_pt(xi - 20, fy - 20)} {_pt(XT - 60, fy - 16)}", base),
        ]
    if closure == "Hook & Loop":
        for px in (xi + 6, xi + 40):
            out += _velcro(px - 26, _top_at(outline, px - 26) + 2, px + 18, _top_at(outline, px + 18) - 2, base)
    else:
        eye = [(px, _top_at(outline, px) + 14) for px in xs]
        out += _laces(eye, "#ffffff" if _dark(base) else "#f1efe8", (12, -8))
    return out


def _marks_trainer(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    return _marks_sport(k, outline, paint, base, closure, running=False)


def _marks_running(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    return _marks_sport(k, outline, paint, base, closure, running=True)


def _marks_slipper(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    xi, _ = k.instep
    fy, _ = _sy(k)
    n = int((xi - XB) // 13)
    fluff = " ".join(f"M{_pt(XB + 3 + 13 * i, _top_at(outline, XB + 3 + 13 * i) + 2)} q6.5,-13 13,0" for i in range(n))
    return [
        _line(fluff, 13, "", "#efe6d6"),
        _line(fluff, 1.2, ' stroke-opacity=".6"'),
        _stitch(f"M{_pt(XB + 4, fy - 9)} L{_pt(XT - 34, fy - 9)}", base),
        _stitch(f"M{_pt(xi + 2, _top_at(outline, xi + 2) + 8)} C{_pt(xi + 40, _top_at(outline, xi + 40) + 8)} {_pt(XT - 40, fy - 40)} {_pt(XT - 16, fy - 20)}", base),
    ]


def _zip(k: Kind, x: float, bottom: float, base: str) -> list[str]:
    return [
        _line(f"M{_pt(x, k.top + 4)} L{_pt(x + 3, bottom)}", 4.5, "", _trim(base, 0.4)),
        _line(f"M{_pt(x, k.top + 4)} L{_pt(x + 3, bottom)}", 1.4, ' stroke-dasharray="1.6 1.6"', METAL),
        f'<rect x="{_f(x - 4)}" y="{_f(k.top + 6)}" width="8" height="18" rx="3" fill="{METAL}" stroke="{INK}" stroke-width="1"/>',
    ]


def _marks_ankle_boot(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    fy, _ = _sy(k)
    return [*_zip(k, XB + 24, fy - 56, base), _stitch(f"M{_pt(XB + 6, fy - 14)} C{_pt(140, fy - 12)} {_pt(220, fy - 8)} {_pt(XT - 30, fy - 8)}", base)]


def _marks_knee_boot(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    fy, _ = _sy(k)
    return [*_zip(k, XB + 20, fy - 70, base), _stitch(f"M{_pt(XB + 6, fy - 14)} C{_pt(140, fy - 12)} {_pt(220, fy - 8)} {_pt(XT - 30, fy - 8)}", base)]


def _marks_chelsea(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    fy, _ = _sy(k)
    gx = XB + 76
    gus = f"M{_pt(gx - 32, _top_at(outline, gx - 32) + 1)} Q{_pt(gx - 10, k.top + 70)} {_pt(gx, k.top + 96)} Q{_pt(gx + 10, k.top + 70)} {_pt(gx + 32, _top_at(outline, gx + 32) + 1)} Z"
    ribs = " ".join(f"M{_pt(gx - 27 + 6 * i, k.top + 6)} L{_pt(gx + (i - 4.5) * 1.6, k.top + 50 + (4.5 - abs(i - 4.5)) * 9)}" for i in range(10))
    elastic = "#4a4a50" if not _dark(base) else "#5c5c63"
    return [
        _path(gus, elastic, LW_DETAIL),
        _line(ribs, 1.0, "", "#8d8d94"),
        _tab(XB + 10, k.top + 2, _trim(base, 0.2), 16),
        _tab(k.front - 12, k.top + 4, _trim(base, 0.2), 14),
        _stitch(f"M{_pt(XB + 6, fy - 16)} C{_pt(140, fy - 14)} {_pt(220, fy - 10)} {_pt(XT - 30, fy - 10)}", base),
    ]


def _boot_laces(k: Kind, outline: str, n: int, lace: str, first: float = 22) -> list[str]:
    _, yi = k.instep
    ys = [k.top + first + (yi - 14 - k.top - first) * i / (n - 1) for i in range(n)]
    eye = [(_front_at(outline, py) - 13, py) for py in ys]
    return _laces(eye, lace, (11, -6))


def _marks_chukka(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    xi, yi = k.instep
    fy, _ = _sy(k)
    seam = f"M{_pt(k.front - 26, k.top + 4)} C{_pt(k.front - 30, yi - 30)} {_pt(xi - 20, fy - 30)} {_pt(xi + 6, fy - 2)}"
    lace = "#7a5236"
    out = [_line(seam, 1.8, "", _detail(base)), _stitch(seam.replace(f"M{_pt(k.front - 26, k.top + 4)}", f"M{_pt(k.front - 32, k.top + 4)}"), base)]
    out += _boot_laces(k, outline, 3, lace, 18)
    out += _bow(_front_at(outline, k.top + 18) - 6, k.top + 14, lace)
    return out


def _hiker(k: Kind, outline: str, base: str, collar: str, lace: str) -> list[str]:
    xi, yi = k.instep
    fy, by = _sy(k)
    pad = f"M{_pt(XB - 3, k.top + 2)} C{_pt(XB + 30, k.top - 10)} {_pt(k.front - 50, k.top - 6)} {_pt(k.front - 18, k.top + 2)} L{_pt(k.front - 18, k.top + 18)} C{_pt(k.front - 50, k.top + 12)} {_pt(XB + 30, k.top + 10)} {_pt(XB - 1, k.top + 26)} Z"
    counter = f"M{_pt(XB - 6, fy - 46)} Q{_pt(XB + 44, fy - 52)} {_pt(XB + 74, fy - 6)} L{_pt(XB - 4, by - 4)} Z"
    out = [_path(pad, collar, LW_DETAIL), _path(counter, collar, LW_DETAIL), _tab(XB + 8, k.top - 2, collar, 14)]
    out += _boot_laces(k, outline, 5, lace)
    hooks = "".join(f'<path d="M{_pt(_front_at(outline, k.top + 22 + 14 * i) - 16, k.top + 22 + 14 * i - 3)} q7,-7 11,1" fill="none" stroke="{METAL}" stroke-width="2.4"/>' for i in range(2))
    out.append(hooks)
    return out


def _marks_walking_boot(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    fy, _ = _sy(k)
    rand = f"M{_pt(XT - 96, fy + 2)} C{_pt(XT - 70, fy - 22)} {_pt(XT - 30, fy - 30)} {_pt(XT + 4, fy - 20)} L{_pt(XT + 4, fy + 2)} Z"
    return [_path(rand, RUBBER, LW_DETAIL), *_hiker(k, outline, base, _shade(base, 0.35), "#d9a441")]


def _marks_safety_boot(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    fy, _ = _sy(k)
    x, t = _tip(k)
    cap_top = _top_at(outline, XT - 50)
    cap = f"M{_pt(XT - 96, fy + 2)} C{_pt(XT - 96, cap_top + 30)} {_pt(XT - 70, cap_top + 2)} {_pt(XT - 34, cap_top + 2)} Q{_pt(x + 8, cap_top + 8)} {_pt(x + 6, t)} L{_pt(XT - 96, fy + 2)} Z"
    return [
        _path(cap, "#4a4c53", LW),
        _stitch(f"M{_pt(XT - 88, fy - 2)} C{_pt(XT - 88, cap_top + 34)} {_pt(XT - 66, cap_top + 10)} {_pt(XT - 34, cap_top + 10)}", "#4a4c53"),
        _highlight(f"M{_pt(XT - 66, cap_top + 14)} Q{_pt(XT - 34, cap_top + 4)} {_pt(XT - 10, cap_top + 20)}", 3.5, 0.55),
        *_hiker(k, outline, base, "#3a3b40" if _dark(base) else _shade(base, 0.4), AMBER),
    ]


def _marks_welly(k: Kind, outline: str, paint: str, base: str, closure: str) -> list[str]:
    xi, yi = k.instep
    fy, by = _sy(k)
    band = f"M{_pt(XB - 6, fy - 30)} C{_pt(XB + 120, fy - 30)} {_pt(xi + 10, fy - 32)} {_pt(XT + 3, fy - 26)} L{_pt(XT + 4, fy + 2)} L{_pt(XB - 6, fy + 2)} Z"
    bx = XB + 70
    trim = _shade(base, 0.35) if not _dark(base) else _tint(base, 0.2)
    return [
        _path(band, trim, LW_DETAIL),
        _path(f"M{_pt(bx, k.top + 3)} L{_pt(bx + 16, k.top + 3)} L{_pt(bx + 16, k.top + 58)} L{_pt(bx, k.top + 58)} Z", trim, LW_DETAIL),
        f'<rect x="{_f(bx - 3)}" y="{_f(k.top + 36)}" width="22" height="14" rx="2" fill="none" stroke="{METAL}" stroke-width="3"/>',
        _path(f"M{_pt(XB - 4, by - 18)} L{_pt(XB - 18, by - 12)} L{_pt(XB - 16, by - 2)} L{_pt(XB - 4, by - 4)} Z", trim, LW_DETAIL),
    ]


#: kind -> its own marks (closures and seams). A kind not listed draws none.
MARKS: dict[str, Callable[..., list[str]]] = {
    "court": _marks_pump,
    "kitten": _marks_pump,
    "block_heel": _marks_pump,
    "ballet": _marks_ballet,
    "loafer": _marks_loafer,
    "brogue": _marks_brogue,
    "trainer": _marks_trainer,
    "running": _marks_running,
    "slipper": _marks_slipper,
    "ankle_boot": _marks_ankle_boot,
    "knee_boot": _marks_knee_boot,
    "chelsea": _marks_chelsea,
    "chukka": _marks_chukka,
    "walking_boot": _marks_walking_boot,
    "safety_boot": _marks_safety_boot,
    "welly": _marks_welly,
}


# --------------------------------------------------------------------------
# Open shoes: a slingback's vamp, a sandal's straps
# --------------------------------------------------------------------------


def _footbed(k: Kind, to_x: float) -> str:
    """The insole seen from the side, from the heel to ``to_x``: what an open back shows."""
    fy, by = _sy(k)
    return f"M{_pt(XB - 1, by - 4)} L{_pt(XB + 52, by - 4)} C{_pt(XB + 110, by - 4)} {_pt(XB + 150, fy - 4)} {_pt(to_x, fy - 4)} L{_pt(to_x, fy + 1)} C{_pt(XB + 150, fy + 1)} {_pt(XB + 110, by + 1)} {_pt(XB + 52, by + 1)} L{_pt(XB - 1, by + 1)} Z"


def _slingback(k: Kind) -> tuple[str, list[str]]:
    """A slingback upper: the vamp alone (its back edge cut at the waist) and the strap round the heel."""
    xi, yi = k.instep
    fy, by = _sy(k)
    x, t = _tip(k)
    cx = xi - 40
    vamp = f"M{_pt(cx, fy - 2)} C{_pt(cx - 4, yi + 30)} {_pt(xi - 30, yi + 2)} {_pt(xi, yi)} {_vamp(k)} C{_pt(XT + 2, t + 6)} {_pt(XT - 40, fy)} {_pt(XT - 110, fy)} L{_pt(cx, fy)} Z"
    strap = f"M{_pt(XB - 3, by - 32)} C{_pt(XB + 40, by - 42)} {_pt(cx - 40, yi + 22)} {_pt(cx + 6, yi + 18)} L{_pt(cx + 6, yi + 28)} C{_pt(cx - 40, yi + 32)} {_pt(XB + 40, by - 30)} {_pt(XB - 3, by - 22)} Z"
    return vamp, [_path(_footbed(k, cx + 4), LINING, LW_DETAIL), _path(strap, "{paint}", LW_DETAIL), f'<rect x="{_f(XB + 36)}" y="{_f(by - 42)}" width="9" height="14" rx="2" fill="none" stroke="{BRASS}" stroke-width="2.4"/>']


def _sandal(k: Kind, paint: str, base: str, closure: str, material: str, uid: str) -> list[str]:
    fy, by = _sy(k)
    bed = f"M{_pt(XB - 2, by - 10)} C{_pt(XB + 120, by - 12)} {_pt(XT - 120, fy - 12)} {_pt(XT - 8, fy - 12)} Q{_pt(XT + 8, fy - 9)} {_pt(XT + 2, fy + 1)} L{_pt(XB - 2, fy + 1)} Z"
    straps: list[str] = []
    if closure == "Slip-On":
        straps += [
            f"M{_pt(146, fy - 8)} C{_pt(152, fy - 82)} {_pt(246, fy - 82)} {_pt(252, fy - 10)} L{_pt(226, fy - 10)} C{_pt(222, fy - 54)} {_pt(176, fy - 56)} {_pt(172, fy - 8)} Z",
            f"M{_pt(238, fy - 10)} C{_pt(246, fy - 62)} {_pt(316, fy - 58)} {_pt(324, fy - 12)} L{_pt(302, fy - 12)} C{_pt(296, fy - 40)} {_pt(264, fy - 42)} {_pt(260, fy - 10)} Z",
        ]
    else:
        ay = by - 78
        straps += [
            f"M{_pt(XB + 2, by - 10)} C{_pt(XB - 2, by - 44)} {_pt(XB, ay + 24)} {_pt(XB + 8, ay)} L{_pt(XB + 26, ay)} C{_pt(XB + 20, ay + 24)} {_pt(XB + 20, by - 44)} {_pt(XB + 28, by - 10)} Z",
            f"M{_pt(XB + 2, ay - 2)} C{_pt(XB + 60, ay - 8)} {_pt(170, ay + 8)} {_pt(200, ay + 22)} L{_pt(194, ay + 38)} C{_pt(160, ay + 26)} {_pt(XB + 60, ay + 12)} {_pt(XB + 2, ay + 16)} Z",
            f"M{_pt(168, fy - 10)} C{_pt(172, fy - 60)} {_pt(196, ay + 34)} {_pt(202, ay + 26)} L{_pt(216, ay + 36)} C{_pt(208, fy - 54)} {_pt(196, fy - 32)} {_pt(196, fy - 10)} Z",
            f"M{_pt(244, fy - 11)} C{_pt(256, fy - 60)} {_pt(314, fy - 58)} {_pt(324, fy - 13)} L{_pt(300, fy - 13)} C{_pt(294, fy - 40)} {_pt(270, fy - 40)} {_pt(268, fy - 11)} Z",
        ]
    out = [_path(bed, "#c9a77c", LW_DETAIL), _line(f"M{_pt(XB + 4, by - 6)} C{_pt(XB + 120, by - 8)} {_pt(XT - 120, fy - 8)} {_pt(XT - 10, fy - 8)}", 1.0, ' stroke-opacity=".5"')]
    out += [_path(d, paint, LW) for d in straps]
    out += _texture(material, " ".join(straps), base, k, uid)
    ay = by - 78
    if closure == "Buckle":
        out.append(f'<rect x="{_f(XB + 98)}" y="{_f(ay - 1)}" width="13" height="20" rx="2" fill="none" stroke="{BRASS}" stroke-width="3"/>')
    elif closure == "Hook & Loop":
        out += _velcro(XB + 80, ay + 1, XB + 124, ay + 10, base)
    return out


# --------------------------------------------------------------------------
# The kinds and the shoe
# --------------------------------------------------------------------------

#: kind -> how it is drawn. The keys are column 4 of :data:`footwear_rows.TYPES`.
KINDS: dict[str, Kind] = {
    # heels and flats: the heel and the cut tell them apart
    "court": Kind(188, (206, 274), "pump", 84, "stiletto", 5, "leather", "point", 3),
    "kitten": Kind(246, (200, 288), "pump", 34, "kitten", 5, "leather", "point", 3),
    "block_heel": Kind(214, (204, 280), "pump", 58, "block", 6, "leather", "almond", 3),
    "ballet": Kind(287, (210, 293), "pump", 0, "none", 5, "leather", "round", 2),
    "loafer": Kind(258, (196, 252), "pump", 14, "low", 8, "leather", "almond", 4),
    "brogue": Kind(254, (156, 236), "lace", 14, "low", 8, "leather", "almond", 4),
    "slipper": Kind(262, (214, 256), "pump", 4, "none", 9, "soft", "round", 4),
    "trainer": Kind(236, (152, 220), "lace", 6, "none", 24, "cup", "round", 6),
    "running": Kind(232, (156, 214), "lace", 16, "none", 28, "midsole", "round", 14),
    # boots: the shaft height reads first
    "ankle_boot": Kind(150, (236, 248), "boot", 44, "stacked", 7, "leather", "almond", 3, 156),
    "chelsea": Kind(160, (238, 254), "boot", 16, "low", 9, "leather", "round", 4, 164),
    "chukka": Kind(184, (236, 254), "boot", 6, "none", 16, "crepe", "round", 4, 168),
    "knee_boot": Kind(40, (236, 250), "boot", 36, "block", 7, "leather", "almond", 3, 146),
    "walking_boot": Kind(150, (240, 246), "boot", 10, "none", 24, "lug", "round", 8, 166),
    "safety_boot": Kind(148, (232, 244), "boot", 10, "none", 26, "lug", "cap", 6, 166),
    "welly": Kind(78, (238, 250), "boot", 10, "none", 18, "welly", "round", 6, 168),
    "sandal": Kind(244, (220, 280), "pump", 10, "none", 8, "footbed", "round", 2),
}


def shoe(paint: str, fill: Fill, label: str | None, kind: str = "trainer", material: str = "leather", closure: str = "", lace: str = "") -> list[str]:
    """One shoe from its outer side, toe right: see the module docstring.

    ``kind`` defaults to a real kind because a shape is also drawn with no
    params at all (a motif, :func:`motifs.drawn_box`); an unknown kind raises.
    """
    k = KINDS[kind]
    base = fill.base
    uid = hashlib.sha1(f"{paint}|{base}|{kind}|{material}|{closure}|{lace}".encode()).hexdigest()[:10]
    dy = 200 - (min(k.top, k.top - 30 if closure == "Ankle Strap" else k.top) + G) / 2
    shadow = f'<ellipse cx="{_f((XB + XT) / 2)}" cy="{_f(G + 3)}" rx="{_f((XT - XB) / 2 + 12)}" ry="7" fill="{INK}" opacity=".12"/>'
    body = [shadow]
    if kind == "sandal":
        body += [*_unit_sole(k, base), *_sandal(k, paint, base, closure, material, uid)]
    elif closure == "Slingback":
        vamp, extra = _slingback(k)
        body += [extra[0], _path(vamp, paint, LW), *_texture(material, vamp, base, k, uid)]
        body += [e.replace("{paint}", paint) for e in extra[1:]]
        body += [*_sole(k, base), *_heel(k, paint, base)]
    else:
        outline = _outline(k)
        if k.cut == "boot":
            body.append(_lining(k, (k.front, k.top + 2), 10))
        elif kind != "slipper":
            body.append(_lining(k, k.instep))
        body += [_path(outline, paint, LW), *_texture(material, outline, base, k, uid)]
        _LACE_OVERRIDE[0] = lace
        try:
            body += MARKS.get(kind, lambda *a: [])(k, outline, paint, base, closure)
        finally:
            _LACE_OVERRIDE[0] = ""
        body += [*_sole(k, base), *_heel(k, paint, base)]
    return [f'<g class="shoe-{kind}" transform="translate(0 {_f(dy)})">', *body, "</g>"]


# --------------------------------------------------------------------------
# The boot sock (the boots row's third distractor)
# --------------------------------------------------------------------------


def boot_sock(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A knitted welly sock from the side: a long leg, heel and toe in the accent, a ribbed fold-over cuff."""
    leg = "M140,96 L236,96 L238,250 C240,282 262,292 300,292 Q346,294 346,322 Q344,346 300,346 L176,346 C138,346 128,322 132,290 Z"
    cuff = "M128,52 L248,52 L244,120 L132,120 Z"
    ribs = " ".join(f"M{x},56 L{x - 1},116" for x in range(140, 244, 8))
    heel = "M132,300 C130,330 150,346 176,346 L190,346 C176,330 172,310 176,290 Z"
    toe = "M300,292 Q346,294 346,322 Q344,346 300,346 Q312,320 300,292 Z"
    accent = fill.accent
    return [
        _path(leg, paint),
        _path(heel, accent, LW_DETAIL),
        _path(toe, accent, LW_DETAIL),
        _path(cuff, _mix(accent, "#ffffff", 0.15)),
        _line(ribs, 1.4, ' stroke-opacity=".7"'),
        _line("M134,124 Q190,130 240,124", 1.4, ' stroke-opacity=".5"'),
    ]


def _every(pts: list[tuple[float, float]], step: float) -> list[tuple[float, float]]:
    """Points from ``pts`` at least ``step`` px apart (punching along a seam)."""
    out: list[tuple[float, float]] = []
    for p in pts:
        if not out or (p[0] - out[-1][0]) ** 2 + (p[1] - out[-1][1]) ** 2 >= step * step:
            out.append(p)
    return out


register({"shoe": shoe, "boot_sock": boot_sock})
