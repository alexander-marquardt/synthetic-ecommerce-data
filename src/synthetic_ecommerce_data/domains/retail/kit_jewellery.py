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
analog_watch    a round case, dial and hands on a strap             strap (leather, mesh, fabric,
                                                                    silicone), case (steel, gold,
                                                                    rose), dial (plain, chrono,
                                                                    dive; gen#1113)
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
charm           one charm on a lobster clasp, or a bead threaded    motif (heart, star, moon, cross,
                on a strand (gen#1113)                              clover, paw, bead, stone), stone
brooch          a brooch over the ends of its pin (gen#1113)        motif (flower, bee, bow, leaf,
                                                                    pearl, stone), stone
jewellery_box   a jewelry box, its covering in the record's color   style (case, mirror, drawers,
                (gen#1113)                                          travel)
jewellery_set   a matching necklace and pair of earrings, and a     pieces (2, 3), motif (plain,
                bracelet in a set of three (gen#1113)               heart, pearl, stone), stone
kids_watch      a kids' watch: a time teacher dial or an LCD in a   face (teacher, digital)
                round case on a silicone strap (gen#1113)
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
    _mix,
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


def _dial_ticks(cx: float, cy: float, r: float, color: str = INK) -> str:
    ticks = []
    for k in range(12):
        a = math.radians(k * 30)
        r0 = r - (6 if k % 3 else 12)
        ticks.append(f"M{cx + r0 * math.sin(a):.1f},{cy - r0 * math.cos(a):.1f} L{cx + r * math.sin(a):.1f},{cy - r * math.cos(a):.1f}")
    return _line(" ".join(ticks), 1.8, "", color)


#: An analog watch's dial (gen#1113): plain, a chronograph's three sub-dials and pushers, or a
#: dive watch's turning bezel with its minute marks.
DIALS = ("plain", "chrono", "dive")


def _silicone_strap(paint: str, metal: str) -> list[str]:
    """A plain silicone strap's adjustment holes, its keeper and its buckle."""
    return [
        *[_circle(200, y, 3, INK, 1) for y in (276, 290, 304, 318, 332)],
        _path("M176,344 L224,344 L224,358 L176,358 Z", _shade(metal, 0.1), LW_DETAIL),
    ]


def _dial(kind: str, metal: str) -> list[str]:
    """The face inside an analog case: the dial, its ticks and the extras of a ``chrono`` or a ``dive`` dial."""
    if kind == "dive":
        bezel = _path("M130,200 A70,70 0 1 0 270,200 A70,70 0 1 0 130,200 Z M144,200 A56,56 0 1 1 256,200 A56,56 0 1 1 144,200 Z", "#2d2d33", LW, ' fill-rule="evenodd"')
        marks = " ".join(f"M{200 + 58 * math.sin(math.radians(k)):.1f},{200 - 58 * math.cos(math.radians(k)):.1f} L{200 + 66 * math.sin(math.radians(k)):.1f},{200 - 66 * math.cos(math.radians(k)):.1f}" for k in range(30, 360, 30))
        return [
            _circle(200, 200, 70, metal), bezel, _line(marks, 2.2, "", "#ffffff"),
            _path("M200,134 L192,146 L208,146 Z", "#ffffff", 1.2),
            _circle(200, 200, 52, "#1f2a38", LW_DETAIL), _dial_ticks(200, 200, 46, "#ffffff"),
        ]
    out = [_circle(200, 200, 70, metal), _circle(200, 200, 58, "#fbf8f2", LW_DETAIL), _dial_ticks(200, 200, 52)]
    if kind == "chrono":
        out += [_circle(x, y, 12, "#ece6da", 1.4) for x, y in ((200, 170), (174, 212), (226, 212))]
        out += [_line(f"M{x},{y} L{x},{y - 9}", 1.4) for x, y in ((200, 170), (174, 212), (226, 212))]
        out += [_path("M258,146 L272,138 L278,150 L264,158 Z", metal, LW_DETAIL), _path("M258,254 L272,262 L278,250 L264,242 Z", metal, LW_DETAIL)]
    return out


def analog_watch(paint: str, fill: Fill, label: str | None, strap: str = "leather", case: str = "steel", dial: str = "plain") -> list[str]:
    """An analog wristwatch: a round case in ``case`` metal, a ``dial`` (plain, chrono or dive) with hands and a ``leather`` (stitched, with a buckle), ``mesh``, ``fabric`` (striped) or ``silicone`` (with holes) strap in the record's fill."""
    _choice("strap", strap, ("leather", "mesh", "fabric", "silicone"))
    _choice("dial", dial, DIALS)
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
    elif strap == "silicone":
        out += _silicone_strap(paint, metal)
    else:
        stripe = _shade(fill.accent or fill.base, 0.1)
        out += [
            _line("M188,34 L190,150 M212,34 L210,150 M188,250 L190,366 M212,250 L210,366", 5, "", stripe),
            _path("M172,322 L228,322 L228,340 L172,340 Z", metal, LW_DETAIL),
            _line("M172,331 L228,331", 1.2),
        ]
    out += [
        _path("M262,188 L280,188 L280,212 L262,212 Z", metal, LW_DETAIL),
        *_dial(dial, metal),
        _line("M200,200 L200,164 M200,200 L226,212", 3.4, "", "#ffffff" if dial == "dive" else INK),
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
        out += _stone_setting(200, 242, 98, paint, stone, "pendant")
    out.append(_highlight("M150,232 Q152,200 178,186", 6, 0.5))
    if label:
        out.append(_word(label, 200, 382, 200, 22))
    return out


def _oval(cx: float, cy: float, rx: float, ry: float) -> str:
    """A closed ellipse as two half arcs: ``motifs.drawn_box`` measures an arc about the middle of its chord, so one full turn from the top would be measured a radius too high."""
    top, bottom = f"{cx},{cy - ry}", f"{cx},{cy + ry}"
    return f"M{top} A{rx},{ry} 0 0 1 {bottom} A{rx},{ry} 0 0 1 {top} Z"


def anklet(paint: str, fill: Fill, label: str | None, style: str = "chain") -> list[str]:
    """An anklet laid in a round, closed by a lobster clasp with an extender: a plain ``chain``, a ``beaded`` one, a chain with small ``charm`` discs, or a ``double`` chain (gen#1113)."""
    _choice("anklet style", style, ("chain", "beaded", "charm", "double"))
    cx, cy, rx, ry = 200.0, 206.0, 158.0, 138.0
    out = list(_chain(_oval(cx, cy, rx, ry), paint, 9 if style == "chain" else 6))
    if style == "double":
        out += _chain(_oval(cx, cy - 14, rx - 30, ry - 22), paint, 5)
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
        for x, x1, y, rows, taper in ((76, 164, 80, 22, 0.35), (238, 322, 48, 30, 0.3)):
            for k in range(rows):  # each wave is as wide as the part is there
                step = (x1 - x - 2 * taper * k) / 10
                wave = f"l{step:.2f},-5 l{step:.2f},5 " * 5
                out.append(_line(f"M{x + taper * k:.1f},{y + 10 * k} {wave.strip()}", 1.2, ' stroke-opacity=".5"'))
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


def _stone_setting(cx: float, cy: float, r: float, paint: str, stone: str, what: str) -> list[str]:
    """A faceted ``stone`` in a round metal setting; a stone the kit has no color for is refused."""
    if stone.lower() not in STONES:
        raise ValueError(f"unknown {what} stone {stone!r}; {', '.join(STONES)}")
    return [_circle(cx, cy, r, paint), _circle(cx, cy, r - 14, _shade(paint, -0.12), 1.4), *_gem(cx, cy - 2, r - 26, stone)]


#: What a charm draws: a pendant's outlines, two of its own, a threaded bead or a set stone.
CHARM_MOTIFS = (*CHARMS, "clover", "paw", "bead", "stone")


def charm(paint: str, fill: Fill, label: str | None, motif: str = "heart", stone: str = "") -> list[str]:
    """One charm in the record's metal, hung from a lobster clasp that clips onto a charm bracelet: a ``motif`` outline (heart, star, moon, cross, a four leaf clover, a paw print) or a faceted ``stone`` of the stone named; a ``bead`` is threaded on a strand instead (gen#1113)."""
    _choice("charm motif", motif, CHARM_MOTIFS)
    if motif == "bead":
        out = [*_chain("M16,240 L384,240", paint, 6)]
        out += [_path("M146,160 Q200,144 254,160 Q296,240 254,320 Q200,336 146,320 Q104,240 146,160 Z", paint)]
        out += [_line("M130,200 Q200,186 270,200", 2.4), _line("M130,280 Q200,294 270,280", 2.4)]
        out.append(_highlight("M140,236 Q142,196 168,176", 6, 0.5))
    else:
        clasp = "M186,52 Q200,30 214,52 L220,110 Q200,130 180,110 Z"
        out = [_path(clasp, paint), _line("M192,62 Q186,86 192,108", 3), *_ring(200, 134, 13, paint, 5)]
        if motif in CHARMS:
            out.append(_path(CHARMS[motif], paint))
        elif motif == "clover":
            out.append(_line("M200,250 Q226,306 262,346", 9))
            out.append(_line("M200,250 Q226,306 262,346", 5, stroke=paint))
            out += [_circle(200 + dx, 250 + dy, 44, paint) for dx, dy in ((0, -48), (48, 0), (0, 48), (-48, 0))]
            out.append(_circle(200, 250, 12, _shade(paint, 0.15), 1.4))
        elif motif == "paw":
            out.append(_path(_oval(200, 286, 64, 52), paint))
            out += [_circle(x, y, 26, paint) for x, y in ((128, 214), (172, 176), (228, 176), (272, 214))]
        else:
            out += _stone_setting(200, 244, 96, paint, stone, "charm")
        out.append(_highlight("M150,232 Q152,200 178,186", 6, 0.5))
    if label:
        out.append(_word(label, 200, 382, 200, 22))
    return out


BROOCH_MOTIFS = ("flower", "bee", "bow", "leaf", "pearl", "stone")


def brooch(paint: str, fill: Fill, label: str | None, motif: str = "flower", stone: str = "") -> list[str]:
    """A brooch in the record's metal, the ends of its pin (a hinge and a safety catch) showing at each side: a ``flower``, a ``bee``, a ``bow``, a ``leaf``, a ``pearl`` cluster, or a faceted ``stone`` of the stone named in an oval setting with a beaded edge (gen#1113)."""
    _choice("brooch motif", motif, BROOCH_MOTIFS)
    out = [_line("M44,200 L356,200", 9), _line("M44,200 L356,200", 4, stroke=STEEL), _circle(44, 200, 12, STEEL, 2)]
    out.append(f'<rect x="338" y="184" width="30" height="32" rx="6" fill="{STEEL}" stroke="{INK}" stroke-width="2"/>')
    if motif == "flower":
        out += [_circle(200 + 66 * math.sin(math.radians(k * 60)), 200 - 66 * math.cos(math.radians(k * 60)), 50, paint) for k in range(6)]
        out += [_circle(200, 200, 38, _shade(paint, 0.15)), _circle(200, 200, 20, _shade(paint, -0.15), 1.4)]
    elif motif == "bee":
        wing = _mix(paint, "#ffffff", 0.55)
        out += [_path(_oval(138, 150, 66, 40), wing), _path(_oval(262, 150, 66, 40), wing)]
        out += [_path(_oval(200, 236, 52, 96), paint), *(_line(f"M{154 + 4 * k},{206 + 34 * k} H{246 - 4 * k}", 7) for k in range(3))]
        out += [_circle(200, 122, 32, paint), _line("M188,94 Q176,58 150,50", 4), _line("M212,94 Q224,58 250,50", 4)]
    elif motif == "bow":
        out += [_path("M200,196 C144,104 52,118 62,196 C52,276 144,290 200,196 Z", paint)]
        out += [_path("M200,196 C256,104 348,118 338,196 C348,276 256,290 200,196 Z", paint)]
        out += [_path("M186,212 L140,350 L168,336 L188,362 L206,220 Z", paint), _path("M214,212 L260,350 L232,336 L212,362 L194,220 Z", paint)]
        out.append(f'<rect x="176" y="168" width="48" height="58" rx="12" fill="{_shade(paint, 0.12)}" stroke="{INK}" stroke-width="{LW}"/>')
    elif motif == "leaf":
        out += [_path("M76,330 Q84,108 330,76 Q318,322 76,330 Z", paint), _line("M76,330 Q196,220 330,76", 4)]
        out += [_line(f"M{x},{y} L{x + dx},{y - dy}", 2.4) for x, y, dx, dy in ((150, 260, -6, 70), (200, 208, -4, 74), (246, 152, -2, 62), (150, 262, 64, -4), (200, 210, 64, -2))]
    elif motif == "pearl":
        out.append(_circle(200, 200, 128, paint))
        out += [_circle(200 + 80 * math.sin(math.radians(k * 60)), 200 - 80 * math.cos(math.radians(k * 60)), 38, PEARL) for k in range(6)]
        out += [_circle(200, 200, 42, PEARL), _highlight("M184,186 Q188,174 200,170", 4, 0.8)]
    else:
        out += [_path(_oval(200, 200, 112, 146), paint), _path(_oval(200, 200, 96, 128), _shade(paint, -0.12), 1.4)]
        out += [_circle(200 + 104 * math.sin(math.radians(k)), 200 - 137 * math.cos(math.radians(k)), 7, paint, 1.4) for k in range(0, 360, 20)]
        if stone.lower() not in STONES:
            raise ValueError(f"unknown brooch stone {stone!r}; {', '.join(STONES)}")
        out += _gem(200, 196, 78, stone)
    if label:
        out.append(_word(label, 200, 384, 200, 22))
    return out


LINING = "#efe6d8"
MIRROR = "#dce8ee"


def _box(x: float, y: float, w: float, h: float, fill: str, rx: float = 8, width: float = LW) -> str:
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}" stroke="{INK}" stroke-width="{width:g}"/>'


def jewellery_box(paint: str, fill: Fill, label: str | None, style: str = "case") -> list[str]:
    """A jewelry box, its covering in the record's color: a closed ``case`` with a clasp, a ``mirror`` lid open over ring rolls and compartments, a chest of two ``drawers`` with knobs under a lid, or a zipped ``travel`` case (gen#1113)."""
    _choice("jewellery box style", style, ("case", "mirror", "drawers", "travel"))
    stitch = ' stroke-dasharray="7 6" stroke-opacity=".55"'
    if style == "case":
        out = [_box(56, 170, 288, 170, paint), _box(48, 110, 304, 74, paint, 12), _line("M66,128 H334", 2, stitch)]
        out += [_line("M74,190 H326 V322 H74 Z", 2, stitch), _box(184, 160, 32, 44, STEEL, 4, 2)]
    elif style == "mirror":
        out = [_box(64, 24, 272, 166, paint), _box(86, 44, 228, 126, MIRROR, 4, 2)]
        out += [_highlight("M118,150 L176,64", 8, 0.7), _highlight("M156,150 L208,74", 5, 0.6)]
        out += [_path("M64,190 L336,190 L360,226 L40,226 Z", LINING, 2), _box(40, 226, 320, 128, paint)]
        out += [_line(f"M{x},196 L{x - 4 * k},222", 2) for k, x in enumerate((130, 200, 270), -1)]
        out += [_line(f"M{60 + 30 * k},208 Q{75 + 30 * k},200 {90 + 30 * k},208", 2) for k in range(2)]
        out += [_line("M60,246 H340", 2, stitch), _box(186, 214, 28, 28, STEEL, 4, 2)]
    elif style == "drawers":
        out = [_box(64, 120, 272, 228, paint), _box(52, 88, 296, 48, paint, 10), _line("M66,104 H334", 2, stitch)]
        for y in (156, 252):
            out += [_box(86, y, 228, 78, _shade(paint, 0.08), 6), _circle(200, y + 39, 11, STEEL, 2)]
        out += [_box(84, 344, 32, 16, _shade(paint, 0.3), 4, 2), _box(284, 344, 32, 16, _shade(paint, 0.3), 4, 2)]
    else:
        out = [_box(50, 116, 300, 196, paint, 64), _line("M72,214 Q72,138 132,138 H268 Q328,138 328,214 Q328,290 268,290 H132 Q72,290 72,214 Z", 3, stitch)]
        out += [_line("M60,214 Q60,128 132,128 H268 Q340,128 340,214", 4), _box(300, 112, 22, 38, STEEL, 5, 2), _circle(311, 160, 10, "none", 2.4)]
    if label:
        out.append(_word(label, 200, 380, 220, 22))
    return out


#: What a jewellery set's pieces show (gen#1113): a polished disc, a heart, a pearl or a set stone.
SET_MOTIFS = ("plain", "heart", "pearl", "stone")


def _heart(cx: float, cy: float, r: float) -> str:
    return (f"M{cx},{cy - r * 0.35} C{cx - r * 0.5},{cy - r * 1.1} {cx - r * 1.3},{cy - r * 0.6} {cx - r},{cy + r * 0.05} "
            f"C{cx - r * 0.75},{cy + r * 0.55} {cx - r * 0.2},{cy + r * 0.8} {cx},{cy + r} "
            f"C{cx + r * 0.2},{cy + r * 0.8} {cx + r * 0.75},{cy + r * 0.55} {cx + r},{cy + r * 0.05} "
            f"C{cx + r * 1.3},{cy - r * 0.6} {cx + r * 0.5},{cy - r * 1.1} {cx},{cy - r * 0.35} Z")  # fmt: skip


def _set_piece(cx: float, cy: float, r: float, paint: str, motif: str, stone: str) -> list[str]:
    if motif == "heart":
        return [_path(_heart(cx, cy, r), paint)]
    if motif == "pearl":
        return [_circle(cx, cy - r * 0.9, r * 0.35, paint, LW_DETAIL), _circle(cx, cy, r * 0.85, PEARL)]
    if motif == "stone":
        return [_circle(cx, cy, r, paint), _circle(cx, cy, r * 0.8, _shade(paint, -0.12), 1.4), *_gem(cx, cy - r * 0.05, r * 0.62, stone)]
    return [_circle(cx, cy, r, paint), _circle(cx, cy, r * 0.75, "none", 1.4)]


def jewellery_set(paint: str, fill: Fill, label: str | None, pieces: str = "2", motif: str = "plain", stone: str = "") -> list[str]:
    """A matching set in the record's metal: a pendant necklace and a pair of drop earrings, and with ``pieces`` 3 a chain bracelet; each piece shows the set's ``motif``, a stone motif the ``stone`` named (gen#1113)."""
    n = _choice("pieces", pieces, ("2", "3"))
    _choice("jewellery set motif", motif, SET_MOTIFS)
    if motif == "stone" and stone.lower() not in STONES:
        raise ValueError(f"unknown jewellery set stone {stone!r}; {', '.join(STONES)}")
    out = [*_chain("M60,28 Q100,112 200,140 Q300,112 340,28", paint, 5), *_ring(200, 150, 9, paint, 4)]
    out += _set_piece(200, 196, 38, paint, motif, stone)
    for x in (92, 308):
        out += [_line(f"M{x - 10},{220} Q{x - 14},{196} {x},{194} Q{x + 12},{198} {x + 6},{214}", 3.4, "", paint), *_ring(x, 238, 6, paint, 3)]
        out += _set_piece(x, 270, 24, paint, motif, stone)
    if n == "3":
        out += [*_chain(_oval(200, 318, 74, 24), paint, 4.5), *_set_piece(200, 342, 16, paint, motif, stone)]
    out.append(_highlight("M176,184 Q178,170 190,164", 4, 0.5))
    if label:
        out.append(_word(label, 200, 388, 200, 20))
    return out


def kids_watch(paint: str, fill: Fill, label: str | None, face: str = "teacher") -> list[str]:
    """A kids' watch on a silicone strap in the record's fill: a ``teacher`` dial (the hours and the minutes printed, a red hour hand, a blue minute hand) or a ``digital`` LCD, in a round plastic case (gen#1113)."""
    _choice("face", face, ("teacher", "digital"))
    case = _mix(paint, "#ffffff", 0.45)
    out = [
        _path("M168,40 L232,40 L236,150 L164,150 Z", paint),
        _path("M164,250 L236,250 L232,360 L168,360 Z", paint),
        *[_circle(200, y, 3, INK, 1) for y in (274, 288, 302, 316, 330)],
        _path("M178,340 L222,340 L222,352 L178,352 Z", _shade(paint, 0.2), LW_DETAIL),
        _circle(200, 200, 78, case),
        _path("M276,188 L290,188 L290,212 L276,212 Z", case, LW_DETAIL),
    ]
    if face == "teacher":
        out += [_circle(200, 200, 64, "#fbf8f2", LW_DETAIL), _dial_ticks(200, 200, 60)]
        for k in range(1, 13):
            ang = math.radians(k * 30)
            out.append(_word(str(k), 200 + 44 * math.sin(ang), 205 - 44 * math.cos(ang), 16, 13))
        out += [_line("M200,200 L200,160", 3, "", "#3f6fb5"), _line("M200,200 L222,212", 4.4, "", "#c8312e"), _circle(200, 200, 4, INK, 1)]
    else:
        out += [
            f'<rect x="146" y="166" width="108" height="68" rx="10" fill="{SCREEN}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
            _word("10:09", 200, 208, 90, 30, "#33403a"),
            _circle(158, 266, 6, case, LW_DETAIL), _circle(242, 266, 6, case, LW_DETAIL),
        ]
    out.append(_highlight("M140,170 Q152,140 182,128", 5, 0.5))
    if label:
        out.append(_word(label, 200, 388, 200, 20))
    return out


register({"jewellery_set": jewellery_set, "kids_watch": kids_watch, "charm": charm, "brooch": brooch, "jewellery_box": jewellery_box, "pendant": pendant, "anklet": anklet, "watch_strap": watch_strap,"hoop_earrings": hoop_earrings, "drop_earrings": drop_earrings, "analog_watch": analog_watch, "digital_watch": digital_watch, "fitness_band": fitness_band, "stud_earrings": stud_earrings, "bangle": bangle, "cufflinks": cufflinks})
