"""Electronics shapes for the retail drawing kit (gen#332): phones, computers, tablets, their
accessories and the products that share a word with them, each a plain device outline.

A real brand is text only (``real_brands``): no drawing prints a name, a logo or a trade dress, so
an Apple iPhone and an invented phone are drawn alike, by their form.

==================  =========================================  ==============================
shape               draws                                      params
==================  =========================================  ==============================
smartphone          a phone, front: its screen and camera      form (flagship, midrange,
                    cut-out                                    budget, foldable, compact)
basic_phone         a phone with a keypad                      form (bar, flip, bigbutton)
laptop              an open laptop                             form (clamshell, two_in_one,
                                                               gaming, workstation)
desktop             a computer                                 form (tower, all_in_one, mini)
tablet              a tablet, front                            form (standard, kids, pro)
e_reader            a narrow reader with lines of text         (none)
phone_case          a phone back in a case                     style (clear, rugged, wallet)
screen_protector    a phone front under a glass sheet          finish (clear, matte, privacy)
charger             a charger                                  kind (wall, wireless, power_bank,
                                                               car)
cable               a cable with its two connectors            end (usb_c, micro, multi)
earbuds             earbuds and their case, or headphones      form (buds, over_ear)
laptop_sleeve       a padded sleeve with a zip                 (none)
mouse               a computer mouse                           form (wireless, gaming, ergonomic)
keyboard            a keyboard                                 layout (full, compact)
monitor             a monitor on its stand                     form (standard, ultrawide, curved)
dishwasher_tablets  a tub of dishwasher tablets                (none)
==================  =========================================  ==============================

A drawing never prints a capacity, a size or a price. Every param is a string with a default.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    Fill,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import PAPER2, _ell, _label, _rect

SCREEN = "#1f2a38"
GLASS = "#cfe3ee"


def _body(x: float, y: float, w: float, h: float, paint: str, r: float = 26) -> list[str]:
    return [_rect(x, y, w, h, paint, r)]


def _screen(x: float, y: float, w: float, h: float, r: float = 12) -> str:
    return _rect(x, y, w, h, SCREEN, r, 1.6)


def smartphone(paint: str, fill: Fill, label: str | None, form: str = "flagship") -> list[str]:
    """A phone from the front: ``flagship`` has a pill cut-out, ``midrange`` a punch hole, ``budget`` a wide bezel and a notch, ``foldable`` a hinge, ``compact`` a small body."""
    if form == "compact":
        x, y, w, h = 138, 70, 124, 252
    elif form == "foldable":
        x, y, w, h = 108, 70, 184, 252
    else:
        x, y, w, h = 124, 54, 152, 292
    out = _body(x, y, w, h, paint)
    bezel = 16 if form == "budget" else 8
    out.append(_screen(x + bezel, y + bezel, w - 2 * bezel, h - 2 * bezel, 14))
    cx = x + w / 2
    if form == "flagship":
        out.append(_rect(cx - 22, y + 14, 44, 12, "#0b0f14", 6, 1))
    elif form == "midrange":
        out.append(_ell(x + 30, y + 24, 6, 6, "#0b0f14", 1))
    elif form == "budget":
        out.append(
            _path(
                f"M{cx - 20},{y + bezel} L{cx + 20},{y + bezel} L{cx + 14},{y + bezel + 12} L{cx - 14},{y + bezel + 12} Z",
                "#0b0f14",
                1,
            )
        )
    elif form == "foldable":
        out += [
            _line(f"M{cx},{y + 8} L{cx},{y + h - 8}", 3, "", paint),
            _line(f"M{cx},{y + 8} L{cx},{y + h - 8}", 1.4, "", INK),
        ]
    else:
        out.append(_ell(cx, y + 20, 5, 5, "#0b0f14", 1))
    out.append(_line(f"M{cx - 22},{y + h - 16} L{cx + 22},{y + h - 16}", 3, "", _tint(SCREEN, 0.6)))
    return _label(out, label)


def basic_phone(paint: str, fill: Fill, label: str | None, form: str = "bar") -> list[str]:
    """A phone with a keypad: ``bar`` a slab, ``flip`` a clamshell with its hinge, ``bigbutton`` large keys."""
    if form == "flip":
        out = [
            _rect(132, 60, 136, 130, paint, 22),
            _screen(146, 76, 108, 78, 8),
            _rect(132, 204, 136, 120, _shade(paint, 0.12), 22),
            _line("M120,198 L280,198", 7, "", INK),
        ]
        out += [
            _ell(158 + 42 * c, 230 + 26 * r, 11, 8, PAPER2, 1.6) for r in range(3) for c in range(3)
        ]
        return _label(out, label)
    big = form == "bigbutton"
    out = [_rect(126, 46, 148, 308, paint, 22), _screen(140, 62, 120, 96 if not big else 84, 8)]
    rows, cols = (3, 3) if big else (4, 3)
    cw_, ch = (36, 30) if big else (30, 20)
    top = 176 if not big else 168
    out += [
        _rect(142 + c * (cw_ + 4), top + r * (ch + 6), cw_, ch, PAPER2, 6, 1.6)
        for r in range(rows)
        for c in range(cols)
    ]
    if big:
        out.append(_ell(200, 322, 16, 10, "#c8312e", 1.6))
    return _label(out, label)


def laptop(paint: str, fill: Fill, label: str | None, form: str = "clamshell") -> list[str]:
    """An open laptop: ``gaming`` has vents and an accent strip, ``two_in_one`` a stylus, ``workstation`` a number pad."""
    out = [
        _path("M96,92 L304,92 L304,238 L96,238 Z", paint),
        _screen(108, 104, 184, 122, 4),
        _path("M64,250 L336,250 L352,292 L48,292 Z", _tint(paint, 0.25)),
    ]
    keys = [
        _rect(86 + c * 26, 258 + r * 9, 20, 6, PAPER2, 1.5, 1) for r in range(2) for c in range(9)
    ]
    if form == "workstation":
        keys = [k for k in keys[:]] + [
            _rect(278 + c * 14, 258 + r * 9, 10, 6, "#b8c2cc", 1.5, 1)
            for r in range(2)
            for c in range(2)
        ]
    out += keys
    out.append(_rect(172, 276, 56, 10, PAPER2, 3, 1.2))
    if form == "gaming":
        out += [
            _line(f"M{66 + i * 6},{262 + i * 2} L{86 - i * 0},{262 + i * 2}", 2, "", "#c8312e")
            for i in range(4)
        ]
        out.append(_line("M108,230 L292,230", 4, "", "#2fbf71"))
    elif form == "two_in_one":
        out += [
            _path("M312,110 L326,110 L326,236 L319,246 L312,236 Z", "#f4f4ee", 1.6),
            _line("M319,116 L319,150", 1.4),
        ]
    return _label(out, label)


def desktop(paint: str, fill: Fill, label: str | None, form: str = "tower") -> list[str]:
    """A computer: a ``tower`` with drive bays, an ``all_in_one`` screen on a stand, a ``mini`` box."""
    if form == "all_in_one":
        out = [
            _rect(70, 70, 260, 176, paint, 14),
            _screen(82, 82, 236, 140, 6),
            _path("M176,246 L224,246 L238,306 L162,306 Z", _tint(paint, 0.2)),
            _rect(130, 306, 140, 14, _tint(paint, 0.2), 6),
        ]
        return _label(out, label)
    if form == "mini":
        out = [
            _rect(100, 190, 200, 88, paint, 16),
            _rect(116, 206, 168, 8, _shade(paint, 0.2), 4, 1.2),
        ]
        out += [_ell(130 + 22 * i, 250, 5, 5, SCREEN, 1.2) for i in range(5)]
        out.append(_ell(272, 250, 7, 7, "#2fbf71", 1.6))
        return _label(out, label)
    out = [
        _rect(120, 48, 160, 304, paint, 10),
        _rect(140, 70, 120, 18, SCREEN, 3, 1.4),
        _rect(140, 98, 120, 18, SCREEN, 3, 1.4),
        _ell(200, 160, 16, 16, _tint(paint, 0.4), 2),
    ]
    out += [
        _line(f"M142,{214 + 12 * i} L258,{214 + 12 * i}", 2, "", _shade(paint, 0.35))
        for i in range(5)
    ]
    return _label(out, label)


def tablet(paint: str, fill: Fill, label: str | None, form: str = "standard") -> list[str]:
    """A tablet: ``kids`` has a thick bumper, ``pro`` a camera bump and a home line."""
    out = [_rect(84, 60, 232, 280, paint, 22), _screen(100, 76, 200, 248, 8)]
    if form == "kids":
        out = [
            _rect(70, 48, 260, 304, _shade(paint, 0.15), 40),
            _rect(84, 62, 232, 276, paint, 28),
            _screen(106, 84, 188, 232, 8),
            _ell(96, 70, 8, 8, "#f2c230", 1.6),
            _ell(304, 330, 8, 8, "#f2c230", 1.6),
        ]
    elif form == "pro":
        out.append(_rect(290, 66, 18, 40, _shade(paint, 0.25), 6, 1.6))
    out.append(_line("M180,314 L220,314", 3, "", _tint(SCREEN, 0.6)))
    return _label(out, label)


def e_reader(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A reader: a narrow body with a pale page of lines of text and a page-turn bar."""
    out = [_rect(112, 50, 176, 300, paint, 18), _rect(126, 66, 148, 240, "#e9e6dc", 6, 1.6)]
    out += [
        _line(f"M138,{86 + 14 * i} L{262 - (i % 3) * 14},{86 + 14 * i}", 2.4, "", "#6b6f76")
        for i in range(14)
    ]
    out.append(_rect(176, 318, 48, 14, _shade(paint, 0.2), 7, 1.6))
    return _label(out, label)


