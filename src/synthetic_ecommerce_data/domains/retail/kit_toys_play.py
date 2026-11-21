"""Drawings of the six toy types of gen#424: a kite, a play kitchen, a dolls' house, a card game,
a marble run and a water gun, and gen#1130's trading card products. Each is its own shape and
registers itself with the kit.

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
                before it, its pip marking the kind; a      strategy), theme
                themed game's name on the box (gen#960)
trading_cards   a trading card game's product (gen#1130):   form (booster_pack,
                a foil pack, a display box of packs, a      expansion, booster_box,
                deck, two decks on a mat, sleeves or a      starter_deck, battle_set,
                deck box                                    sleeves, deck_box), theme
marble_run     a stand with sloped channels, each ending   tiers (3, 4)
                over the next, and marbles on them
water_gun       a pistol, a blaster with a pump grip or a   kind (pistol, blaster,
                backpack tank with a hose and a nozzle      backpack)
==============  ==========================================  ==========================

No drawing prints a number: a style's sizes share one image.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import dark_blues
from synthetic_ecommerce_data.domains.retail.kit import (
    Fill,
    _highlight,
    _line,
    _panel,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

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


def card_game(
    paint: str, fill: Fill, label: str | None, kind: str = "family", theme: str = ""
) -> list[str]:
    """A card game: a tuck box behind a fan of three cards. The kind is a pip on the cards:
    a round pip for family, a star for party, a square one for strategy. The kind may be a toy
    type's own words ("party card game", gen#960). A themed game's theme is on the box's panel,
    as its title shows it (gen#960)."""
    kind = kind.lower().removesuffix(" card game")
    out = [_rect(70, 90, 170, 250, paint, 10)]
    panel = _rect(90, 120, 130, 60, _tint(fill.base, 0.6), 6)
    out += _panel(90, 120, 130, 60, theme.title(), 22) if theme else [panel]
    for ang, x in ((-18, 190), (0, 235), (18, 280)):
        pip = {
            "party": _path(
                "M0,-22 L7,-7 L22,-7 L10,3 L14,18 L0,9 L-14,18 L-10,3 L-22,-7 L-7,-7 Z",
                "#c8312e",
                2,
            ),
            "strategy": _rect(-14, -14, 28, 28, dark_blues.NAVY, 3, 2),
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


def _card_back(x: float, y: float, w: float, h: float, paint: str) -> list[str]:
    """A trading card face down: a white border round a painted back with a diamond on it."""
    cx, cy = x + w / 2, y + h / 2
    return [
        _rect(x, y, w, h, "#ffffff", 8),
        _rect(x + 8, y + 8, w - 16, h - 16, paint, 5, 2),
        _path(
            f"M{cx:g},{cy - h / 4:g} L{cx + w / 4:g},{cy:g} L{cx:g},{cy + h / 4:g} "
            f"L{cx - w / 4:g},{cy:g} Z",
            _tint(paint, 0.45),
            2,
        ),
    ]


def _foil_pack(x: float, y: float, w: float, h: float, paint: str, theme: str = "") -> list[str]:
    """A sealed foil booster pack: crimped strips at its top and bottom, a gloss streak and a
    panel, the theme on it when the pack is an expansion's."""
    dark = _shade(paint, 0.3)
    teeth = 8
    step = w / teeth
    top = " ".join(
        f"L{x + (i + 0.5) * step:g},{y} L{x + (i + 1) * step:g},{y + 8}" for i in range(teeth)
    )
    right = x + w
    bottom = " ".join(
        f"L{right - (i + 0.5) * step:g},{y + h} L{right - (i + 1) * step:g},{y + h - 8}"
        for i in range(teeth)
    )
    out = [
        _path(f"M{x},{y + 8} {top} L{x + w},{y + h - 8} {bottom} Z", paint),
        _rect(x, y + 8, w, 16, dark, 0, 2),
        _rect(x, y + h - 24, w, 16, dark, 0, 2),
        _highlight(f"M{x + 18:g},{y + 44:g} L{x + 34:g},{y + h - 44:g}", 7, 0.45),
    ]
    if theme:
        return out + _panel(x + 14, y + h * 0.58, w - 28, 44, theme, 20)
    cx, cy = x + w / 2, y + h * 0.45
    return out + [_path(f"M{cx:g},{cy - 34:g} L{cx + 26:g},{cy:g} L{cx:g},{cy + 34:g} "
                        f"L{cx - 26:g},{cy:g} Z", _tint(paint, 0.55), 2.4)]  # fmt: skip


def trading_cards(paint: str, fill: Fill, label: str | None, form: str = "booster_pack",
                  theme: str = "") -> list[str]:  # fmt: skip
    """A deck-building trading card game's product (gen#1130), its ``form``: a foil
    ``booster_pack`` (an ``expansion`` pack shows its theme), a ``booster_box`` of pack tops in an
    open display box, a ``starter_deck`` of stacked cards with the top one face up, a
    ``battle_set`` of two decks on a play mat, ``sleeves``, a clear stack with a card half in it,
    or an upright ``deck_box`` with a flip lid. No form is the tuck box and fan of
    :func:`card_game`."""
    dark = _shade(fill.base, 0.3)
    f = form.lower()
    if f == "booster_box":
        out = [_rect(60, 120, 280, 90, dark, 6)]
        for i in range(5):
            px, py = 78 + i * 50, 92 + (i % 2) * 10
            out += [_rect(px, py, 44, 110, paint, 3, 2), _rect(px, py, 44, 12, dark, 0, 1.6)]
        out += [_rect(60, 190, 280, 150, paint, 6), *_panel(110, 236, 180, 56, theme or None, 24)]
    elif f == "starter_deck":
        out = []
        for i in (3, 2, 1):
            out += [_rect(122 + i * 7, 62 + i * 7, 160, 240, "#ffffff", 8)]
        out += [
            _rect(122, 62, 160, 240, paint, 8),
            _rect(136, 78, 132, 104, _tint(paint, 0.55), 4, 2),
            _rect(136, 194, 132, 90, "#ffffff", 4, 2),
            *(_line(f"M146,{y} L258,{y}", 2.4) for y in (214, 236, 258)),
        ]
    elif f == "battle_set":
        out = [_rect(40, 190, 320, 150, _tint(fill.base, 0.5), 18)]
        for x in (72, 228):
            for i in (2, 1):
                out.append(_rect(x + i * 5, 150 + i * 5, 100, 150, "#ffffff", 7))
            out += _card_back(x, 150, 100, 150, paint)
    elif f == "sleeves":
        out = [_rect(132 + i * 8, 92 + i * 8, 150, 230, GLASS, 8, 2) for i in (3, 2, 1)]
        out += _card_back(140, 50, 134, 200, paint)
        out += [
            _path(
                "M124,140 L290,140 L290,322 Q290,330 282,330 L132,330 Q124,330 124,322 Z",
                GLASS,
                2.6,
                ' fill-opacity="0.75"',
            ),
            _highlight("M140,160 L140,310", 6, 0.6),
        ]
    elif f == "deck_box":
        out = [
            _path("M290,130 L326,106 L326,316 L290,340 Z", dark),
            _rect(110, 130, 180, 210, paint, 6),
            _path("M110,130 L146,106 L326,106 L290,130 Z", _shade(paint, 0.15)),
            _rect(110, 130, 180, 64, _shade(paint, 0.2), 6, 2),
            _rect(184, 178, 32, 30, METAL, 6, 2),
            *_panel(132, 236, 136, 60, None),
        ]
    else:
        out = _foil_pack(120, 50, 160, 300, paint, theme if f == "expansion" else "")
    return _label(out, label)


SHAPES = {
    "kite": kite,
    "play_kitchen": play_kitchen,
    "dolls_house": dolls_house,
    "card_game": card_game,
    "trading_cards": trading_cards,
    "marble_run": marble_run,
    "water_gun": water_gun,
}
register(SHAPES)
