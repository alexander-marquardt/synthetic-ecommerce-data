"""Gaming for the retail drawing kit: game controllers and gaming headsets (gen#956, slice 2b),
video games and consoles (gen#1120).

===============  ============================================  ==================================
shape            draws                                         params
===============  ============================================  ==================================
game_controller  a gamepad with a d-pad, two sticks and four   controller_form (classic, pro,
                 face buttons; ``pro`` adds triggers and two   mobile), connection (wireless,
                 back paddles, ``mobile`` is two grips either  wired)
                 side of a phone; a cable when wired, a lit
                 bar when wireless
gaming_headset   a headband, two ear cups with lit rings and   connection (wireless, wired)
                 a boom mic; a cable and plug when wired, a
                 power light when wireless
video_game       a game case with its cover art and a disc     format (disc, download code),
                 beside it; ``download code`` is a card with   edition (standard, deluxe)
                 a code strip; ``deluxe`` adds a slipcover
                 behind and a gold band
game_console     a console box with a disc slot and a power    console_form (home, slim,
                 light; ``slim`` is thinner, ``handheld`` a    handheld)
                 screen between two sets of controls
===============  ============================================  ==================================

Each param's values are the lower-cased attribute values of the spec rows. A derived style that
changes a controller's ``controller_form`` or either type's ``connection`` draws what it states
(gen#512). Video games and consoles are templates only (gen#1120), so no derived style redraws
them.
"""

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
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: A stick's and a phone screen's dark plastic, a plug's metal.
MESH = "#3a3b40"
STEEL = "#c3c7cd"
#: A power light's green and a lit ring's cyan.
LIGHT = "#2fbf71"
GLOW = "#5fd3e8"
#: A deluxe edition's gold band.
GOLD = "#d4a537"
#: The four face buttons.
FACE = ("#2fbf71", "#c8312e", "#3f6fb5", "#f2c230")

_PAD = ("M90,170 C90,130 130,118 160,124 L240,124 C270,118 310,130 310,170 L330,270 "
        "C336,306 300,318 282,296 L254,258 L146,258 L118,296 C100,318 64,306 70,270 Z")  # fmt: skip


def _controls(lx: float, rx: float, y: float, fill: Fill) -> list[str]:
    """A d-pad centered at (``lx``, ``y``) and four face buttons centered at (``rx``, ``y``)."""
    out = [
        _rect(lx - 7, y - 22, 14, 44, _shade(fill.base, 0.4), 3, LW_DETAIL),
        _rect(lx - 22, y - 7, 44, 14, _shade(fill.base, 0.4), 3, LW_DETAIL),
    ]
    spots = ((0, -16), (16, 0), (0, 16), (-16, 0))
    pairs = zip(spots, FACE, strict=True)
    out += [_ell(rx + dx, y + dy, 7, 7, c, LW_DETAIL) for (dx, dy), c in pairs]
    return out


def game_controller(paint: str, fill: Fill, label: str | None, controller_form: str = "classic",
                    connection: str = "wireless") -> list[str]:  # fmt: skip
    """A game controller by ``controller_form``; a cable when ``connection`` is wired."""
    if controller_form == "mobile":
        out = [
            _rect(122, 150, 156, 120, MESH, 10, LW_DETAIL),
            _rect(134, 160, 132, 100, "#1f2024", 6, LW_DETAIL),
            _rect(48, 140, 80, 150, paint, 30),
            _rect(272, 140, 80, 150, paint, 30),
            *_controls(88, 312, 190, fill),
            _ell(88, 248, 16, 16, MESH, LW_DETAIL),
            _ell(312, 248, 16, 16, MESH, LW_DETAIL),
            _highlight("M60,170 L60,260", 4, 0.5),
        ]
        cable = "M88,290 C88,330 120,350 160,356"
        bar = (180, 136)
    else:
        out = []
        if controller_form == "pro":
            out += [_rect(110, 100, 56, 30, _shade(fill.base, 0.3), 10, LW_DETAIL),
                    _rect(234, 100, 56, 30, _shade(fill.base, 0.3), 10, LW_DETAIL)]  # fmt: skip
        out += [_path(_PAD, paint), *_controls(140, 260, 172, fill)]
        out += [_ell(x, 226, 18, 18, MESH, LW_DETAIL) for x in (172, 228)]
        if controller_form == "pro":
            out += [_rect(96, 300, 30, 14, _shade(fill.base, 0.35), 5, LW_DETAIL),
                    _rect(274, 300, 30, 14, _shade(fill.base, 0.35), 5, LW_DETAIL)]  # fmt: skip
        out.append(_highlight("M104,150 C112,136 128,132 146,134", 4, 0.5))
        cable = "M200,124 C200,80 240,60 290,44"
        bar = (180, 140)
    if connection == "wired":
        out.append(_line(cable, 5.0))
    else:
        out.append(_rect(bar[0], bar[1], 40, 6, LIGHT, 3, 1.0))
    return _label(out, label)