def phone_case(paint: str, fill: Fill, label: str | None, style: str = "clear") -> list[str]:
    """A phone back in its case: ``clear`` shows the phone through, ``rugged`` has corner bumpers, ``wallet`` a folio flap and a strap."""
    phone = "#2a2a2e"
    out = [
        _rect(112, 46, 176, 308, paint, 34),
        _rect(124, 58, 152, 284, phone, 26),
        _rect(134, 68, 56, 62, _shade(phone, 0.3), 14, 1.6),
    ]
    out += [_ell(152, 88, 9, 9, "#6c7a89", 1.6), _ell(172, 112, 9, 9, "#6c7a89", 1.6)]
    if style == "rugged":
        out += [
            _path(f"M{x},{y} l{dx * 26},0 l0,{dy * 26} Z", _shade(paint, 0.3), 1.6)
            for x, y, dx, dy in (
                (112, 46, 1, 1),
                (288, 46, -1, 1),
                (112, 354, 1, -1),
                (288, 354, -1, -1),
            )
        ]
    elif style == "wallet":
        out += [
            _line("M276,60 L276,340", 5, "", _shade(paint, 0.3)),
            _rect(268, 190, 30, 20, _tint(paint, 0.3), 4, 1.6),
        ]
    else:
        out.append(_highlight_line())
    return _label(out, label)


