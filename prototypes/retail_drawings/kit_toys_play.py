"""Drawings of the six toy types of gen#424: a kite, a play kitchen, a dolls' house, a card game,
a marble run and a water gun. Each is its own shape and registers itself with the kit.

==============  ==========================================  ==========================
shape           what it draws                               params
==============  ==========================================  ==========================
kite            a diamond, a delta, a parafoil of cells or  kind (diamond, delta,
                a wide stunt kite with two handles          parafoil, stunt)
play_kitchen    a cooker with four rings, an oven door,     sink (yes, no)
                a shelf and, when it has one, a sink
dolls_house     an open-fronted house of rooms under a      floors (2, 3)
                pitched roof, with a front door
card_game       a tuck box with a fan of three cards        kind (family, party,
                before it, its pip marking the kind         strategy)
marble_run      a stand with sloped channels, each ending   tiers (3, 4)
                over the next, and marbles on them
water_gun       a pistol, a blaster with a pump grip or a   kind (pistol, blaster,
                backpack tank with a hose and a nozzle      backpack)
==============  ==========================================  ==========================

No drawing prints a number: a style's sizes share one image.
"""

from __future__ import annotations

from kit import Fill, _highlight, _line, _path, _shade, _tint, register
from kit_sports import _ell, _label, _rect

METAL, GLASS, WOOD = "#b9bdc4", "#cfe3ee", "#d9b98a"


def kite(paint: str, fill: Fill, label: str | None, kind: str = "diamond") -> list[str]:
    """A kite on its string: the four ``kind`` shapes differ in outline, spars and tail."""
    dark = _shade(fill.base, 0.3)
    k = kind.lower()
    if k == "delta":
        out = [
            _path("M200,40 L335,250 L200,205 L65,250 Z", paint),
            _line("M200,40 L200,205", 3),
            _path("M200,205 L335,250 L200,230 Z", dark, 2),
        ]
    elif k == "parafoil":
        out = [_path("M50,150 C120,60 280,60 350,150 C280,205 120,205 50,150 Z", paint)]
        out += [
            _line(f"M{x},{y} L{x},{205 - (y - 60) * 0.55:.0f}", 2.4)
            for x, y in ((110, 92), (155, 74), (200, 70), (245, 74), (290, 92))
        ]
        out += [_line("M200,200 L120,300 M200,200 L280,300", 2, ' stroke-dasharray="5 4"')]
    elif k == "stunt":
        out = [
            _path("M200,70 L370,230 L200,190 L30,230 Z", paint),
            _line("M30,230 L370,230", 4),
            _line("M200,70 L200,190", 3),
            _path("M200,190 L370,230 L200,215 Z", dark, 2),
        ]
        out += [
            _line("M200,230 L120,350 M200,230 L280,350", 2, ' stroke-dasharray="5 4"'),
            _rect(96, 346, 48, 14, "#f2c230", 5),
            _rect(256, 346, 48, 14, "#f2c230", 5),
        ]
        return _label(out, label)
    else:
        out = [
            _path("M200,40 L315,160 L200,300 L85,160 Z", paint),
            _line("M200,40 L200,300 M85,160 L315,160", 3),
            _path("M200,40 L315,160 L200,160 Z", dark, 2),
        ]
    out.append(_line("M200,300 C150,320 250,340 200,370 C170,385 230,392 215,396", 2.4))
    if k == "diamond":
        out += [
            _path(f"M{x},{y} l12,-8 l0,16 Z M{x},{y} l-12,-8 l0,16 Z", _tint(fill.base, 0.4), 2)
            for x, y in ((190, 330), (205, 360))
        ]
    out.append(_highlight("M130,150 L190,90", 3, 0.5))
    return _label(out, label)


def play_kitchen(paint: str, fill: Fill, label: str | None, sink: str = "yes") -> list[str]:
    """A play kitchen: a cooker block with four rings, an oven door with a window and a handle,
    a shelf above and, with ``sink`` yes, a basin with a tap beside it."""
    dark = _shade(fill.base, 0.35)
    out = [
        _rect(70, 150, 260 if sink == "yes" else 190, 215, paint, 8),
        _rect(60, 128, 280 if sink == "yes" else 210, 28, _tint(fill.base, 0.3), 6),
        _rect(80, 40, 180 if sink == "yes" else 170, 14, WOOD, 4),
        _line("M95,54 L95,128 M245,54 L245,128", 4),
    ]
    for cx, cy in ((110, 141), (160, 141)):
        out.append(_ell(cx, cy, 20, 6, "#4b4f58", 2))
    out += [
        _rect(90, 200, 150, 140, dark, 6),
        _rect(105, 215, 120, 70, GLASS, 5),
        _line("M110,308 L220,308", 6, "", METAL),
    ]
    if sink == "yes":
        out += [
            _rect(250, 135, 70, 18, METAL, 4),
            _line("M285,135 L285,100 Q285,86 300,92", 5, "", METAL),
            _rect(250, 200, 70, 70, _tint(fill.base, 0.5), 6),
        ]
    return _label(out, label)