def gaming_headset(paint: str, fill: Fill, label: str | None,
                   connection: str = "wired") -> list[str]:  # fmt: skip
    """A gaming headset with a boom mic; a cable and plug when ``connection`` is wired."""
    out = [
        _path("M100,210 C100,70 300,70 300,210 L280,210 C280,96 120,96 120,210 Z", paint),
        _rect(150, 98, 100, 14, _shade(fill.base, 0.3), 7, LW_DETAIL),
        _rect(76, 186, 68, 116, paint, 28),
        _rect(256, 186, 68, 116, paint, 28),
        _rect(140, 198, 16, 92, _shade(fill.base, 0.45), 6, LW_DETAIL),
        _rect(244, 198, 16, 92, _shade(fill.base, 0.45), 6, LW_DETAIL),
        _ell(110, 244, 18, 30, GLOW, LW_DETAIL),
        _ell(290, 244, 18, 30, GLOW, LW_DETAIL),
        _line("M104,292 C104,340 150,352 186,340", 6.0),
        _ell(192, 338, 11, 9, MESH, LW_DETAIL),
    ]
    if connection == "wired":
        out += [_line("M300,302 C306,340 290,364 262,374", 4.0),
                _rect(242, 366, 22, 14, STEEL, 3, LW_DETAIL)]  # fmt: skip
    else:
        out.append(_ell(290, 200, 5, 5, LIGHT, 1.2))
    out.append(_highlight("M118,170 C122,124 150,98 184,92", 5, 0.5))
    return _label(out, label)


def video_game(paint: str, fill: Fill, label: str | None, format: str = "disc",
               edition: str = "standard") -> list[str]:  # fmt: skip
    """A video game by ``format``: a case and its disc, or a download code card; ``deluxe`` adds
    a slipcover behind it and a gold band across it."""
    art = _tint(fill.base, 0.45)
    out: list[str] = []
    if format == "download code":
        if edition == "deluxe":
            out.append(_rect(100, 112, 240, 150, _shade(fill.base, 0.3), 12, LW_DETAIL))
        out += [
            _rect(70, 130, 260, 160, paint, 12),
            _rect(90, 150, 100, 120, art, 6, LW_DETAIL),
            _rect(206, 226, 108, 28, STEEL, 4, LW_DETAIL),
            _line("M216,240 L304,240", 2.0),
        ]
        emblem, band, gloss = (140, 210), (70, 160, 260), "M84,146 L84,276"
    else:
        if edition == "deluxe":
            out.append(_rect(136, 44, 180, 300, _shade(fill.base, 0.3), 10, LW_DETAIL))
        out += [
            _ell(262, 204, 92, 92, STEEL, LW_DETAIL),
            _ell(262, 204, 22, 22, "#ffffff", LW_DETAIL),
            _rect(100, 60, 180, 290, paint, 10),
            _rect(100, 60, 20, 290, _shade(fill.base, 0.35), 4, LW_DETAIL),
            _rect(136, 104, 128, 160, art, 6, LW_DETAIL),
        ]
        emblem, band, gloss = (200, 184), (120, 290, 160), "M112,80 L112,330"
    out.append(_ell(*emblem, 30, 30, _shade(fill.base, 0.5), LW_DETAIL))
    if edition == "deluxe":
        x, y, w = band
        out.append(_rect(x, y, w, 18, GOLD, 2, LW_DETAIL))
    out.append(_highlight(gloss, 4, 0.5))
    return _label(out, label)


def game_console(paint: str, fill: Fill, label: str | None,
                 console_form: str = "home") -> list[str]:  # fmt: skip
    """A game console by ``console_form``: a home box (``slim`` is thinner) with a disc slot and
    a power light, or a handheld with its screen between two sets of controls."""
    if console_form == "handheld":
        out = [
            _rect(40, 140, 320, 150, paint, 44),
            _rect(118, 158, 164, 114, MESH, 8, LW_DETAIL),
            _rect(128, 168, 144, 94, "#1f2024", 4, LW_DETAIL),
            *_controls(80, 320, 194, fill),
            _ell(80, 254, 14, 14, MESH, LW_DETAIL),
            _ell(320, 254, 14, 14, MESH, LW_DETAIL),
            _highlight("M64,170 L64,260", 4, 0.5),
        ]
        return _label(out, label)
    y, h = (164, 72) if console_form == "slim" else (128, 128)
    out = [
        _rect(50, y, 300, h, paint, 14),
        _rect(50, y + h - 18, 300, 18, _shade(fill.base, 0.35), 6, LW_DETAIL),
        _rect(80, y + 22, 140, 9, MESH, 3, LW_DETAIL),
        _ell(318, y + 26, 6, 6, LIGHT, 1.2),
        _rect(290, y + 44, 40, 8, _shade(fill.base, 0.25), 3, LW_DETAIL),
        _highlight(f"M66,{y + 14} L200,{y + 14}", 4, 0.5),
    ]
    return _label(out, label)


SHAPES = {"game_controller": game_controller, "gaming_headset": gaming_headset,
          "video_game": video_game, "game_console": game_console}  # fmt: skip
register(SHAPES)