def _highlight_line() -> str:
    return _line("M130,330 L270,70", 6, ' stroke-opacity="0.35"', "#ffffff")


def screen_protector(paint: str, fill: Fill, label: str | None, finish: str = "clear") -> list[str]:
    """A phone under a glass sheet: ``clear`` a gloss line, ``matte`` a stipple, ``privacy`` louver stripes."""
    out = [
        _rect(120, 50, 160, 300, "#2a2a2e", 28),
        _screen(130, 62, 140, 276, 16),
        _rect(112, 40, 176, 320, "none", 30, 2.4),
    ]
    if finish == "matte":
        out += [
            _ell(140 + (i * 37) % 120, 80 + (i * 53) % 240, 1.8, 1.8, GLASS, 0) for i in range(40)
        ]
    elif finish == "privacy":
        out += [_line(f"M{132 + 14 * i},64 L{132 + 14 * i},336", 1.6, "", GLASS) for i in range(9)]
    else:
        out.append(_highlight_line())
    out.append(_rect(168, 16, 64, 18, paint, 6, 1.6))
    return _label(out, label)


def charger(paint: str, fill: Fill, label: str | None, kind: str = "wall") -> list[str]:
    """A charger: a ``wall`` plug with prongs, a ``wireless`` pad, a ``power_bank`` and a ``car`` adapter."""
    if kind == "wireless":
        out = [
            _ell(200, 230, 120, 40, _shade(paint, 0.2)),
            _ell(200, 214, 120, 40, paint),
            _ell(200, 214, 70, 20, _tint(paint, 0.3), 1.6),
            _line("M320,214 C360,240 360,300 330,330", 5),
        ]
    elif kind == "power_bank":
        out = (
            [_rect(120, 90, 160, 220, paint, 22)]
            + [_ell(160 + 26 * i, 130, 7, 7, "#2fbf71" if i < 3 else PAPER2, 1.6) for i in range(4)]
            + [_rect(176, 296, 48, 12, SCREEN, 3, 1.4)]
        )
    elif kind == "car":
        out = [
            _rect(150, 92, 100, 150, paint, 14),
            _rect(166, 242, 68, 26, _shade(paint, 0.3), 6),
            _rect(184, 268, 32, 40, "#b8c2cc", 4),
            _ell(200, 130, 12, 12, "#2fbf71", 1.6),
        ]
    else:
        out = [
            _rect(130, 90, 140, 150, paint, 20),
            _rect(168, 240, 12, 30, "#b8c2cc", 2),
            _rect(220, 240, 12, 30, "#b8c2cc", 2),
            _line("M200,90 C200,50 300,40 330,70", 5),
        ]
    return _label(out, label)


