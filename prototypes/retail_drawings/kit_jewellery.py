"""Hoop and drop earrings, analog and digital watches and a fitness band for the kit (gen#423).

Each type is drawn as its own object, on the kit's 400 x 400 sheet, in its house style: ink
outlines, the record's fill on the product's main surface (the metal of an earring, the strap of
a watch). A statement a row makes about the product is a parameter here, so a title that says
"twisted" or "pearl" or "four buttons" is a drawing that shows it.

==============  ==================================================  ===========================
shape           draws                                               params
==============  ==================================================  ===========================
hoop_earrings   a pair of hoops hung from ear wires                 size (small, medium, large),
                                                                    band (plain, twisted, beaded)
drop_earrings   a pair of posts, each with a hanging drop           drop (pearl, teardrop, bar),
                                                                    gem (a color, default pearl)
analog_watch    a round case, dial and hands on a strap             strap (leather, mesh, fabric),
                                                                    case (steel, gold, rose)
digital_watch   a square case with an LCD and side buttons          buttons (2, 4)
fitness_band    a slim touch screen on a ribbed silicone band       screen (heart, steps, clock)
==============  ==================================================  ===========================

Every params value is a string, as a style row's ``params`` carry it.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _word, register
from kit_more import _circle, _ring

STEEL, GOLD_CASE, ROSE_CASE = "#cfd5da", "#d4af37", "#d8a28f"
CASES = {"steel": STEEL, "gold": GOLD_CASE, "rose": ROSE_CASE}
PEARL = "#f4efe6"
SCREEN = "#c9d6c4"
HOOP_RADIUS = {"small": 30.0, "medium": 44.0, "large": 58.0}


def _choice(what: str, value: str, options: tuple[str, ...]) -> str:
    if value not in options:
        raise ValueError(f"unknown {what} {value!r}; {', '.join(options)}")
    return value


def hoop_earrings(paint: str, fill: Fill, label: str | None, size: str = "medium", band: str = "plain") -> list[str]:
    """A pair of hoops in the record's metal: ``size`` sets the diameter, ``band`` the wire (plain, twisted rope or beaded)."""
    r = HOOP_RADIUS[_choice("hoop size", size, tuple(HOOP_RADIUS))]
    _choice("hoop band", band, ("plain", "twisted", "beaded"))
    out: list[str] = []
    for cx in (118, 282):
        cy = 150 + r
        out += [_line(f"M{cx},{cy - r - 22:.1f} L{cx},{cy - r:.1f}", 4), _circle(cx, cy - r - 24, 5, paint, 1.6)]
        if band == "beaded":
            out += _ring(cx, cy, r, paint, 4)
            for k in range(14):
                a = math.radians(k * 360 / 14)
                out.append(_circle(cx + r * math.sin(a), cy - r * math.cos(a), 5, paint, 1.4))
        else:
            out += _ring(cx, cy, r, paint, 11 if band == "twisted" else 9)
            if band == "twisted":
                for k in range(22):
                    a = math.radians(k * 360 / 22)
                    d = f"M{cx + (r - 6) * math.sin(a):.1f},{cy - (r - 6) * math.cos(a):.1f} L{cx + (r + 6) * math.sin(a + 0.25):.1f},{cy - (r + 6) * math.cos(a + 0.25):.1f}"
                    out.append(_line(d, 1.4, ' stroke-opacity=".55"'))
        out.append(_highlight(f"M{cx - r * 0.7:.1f},{cy - r * 0.5:.1f} Q{cx - r * 0.55:.1f},{cy - r * 0.85:.1f} {cx - r * 0.1:.1f},{cy - r * 1.02:.1f}", 3, 0.6))
    if label:
        out.append(_word(label, 200, 330, 200, 22))
    return out


