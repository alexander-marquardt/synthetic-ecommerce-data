"""Hedge trimmer, garden furniture and parasol shapes for the retail drawing kit (gen#203).

Each type of the specs ``hedge_trimmer``, ``garden_furniture_set`` and ``parasol`` has its own
flat drawing in the kit's house style (see :mod:`kit_garden`, whose part machinery it shares).

==================  ==========================================  ===========================
shape               draws                                       params
==================  ==========================================  ===========================
hedge_trimmer       a housing with a handle and a long toothed  power (cordless, petrol,
                    blade                                       electric)
garden_furniture    a dining set (a table and chairs), a        kind (dining, bistro,
                    bistro pair, a corner lounge, or sun        corner, lounger), seats,
                    loungers; one ``class="seat"`` group per    cushions (yes, no)
                    seat, cushions on the seats when ``yes``
parasol             a scalloped canopy on a center pole or a    kind (center, cantilever),
                    cantilever arm and post                     tilt (yes, no), base (yes,
                                                                no)
==================  ==========================================  ===========================

A drawing never prints a size: a hedge trimmer's blade length and a parasol's diameter are SKU
axes that share one image per colorway. A furniture set's ``seats`` is both a drawing param and
a SKU axis, so each SKU's image draws its own seat count (:func:`export.drawing_spec`). What the
record states is drawn: the power source as a battery pack, a fuel cap or a cable, the tilt as a
``tilt`` group, the base as a ``base`` group, the cushions as ``cushion`` groups.
A decoy title that names a part's color passes ``part`` and ``part_color`` (:data:`kit_garden.PARTS`).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import Fill, _highlight, _line, _path, _shade, _tint, register
from kit_garden import BATTERY_CLASS, CABLE_CLASS, FUEL_CLASS, GREASE, _Part
from kit_sports import POLE, _ell, _label, _rect

SEAT_CLASS = "seat"
CUSHION_CLASS = "cushion"
TILT_CLASS = "tilt"
BASE_CLASS = "base"


def hedge_trimmer(paint: str, fill: Fill, label: str | None, power: str = "cordless",
                  part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A hedge trimmer: a housing at the left with a D handle over it, and a long blade with a
    row of teeth along its lower edge. ``power`` adds a battery pack (cordless), a fuel cap on a
    tank (petrol) or a trailing cable (electric)."""
    power = power.lower()
    pt = _Part("hedge_trimmer", part, part_color)
    teeth = "M176,276 " + " ".join(f"L{x + 9},292 L{x + 18},276" for x in range(176, 380, 18))
    out = [
        _path(teeth + " Z", POLE),
        pt.mark("blade", _path("M170,244 L384,244 L384,276 L170,276 Z", pt.fill("blade", POLE))),
        _line("M190,260 L376,260", 2, ' stroke-opacity=".4"'),
        pt.mark("guard", _path("M160,226 L196,226 L196,244 L160,244 Z", pt.fill("guard", GREASE))),
        _path("M56,248 Q56,212 96,210 L170,210 L170,284 L96,284 Q56,284 56,248 Z", paint),
        _highlight("M76,232 Q86,220 120,218", 4, 0.5),
        pt.mark(
            "handle",
            _line("M78,210 Q58,140 118,140 L168,140 L168,210", 9, stroke=pt.fill("handle", POLE)),
        ),
        _rect(108, 214, 26, 30, GREASE, 6),
    ]
    if power == "cordless":
        out.append(
            f'<g class="{BATTERY_CLASS}">{_rect(30, 236, 34, 52, _shade(fill.base, 0.35), 6)}{_line("M38,252 L56,252 M38,266 L52,266", 2.4, stroke="#ffffff")}</g>'
        )
    elif power == "petrol":
        out += [
            _rect(74, 284, 80, 30, _shade(fill.base, 0.35), 6),
            f'<g class="{FUEL_CLASS}">{_ell(114, 280, 14, 7, POLE, 2.4)}</g>',
        ]
    else:
        out.append(
            f'<g class="{CABLE_CLASS}">{_line("M56,262 Q20,300 40,340 Q100,372 200,356", 3.4, stroke="#e07a1f")}</g>'
        )
    return _label(out, label)