def cable(paint: str, fill: Fill, label: str | None, end: str = "usb_c") -> list[str]:
    """A cable: a loop between two connectors; ``usb_c`` has rounded tips, ``micro`` a flat tapered tip, ``multi`` three heads."""
    out = [
        _line("M96,200 C96,70 304,70 304,200 C304,320 120,330 120,250", 9, "", paint),
        _line("M96,200 C96,70 304,70 304,200 C304,320 120,330 120,250", 3, "", INK),
    ]
    out += [_rect(80, 200, 32, 44, "#b8c2cc", 6), _rect(88, 244, 16, 24, SCREEN, 3, 1.6)]
    if end == "micro":
        out += [_path("M104,274 L136,274 L126,296 L114,296 Z", "#b8c2cc", 1.6)]
    elif end == "multi":
        out += [_rect(256, 200 + 22 * i, 36, 14, "#b8c2cc", 4, 1.6) for i in range(3)]
    else:
        out += [_rect(288, 200, 32, 44, "#b8c2cc", 14), _rect(296, 244, 16, 24, SCREEN, 3, 1.6)]
    return _label(out, label)


def earbuds(paint: str, fill: Fill, label: str | None, form: str = "buds") -> list[str]:
    """Earbuds in their case, or over-ear headphones on a band."""
    if form == "over_ear":
        out = [
            _line("M110,230 C110,70 290,70 290,230", 12, "", _shade(paint, 0.2)),
            _rect(84, 200, 52, 98, paint, 22),
            _rect(264, 200, 52, 98, paint, 22),
            _rect(96, 218, 28, 62, _shade(paint, 0.25), 12, 1.6),
            _rect(276, 218, 28, 62, _shade(paint, 0.25), 12, 1.6),
        ]
        return _label(out, label)
    out = [
        _rect(130, 220, 140, 90, paint, 30),
        _line("M130,250 L270,250", 2),
        _ell(200, 232, 5, 5, "#2fbf71", 1.2),
    ]
    for sx in (-1, 1):
        cx = 200 + sx * 62
        out += [
            _path(
                f"M{cx - 14},120 C{cx - 16},170 {cx - 4},196 {cx},196 C{cx + 4},196 {cx + 16},170 {cx + 14},120 Z",
                PAPER2,
                2.4,
            ),
            _ell(cx, 112, 26, 26, paint),
        ]
    return _label(out, label)