def drop_earrings(paint: str, fill: Fill, label: str | None, drop: str = "pearl", gem: str = PEARL) -> list[str]:
    """A pair of drop earrings: a metal post and cap, a short chain and a hanging ``drop`` (pearl, teardrop or bar) of the ``gem`` color."""
    _choice("drop", drop, ("pearl", "teardrop", "bar"))
    out: list[str] = []
    for cx in (130, 270):
        out += [
            _circle(cx, 70, 12, paint),
            _line(f"M{cx},82 L{cx},150", 3),
            *[_circle(cx, y, 4, paint, 1.2) for y in (96, 112, 128)],
            _circle(cx, 150, 8, paint, 2),
        ]
        if drop == "pearl":
            out += [_circle(cx, 200, 38, gem), _highlight(f"M{cx - 22},188 Q{cx - 18},172 {cx - 4},166", 5, 0.8)]
        elif drop == "teardrop":
            out += [
                _path(f"M{cx},158 Q{cx + 46},228 {cx},268 Q{cx - 46},228 {cx},158 Z", gem),
                _path(f"M{cx},158 Q{cx + 46},228 {cx},268 Q{cx - 46},228 {cx},158 Z", "none", LW_DETAIL, stroke=_shade(paint, 0.2)),
                _line(f"M{cx},170 L{cx},256 M{cx - 16},210 L{cx + 16},210", 1.0, ' stroke-opacity=".4"'),
                _highlight(f"M{cx - 14},206 Q{cx - 12},192 {cx - 4},184", 4, 0.8),
            ]
        else:
            out += [
                f'<rect x="{cx - 9}" y="158" width="18" height="108" rx="6" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
                _line(f"M{cx - 4},168 L{cx - 4},254", 3, ' stroke-opacity=".5"', "#ffffff"),
            ]
    if label:
        out.append(_word(label, 200, 330, 200, 22))
    return out


def _dial_ticks(cx: float, cy: float, r: float) -> str:
    ticks = []
    for k in range(12):
        a = math.radians(k * 30)
        r0 = r - (6 if k % 3 else 12)
        ticks.append(f"M{cx + r0 * math.sin(a):.1f},{cy - r0 * math.cos(a):.1f} L{cx + r * math.sin(a):.1f},{cy - r * math.cos(a):.1f}")
    return _line(" ".join(ticks), 1.8)


def analog_watch(paint: str, fill: Fill, label: str | None, strap: str = "leather", case: str = "steel") -> list[str]:
    """An analog wristwatch: a round case in ``case`` metal, a dial with hands and a ``leather`` (stitched, with a buckle), ``mesh`` or ``fabric`` (striped) strap in the record's fill."""
    _choice("strap", strap, ("leather", "mesh", "fabric"))
    metal = CASES[_choice("case", case, tuple(CASES))]
    upper, lower = "M170,30 L230,30 L238,150 L162,150 Z", "M162,250 L238,250 L230,370 L170,370 Z"
    out = [_path(upper, paint), _path(lower, paint)]
    if strap == "leather":
        out += [
            _line("M178,38 L184,146 M222,38 L216,146 M178,262 L184,362 M222,262 L216,362", 1.2, ' stroke-dasharray="4 3"'),
            _path("M176,318 L224,318 L224,338 L176,338 Z", "none", LW_DETAIL),
            _path("M196,312 L204,312 L204,344 L196,344 Z", metal, LW_DETAIL),
            *[_circle(200, y, 2.6, INK, 1) for y in (290, 300, 354)],
        ]
    elif strap == "mesh":
        rows = " ".join(f"M{166 + (y - 30) * 0.06:.1f},{y} L{234 - (y - 30) * 0.06:.1f},{y}" for y in range(36, 150, 6))
        rows += " " + " ".join(f"M{162 + (y - 250) * 0.06:.1f},{y} L{238 - (y - 250) * 0.06:.1f},{y}" for y in range(256, 370, 6))
        out += [_line(rows, 0.8, ' stroke-opacity=".45"'), _path("M174,330 L226,330 L225,348 L175,348 Z", metal, LW_DETAIL)]
    else:
        stripe = _shade(fill.accent or fill.base, 0.1)
        out += [
            _line("M188,34 L190,150 M212,34 L210,150 M188,250 L190,366 M212,250 L210,366", 5, "", stripe),
            _path("M172,322 L228,322 L228,340 L172,340 Z", metal, LW_DETAIL),
            _line("M172,331 L228,331", 1.2),
        ]
    out += [
        _path("M262,188 L280,188 L280,212 L262,212 Z", metal, LW_DETAIL),
        _circle(200, 200, 70, metal),
        _circle(200, 200, 58, "#fbf8f2", LW_DETAIL),
        _dial_ticks(200, 200, 52),
        _line("M200,200 L200,164 M200,200 L226,212", 3.4),
        _line("M200,200 L174,226", 1.2, "", "#c8312e"),
        _circle(200, 200, 4, INK, 1),
        _highlight("M148,166 Q160,142 186,134", 5, 0.5),
    ]
    return out


