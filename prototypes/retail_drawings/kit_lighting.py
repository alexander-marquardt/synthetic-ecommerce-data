"""Lighting shapes for the retail drawing kit (gen#197): floor, desk, ceiling and wall lights,
and lampshades.

Same house style as :mod:`kit`: flat outlines in the kit's ink, the record's fill (color and
pattern) on the product's main surface. On a light that surface is the shade (a wall light's
glass, a desk lamp's whole body); the frame, pole or ceiling rose is drawn in the ``finish``,
a SKU option, so a brass SKU's image shows a brass frame (``export.drawing_spec`` draws a
SKU's own value of a param its drawing takes).

==============  ===================================================  =========================
shape           draws                                                params
==============  ===================================================  =========================
floor_lamp      a floor lamp on its base                             style (arc, tripod,
                                                                     uplighter, task,
                                                                     mother-and-child), finish
desk_lamp       a desk lamp, painted all over                        arm (adjustable,
                                                                     gooseneck, clamp-on), base
ceiling_light   a ceiling light under its rose                       kind (pendant, flush,
                                                                     semi-flush, chandelier,
                                                                     spotlight bar), lights,
                                                                     finish
wall_light      a wall light on its back plate                       kind (sconce, swing arm,
                                                                     picture light), power,
                                                                     finish
lampshade       a shade alone, to scale against a fixed fitting      form (drum, empire,
                                                                     tapered, scalloped,
                                                                     pleated), diameter_cm
==============  ===================================================  =========================

A table lamp is :func:`kit_home.table_lamp`, whose ``style`` and ``shade_color`` params this
module's palettes (:data:`SHADE_COLORS`) serve. Every params value is a string, as a row's
``params`` carry it.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _tint, _word, register

#: A finish (a SKU's ``finish``, lowercased) -> the color its frame is drawn in.
FINISHES = {
    "brass": "#c9a227", "antique brass": "#9c7a34", "chrome": "#d5dbe0",
    "satin nickel": "#b4b6ae", "matte black": "#2f2f33", "copper": "#c06a3c",
    "oak": "#c69c6d", "walnut": "#6b4a2f", "matte white": "#f2f1ec",
}  # fmt: skip
#: A shade color (a table lamp SKU's ``shade_color``, lowercased) -> its hex.
SHADE_COLORS = {
    "white": "#f6f3ea", "cream": "#efe6cf", "natural": "#e3d6bb", "grey": "#a3a7ab",
    "black": "#2f2f33", "navy": "#26365c", "dark green": "#3f5f45", "pink": "#e8b4b8",
}  # fmt: skip
GLOW = "#fbe7a1"
BULB = "#fff6d8"
#: The floor a standing light stands on.
FLOOR = 364


def finish_color(finish: str) -> str:
    """The frame color of a finish; an unknown finish is a refused drawing, never a guess."""
    try:
        return FINISHES[finish.lower()]
    except KeyError:
        raise ValueError(f"unknown finish {finish!r}; one of {sorted(FINISHES)}") from None


def shade_color(name: str) -> str:
    try:
        return SHADE_COLORS[name.lower()]
    except KeyError:
        raise ValueError(f"unknown shade color {name!r}; one of {sorted(SHADE_COLORS)}") from None


def _rod(d: str, color: str, width: float = 6) -> list[str]:
    """A pole, arm or cord in ``color``: an ink outline under the rod's own stroke."""
    cap = ' stroke-linecap="round" stroke-linejoin="round"'
    return [
        f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{width + 3:g}"{cap}/>',
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width:g}"{cap}/>',
    ]


def _circle(cx: float, cy: float, r: float, fill: str, width: float = LW_DETAIL) -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _glow(d: str) -> str:
    return _path(d, GLOW, 1.0, ' fill-opacity=".7" stroke-opacity="0"')


def _base(cx: float, rx: float, metal: str) -> list[str]:
    """A round weighted base seen a little from above, standing on the floor."""
    return [
        f'<ellipse cx="{cx:g}" cy="{FLOOR - 6}" rx="{rx:g}" ry="{rx * 0.24:.1f}" fill="{_shade(metal, 0.25)}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<ellipse cx="{cx:g}" cy="{FLOOR - 11}" rx="{rx:g}" ry="{rx * 0.24:.1f}" fill="{metal}" stroke="{INK}" stroke-width="{LW}"/>',
    ]


