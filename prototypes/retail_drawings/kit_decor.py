"""Home accessories and decor shapes for the retail drawing kit (gen#217).

Each type of the specs of gen#217 (``type_specs/clock.py`` and the rest) has its own flat drawing in the kit's house style: outlines in the
kit's ink, the record's fill (color and pattern) on the product's main surface.

===============  ==========================================  ==========================
shape            draws                                       params
===============  ==========================================  ==========================
clock            a round wall clock, an arched mantel clock  type (wall, mantel, alarm)
                 or a twin-bell alarm clock
ornament         a vase, a bird figure or a glass orb        form (vase, bird, orb)
                 on a stand
stems            a bunch of artificial stems: eucalyptus,    flower (eucalyptus, peony,
                 peony, rose or pampas, loose or in a vase   rose, pampas), holder (loose,
                                                             vase)
trinket_tray     a round or a rectangular tray with a rim    outline (round, rectangular)
wallpaper        a roll with its paper unrolled              finish (matt, metallic)
diary            a closed diary with a ribbon marker,        band (no, yes)
                 with or without an elastic band
picnic_blanket   a blanket laid flat, with a lifted corner   backing (plain, waterproof)
                 that shows its underside
door_stop        a wedge, or a weighted stop with a handle   kind (wedge, weighted)
===============  ==========================================  ==========================

A drawing never prints a size, a year or a diameter: a style's SKUs share one image per colorway.
Every param is a
string with a default, so each shape also draws bare. The foliage, a ribbon or a sheet's reverse
is never the product's color; the fill paints the main surface only.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, Fill, _highlight, _line, _panel, _path, _shade, _tint, register

LEAF = "#5f8a4e"
LEAF_DARK = "#44683a"
STEM = "#4e6e3f"
METAL = "#8d949c"
PAPER = "#fbfaf6"
#: Marks around a clock face: one per hour.
HOURS = 12


def _ell(cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _rect(x: float, y: float, w: float, h: float, fill: str, r: float = 6, width: float = LW) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _label(out: list[str], label: str | None) -> list[str]:
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


# --------------------------------------------------------------------------
# Clocks
# --------------------------------------------------------------------------


def _dial(cx: float, cy: float, r: float) -> list[str]:
    """A clock face: paper, hour marks, two hands and a pin (the same time on every clock)."""
    out = [_ell(cx, cy, r, r, PAPER, 2.4)]
    for h in range(HOURS):
        a = math.radians(h * 30)
        inner = r * (0.78 if h % 3 == 0 else 0.86)
        out.append(_line(f"M{cx + inner * math.sin(a):.1f},{cy - inner * math.cos(a):.1f} L{cx + r * 0.94 * math.sin(a):.1f},{cy - r * 0.94 * math.cos(a):.1f}", 2.4))
    out += [
        _line(f"M{cx},{cy} L{cx - r * 0.3:.1f},{cy - r * 0.42:.1f}", 4.4),
        _line(f"M{cx},{cy} L{cx + r * 0.48:.1f},{cy - r * 0.2:.1f}", 3.0),
        _ell(cx, cy, 5, 5, INK, 1),
    ]
    return out


def clock(paint: str, fill: Fill, label: str | None, type: str = "wall") -> list[str]:  # noqa: A002
    """A clock: ``wall`` (a round frame), ``mantel`` (an arched case on feet) or ``alarm`` (twin bells)."""
    dark = _shade(fill.base, 0.3)
    kind = type.lower()
    if kind == "mantel":
        out = [
            _path("M96,330 L96,190 Q96,84 200,84 Q304,84 304,190 L304,330 Z", paint),
            _path("M80,330 L320,330 L320,352 L80,352 Z", dark),
            _path("M96,330 L96,348 M304,330 L304,348", 2),
            *_dial(200, 196, 78),
            _line("M168,300 L232,300", 2.4),
            _highlight("M112,172 Q114,120 160,100", 4, 0.5),
        ]
    elif kind == "alarm":
        out = [
            _line("M120,330 L100,360 M280,330 L300,360", 8),
            _path("M118,98 Q150,56 184,92 Z", dark),
            _path("M282,98 Q250,56 216,92 Z", dark),
            _line("M200,100 L200,84 M184,84 L216,84", 5),
            _ell(200, 214, 124, 124, paint),
            *_dial(200, 214, 90),
            _highlight("M104,178 Q112,130 150,112", 4, 0.5),
        ]
    else:
        out = [
            _ell(200, 200, 150, 150, paint),
            _ell(200, 200, 126, 126, dark, 2.4),
            *_dial(200, 200, 116),
            _highlight("M88,152 Q104,100 156,76", 5, 0.5),
        ]
    return _label(out, label)


# --------------------------------------------------------------------------
# Ornaments
# --------------------------------------------------------------------------


def ornament(paint: str, fill: Fill, label: str | None, form: str = "vase") -> list[str]:
    """A decorative object: a ``vase``, a ``bird`` figure or a glass ``orb`` on a stand."""
    dark = _shade(fill.base, 0.3)
    kind = form.lower()
    if kind == "bird":
        out = [
            _path("M70,300 Q70,200 150,190 Q150,120 210,120 Q250,120 262,150 L330,164 L262,178 Q250,250 300,290 L330,330 L236,330 Q200,330 190,300 Z", paint),
            _ell(222, 142, 5, 5, INK, 1),
            _path("M120,226 Q166,206 196,262 Q150,286 112,262 Z", dark, 2.4),
            _line("M150,330 L150,358 M210,330 L210,358 M140,358 L162,358 M200,358 L224,358", 4),
            _highlight("M96,262 Q94,226 126,206", 4, 0.5),
        ]
    elif kind == "orb":
        out = [
            _path("M150,350 L250,350 L238,318 L162,318 Z", dark),
            _ell(200, 196, 112, 112, paint),
            _ell(200, 196, 84, 84, "none", 1.6),
            _highlight("M122,150 Q140,100 196,90", 6, 0.6),
            _highlight("M262,250 Q244,284 210,294", 4, 0.35),
        ]
    else:
        out = [
            _path("M170,56 L230,56 L226,100 Q320,150 316,244 Q312,340 250,350 L150,350 Q88,340 84,244 Q80,150 174,100 Z", paint),
            _ell(200, 56, 30, 8, dark, 2.4),
            _line("M110,190 Q200,222 290,190", 2, ' stroke-opacity=".5"'),
            _highlight("M112,236 Q108,186 138,150", 5, 0.5),
        ]
    return _label(out, label)


# --------------------------------------------------------------------------
# Artificial flowers and stems
# --------------------------------------------------------------------------


def _leaves(x: float, y: float, n: int, dy: float, size: float) -> list[str]:
    out: list[str] = []
    for i in range(n):
        side = -1 if i % 2 else 1
        yy = y + i * dy
        out.append(_path(f"M{x},{yy} Q{x + side * size:.1f},{yy - size * 0.6:.1f} {x + side * size * 1.5:.1f},{yy - size * 0.1:.1f} Q{x + side * size * 0.8:.1f},{yy + size * 0.5:.1f} {x},{yy} Z", LEAF, 2))
    return out


def _bloom(kind: str, cx: float, cy: float, r: float, paint: str, dark: str) -> list[str]:
    if kind == "peony":
        return [_ell(cx, cy, r, r * 0.92, paint), _ell(cx, cy + 4, r * 0.74, r * 0.66, paint, 2), _ell(cx, cy + 6, r * 0.46, r * 0.4, dark, 2), _line(f"M{cx - r * 0.5:.1f},{cy - r * 0.2:.1f} Q{cx:.1f},{cy - r * 0.6:.1f} {cx + r * 0.5:.1f},{cy - r * 0.2:.1f}", 1.8)]
    return [
        _path(f"M{cx - r:.1f},{cy - r * 0.2:.1f} Q{cx - r:.1f},{cy - r * 1.1:.1f} {cx:.1f},{cy - r:.1f} Q{cx + r:.1f},{cy - r * 1.1:.1f} {cx + r:.1f},{cy - r * 0.2:.1f} Q{cx + r:.1f},{cy + r * 0.9:.1f} {cx:.1f},{cy + r:.1f} Q{cx - r:.1f},{cy + r * 0.9:.1f} {cx - r:.1f},{cy - r * 0.2:.1f} Z", paint),
        _path(f"M{cx - r * 0.5:.1f},{cy:.1f} Q{cx - r * 0.5:.1f},{cy - r * 0.6:.1f} {cx:.1f},{cy - r * 0.5:.1f} Q{cx + r * 0.5:.1f},{cy - r * 0.6:.1f} {cx + r * 0.5:.1f},{cy:.1f} Q{cx + r * 0.4:.1f},{cy + r * 0.5:.1f} {cx:.1f},{cy + r * 0.45:.1f} Z", dark, 2),
        _line(f"M{cx - r * 0.2:.1f},{cy - r * 0.1:.1f} Q{cx:.1f},{cy + r * 0.2:.1f} {cx + r * 0.25:.1f},{cy - r * 0.05:.1f}", 1.8),
    ]


def stems(paint: str, fill: Fill, label: str | None, flower: str = "eucalyptus", holder: str = "loose") -> list[str]:
    """Artificial stems: ``eucalyptus`` (leaf pairs), ``peony`` or ``rose`` (blooms), ``pampas`` (plumes); ``loose`` or in a ``vase``."""
    dark = _shade(fill.base, 0.3)
    kind = flower.lower()
    base = 300 if holder.lower() == "vase" else 352
    out: list[str] = []
    if kind == "pampas":
        for x, top in ((140, 70), (200, 40), (262, 84)):
            out += [_line(f"M{x},{base} L{x},{top + 60}", 5, stroke=STEM), _path(f"M{x},{top + 70} Q{x - 40},{top + 30} {x},{top} Q{x + 40},{top + 30} {x},{top + 70} Z", paint), _line(f"M{x},{top + 66} L{x},{top + 8}", 1.6, ' stroke-opacity=".5"'), _line(f"M{x},{top + 56} L{x - 18},{top + 30} M{x},{top + 56} L{x + 18},{top + 30}", 1.4, ' stroke-opacity=".5"')]
    elif kind == "eucalyptus":
        for x, top in ((150, 70), (200, 40), (252, 86)):
            out += [_line(f"M{x},{base} L{x},{top}", 5, stroke=STEM)]
            for i in range(5):
                y = top + 18 + i * 42
                if y > base - 30:
                    break
                for side in (-1, 1):
                    out.append(_ell(x + side * 22, y, 18, 11, paint, 2.4))
            out.append(_ell(x, top - 6, 11, 17, paint, 2.4))
    else:
        for x, top in ((142, 120), (206, 76), (264, 134)):
            out += [_line(f"M{x},{base} L{x},{top + 30}", 5, stroke=STEM), *_leaves(x, top + 90, 2, 52, 26)]
            out += _bloom(kind, x, top, 40 if kind == "peony" else 34, paint, dark)
    if holder.lower() == "vase":
        out += [
            _path("M150,300 L250,300 L262,352 Q262,360 250,360 L150,360 Q138,360 138,352 Z", "#dfe8ea"),
            _highlight("M154,312 L152,346", 4, 0.6),
        ]
    return _label(out, label)


# --------------------------------------------------------------------------
# Trays
# --------------------------------------------------------------------------


def trinket_tray(paint: str, fill: Fill, label: str | None, outline: str = "round") -> list[str]:
    """A decorative tray seen from above at an angle: ``round`` or ``rectangular``, with a raised rim."""
    dark = _shade(fill.base, 0.3)
    if outline.lower() == "rectangular":
        out = [
            _path("M50,170 L350,170 L376,290 L24,290 Z", paint),
            _path("M78,188 L322,188 L342,276 L58,276 Z", _tint(fill.base, 0.3), 2.4),
            _path("M24,290 L376,290 L376,314 L24,314 Z", dark, 2.4),
            _rect(150, 228, 100, 14, dark, 7, 2.4),
            _highlight("M80,182 L318,182", 4, 0.5),
        ]
    else:
        out = [
            _ell(200, 214, 170, 100, paint),
            _ell(200, 218, 138, 78, _tint(fill.base, 0.3), 2.4),
            _path("M30,214 Q30,262 80,290 Q200,330 320,290 Q370,262 370,214", "none", 2.4),
            _highlight("M80,160 Q130,130 200,126", 4, 0.5),
        ]
    return _label(out, label)


# --------------------------------------------------------------------------
# Wallpaper
# --------------------------------------------------------------------------


def wallpaper(paint: str, fill: Fill, label: str | None, finish: str = "matt") -> list[str]:
    """A wallpaper roll with its paper unrolled to the right; ``metallic`` adds a sheen."""
    dark = _shade(fill.base, 0.3)
    out = [
        _path("M130,90 L338,90 L338,326 L130,326 Z", paint),
        _path("M96,70 L132,70 L132,346 L96,346 Z", paint),
        _ell(114, 70, 18, 10, _tint(fill.base, 0.25)),
        _ell(114, 346, 18, 10, paint),
        _ell(114, 70, 6, 4, dark, 1.6),
        _line("M338,90 L338,326", 4),
    ]
    if finish.lower() == "metallic":
        out += [_highlight("M160,120 L300,300", 8, 0.55), _highlight("M200,100 L322,260", 5, 0.4)]
    else:
        out += [_line("M150,120 L320,120 M150,180 L320,180 M150,240 L320,240 M150,300 L320,300", 1.4, ' stroke-opacity=".25"')]
    return _label(out, label)


# --------------------------------------------------------------------------
# Diaries
# --------------------------------------------------------------------------


def diary(paint: str, fill: Fill, label: str | None, band: str = "no") -> list[str]:
    """A closed diary: a hard cover, a spine, a ribbon marker; ``yes`` adds an elastic band."""
    dark = _shade(fill.base, 0.3)
    out = [
        _path("M96,48 L316,48 Q330,48 330,62 L330,338 Q330,352 316,352 L96,352 Z", paint),
        _path("M70,56 L96,48 L96,352 L70,344 Z", dark, 2.4),
        _line("M310,52 L310,348", 2, ' stroke-opacity=".45"'),
        _line("M276,352 L276,378 L286,368 L296,378 L296,352", 3, stroke="#c0392b"),
        _rect(140, 96, 130, 60, "none", 6, 2),
        _highlight("M112,64 L112,330", 4, 0.4),
    ]
    if band.lower() == "yes":
        out += [_path("M236,48 L252,48 L252,352 L236,352 Z", dark, 2)]
    return _label(out, label)


# --------------------------------------------------------------------------
# Picnic blankets and door stops
# --------------------------------------------------------------------------


def picnic_blanket(paint: str, fill: Fill, label: str | None, backing: str = "plain") -> list[str]:
    """A blanket laid flat with a lifted corner; the underside of a ``waterproof`` one is a glossy backing."""
    dark = _shade(fill.base, 0.3)
    under = "#8fb4c4" if backing.lower() == "waterproof" else dark
    out = [
        _path("M110,130 L370,130 L330,310 L40,310 Z", paint),
        _path("M40,310 L330,310 L330,324 L40,324 Z", dark, 2.4),
        _path("M330,310 L370,130 L378,142 L338,324 Z", dark, 2.4),
        _path("M40,310 L110,130 L150,236 Z", under, 2.4),
        _path("M40,310 L150,236 L150,310 Z", paint, 2.4),
        _line("M150,236 L124,310", 2, ' stroke-opacity=".5"'),
    ]
    for x in range(52, 334, 32):
        out.append(_line(f"M{x},324 L{x - 4},346", 2.4))
    if backing.lower() == "waterproof":
        out += [_highlight("M62,286 L112,166", 4, 0.6)]
    return _label(out, label)


def door_stop(paint: str, fill: Fill, label: str | None, kind: str = "wedge") -> list[str]:
    """A door stop: a ``wedge`` of rubber or wood, or a ``weighted`` cylinder with a carrying handle."""
    dark = _shade(fill.base, 0.3)
    if kind.lower() == "weighted":
        out = [
            _path("M130,150 Q130,100 200,100 Q270,100 270,150", "none", 7),
            _path("M130,150 Q130,100 200,100 Q270,100 270,150", "none", 3, stroke=METAL),
            _path("M110,150 L290,150 L300,330 Q300,350 280,350 L120,350 Q100,350 100,330 Z", paint),
            _ell(200, 150, 90, 18, _tint(fill.base, 0.2)),
            _line("M112,300 L288,300", 2, ' stroke-opacity=".4"'),
            _highlight("M124,176 L130,320", 5, 0.5),
        ]
    else:
        out = [
            _path("M40,320 L360,320 L360,230 Q330,200 40,320 Z", paint),
            _path("M40,320 L360,320 L360,340 L40,340 Z", dark, 2.4),
            _line("M110,296 L330,236 M150,312 L340,262 M210,316 L346,282", 1.6, ' stroke-opacity=".4"'),
            _highlight("M80,306 L300,246", 4, 0.5),
        ]
    return _label(out, label)


SHAPES = {
    "clock": clock, "ornament": ornament, "stems": stems, "trinket_tray": trinket_tray,
    "wallpaper": wallpaper, "diary": diary,
    "picnic_blanket": picnic_blanket, "door_stop": door_stop,
}  # fmt: skip
register(SHAPES)
