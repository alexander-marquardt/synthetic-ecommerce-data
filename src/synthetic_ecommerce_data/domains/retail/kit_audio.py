"""Audio for the retail drawing kit (gen#956): headphones, portable speakers and soundbars.

================  ============================================  ===================================
shape             draws                                         params
================  ============================================  ===================================
headphones        a headband over two ear cups: large ovals     fit (over-ear, on-ear), connection
                  that cover the ear, or small round pads; a    (wireless, wired, usb-c)
                  cable and a jack, a cable and a USB-C plug,
                  or a power light on a cup
portable_speaker  an upright cylinder speaker with its grille,  speaker_size (mini, compact,
                  a carry loop and buttons, drawn small,        large)
                  medium or tall
soundbar          a long bar with a driver per front channel,   channels (2.0, 2.1, 3.1, 5.1)
                  and a subwoofer box beside it when the
                  channels end in .1
================  ============================================  ===================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a headphone's ``fit`` or a soundbar's ``channels`` draws what it states (gen#512).
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

#: The dark mesh of a grille and the cushion of an ear pad.
MESH = "#3a3b40"
#: A plug's metal and a power light's green.
STEEL = "#c3c7cd"
LIGHT = "#2fbf71"


def _plug(connection: str) -> list[str]:
    """The cable down from the left cup and its plug: a 3.5 mm jack or a USB-C plug."""
    out = [_line("M112,312 C112,340 150,346 170,352", 3.0)]
    if connection == "usb-c":
        plug = [_rect(166, 342, 30, 20, STEEL, 4, LW_DETAIL), _rect(195, 347, 10, 10, MESH, 3)]
        return [*out, *plug]
    return [*out, _rect(166, 344, 22, 16, MESH, 3, LW_DETAIL), _rect(187, 349, 18, 6, STEEL, 2)]


def headphones(paint: str, fill: Fill, label: str | None, fit: str = "over-ear",
               connection: str = "wireless") -> list[str]:  # fmt: skip
    """Headphones: the band, two cups by ``fit`` and, by ``connection``, a cable or a light."""
    over = fit == "over-ear"
    rx, ry = (40, 62) if over else (32, 38)
    out = [
        _path("M100,236 C100,60 300,60 300,236 L284,236 C284,84 116,84 116,236 Z",
              _shade(fill.base, 0.15)),  # fmt: skip
        _rect(176, 64, 48, 18, MESH, 8, LW_DETAIL),
    ]
    for cx in (108, 292):
        out += [
            _ell(cx, 250, rx, ry, paint),
            _ell(cx, 250, rx - 12, ry - 14, _shade(fill.base, 0.3), LW_DETAIL),
        ]
    if connection == "wireless":
        out += [_ell(292, 296 if over else 278, 4, 4, LIGHT, 1.2)]
    else:
        out += _plug(connection)
    out.append(_highlight(f"M{108 - rx + 10},236 C{108 - rx + 10},210 98,200 108,196", 4, 0.5))
    return _label(out, label)


def portable_speaker(paint: str, fill: Fill, label: str | None,
                     speaker_size: str = "compact") -> list[str]:  # fmt: skip
    """An upright cylinder speaker: body, grille, a carry loop and buttons, by ``speaker_size``."""
    w, h = {"mini": (90, 120), "compact": (120, 190), "large": (150, 260)}[speaker_size]
    x0, y1 = 200 - w / 2, 330
    y0 = y1 - h
    out = [
        _rect(x0, y0, w, h, paint, w / 2.4),
        _rect(x0 + 10, y0 + 30, w - 20, h - 60, MESH, 10, LW_DETAIL),
        _line(f"M{x0 + w * 0.3:.1f},{y0} C{x0 + w * 0.3:.1f},{y0 - 34} "
              f"{x0 + w * 0.7:.1f},{y0 - 34} {x0 + w * 0.7:.1f},{y0}", 6,
              "", _shade(fill.base, 0.35)),  # fmt: skip
    ]
    out += [_line(f"M{x0 + 16},{y} L{x0 + w - 16},{y}", 1.0, "", _tint(MESH, 0.3))
            for y in range(int(y0) + 42, int(y1) - 36, 10)]  # fmt: skip
    out += [_ell(200 + dx, y0 + 15, 5, 5, _tint(fill.base, 0.5), LW_DETAIL) for dx in (-16, 0, 16)]
    out.append(_highlight(f"M{x0 + 6},{y0 + 40} L{x0 + 6},{y1 - 40}", 4, 0.5))
    return _label(out, label)


def soundbar(paint: str, fill: Fill, label: str | None, channels: str = "2.1") -> list[str]:
    """A soundbar: the bar and a driver per front channel, and a subwoofer box for a ``.1``."""
    fronts = int(channels.split(".")[0])
    sub = channels.endswith(".1")
    x0, x1 = (30, 290) if sub else (40, 360)
    out = [
        _rect(x0, 170, x1 - x0, 56, paint, 22),
        _rect(x0 + 14, 180, x1 - x0 - 28, 36, MESH, 14, LW_DETAIL),
    ]
    step = (x1 - x0 - 60) / max(fronts - 1, 1)
    out += [_ell(x0 + 30 + i * step, 198, 11, 11, _tint(MESH, 0.25), LW_DETAIL)
            for i in range(fronts)]  # fmt: skip
    if sub:
        out += [
            _rect(300, 150, 80, 170, paint, 10),
            _ell(340, 250, 28, 28, MESH, LW_DETAIL),
            _ell(340, 250, 10, 10, _tint(MESH, 0.25), LW_DETAIL),
        ]
    out.append(_highlight(f"M{x0 + 24},176 L{x1 - 24},176", 3, 0.5))
    return _label(out, label)


SHAPES = {"headphones": headphones, "portable_speaker": portable_speaker, "soundbar": soundbar}
register(SHAPES)