def digital_watch(paint: str, fill: Fill, label: str | None, buttons: str = "2") -> list[str]:
    """A digital sports watch: a square case holding an LCD that reads the time, ``buttons`` (2 or 4) on its sides, a silicone strap with adjustment holes in the record's fill."""
    n = int(_choice("buttons", buttons, ("2", "4")))
    case = _shade(fill.base, 0.35)
    out = [
        _path("M168,30 L232,30 L236,150 L164,150 Z", paint),
        _path("M164,250 L236,250 L232,370 L168,370 Z", paint),
        *[_circle(200, y, 3, INK, 1) for y in (276, 290, 304, 318, 332)],
        _path("M176,330 L224,330 L224,346 L176,346 Z", _shade(paint, 0.2), LW_DETAIL),
        f'<rect x="140" y="130" width="120" height="140" rx="20" fill="{case}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="154" y="148" width="92" height="76" rx="8" fill="{SCREEN}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _line("M164,178 L174,178 L174,200 L164,200 L164,214 L174,214 M182,178 L192,178 L192,214 L182,214 Z M206,178 L216,178 L216,214 L206,214 Z M224,178 L234,178 L234,214 L224,214 Z", 3, "", "#33403a"),
        _circle(200, 190, 2.4, "#33403a", 0.5),
        _word("MON 14", 200, 238, 80, 14),
    ]
    for y in (160, 240)[:1] if n == 2 else (160, 240):
        out += [f'<rect x="132" y="{y - 12}" width="10" height="24" rx="3" fill="{case}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>']
    for y in (160, 240) if n == 4 else (200,):
        out += [f'<rect x="258" y="{y - 12}" width="10" height="24" rx="3" fill="{case}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>']
    out.append(_highlight("M152,142 Q170,136 200,136", 4, 0.45))
    return out


def fitness_band(paint: str, fill: Fill, label: str | None, screen: str = "heart") -> list[str]:
    """A smart-style fitness band: a slim pill-shaped touch screen showing a ``heart`` rate, ``steps`` or the ``clock``, set in a ribbed silicone band in the record's fill."""
    _choice("screen", screen, ("heart", "steps", "clock"))
    out = [
        _path("M184,24 L216,24 L218,128 L182,128 Z", paint),
        _path("M182,272 L218,272 L216,376 L184,376 Z", paint),
        _line(" ".join(f"M{184 + (y - 24) * 0.02:.1f},{y} L{216 - (y - 24) * 0.02:.1f},{y}" for y in range(34, 126, 9)), 1.2, ' stroke-opacity=".4"'),
        _line(" ".join(f"M{182 + (y - 272) * 0.02:.1f},{y} L{218 - (y - 272) * 0.02:.1f},{y}" for y in range(282, 374, 9)), 1.2, ' stroke-opacity=".4"'),
        _path("M172,330 L228,330 L228,346 L172,346 Z", _shade(paint, 0.2), LW_DETAIL),
        f'<rect x="164" y="118" width="72" height="164" rx="26" fill="#2f2f35" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="174" y="132" width="52" height="136" rx="18" fill="#10151c" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
    ]
    if screen == "heart":
        out += [
            _path("M200,196 C180,176 186,160 200,172 C214,160 220,176 200,196 Z", "#e0474c", 1.2),
            _line("M180,222 L190,222 L194,212 L200,230 L206,216 L210,222 L220,222", 2, "", "#7fe0a0"),
            _word("72", 200, 248, 30, 16, "#ffffff"),
        ]
    elif screen == "steps":
        out += [
            _path("M190,160 C182,160 182,176 190,176 C198,176 198,160 190,160 Z M210,184 C202,184 202,200 210,200 C218,200 218,184 210,184 Z", "#7fe0a0", 1.0),
            _word("8,412", 200, 226, 44, 14, "#ffffff"),
            _line("M180,246 L220,246", 3, "", "#7fe0a0"),
        ]
    else:
        out += [_word("10:42", 200, 196, 44, 22, "#ffffff"), _word("MON", 200, 228, 30, 11, "#9fb3c8"), _line("M182,246 L218,246", 2, "", "#9fb3c8")]
    out.append(_highlight("M176,142 Q178,136 190,134", 3, 0.4))
    return out


register({"hoop_earrings": hoop_earrings, "drop_earrings": drop_earrings, "analog_watch": analog_watch, "digital_watch": digital_watch, "fitness_band": fitness_band})
