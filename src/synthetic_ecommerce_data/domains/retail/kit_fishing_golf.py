"""Fishing and golf shapes for the retail drawing kit (gen#959, slice 1).

The Fishing and Golf families of Sports & Outdoors: each product is drawn as what it is, so a
reel never reads as a rod and a golf ball never as a baseball. Outlines are the kit's ink, and
the record's fill (color and pattern) paints the main surface: a rod's blank, a reel's body, a
tackle box's shell, a club's head, a ball's cover and a glove's back.

===============  =============================================  ==================================
shape            draws                                          params
===============  =============================================  ==================================
fishing_rod      a rod on the slant: cork handle, reel seat,    rod_type (spinning, casting, fly)
                 the blank and its line guides
fishing_reel     a reel from the side on its foot               reel_type (spinning, baitcasting,
                                                                spincast)
tackle_box       a box with its carry handle                    tackle_type (cantilever, drawer,
                                                                hip roof)
golf_club        a club upright: grip, shaft and head           club_type (driver, fairway wood,
                                                                7 iron, sand wedge, putter)
golf_ball        a dimpled ball cut open to show its layers     construction (2-piece, 3-piece,
                                                                4-piece)
golf_glove       a glove from the back, with its wrist tab      material (cabretta leather,
                                                                synthetic, hybrid)
===============  =============================================  ==================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a rod's ``rod_type`` or a ball's ``construction`` draws what it states (gen#512).
A drawing never prints a length or a size: a style's SKUs share one image per colorway. Every
param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import POLE, _ell, _label, _rect, _tilted

#: A rod's cork handle and the dark rubber of a grip.
CORK = "#d9b27c"
GRIP = "#33363c"
#: The clear lid of a hip-roof tackle box's top tray.
CLEAR = "#dfe8ee"


def fishing_rod(paint: str, fill: Fill, label: str | None, rod_type: str = "spinning") -> list[str]:
    """A rod on the slant: guides hang under a ``spinning`` blank, sit on a ``casting`` one with
    a trigger, and a ``fly`` rod has small snake guides and its reel seat at the very end."""
    kind = rod_type.lower()
    dark = _shade(fill.base, 0.35)
    parts = []
    if kind == "fly":
        parts += [_rect(36, 192, 24, 16, POLE, 4), _rect(60, 191, 80, 18, CORK, 8)]
    else:
        parts += [_rect(30, 192, 90, 16, CORK, 8), _rect(120, 189, 30, 22, POLE, 4)]
    parts.append(_path("M140,194 L380,198.5 L380,201.5 L140,206 Z", paint))
    parts.append(_line("M150,197 L370,199.5", 2, ' stroke-opacity=".5"', _tint(fill.base, 0.6)))
    if kind == "casting":
        parts.append(_path("M126,211 Q132,228 144,230 L146,211 Z", POLE, 2.4))
    for i, x in enumerate((190, 240, 285, 325, 358)):
        r = max(3.0, 11 - 2 * i)
        if kind == "fly":
            parts.append(_line(f"M{x - 6},201 Q{x},210 {x + 6},201", 2, stroke=dark))
        elif kind == "casting":
            parts += [_line(f"M{x},197 L{x},{189 - r}", 2, stroke=POLE), _ell(x, 189 - 2 * r, r * 0.7, r, "none", LW_DETAIL)]
        else:
            parts += [_line(f"M{x},203 L{x},{211 + r}", 2, stroke=POLE), _ell(x, 211 + 2 * r, r * 0.7, r, "none", LW_DETAIL)]
    parts.append(_ell(381, 200, 3, 3, dark, LW_DETAIL))
    return _label(_tilted(parts, -32), label)


def fishing_reel(paint: str, fill: Fill, label: str | None, reel_type: str = "spinning") -> list[str]:
    """A reel from the side: a ``spinning`` reel's open spool and bail, a low ``baitcasting``
    body with a round side plate and a two-knob handle, or a ``spincast`` reel's closed cone."""
    kind = reel_type.lower()
    dark = _shade(fill.base, 0.35)
    out = [_rect(60, 96, 280, 14, POLE, 6)]
    if kind == "baitcasting":
        out += [
            _rect(170, 110, 60, 40, POLE, 6),
            _path("M100,190 Q100,150 160,146 L250,146 Q310,150 310,200 Q310,256 250,258 L160,258 Q100,256 100,190 Z", paint),
            _ell(205, 202, 52, 46, dark),
            _ell(205, 202, 18, 18, POLE),
            _line("M205,202 L300,282", 6, stroke=POLE),
            _ell(270, 260, 14, 10, dark), _ell(320, 296, 14, 10, dark),
        ]
    elif kind == "spincast":
        out += [
            _rect(186, 110, 28, 50, POLE, 6),
            _path("M120,170 L250,160 Q300,200 250,248 L120,238 Z", paint),
            _path("M250,160 L330,186 Q340,204 330,222 L250,248 Q300,204 250,160 Z", dark),
            _ell(150, 158, 22, 10, dark),
            _line("M140,204 L80,278", 6, stroke=POLE), _ell(78, 288, 14, 10, dark),
        ]
    else:
        out += [
            _rect(186, 110, 28, 70, POLE, 6),
            _ell(200, 230, 70, 58, paint),
            _rect(260, 190, 70, 80, dark, 10),
            _rect(330, 204, 16, 52, POLE, 4),
            _line("M262,192 Q300,150 340,206", 4, stroke=POLE),
            _line("M150,230 L90,300", 6, stroke=POLE), _ell(86, 310, 16, 11, dark),
        ]
    out.append(_highlight("M150,186 Q190,170 230,176", 5, 0.5))
    return _label(out, label)


