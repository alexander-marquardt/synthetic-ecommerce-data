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
stud_earrings   a pair of studs, each on a post with a butterfly    stud (ball, gem, pearl, knot),
                back (gen#1113)                                     stone (a stone name, for gem)
bangle          a rigid round bangle seen at an angle (gen#1113)    style (plain, hammered,
                                                                    twisted, stacked)
cufflinks       a pair of cufflinks, each a face on a swivel bar    face (round, square, knot,
                (gen#1113)                                          stone), stone (a stone name)
pendant         one large pendant on a fine chain (gen#1113)        charm (heart, star, moon, cross,
                                                                    disc, pearl, stone), stone
anklet          a fine chain laid in a round, with a clasp and an   style (chain, beaded, charm,
                extender (gen#1113)                                 double)
watch_strap     the two parts of a strap, side by side (gen#1113)   material (leather, silicone,
                                                                    fabric, mesh)
==============  ==================================================  ===========================

Every params value is a string, as a style row's ``params`` carry it.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _word,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_accessories import STONES, _annulus, _chain, _gem
from synthetic_ecommerce_data.domains.retail.kit_more import _circle, _ring

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


def stud_earrings(paint: str, fill: Fill, label: str | None, stud: str = "ball", stone: str = "") -> list[str]:
    """A pair of studs seen from the front, each with its post and butterfly back below: a polished metal ``ball``, a ``gem`` of the ``stone`` in a metal bezel, a ``pearl`` in a metal cup, or a ``knot`` of metal (gen#1113)."""
    _choice("stud", stud, ("ball", "gem", "pearl", "knot"))
    out: list[str] = []
    for cx in (130, 270):
        out += [
            _line(f"M{cx},150 L{cx},252", 5),
            f'<rect x="{cx - 22}" y="232" width="44" height="18" rx="7" fill="{paint}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        ]
        if stud == "ball":
            out += [_circle(cx, 150, 40, paint), _highlight(f"M{cx - 24},138 Q{cx - 18},118 {cx - 2},112", 6, 0.75)]
        elif stud == "pearl":
            out += [_circle(cx, 156, 14, paint, 1.6), _circle(cx, 148, 40, PEARL), _highlight(f"M{cx - 24},136 Q{cx - 18},116 {cx - 2},110", 6, 0.8)]
        elif stud == "gem":
            out += [_circle(cx, 150, 44, paint), *_gem(cx, 150, 30, stone or "cubic zirconia")]
        else:
            out += [_circle(cx, 150, 40, paint)]
            out += [_line(f"M{cx - 30},{150 + 8 * k} Q{cx},{126 + 8 * k} {cx + 30},{150 + 8 * k}", 2.4, ' stroke-opacity=".6"') for k in (-2, 0, 2)]
    if label:
        out.append(_word(label, 200, 330, 200, 22))
    return out


def bangle(paint: str, fill: Fill, label: str | None, style: str = "plain") -> list[str]:
    """A rigid bangle in the record's metal, tilted so its round shows as an ellipse: ``plain`` polish, ``hammered`` dimples, a ``twisted`` rope, or a ``stacked`` set of three (each a ``class="band"``) (gen#1113)."""
    _choice("bangle style", style, ("plain", "hammered", "twisted", "stacked"))
    out: list[str] = []
    if style == "stacked":
        for y in (168, 200, 232):
            out.append(f'<g class="band">{_annulus(200, y, 130, 116, paint, 0.42)}{_highlight(f"M96,{y + 8} Q120,{y + 38} 180,{y + 52}", 3, 0.5)}</g>')
        return out + ([_word(label, 200, 340, 200, 22)] if label else [])
    out += [_annulus(200, 200, 140, 116, paint, 0.5), _highlight("M84,214 Q108,262 182,276", 5, 0.55)]
    if style == "hammered":
        for k in range(12):
            a = math.radians(k * 30 + 15)
            out.append(f'<ellipse cx="{200 + 128 * math.cos(a):.1f}" cy="{200 + 64 * math.sin(a):.1f}" rx="6" ry="4" fill="{_shade(paint, 0.15)}" stroke="none"/>')
    elif style == "twisted":
        for k in range(24):
            a = math.radians(k * 15)
            x0, y0 = 200 + 118 * math.cos(a), 200 + 59 * math.sin(a)
            x1, y1 = 200 + 138 * math.cos(a + 0.12), 200 + 69 * math.sin(a + 0.12)
            out.append(_line(f"M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}", 1.4, ' stroke-opacity=".55"'))
    if label:
        out.append(_word(label, 200, 340, 200, 22))
    return out


def cufflinks(paint: str, fill: Fill, label: str | None, face: str = "round", stone: str = "") -> list[str]:
    """A pair of cufflinks, each a ``face`` (a ``round`` or ``square`` plate, a ``knot`` of metal, or a ``stone`` inlay of the ``stone`` named) on a post with a swivel bar (gen#1113)."""
    _choice("cufflink face", face, ("round", "square", "knot", "stone"))
    out: list[str] = []
    for cx in (124, 276):
        out += [
            _line(f"M{cx},180 L{cx},256", 7),
            _line(f"M{cx},180 L{cx},256", 3.5, stroke=paint),
            f'<rect x="{cx - 34}" y="250" width="68" height="16" rx="8" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        ]
        if face == "square":
            out += [f'<rect x="{cx - 50}" y="96" width="100" height="100" rx="10" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
                    f'<rect x="{cx - 38}" y="108" width="76" height="76" rx="6" fill="none" stroke="{INK}" stroke-width="1.2" stroke-opacity=".5"/>']
        elif face == "knot":
            out += [_circle(cx, 146, 48, paint)]
            out += [_line(f"M{cx - 40},{146 + 10 * k} Q{cx},{116 + 10 * k} {cx + 40},{146 + 10 * k}", 2.6, ' stroke-opacity=".6"') for k in (-2, 0, 2)]
        elif face == "stone":
            out += [_circle(cx, 146, 52, paint), _circle(cx, 146, 38, STONES.get(stone.lower(), "#2c2c32") if stone else "#2c2c32", 1.6)]
        else:
            out += [_circle(cx, 146, 52, paint), _circle(cx, 146, 40, "none", 1.2)]
        out.append(_highlight(f"M{cx - 32},126 Q{cx - 24},104 {cx - 4},98", 5, 0.6))
    if label:
        out.append(_word(label, 200, 330, 200, 22))
    return out


def _star(cx: float, cy: float, r: float) -> str:
    pts = []
    for k in range(10):
        a, q = math.radians(k * 36), r if k % 2 == 0 else r * 0.45
        pts.append(f"{cx + q * math.sin(a):.1f},{cy - q * math.cos(a):.1f}")
    return "M" + " L".join(pts) + " Z"


#: The outline of each metal charm, about 150 units across, hung at (200, 130).
CHARMS = {
    "heart": "M200,188 C170,140 106,152 110,214 C114,266 168,300 200,334 C232,300 286,266 290,214 C294,152 230,140 200,188 Z",
    "star": _star(200, 240, 104),
    "moon": "M226,150 A92,92 0 1 0 284,286 A76,76 0 1 1 226,150 Z",
    "cross": "M180,146 H220 V206 H276 V246 H220 V346 H180 V246 H124 V206 H180 Z",
}


def pendant(paint: str, fill: Fill, label: str | None, charm: str = "heart", stone: str = "") -> list[str]:
    """One large pendant on a fine chain, in the record's metal: a ``charm`` (heart, star, moon, cross or a plain disc), a round pearl, or a faceted ``stone`` of the stone named in a round setting (gen#1113)."""
    _choice("pendant charm", charm, (*CHARMS, "disc", "pearl", "stone"))
    out = [*_chain("M70,28 Q110,92 200,124 Q290,92 330,28", paint, 6), *_ring(200, 134, 13, paint, 5)]
    if charm in CHARMS:
        out += [_path(CHARMS[charm], paint)]
    elif charm == "disc":
        out += [_circle(200, 242, 94, paint), _circle(200, 242, 80, "none", 1.4)]
    elif charm == "pearl":
        out += [_path("M178,142 Q200,128 222,142 L232,172 Q200,160 168,172 Z", paint), _circle(200, 246, 88, PEARL)]
    else:
        if stone.lower() not in STONES:
            raise ValueError(f"unknown pendant stone {stone!r}; {', '.join(STONES)}")
        out += [_circle(200, 242, 98, paint), _circle(200, 242, 84, _shade(paint, -0.12), 1.4), *_gem(200, 240, 72, stone)]
    out.append(_highlight("M150,232 Q152,200 178,186", 6, 0.5))
    if label:
        out.append(_word(label, 200, 382, 200, 22))
    return out


def anklet(paint: str, fill: Fill, label: str | None, style: str = "chain") -> list[str]:
    """An anklet laid in a round, closed by a lobster clasp with an extender: a plain ``chain``, a ``beaded`` one, a chain with small ``charm`` discs, or a ``double`` chain (gen#1113)."""
    _choice("anklet style", style, ("chain", "beaded", "charm", "double"))
    cx, cy, rx, ry = 200.0, 206.0, 158.0, 138.0
    ring = f"M{cx},{cy - ry} A{rx},{ry} 0 1 1 {cx - 0.1},{cy - ry} Z"
    out = list(_chain(ring, paint, 9 if style == "chain" else 6))
    if style == "double":
        out += _chain(f"M{cx},{cy - ry + 8} A{rx - 30},{ry - 22} 0 1 1 {cx - 0.1},{cy - ry + 8} Z", paint, 5)
    steps = {"beaded": range(0, 360, 12), "charm": range(60, 301, 40)}.get(style, ())
    for deg in steps:
        t = math.radians(deg)
        x, y = cx + rx * math.sin(t), cy - ry * math.cos(t)
        if style == "beaded":
            out.append(_circle(x, y, 12, paint, 2))
        else:
            out += [_line(f"M{x:.1f},{y:.1f} L{x:.1f},{y + 20:.1f}", 3), _circle(x, y + 34, 17, paint, 2.2)]
    out += [_circle(cx, cy - ry, 14, paint), _circle(cx + 4, cy - ry - 2, 5, "#ffffff", 1.4)]
    out += [_circle(cx + 26 + 17 * k, cy - ry - 8, 6, paint, 1.8) for k in range(3)]
    if label:
        out.append(_word(label, 200, 212, 160, 22))
    return out


def watch_strap(paint: str, fill: Fill, label: str | None, material: str = "leather") -> list[str]:
    """A two part watch strap laid flat, the short part with its buckle beside the long part with its holes: ``leather`` is stitched, ``silicone`` is ribbed, ``fabric`` is woven with a center stripe and ``mesh`` is a fine metal weave with a slide clasp (gen#1113)."""
    _choice("strap material", material, ("leather", "silicone", "fabric", "mesh"))
    short = "M72,70 L168,70 L160,300 L80,300 Z"
    long = "M232,30 L328,30 L318,330 Q318,372 280,372 Q242,372 242,330 Z"
    out = [_path(d, paint) for d in (short, long)]
    for x0, y in ((66, 300), (226, 30)):  # the spring bar end of each part
        out.append(f'<rect x="{x0}" y="{y - 9}" width="108" height="18" rx="9" fill="{_shade(paint, -0.18)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
    if material == "leather":
        for d in ("M84,82 L90,286 M156,82 L150,286", "M246,46 L254,328 Q256,358 280,358 Q304,358 306,328 L314,46"):
            out.append(_line(d, 2, ' stroke-dasharray="8 6" stroke-opacity=".7"'))
    elif material == "silicone":
        out += [_line(f"M{82 + k * 0.3:.1f},{100 + 18 * k} H{158 - k * 0.3:.1f}", 3, ' stroke-opacity=".4"') for k in range(10)]
        out += [_line(f"M{242 + k * 0.3:.1f},{60 + 18 * k} H{318 - k * 0.3:.1f}", 3, ' stroke-opacity=".4"') for k in range(7)]
    elif material == "fabric":
        stripe = _shade(paint, 0.45)
        out += [_path("M108,70 L132,70 L131,290 L109,290 Z", stripe, 1.2), _path("M268,40 L292,40 L290,370 L270,370 Z", stripe, 1.2)]
        out += [_line(f"M{76 + k * 0.4:.1f},{84 + 10 * k} H{164 - k * 0.4:.1f}", 1, ' stroke-opacity=".35"') for k in range(20)]
        out += [_line(f"M{236 + k * 0.4:.1f},{46 + 10 * k} H{324 - k * 0.4:.1f}", 1, ' stroke-opacity=".35"') for k in range(29)]
    else:
        for k in range(22):
            out.append(_line(f"M{74 + k * 0.4:.1f},{80 + 10 * k} l8,-5 " + "l8,5 l8,-5 " * 5, 1.2, ' stroke-opacity=".5"'))
        for k in range(30):
            out.append(_line(f"M{238 + k * 0.35:.1f},{48 + 10 * k} l8,-5 " + "l8,5 l8,-5 " * 4, 1.2, ' stroke-opacity=".5"'))
    if material == "mesh":
        out.append(f'<rect x="62" y="38" width="116" height="44" rx="8" fill="{STEEL}" stroke="{INK}" stroke-width="{LW}"/>')
    else:  # a pin buckle, and the holes of the long part
        out += [f'<rect x="60" y="28" width="120" height="50" rx="12" fill="none" stroke="{INK}" stroke-width="15"/>',
                f'<rect x="60" y="28" width="120" height="50" rx="12" fill="none" stroke="{STEEL}" stroke-width="9"/>',
                _line("M120,78 L120,26", 7), _line("M120,78 L120,28", 3, stroke=STEEL)]
        out += [_circle(280, 206 + 28 * k, 6, "#ffffff", 2) for k in range(5)]
    if label:
        out.append(_word(label, 120, 340, 140, 20))
    return out


register({"pendant": pendant, "anklet": anklet, "watch_strap": watch_strap, "hoop_earrings": hoop_earrings, "drop_earrings": drop_earrings, "analog_watch": analog_watch, "digital_watch": digital_watch, "fitness_band": fitness_band, "stud_earrings": stud_earrings, "bangle": bangle, "cufflinks": cufflinks})