def _drum(cx: float, top: float, w_top: float, w_bot: float, h: float, paint: str) -> list[str]:
    """A shade from the side: its top and bottom widths and its height, trimmed at both rims."""
    x0, x1 = cx - w_top / 2, cx + w_top / 2
    b0, b1 = cx - w_bot / 2, cx + w_bot / 2
    return [
        _path(f"M{x0:.1f},{top:.1f} L{x1:.1f},{top:.1f} L{b1:.1f},{top + h:.1f} L{b0:.1f},{top + h:.1f} Z", paint),
        _line(f"M{x0 + 2:.1f},{top + 6:.1f} L{x1 - 2:.1f},{top + 6:.1f} M{b0 + 2:.1f},{top + h - 6:.1f} L{b1 - 2:.1f},{top + h - 6:.1f}", 1.2, ' stroke-opacity=".6"'),
    ]


def _dome(cx: float, top: float, w: float, h: float, paint: str) -> list[str]:
    """A dome shade, open at the bottom, a bulb glowing under its rim."""
    x0, x1, y1 = cx - w / 2, cx + w / 2, top + h
    return [
        _glow(f"M{x0 + 8:.1f},{y1:.1f} L{x1 - 8:.1f},{y1:.1f} L{cx + w * 0.8:.1f},{y1 + h * 1.4:.1f} L{cx - w * 0.8:.1f},{y1 + h * 1.4:.1f} Z"),
        _circle(cx, y1 - 2, w * 0.1, BULB),
        _path(f"M{x0:.1f},{y1:.1f} C{x0 + 2:.1f},{top + h * 0.2:.1f} {cx - w * 0.2:.1f},{top:.1f} {cx:.1f},{top:.1f} C{cx + w * 0.2:.1f},{top:.1f} {x1 - 2:.1f},{top + h * 0.2:.1f} {x1:.1f},{y1:.1f} Z", paint),
        _highlight(f"M{cx - w * 0.3:.1f},{top + h * 0.75:.1f} Q{cx - w * 0.28:.1f},{top + h * 0.3:.1f} {cx - w * 0.08:.1f},{top + h * 0.15:.1f}", 3, 0.5),
    ]