def _chair(
    x: float, base: float, w: float, h: float, paint: str, fill: Fill, cushion: bool, pt: _Part
) -> str:
    """One chair or seat: a backrest, a seat and two legs, in a ``seat`` group."""
    leg = pt.fill("legs", GREASE)
    seat_y = base - h * 0.42
    parts = [
        pt.mark("legs", _line(f"M{x + 4:.1f},{seat_y:.1f} L{x + 2:.1f},{base:.1f}", 5, stroke=leg)),
        pt.mark(
            "legs",
            _line(f"M{x + w - 4:.1f},{seat_y:.1f} L{x + w - 2:.1f},{base:.1f}", 5, stroke=leg),
        ),
        _rect(x + 3, base - h, w - 6, h * 0.5, paint, 5),
        _rect(x, seat_y - 6, w, 12, _shade(fill.base, 0.2), 4),
    ]
    if cushion:
        parts.append(
            f'<g class="{CUSHION_CLASS}">{pt.mark("cushions", _rect(x + 5, seat_y - 14, w - 10, 10, pt.fill("cushions", _tint(fill.base, 0.55)), 4))}</g>'
        )
    return f'<g class="{SEAT_CLASS}">{"".join(parts)}</g>'


def _dining(n: int, paint: str, fill: Fill, cushion: bool, pt: _Part) -> list[str]:
    top = _rect(60, 150, 280, 16, _tint(fill.base, 0.25), 5)
    legs = _line("M84,166 L84,300 M316,166 L316,300", 8, stroke=pt.fill("legs", GREASE))
    out = [pt.mark("legs", legs), top]
    per = max(1, math.ceil(n / 2))
    w = min(60.0, 340.0 / per - 8)
    for row, (base, scale) in enumerate(((290.0, 0.8), (338.0, 1.0))):
        count = per if row == 1 else n - per
        width = w * scale
        gap = (360.0 - count * width) / (count + 1)
        out += [
            _chair(20 + gap + i * (width + gap), base, width, 84 * scale, paint, fill, cushion, pt)
            for i in range(count)
        ]
    return out


def _bistro(paint: str, fill: Fill, cushion: bool, pt: _Part) -> list[str]:
    return [
        pt.mark(
            "legs", _line("M200,196 L200,326 M160,330 L240,330", 7, stroke=pt.fill("legs", GREASE))
        ),
        _ell(200, 190, 62, 12, _tint(fill.base, 0.25)),
        _chair(40, 330, 64, 108, paint, fill, cushion, pt),
        _chair(296, 330, 64, 108, paint, fill, cushion, pt),
    ]


def _corner(n: int, paint: str, fill: Fill, cushion: bool, pt: _Part) -> list[str]:
    main = max(1, n - 2)
    w = min(64.0, 250.0 / main)
    out = [_line("M20,334 L380,334", 4)]
    x0 = 24.0
    for i in range(main):
        out.append(_chair(x0 + i * w, 330, w, 120, paint, fill, cushion, pt))
    rx = x0 + main * w + 6
    for j in range(min(2, n)):
        out.append(_chair(rx + j * 10, 290 - j * 56, 64, 96, paint, fill, cushion, pt))
    out.append(
        pt.mark(
            "legs",
            _line(f"M{x0 + 30:.1f},334 L{x0 + 30:.1f},344", 5, stroke=pt.fill("legs", GREASE)),
        )
    )
    return out


def _lounger(n: int, paint: str, fill: Fill, cushion: bool, pt: _Part) -> list[str]:
    out = []
    for i in range(n):
        dy = i * 36
        x = 30 + i * 40
        seat = f"M{x},{296 - dy} L{x + 200},{296 - dy} L{x + 250},{244 - dy} L{x + 232},{232 - dy} L{x + 190},{270 - dy} L{x},{270 - dy} Z"
        parts = [
            pt.mark(
                "legs",
                _line(
                    f"M{x + 20},{296 - dy} L{x + 14},{330} M{x + 180},{296 - dy} L{x + 186},{330}",
                    6,
                    stroke=pt.fill("legs", GREASE),
                ),
            ),
            _path(seat, paint),
        ]
        if cushion:
            parts.append(
                f'<g class="{CUSHION_CLASS}">{pt.mark("cushions", _path(f"M{x + 6},{270 - dy} L{x + 190},{270 - dy} L{x + 222},{238 - dy} L{x + 214},{232 - dy} L{x + 180},{262 - dy} L{x + 6},{262 - dy} Z", pt.fill("cushions", _tint(fill.base, 0.55))))}</g>'
            )
        out.append(f'<g class="{SEAT_CLASS}">{"".join(parts)}</g>')
    return out[::-1]