def laptop_sleeve(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A padded sleeve with a zip along the top and a pull tab."""
    out = [
        _rect(70, 110, 260, 190, paint, 22),
        _line("M84,150 L316,150", 3.5, "", _shade(paint, 0.35)),
        _rect(300, 138, 16, 24, "#b8c2cc", 4, 1.6),
    ]
    out += [
        _line(f"M{96 + 40 * i},166 L{96 + 40 * i},284", 1.8, "", _shade(paint, 0.2))
        for i in range(6)
    ]
    out.append(_rect(110, 90, 180, 24, SCREEN, 4, 1.6))
    return _label(out, label)


def mouse(paint: str, fill: Fill, label: str | None, form: str = "wireless") -> list[str]:
    """A computer mouse: ``wireless`` a plain oval with two buttons and a wheel, ``gaming`` side buttons and a light strip, ``ergonomic`` a tall vertical grip."""
    if form == "ergonomic":
        out = [
            _path(
                "M150,320 C120,250 130,140 190,90 C240,60 290,100 280,190 C274,260 250,320 150,320 Z",
                paint,
            ),
            _line("M180,100 C200,150 200,180 190,220", 2.4),
            _line("M170,262 C210,250 240,230 262,204", 2.4),
        ]
        return _label(out, label)
    out = [
        _path(
            "M200,60 C290,60 300,150 300,230 C300,320 260,350 200,350 C140,350 100,320 100,230 C100,150 110,60 200,60 Z",
            paint,
        ),
        _line("M100,160 L300,160", 2.4),
        _line("M200,60 L200,160", 2.4),
        _rect(192, 96, 16, 36, PAPER2, 6, 1.6),
    ]
    if form == "gaming":
        out += [
            _rect(92, 190, 14, 28, "#c8312e", 4, 1.6),
            _rect(92, 226, 14, 28, "#c8312e", 4, 1.6),
            _line("M130,330 C170,342 230,342 270,330", 4, "", "#2fbf71"),
        ]
    return _label(out, label)


def keyboard(paint: str, fill: Fill, label: str | None, layout: str = "full") -> list[str]:
    """A keyboard: ``full`` with a number pad, ``compact`` without."""
    w = 300 if layout == "full" else 240
    x = 200 - w / 2
    out = [_rect(x - 14, 130, w + 28, 150, paint, 14)]
    for r in range(4):
        for c in range(int((w - 14) // 22)):
            out.append(_rect(x + c * 22, 144 + r * 28, 18, 22, PAPER2, 3, 1.4))
    out.append(_rect(x + 40, 256, 120, 16, PAPER2, 3, 1.4))
    return _label(out, label)


def monitor(paint: str, fill: Fill, label: str | None, form: str = "standard") -> list[str]:
    """A monitor on a stand: ``standard`` 16:9, ``ultrawide`` a long panel, ``curved`` a bowed panel."""
    if form == "ultrawide":
        out = [_rect(40, 110, 320, 120, paint, 8), _screen(50, 120, 300, 100, 3)]
    elif form == "curved":
        out = [
            _path("M60,86 C160,120 240,120 340,86 L340,246 C240,280 160,280 60,246 Z", paint),
            _path(
                "M72,102 C160,132 240,132 328,102 L328,230 C240,260 160,260 72,230 Z", SCREEN, 1.6
            ),
        ]
    else:
        out = [_rect(70, 80, 260, 160, paint, 10), _screen(80, 90, 240, 136, 4)]
    out += [
        _path("M184,242 L216,242 L224,300 L176,300 Z", _tint(paint, 0.2)),
        _rect(140, 300, 120, 14, _tint(paint, 0.2), 6),
    ]
    return _label(out, label)


def dishwasher_tablets(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A tub of dishwasher tablets: a lidded tub and tablets stood beside it."""
    out = [_rect(110, 130, 160, 170, paint, 14), _rect(104, 114, 172, 28, _shade(paint, 0.25), 8)]
    out += [_rect(296 + 0, 244 + 18 * i, 52, 14, PAPER2, 6, 1.6) for i in range(3)]
    out.append(_ell(190, 214, 40, 40, PAPER2, 1.6))
    return _label(out, label)


SHAPES = {
    "smartphone": smartphone, "basic_phone": basic_phone, "laptop": laptop, "desktop": desktop,
    "tablet": tablet, "e_reader": e_reader, "phone_case": phone_case,
    "screen_protector": screen_protector, "charger": charger, "cable": cable,
    "earbuds": earbuds, "laptop_sleeve": laptop_sleeve, "mouse": mouse, "keyboard": keyboard,
    "monitor": monitor, "dishwasher_tablets": dishwasher_tablets,

}  # fmt: skip
register(SHAPES)