def tackle_box(paint: str, fill: Fill, label: str | None, tackle_type: str = "cantilever") -> list[str]:
    """A tackle box: ``cantilever`` trays fanned open over the box, a ``drawer`` box with three
    drawer fronts, or a ``hip roof`` box whose clear top trays open from the middle."""
    kind = tackle_type.lower()
    dark = _shade(fill.base, 0.35)
    out = [_rect(70, 200, 260, 140, paint, 10), _line("M70,240 L330,240", 2, stroke=dark)]
    if kind == "drawer":
        out[0] = _rect(70, 140, 260, 200, paint, 10)
        out += [_rect(90, 170 + 52 * i, 220, 40, _tint(fill.base, 0.3), 6, 2) for i in range(3)]
        out += [_rect(180, 182 + 52 * i, 40, 10, dark, 4, LW_DETAIL) for i in range(3)]
        out.append(_path("M150,140 Q150,100 200,100 Q250,100 250,140", "none", 8, stroke=dark))
    elif kind == "hip roof":
        out += [
            _path("M70,200 L120,150 L196,150 L196,200 Z", CLEAR, 2.4),
            _path("M330,200 L280,150 L204,150 L204,200 Z", CLEAR, 2.4),
            *[_line(f"M{x},156 L{x},198", LW_DETAIL) for x in (130, 160, 240, 270)],
            _path("M170,150 Q170,118 200,118 Q230,118 230,150", "none", 8, stroke=dark),
        ]
    else:
        out += [
            _rect(90, 160, 220, 40, _tint(fill.base, 0.3), 6, 2),
            _rect(110, 120, 220, 40, _tint(fill.base, 0.45), 6, 2),
            _line("M100,200 L130,160 M290,200 L320,160", 3, stroke=POLE),
            *[_line(f"M{x},124 L{x},156", LW_DETAIL) for x in (165, 220, 275)],
        ]
    out += [_rect(186, 232, 28, 16, POLE, 3, LW_DETAIL), _highlight("M86,260 L86,326", 5, 0.5)]
    return _label(out, label)


def golf_club(paint: str, fill: Fill, label: str | None, club_type: str = "driver") -> list[str]:
    """A club upright: a dark grip, a steel shaft and the head the ``club_type`` names, a big
    round wood, a slim ``fairway wood``, a bladed ``7 iron``, a lofted grooved ``sand wedge``
    or a flat ``putter``."""
    kind = club_type.lower()
    dark = _shade(fill.base, 0.35)
    out = [_rect(214, 40, 18, 80, GRIP, 6), _path("M216,120 L230,120 L206,300 L200,300 Z", POLE, 2.4)]
    if kind == "putter":
        out += [_rect(118, 296, 118, 34, paint, 6), _line("M130,306 L224,306", 2, stroke=dark)]
    elif kind in ("7 iron", "sand wedge"):
        lofted = kind == "sand wedge"
        face = "M200,290 L214,300 L188,352 Q140,358 128,338 Q130,316 200,290 Z" if lofted else "M200,288 L214,300 L196,344 Q140,348 132,330 Q136,312 200,288 Z"
        out.append(_path(face, paint))
        grooves = 5 if lofted else 3
        out += [_line(f"M{146 + 4 * i},{316 + 6 * i} L{190 - 2 * i},{306 + 6 * i}", LW_DETAIL, stroke=dark) for i in range(grooves)]
    else:
        rx, ry = (46, 28) if kind == "fairway wood" else (66, 40)
        out += [_ell(200 - rx * 0.6, 312, rx, ry, paint), _path(f"M{200 - rx * 1.4},322 Q{200 - rx * 0.6},{312 + ry + 8} {200 + rx * 0.2},320", "none", 2.4, stroke=dark)]
    out.append(_highlight("M220,48 L220,112", 4, 0.4))
    return _label(out, label)