def _cone(x: float, y: float, angle: float, length: float, mouth: float, paint: str) -> list[str]:
    """A task shade: a cone from its pivot (x, y) along ``angle`` degrees, open at the mouth."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    ex, ey = x + ux * length, y + uy * length
    neck = mouth * 0.28
    pts = [
        (x + px * neck, y + py * neck), (ex + px * mouth / 2, ey + py * mouth / 2),
        (ex - px * mouth / 2, ey - py * mouth / 2), (x - px * neck, y - py * neck),
    ]  # fmt: skip
    d = "M" + " L".join(f"{u:.1f},{v:.1f}" for u, v in pts) + " Z"
    gx, gy = ex + ux * length * 1.6, ey + uy * length * 1.6
    glow = f"M{pts[1][0]:.1f},{pts[1][1]:.1f} L{gx + px * mouth * 1.2:.1f},{gy + py * mouth * 1.2:.1f} L{gx - px * mouth * 1.2:.1f},{gy - py * mouth * 1.2:.1f} L{pts[2][0]:.1f},{pts[2][1]:.1f} Z"
    return [_glow(glow), _path(d, paint), _circle(x, y, neck * 0.9, _shade(paint, 0.15) if paint.startswith("#") else INK)]


# --------------------------------------------------------------------------
# Floor lamps
# --------------------------------------------------------------------------


def floor_lamp(paint: str, fill: Fill, label: str | None, style: str = "arc", finish: str = "brass") -> list[str]:
    """A floor lamp: ``style`` sets its form, ``finish`` its frame, the fill its shade."""
    metal = finish_color(finish)
    style = style.lower()
    if style == "arc":
        out = [*_base(108, 46, metal), *_rod("M108,350 L108,206 C108,78 214,40 296,112", metal, 7)]
        out += _rod("M296,112 L296,150", INK, 1.5)
        return out + _dome(296, 150, 116, 66, paint)
    if style == "tripod":
        out = _rod("M200,196 L118,360 M200,196 L282,360 M200,196 L204,372", metal, 7)
        out += [_circle(200, 196, 7, metal)]
        out += _rod("M200,196 L200,160", metal, 5)
        return out + _drum(200, 58, 132, 150, 110, paint)
    if style == "uplighter":
        out = [*_base(200, 52, metal), *_rod("M200,350 L200,128", metal, 7)]
        out += [_glow("M120,104 L280,104 L340,30 L60,30 Z")]
        out.append(_path("M118,100 L282,100 Q270,148 200,150 Q130,148 118,100 Z", paint))
        out.append(f'<ellipse cx="200" cy="100" rx="82" ry="10" fill="{_tint(paint, 0.4) if paint.startswith("#") else BULB}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
        return out
    if style == "task":
        out = [*_base(150, 46, metal), *_rod("M150,350 L150,110 L232,64", metal, 7)]
        out += [_circle(150, 110, 7, metal), _circle(232, 64, 6, metal)]
        return out + _cone(232, 64, 52, 80, 92, paint)
    if style == "mother-and-child":
        out = [*_base(190, 52, metal), *_rod("M190,350 L190,128 M190,236 L238,196 L262,160", metal, 6)]
        out += [_glow("M118,104 L262,104 L320,30 L60,30 Z")]
        out.append(_path("M116,100 L264,100 Q252,144 190,146 Q128,144 116,100 Z", paint))
        out.append(f'<ellipse cx="190" cy="100" rx="74" ry="9" fill="{BULB}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
        out += [_circle(238, 196, 5, metal)]
        return out + _cone(262, 160, 20, 48, 58, paint)
    raise ValueError(f"unknown floor lamp style {style!r}")


# --------------------------------------------------------------------------
# Desk lamps
# --------------------------------------------------------------------------


def _light(paint: str) -> bool:
    """Whether a ``#rrggbb`` paint is light enough that a white mark on it would not show."""
    if not paint.startswith("#"):
        return False
    r, g, b = (int(paint[i : i + 2], 16) for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b > 160


def _charging_pad(cx: float, y: float, paint: str) -> list[str]:
    """The phone-charging coil marked on a desk lamp's base: white on a dark base, ink on a
    light one, so a white lamp's pad still shows."""
    ink = INK if _light(paint) else "#ffffff"
    return [
        f'<ellipse cx="{cx:g}" cy="{y:g}" rx="{r}" ry="{r * 0.28:.1f}" fill="none" stroke="{ink}" stroke-opacity=".75" stroke-width="1.6"/>'
        for r in (14, 24, 34)
    ]


def desk_lamp(paint: str, fill: Fill, label: str | None, arm: str = "adjustable", base: str = "round") -> list[str]:
    """A desk lamp painted all over in the fill: ``arm`` sets its form, a ``pad`` base marks
    the phone-charging coil."""
    arm = arm.lower()
    dark = _shade(paint, 0.3) if paint.startswith("#") else INK
    out: list[str] = []
    if arm == "clamp-on":
        out.append(_path("M40,300 L300,300 L300,330 L40,330 Z", "#c69c6d"))
        out.append(_line("M60,308 L280,308", 1.2, ' stroke-opacity=".4"'))
        out.append(_path("M276,284 L316,284 L316,350 L292,350 L292,334 L304,334 L304,296 L276,296 Z", paint))
        out += _rod("M298,350 L298,372", INK, 4)
        out.append(_path("M284,370 L312,370 L312,378 L284,378 Z", dark))
        out += _rod("M296,284 L250,170", paint, 9)
        out += _rod("M250,170 L140,112", paint, 9)
        out += [_circle(296, 284, 8, dark), _circle(250, 170, 9, dark)]
        out += _line("M286,262 L262,206", 1.4, "", "#ffffff")
        return out + _cone(140, 112, 112, 70, 86, paint)
    width = 150 if base == "pad" else 110
    cx = 150
    out.append(f'<ellipse cx="{cx}" cy="350" rx="{width / 2:g}" ry="16" fill="{dark}" stroke="{INK}" stroke-width="{LW}"/>')
    out.append(f'<ellipse cx="{cx}" cy="342" rx="{width / 2:g}" ry="16" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>')
    if base == "pad":
        out += _charging_pad(cx, 342, paint)
    if arm == "adjustable":
        out += _rod(f"M{cx},336 L210,214", paint, 9)
        out += _rod("M210,214 L300,150", paint, 9)
        out += _line(f"M{cx + 12},322 L216,232 M216,206 L292,156", 1.4, ' stroke-dasharray="3 3"')
        out += [_circle(cx, 336, 8, dark), _circle(210, 214, 9, dark)]
        return out + _cone(300, 150, 100, 66, 84, paint)
    if arm == "gooseneck":
        out += _rod(f"M{cx},336 L{cx},240", paint, 9)
        neck = f"M{cx},240 C{cx},160 200,98 280,100"
        out += _rod(neck, paint, 9)
        out += [_line(f"M{cx - 6 + t * 2:.0f},{240 - t * 13:.0f} l12,0", 1.0) for t in range(0, 7)]
        out.append(_path("M262,92 L340,98 Q350,100 348,110 L344,118 L262,112 Z", paint))
        out.append(_glow("M266,114 L342,120 L360,210 L240,200 Z"))
        out.append(_line("M270,112 L340,118", 2.2, "", BULB))
        return out
    raise ValueError(f"unknown desk lamp arm {arm!r}")


# --------------------------------------------------------------------------
# Ceiling lights
# --------------------------------------------------------------------------


def _rose(cx: float, w: float, metal: str) -> str:
    """The ceiling rose (canopy) the light hangs from, against the ceiling line."""
    return _path(f"M{cx - w / 2:.1f},34 L{cx + w / 2:.1f},34 L{cx + w / 2 - 6:.1f},48 L{cx - w / 2 + 6:.1f},48 Z", metal)


def _ceiling() -> str:
    return _line("M30,34 L370,34", 2.0, ' stroke-opacity=".35"')


def ceiling_light(paint: str, fill: Fill, label: str | None, kind: str = "pendant", lights: str = "1", finish: str = "brass") -> list[str]:
    """A ceiling light: ``kind`` sets its form, ``lights`` how many shades or heads it has,
    ``finish`` its rose, rods and arms, the fill its shades."""
    metal = finish_color(finish)
    kind, n = kind.lower(), max(1, int(lights))
    out = [_ceiling()]
    if kind == "pendant":
        if n == 1:
            out += [_rose(200, 64, metal), *_rod("M200,48 L200,170", INK, 1.6)]
            return out + _dome(200, 170, 190, 100, paint)
        xs = [70 + (260 * i / (n - 1)) for i in range(n)]
        out.append(_path(f"M{xs[0] - 22:.1f},34 L{xs[-1] + 22:.1f},34 L{xs[-1] + 16:.1f},46 L{xs[0] - 16:.1f},46 Z", metal))
        w = min(96.0, 300 / n)
        for i, x in enumerate(xs):
            drop = 150 + 40 * ((i + 1) % 2)
            out += _rod(f"M{x:.1f},46 L{x:.1f},{drop}", INK, 1.4)
            out += _dome(x, drop, w, w * 0.62, paint)
        return out
    if kind == "flush":
        out.append(_path("M78,36 L322,36 L316,92 Q200,112 84,92 Z", paint))
        out.append(f'<ellipse cx="200" cy="96" rx="112" ry="12" fill="{_tint(paint, 0.45) if paint.startswith("#") else BULB}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
        out.append(_path("M78,34 L322,34 L322,42 L78,42 Z", metal, LW_DETAIL))
        out.append(_glow("M100,110 L300,110 L360,240 L40,240 Z"))
        return out
    if kind == "semi-flush":
        out += [_rose(200, 90, metal), *_rod("M170,48 L140,124 M230,48 L260,124 M200,48 L200,124", metal, 4)]
        out.append(_glow("M100,180 L300,180 L350,300 L50,300 Z"))
        out.append(_path("M86,120 L314,120 Q300,190 200,192 Q100,190 86,120 Z", paint))
        out.append(f'<ellipse cx="200" cy="120" rx="114" ry="12" fill="{_shade(paint, 0.15) if paint.startswith("#") else INK}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
        out += [_circle(200, 122, 5, metal)]
        return out
    if kind == "chandelier":
        out += [_rose(200, 60, metal), *_rod("M200,48 L200,150", metal, 4)]
        out.append(_path("M186,150 L214,150 L220,222 Q200,236 180,222 Z", metal))
        for i in range(n):
            t = (i + 0.5) / n
            x = 50 + 300 * t
            sag = 238 + 30 * math.sin(math.pi * t)
            out += _rod(f"M200,210 Q{(200 + x) / 2:.1f},{sag + 30:.1f} {x:.1f},{sag - 40:.1f}", metal, 4)
            out.append(_path(f"M{x - 10:.1f},{sag - 40:.1f} L{x + 10:.1f},{sag - 40:.1f} L{x + 8:.1f},{sag - 52:.1f} L{x - 8:.1f},{sag - 52:.1f} Z", metal, LW_DETAIL))
            out.append(_path(f"M{x - 4:.1f},{sag - 52:.1f} L{x + 4:.1f},{sag - 52:.1f} L{x + 4:.1f},{sag - 70:.1f} L{x - 4:.1f},{sag - 70:.1f} Z", "#ffffff", LW_DETAIL))
            out += _drum(x, sag - 104, 26, 44, 40, paint)
        return out
    if kind == "spotlight bar":
        out.append(_path("M54,36 L346,36 L346,56 L54,56 Z", metal))
        for i in range(n):
            x = 54 + 292 * (i + 0.5) / n
            tilt = -18 + 36 * (i / (n - 1)) if n > 1 else 0
            out += _rod(f"M{x:.1f},56 L{x:.1f},76", metal, 4)
            out.append(f'<g transform="rotate({tilt:.1f} {x:.1f} 80)">')
            out.append(_glow(f"M{x - 20:.1f},156 L{x + 20:.1f},156 L{x + 48:.1f},280 L{x - 48:.1f},280 Z"))
            out.append(_path(f"M{x - 22:.1f},76 L{x + 22:.1f},76 L{x + 24:.1f},156 L{x - 24:.1f},156 Z", paint))
            out.append(f'<ellipse cx="{x:.1f}" cy="156" rx="24" ry="6" fill="{BULB}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
            out.append("</g>")
        return out
    raise ValueError(f"unknown ceiling light kind {kind!r}")


# --------------------------------------------------------------------------
# Wall lights
# --------------------------------------------------------------------------


def _plate(x: float, y: float, w: float, h: float, metal: str) -> str:
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{min(w, h) / 2:g}" fill="{metal}" stroke="{INK}" stroke-width="{LW}"/>'


def _plug(out: list[str], x: float, y: float) -> None:
    """A fabric cable looping down from (x, y) to a three-pin plug: a plug-in light."""
    out += _rod(f"M{x:.1f},{y:.1f} C{x - 10:.1f},{y + 120:.1f} {x + 140:.1f},{y + 90:.1f} {x + 150:.1f},{y + 150:.1f}", "#efe6cf", 3)
    out.append(f'<rect x="{x + 138:.1f}" y="{y + 150:.1f}" width="24" height="28" rx="4" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
    out.append(_line(f"M{x + 144:.1f},{y + 178:.1f} l0,8 M{x + 156:.1f},{y + 178:.1f} l0,8 M{x + 150:.1f},{y + 150:.1f} l0,-6", 2.4))


def _battery(out: list[str], x: float, y: float) -> None:
    """A cordless light's charge marks: a battery with three bars and its USB-C port."""
    out.append(f'<rect x="{x:g}" y="{y:g}" width="34" height="16" rx="3" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
    out.append(f'<rect x="{x + 34:g}" y="{y + 5:g}" width="4" height="6" fill="{INK}"/>')
    out += [f'<rect x="{x + 4 + 10 * i:g}" y="{y + 4:g}" width="7" height="8" fill="#5fae5a"/>' for i in range(3)]


def wall_light(paint: str, fill: Fill, label: str | None, kind: str = "sconce", power: str = "hardwired", finish: str = "brass") -> list[str]:
    """A wall light seen from the side or the front: ``kind`` sets its form, ``power`` adds a
    plug-in cable or a cordless light's battery, ``finish`` its plate and arm, the fill its shade."""
    metal = finish_color(finish)
    kind, power = kind.lower(), power.lower()
    out: list[str] = [_line("M48,30 L48,370", 2.0, ' stroke-opacity=".35"')]
    if kind == "sconce":
        out.append(_plate(48, 150, 34, 110, metal))
        out += _rod("M82,206 C130,206 168,196 188,150", metal, 6)
        out += [_circle(188, 150, 6, metal)]
        out.append(_glow("M140,64 L240,64 L280,10 L100,10 Z"))
        out.append(_glow("M140,206 L240,206 L270,280 L110,280 Z"))
        out += _drum(190, 70, 104, 132, 136, paint)
        cable_at = (65, 260)
    elif kind == "swing arm":
        out.append(_plate(48, 120, 30, 90, metal))
        out += _rod("M78,164 L120,164 M120,164 L230,128", metal, 6)
        out += [_circle(120, 164, 7, metal), _circle(230, 128, 6, metal)]
        out += _cone(230, 128, 40, 74, 96, paint)
        cable_at = (63, 210)
    elif kind == "picture light":
        out.append(f'<rect x="92" y="150" width="236" height="190" fill="#8a6a4a" stroke="{INK}" stroke-width="{LW}"/>')
        out.append(f'<rect x="108" y="166" width="204" height="158" fill="#cfe0e8" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
        out.append(_path("M108,290 L160,236 L196,270 L246,214 L312,284 L312,324 L108,324 Z", "#7f9f6f", LW_DETAIL))
        out.append(_glow("M100,106 L320,106 L328,220 L92,220 Z"))
        out.append(_plate(190, 96, 40, 40, metal))
        out += _rod("M210,116 L210,86", metal, 5)
        out.append(_path("M96,70 L324,70 Q334,70 330,84 L318,108 L102,108 L90,84 Q86,70 96,70 Z", paint))
        out.append(_line("M108,102 L312,102", 2.6, "", BULB))
        cable_at = (210, 136)
    else:
        raise ValueError(f"unknown wall light kind {kind!r}")
    if power == "plug-in":
        _plug(out, *cable_at)
    elif power == "rechargeable":
        _battery(out, 280, 330)
    return out


# --------------------------------------------------------------------------
# Lampshades
# --------------------------------------------------------------------------

#: Sheet units per centimetre: a 50 cm shade spans 300 of the 400-unit sheet.
PX_PER_CM = 6.0
#: The fixed fitting every shade is drawn against: a 4 cm bulb holder ring.
FITTING_CM = 4.0
#: form (the attribute ``shape``) -> (top width, height), each as a share of the bottom diameter.
SHADE_FORMS = {
    "drum": (1.0, 0.62), "empire": (0.5, 0.72), "tapered": (0.72, 0.66),
    "scalloped": (0.6, 0.7), "pleated": (0.55, 0.72),
}  # fmt: skip


def lampshade(paint: str, fill: Fill, label: str | None, form: str = "drum", diameter_cm: str = "30") -> list[str]:
    """A shade alone, its bottom ``diameter_cm`` drawn to scale beside a fixed fitting ring and
    dimensioned underneath: a 40 cm drum is visibly larger than a 25 cm one."""
    form = form.lower()
    top_share, h_share = SHADE_FORMS[form]
    d = float(diameter_cm) * PX_PER_CM
    w_top, h = d * top_share, d * h_share
    cx, bottom = 200.0, 300.0
    top = bottom - h
    out: list[str] = []
    if form == "scalloped":
        x0, x1 = cx - w_top / 2, cx + w_top / 2
        b0, b1 = cx - d / 2, cx + d / 2
        n = max(5, round(d / 34))
        step = (b1 - b0) / n
        hem = " ".join(f"Q{b1 - step * (i + 0.5):.1f},{bottom + 16:.1f} {b1 - step * (i + 1):.1f},{bottom:.1f}" for i in range(n))
        out.append(_path(f"M{x0:.1f},{top:.1f} L{x1:.1f},{top:.1f} L{b1:.1f},{bottom:.1f} {hem} Z", paint))
        out.append(_line(f"M{x0 + 2:.1f},{top + 6:.1f} L{x1 - 2:.1f},{top + 6:.1f}", 1.2, ' stroke-opacity=".6"'))
    else:
        out += _drum(cx, top, w_top, d, h, paint)
    if form == "pleated":
        n = max(8, round(d / 14))
        for i in range(1, n):
            t = i / n
            xt, xb = cx - w_top / 2 + w_top * t, cx - d / 2 + d * t
            out.append(_line(f"M{xt:.1f},{top + 2:.1f} L{xb:.1f},{bottom - 2:.1f}", 1.1, ' stroke-opacity=".45"'))
    ring = FITTING_CM * PX_PER_CM / 2
    out.append(f'<ellipse cx="{cx:g}" cy="{top:.1f}" rx="{w_top / 2:.1f}" ry="{max(4.0, w_top * 0.08):.1f}" fill="{_shade(paint, 0.35) if paint.startswith("#") else INK}" fill-opacity=".55" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
    out.append(_line(f"M{cx - w_top / 2 + 4:.1f},{top:.1f} L{cx - ring:.1f},{top:.1f} M{cx + ring:.1f},{top:.1f} L{cx + w_top / 2 - 4:.1f},{top:.1f}", 1.6, "", "#9aa0a6"))
    out.append(f'<ellipse cx="{cx:g}" cy="{top:.1f}" rx="{ring:.1f}" ry="{ring * 0.4:.1f}" fill="#d5dbe0" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
    dim = bottom + 34
    out.append(_line(f"M{cx - d / 2:.1f},{dim:.1f} L{cx + d / 2:.1f},{dim:.1f} M{cx - d / 2:.1f},{dim - 8:.1f} L{cx - d / 2:.1f},{dim + 8:.1f} M{cx + d / 2:.1f},{dim - 8:.1f} L{cx + d / 2:.1f},{dim + 8:.1f}", 1.4))
    out.append(f'<rect x="{cx - 34:g}" y="{dim - 11:.1f}" width="68" height="22" fill="#ffffff"/>')
    out.append(_word(f"{diameter_cm} cm", cx, dim, 64, 16))
    return out


register(
    {"floor_lamp": floor_lamp, "desk_lamp": desk_lamp, "ceiling_light": ceiling_light,
     "wall_light": wall_light, "lampshade": lampshade},
)  # fmt: skip


# --------------------------------------------------------------------------
# Table lamps (drawn through kit_home.table_lamp)
# --------------------------------------------------------------------------


def styled_table_lamp(paint: str, fill: Fill, style: str, shade_color_name: str, power: str) -> list[str]:
    """A table lamp by ``style``: the base takes the fill (the record's color is the base's),
    the shade ``shade_color_name``; ``power`` draws a cable and plug or a cordless battery."""
    style, power = style.lower(), power.lower()
    shade = shade_color(shade_color_name)
    dark = _shade(paint, 0.3) if paint.startswith("#") else INK
    out: list[str] = []
    if power == "plug-in":
        out += _rod("M236,346 Q300,356 318,334 Q332,310 352,324", "#efe6cf", 2.4)
        out.append(f'<rect x="346" y="318" width="16" height="22" rx="3" fill="#ffffff" stroke="{INK}" stroke-width="1.4" transform="rotate(30 354 329)"/>')
    if style == "mushroom":
        out.append(_path("M176,336 L224,336 L214,200 L186,200 Z", paint))
        out.append(f'<ellipse cx="200" cy="340" rx="58" ry="12" fill="{dark}" stroke="{INK}" stroke-width="{LW}"/>')
        out.append(_glow("M120,198 L280,198 L310,250 L90,250 Z"))
        out += _dome(200, 96, 200, 108, shade)[1:]
    elif style == "ceramic":
        base = "M200,206 C150,206 140,262 156,296 C166,318 176,326 172,338 L228,338 C224,326 234,318 244,296 C260,262 250,206 200,206 Z"
        out += [_line("M200,186 L200,208", 6), _path(base, paint), _highlight("M168,236 Q156,262 166,290", 6, 0.4)]
        out.append(f'<rect x="158" y="336" width="84" height="14" rx="4" fill="{dark}" stroke="{INK}" stroke-width="{LW}"/>')
        out += _drum(200, 62, 108, 188, 124, shade)
    elif style == "bedside":
        out.append(_path("M184,338 L216,338 L212,196 L188,196 Z", paint))
        out.append(f'<rect x="150" y="334" width="100" height="16" rx="5" fill="{dark}" stroke="{INK}" stroke-width="{LW}"/>')
        out += _drum(200, 96, 140, 140, 100, shade)
    elif style == "touch":
        out.append(_path("M168,340 C150,300 186,250 192,196 L208,196 C214,250 250,300 232,340 Z", paint))
        out.append(f'<ellipse cx="200" cy="342" rx="60" ry="10" fill="{dark}" stroke="{INK}" stroke-width="{LW}"/>')
        out += [f'<circle cx="200" cy="{y}" r="{r}" fill="none" stroke="#ffffff" stroke-opacity=".8" stroke-width="1.6"/>' for y, r in ((296, 8), (296, 14))]
        out += _drum(200, 80, 120, 176, 116, shade)
    else:
        raise ValueError(f"unknown table lamp style {style!r}")
    if power == "rechargeable":
        _battery(out, 262, 322)
    return out