def dolls_house(paint: str, fill: Fill, label: str | None, floors: str = "2") -> list[str]:
    """A dolls' house with its front open: ``floors`` rooms stacked under a pitched roof, each
    with a window, and a front door on the ground floor."""
    n = 3 if str(floors) == "3" else 2
    h = 200 // n
    top = 340 - n * h
    out = [
        _path(f"M70,{top} L200,{top - 70} L330,{top} Z", _shade(fill.base, 0.4)),
        _rect(250, top - 60, 24, 40, "#8a4b3a", 3),
    ]
    for i in range(n):
        y = top + i * h
        out += [
            _rect(80, y, 240, h, _tint(fill.base, 0.65), 2),
            _line(f"M200,{y} L200,{y + h}", 2),
            _rect(100, y + 14, 60, h - 34, GLASS, 3),
            _rect(240, y + 14, 60, h - 34, paint, 3),
        ]
    out += [
        _rect(172, 340 - 62, 56, 62, "#8a4b3a", 4),
        _ell(216, 310, 4, 4, METAL, 1.5),
        _line("M60,340 L340,340", 5),
    ]
    return _label(out, label)


def card_game(paint: str, fill: Fill, label: str | None, kind: str = "family") -> list[str]:
    """A card game: a tuck box behind a fan of three cards. The kind is a pip on the cards:
    a round pip for family, a star for party, a square one for strategy."""
    out = [_rect(70, 90, 170, 250, paint, 10), _rect(90, 120, 130, 60, _tint(fill.base, 0.6), 6)]
    for ang, x in ((-18, 190), (0, 235), (18, 280)):
        pip = {
            "party": _path(
                "M0,-22 L7,-7 L22,-7 L10,3 L14,18 L0,9 L-14,18 L-10,3 L-22,-7 L-7,-7 Z",
                "#c8312e",
                2,
            ),
            "strategy": _rect(-14, -14, 28, 28, "#26365c", 3, 2),
        }.get(kind.lower(), _ell(0, 0, 15, 15, "#c8312e", 2))
        out.append(
            f'<g transform="translate({x} 250) rotate({ang})">'
            + _rect(-50, -80, 100, 160, "#ffffff", 8)
            + pip
            + "</g>"
        )
    return _label(out, label)


def marble_run(paint: str, fill: Fill, label: str | None, tiers: str = "3") -> list[str]:
    """A marble run: a base and an upright, ``tiers`` sloped channels that zig-zag down it, and
    a marble at the top of each."""
    n = 4 if str(tiers) == "4" else 3
    gap = 250 // n
    out = [_rect(60, 350, 280, 22, _shade(fill.base, 0.3), 6), _rect(186, 50, 28, 300, WOOD, 4)]
    for i in range(n):
        y = 80 + i * gap
        left = i % 2 == 0
        x0, x1 = (80, 200) if left else (200, 320)
        ya, yb = (y, y + 38) if left else (y + 38, y)
        out.append(
            _path(f"M{x0},{ya} L{x1},{yb + 0} L{x1},{yb + 16} L{x0},{ya + 16} Z", paint, 2.6)
        )
        out.append(_ell(x0 + 14 if left else x1 - 14, (ya if left else yb) - 9, 9, 9, "#f2c230", 2))
    return _label(out, label)


def water_gun(paint: str, fill: Fill, label: str | None, kind: str = "pistol") -> list[str]:
    """A water gun: a ``pistol`` with a clear tank under the barrel, a ``blaster`` with a pump
    grip under a long barrel, or a ``backpack`` tank on a strap with a hose to a nozzle."""
    dark = _shade(fill.base, 0.3)
    k = kind.lower()
    if k == "backpack":
        out = [
            _rect(70, 90, 110, 220, paint, 16),
            _rect(86, 130, 78, 150, GLASS, 8),
            _rect(110, 60, 30, 30, dark, 5),
            _line("M180,250 C230,260 240,200 260,190", 7, "", "#4b4f58"),
            _rect(250, 160, 100, 36, paint, 10),
            _rect(344, 170, 30, 16, dark, 4),
            _line("M300,196 L300,250", 12, "", dark),
        ]
    elif k == "blaster":
        out = [
            _rect(50, 140, 290, 44, paint, 12),
            _rect(330, 150, 40, 24, dark, 5),
            _rect(130, 184, 90, 26, _tint(fill.base, 0.3), 8),
            _rect(70, 100, 100, 40, GLASS, 8),
            _line("M90,184 L80,260 L120,260 L128,184", 6, "", dark),
        ]
    else:
        out = [
            _rect(70, 130, 220, 52, paint, 14),
            _rect(284, 142, 70, 28, dark, 6),
            _path("M110,182 L96,300 L150,300 L170,182 Z", dark),
            _rect(160, 200, 120, 60, GLASS, 12),
            _line("M200,182 Q206,214 224,214", 4),
        ]
    return _label(out, label)


SHAPES = {
    "kite": kite,
    "play_kitchen": play_kitchen,
    "dolls_house": dolls_house,
    "card_game": card_game,
    "marble_run": marble_run,
    "water_gun": water_gun,
}
register(SHAPES)