def golf_ball(paint: str, fill: Fill, label: str | None, construction: str = "2-piece") -> list[str]:
    """A dimpled ball with a quarter cut away: a ``2-piece`` ball shows its core and cover, a
    ``3-piece`` one a mantle between, and a ``4-piece`` one two mantles."""
    layers = {"3-piece": 3, "4-piece": 4}.get(construction.lower(), 2)
    dark = _shade(fill.base, 0.3)
    out = [_ell(200, 200, 120, 120, paint)]
    out += [_ell(200 + dx, 200 + dy, 7, 7, dark, LW_DETAIL, ' fill-opacity=".35"')
            for dx in range(-90, 1, 30) for dy in range(-90, 91, 30) if dx * dx + dy * dy < 100 * 100]  # fmt: skip
    out += [_ell(200 + dx, 200 + dy, 7, 7, dark, LW_DETAIL, ' fill-opacity=".35"')
            for dx in range(30, 91, 30) for dy in range(30, 91, 30) if dx * dx + dy * dy < 100 * 100]  # fmt: skip
    out.append(_path("M200,200 L320,200 A120,120 0 0 0 200,80 Z", _tint(fill.base, 0.2)))
    core = ("#e8823a", "#f2c230", "#3f6fb5", "#c8312e")
    for i in range(layers - 1):
        r = 108 - i * (70 / max(1, layers - 1))
        out.append(_path(f"M200,200 L{200 + r:.1f},200 A{r:.1f},{r:.1f} 0 0 0 200,{200 - r:.1f} Z", core[i], 2))
    out.append(_highlight("M120,150 Q140,108 186,94", 6, 0.5))
    return _label(out, label)


def golf_glove(paint: str, fill: Fill, label: str | None, material: str = "cabretta leather") -> list[str]:
    """A glove from the back with its wrist tab: ``cabretta leather`` shows perforated fingers,
    ``synthetic`` stretch panels between the knuckles, and ``hybrid`` both."""
    kind = material.lower()
    dark = _shade(fill.base, 0.35)
    out = [
        _path("M130,340 L124,214 L112,150 Q110,128 128,128 Q142,130 146,152 L156,206 L160,104 Q162,82 180,84 Q196,86 196,106 L200,200 L212,92 Q216,72 234,76 Q250,80 248,100 L240,204 L262,124 Q270,106 286,112 Q300,120 294,140 L270,234 Q266,262 278,282 L300,312 L282,340 Z", paint),
        _path("M118,236 Q86,226 70,196 Q66,178 84,176 Q104,180 124,214 Z", paint),
        _rect(128, 300, 160, 46, dark, 8),
        _rect(140, 308, 70, 30, _tint(fill.base, 0.4), 6, 2),
    ]
    if kind in ("cabretta leather", "hybrid"):
        out += [_ell(x, y, 2.6, 2.6, dark, 1) for x in (132, 178, 224, 270) for y in (150, 170)]
    if kind in ("synthetic", "hybrid"):
        out += [_line(f"M{x},214 L{x + 6},262", 2, ' stroke-dasharray="4 4"', dark) for x in (176, 204, 232)]
    out.append(_highlight("M150,230 Q200,214 250,232", 5, 0.4))
    return _label(out, label)


SHAPES = {
    "fishing_rod": fishing_rod, "fishing_reel": fishing_reel, "tackle_box": tackle_box,
    "golf_club": golf_club, "golf_ball": golf_ball, "golf_glove": golf_glove,
}  # fmt: skip
register(SHAPES)