def garden_furniture(paint: str, fill: Fill, label: str | None, kind: str = "dining", seats: str = "4",
                     cushions: str = "yes", part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A garden furniture set: ``dining`` (a table and ``seats`` chairs in two rows), ``bistro``
    (a round table and two chairs), ``corner`` (a sofa run and a return of ``seats`` seats) or
    ``lounger`` (``seats`` sun loungers). Each seat is a ``seat`` group; ``cushions`` ``yes``
    puts a ``cushion`` group on each."""
    pt = _Part("garden_furniture", part, part_color)
    n, cushion = int(seats), cushions.lower() == "yes"
    draw = {"dining": _dining, "corner": _corner, "lounger": _lounger}.get(kind.lower())
    out = [_line("M20,340 L380,340", 4)]
    out += (
        _bistro(paint, fill, cushion, pt)
        if kind.lower() == "bistro"
        else (draw or _dining)(n, paint, fill, cushion, pt)
    )
    return _label(out, label)


def _canopy(
    cx: float, left: float, right: float, top: float, edge: float, paint: str, fill: Fill, pt: _Part
) -> list[str]:
    span = (right - left) / 4
    pts = [left + span * i for i in range(5)]
    edge_d = " ".join(
        f"Q{(a + b) / 2:.1f},{edge + 22} {b:.1f},{edge}" for a, b in zip(pts, pts[1:], strict=False)
    )
    dome = (
        f"M{left},{edge} Q{cx},{top} {right},{edge} "
        + " ".join(
            f"Q{(b + a) / 2:.1f},{edge + 22} {a:.1f},{edge}"
            for a, b in zip(pts[::-1], pts[::-1][1:], strict=False)
        )
        + " Z"
    )
    ribs = "".join(f"M{cx},{top + 14} L{x:.1f},{edge}" for x in pts[1:-1])
    return [
        _path(dome, paint),
        _line(ribs, 2, ' stroke-opacity=".4"'),
        pt.mark(
            "valance",
            _path(
                f"M{left},{edge} {edge_d} L{right},{edge - 6} L{left},{edge - 6} Z",
                pt.fill("valance", _shade(fill.base, 0.2)),
                2.4,
            ),
        ),
        _highlight(f"M{left + 40},{edge - 26} Q{cx - 30},{top + 24} {cx - 6},{top + 18}", 4, 0.5),
    ]


def parasol(paint: str, fill: Fill, label: str | None, kind: str = "center", tilt: str = "no",
            base: str = "no", part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A parasol: a scalloped canopy on a ``center`` pole or a ``cantilever`` post and arm that
    holds it to one side. ``tilt`` ``yes`` adds a tilt joint group, ``base`` ``yes`` a base group
    (a block under the pole, a cross foot under the post)."""
    pt = _Part("parasol", part, part_color)
    kind, tilt, base = kind.lower(), tilt.lower() == "yes", base.lower() == "yes"
    pole = pt.fill("pole", POLE)
    foot = pt.fill("base", GREASE)
    if kind == "cantilever":
        out = [
            pt.mark("pole", _line("M330,334 L330,120", 9, stroke=pole)),
            pt.mark("pole", _line("M330,120 Q300,84 200,100", 7, stroke=pole)),
            *_canopy(160, 30, 290, 70, 150, paint, fill, pt),
        ]
        joint = (300, 96)
        if base:
            out.append(
                f'<g class="{BASE_CLASS}">{pt.mark("base", _rect(250, 322, 130, 16, foot, 4))}{_line("M315,322 L345,338", 3)}</g>'
            )
    else:
        out = [
            pt.mark("pole", _line("M200,60 L200,330", 8, stroke=pole)),
            *_canopy(200, 30, 370, 60, 170, paint, fill, pt),
        ]
        joint = (200, 236)
        if base:
            out.append(
                f'<g class="{BASE_CLASS}">{pt.mark("base", _rect(150, 312, 100, 26, foot, 4))}</g>'
            )
    if tilt:
        out.append(
            f'<g class="{TILT_CLASS}">{_ell(joint[0], joint[1], 12, 12, POLE, 2.4)}{_line(f"M{joint[0]},{joint[1]} l22,-14", 3.4)}</g>'
        )
    return _label(out, label)


SHAPES = {"hedge_trimmer": hedge_trimmer, "garden_furniture": garden_furniture, "parasol": parasol}
register(SHAPES)
