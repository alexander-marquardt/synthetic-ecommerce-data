"""Small appliance shapes for the retail drawing kit (gen#202): fans, heaters, kettles, toasters.

Each type of the appliance rows (:mod:`appliance_rows`) has its own flat drawing in the
kit's house style: outlines in the kit's ink and the record's fill (color and pattern) on
the appliance's body, so a shopper tells a desk fan from a pedestal fan, an oil-filled
radiator from a convector and a jug kettle from a gooseneck at thumbnail size.

==============  ===================================================  ======================
shape           draws                                                params
==============  ===================================================  ======================
desk_fan        a caged fan head, front on, on a short stand or a    kind, blades
                clip; its blades counted
pedestal_fan    a caged fan head on a tall telescopic pole and a     base, blades
                round or cross base; its blades counted
tower_fan       a slim column with a louvred grille, or a bladeless  kind, height
                open loop, on a round foot; drawn to its height
ceiling_fan     a fan under a ceiling canopy and downrod, seen from  blades, light, wood
                a little below: its blades counted, a light bowl
handheld_fan    a small caged head on a handle, or a neck fan's      kind, blades, fold
                horseshoe band with its vents
heater          a fan heater, an oil-filled radiator (its fins       kind, fin_count, tubes
                counted), a convector, a halogen heater (its tubes
                counted) or a ceramic heater
kettle          a jug, dome, gooseneck or travel kettle on its       kind, material
                power base; a glass body shows its water
toaster         a toaster from above and in front, its slots         slots, long
                counted
==============  ===================================================  ======================

Counted marks carry a class, so a test counts them in the SVG: ``class="blade"``,
``class="fin"``, ``class="tube"`` and ``class="slot"``. No drawing prints a size, a
wattage or a capacity: one image serves every size its color sells.

Every params value is a string, as a style row's ``params`` carry it, and every param has
a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _tint, register
from kit_garments import _dark

STEEL = "#cfd5da"
STEEL_DARK = "#8f989f"
WOOD = "#b8875a"
BLACK = "#2f2f35"
GLOW = "#f39a3b"
GLASS = "#e3eef0"
WATER = "#9cc7e6"
PAPER = "#fbfaf6"


def _int(value: str, default: int) -> int:
    try:
        return int(float(str(value).split()[0]))
    except (ValueError, IndexError):
        return default


def _yes(value: str) -> bool:
    return str(value).lower() in {"yes", "true", "1"}


def _rect(
    x: float, y: float, w: float, h: float, fill: str, rx: float = 0, width: float = LW, extra: str = ""
) -> str:
    return (
        f'<rect{extra} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" '
        f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'
    )


def _circle(cx: float, cy: float, r: float, fill: str, width: float = LW, extra: str = "") -> str:
    return (
        f'<circle{extra} cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
        f'stroke="{INK}" stroke-width="{width}"/>'
    )


def _ellipse(
    cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW, extra: str = ""
) -> str:
    return (
        f'<ellipse{extra} cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
        f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'
    )


def _shadow(cx: float, cy: float, rx: float) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{rx * 0.1:.1f}" fill="#000000" fill-opacity=".08"/>'


# --------------------------------------------------------------------------
# Fans
# --------------------------------------------------------------------------


def _caged_head(cx: float, cy: float, r: float, n: int, paint: str, fill: Fill) -> list[str]:
    """A fan head front on: a dark back, ``n`` blades (each ``class="blade"``), a hub, a
    grille of rings and spokes, and a rim painted in the fill."""
    blade = _tint(fill.base, 0.45)
    out = [_circle(cx, cy, r, _shade(fill.base, 0.55), LW_DETAIL)]
    for i in range(n):
        a = 360 * i / n
        bx, by = cx, cy - r * 0.5
        out.append(
            f'<ellipse class="blade" cx="{bx:.1f}" cy="{by:.1f}" rx="{r * 0.2:.1f}" ry="{r * 0.4:.1f}" '
            f'fill="{blade}" stroke="{INK}" stroke-width="{LW_DETAIL}" '
            f'transform="rotate({a:.1f} {cx:.1f} {cy:.1f}) rotate(24 {bx:.1f} {by:.1f})"/>'
        )
    out.append(_circle(cx, cy, r * 0.17, paint, LW_DETAIL))
    out.append(_circle(cx, cy, r * 0.07, _shade(fill.base, 0.3), 1))
    for k in (0.38, 0.62, 0.84):
        out.append(_circle(cx, cy, r * k, "none", 1, ' stroke-opacity=".55"'))
    for i in range(24):
        a = math.radians(360 * i / 24)
        out.append(
            _line(
                f"M{cx + r * 0.2 * math.cos(a):.1f},{cy + r * 0.2 * math.sin(a):.1f} "
                f"L{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}",
                0.9,
                ' stroke-opacity=".45"',
            )
        )
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{paint}" stroke-width="9"/>')
    out.append(_circle(cx, cy, r - 4.5, "none", LW_DETAIL))
    out.append(_circle(cx, cy, r + 4.5, "none", LW_DETAIL))
    return out


def desk_fan(paint: str, fill: Fill, label: str | None, kind: str = "stand", blades: str = "5") -> list[str]:
    """A desk fan front on: the caged head, its neck and a low stand with speed buttons, or a
    clip that grips a desk edge."""
    cx, cy, r = 200.0, 150.0, 108.0
    out = [_shadow(cx, 342, 110)]
    out.append(_rect(cx - 13, cy + r - 6, 26, 62, paint, 4, LW))
    if kind == "clip":
        out.append(_path(f"M{cx - 52},{cy + r + 52} L{cx + 52},{cy + r + 52} L{cx + 52},{cy + r + 110} L{cx + 30},{cy + r + 110} L{cx + 30},{cy + r + 72} L{cx - 52},{cy + r + 72} Z", paint))
        out.append(_rect(cx - 10, cy + r + 88, 40, 10, BLACK, 3, LW_DETAIL))
        out.append(_line(f"M{cx + 10},{cy + r + 98} L{cx + 10},{cy + r + 118}", 4))
    else:
        out.append(_ellipse(cx, cy + r + 66, 92, 22, _shade(fill.base, 0.2)))
        out.append(_path(f"M{cx - 92},{cy + r + 58} Q{cx},{cy + r + 26} {cx + 92},{cy + r + 58} L{cx + 92},{cy + r + 66} Q{cx},{cy + r + 96} {cx - 92},{cy + r + 66} Z", paint))
        for i in range(3):
            out.append(_ellipse(cx - 30 + i * 30, cy + r + 56, 9, 4, _tint(fill.base, 0.6), 1))
    out += _caged_head(cx, cy, r, _int(blades, 5), paint, fill)
    return out


def pedestal_fan(paint: str, fill: Fill, label: str | None, base: str = "round", blades: str = "5") -> list[str]:
    """A pedestal fan: the caged head on a two-part telescopic pole, with a control box, on a
    round base or a cross of four feet."""
    cx, cy, r = 200.0, 112.0, 92.0
    out = [_shadow(cx, 368, 120)]
    out.append(_rect(cx - 7, cy + r - 4, 14, 90, _tint(fill.base, 0.25), 3, LW_DETAIL))
    out.append(_rect(cx - 11, cy + r + 82, 22, 70, paint, 4, LW))
    out.append(_rect(cx - 22, cy + r + 98, 44, 26, _shade(fill.base, 0.2), 6, LW_DETAIL))
    out.append(_circle(cx - 9, cy + r + 111, 4, PAPER, 1))
    out.append(_circle(cx + 9, cy + r + 111, 4, PAPER, 1))
    if base == "cross":
        for d in (-1, 1):
            out.append(_path(f"M{cx},{356} L{cx + d * 110},{366} L{cx + d * 110},{372} L{cx},{366} Z", paint, LW_DETAIL))
        out.append(_path(f"M{cx - 50},{356} L{cx + 50},{356} L{cx + 34},{350} L{cx - 34},{350} Z", _shade(fill.base, 0.2), LW_DETAIL))
    else:
        out.append(_ellipse(cx, 362, 88, 16, _shade(fill.base, 0.2)))
        out.append(_ellipse(cx, 355, 88, 16, paint))
    out += _caged_head(cx, cy, r, _int(blades, 5), paint, fill)
    return out


def tower_fan(paint: str, fill: Fill, label: str | None, kind: str = "column", height: str = "80") -> list[str]:
    """A tower fan drawn to its height (110 cm fills the sheet): a slim column with a louvred
    grille and a top control panel, or a bladeless fan's tall open loop over a vented base."""
    h = 300 * min(max(_int(height, 80), 50), 110) / 110
    cx, foot = 200.0, 352.0
    top = foot - h
    out = [_shadow(cx, foot + 6, 80)]
    out.append(_ellipse(cx, foot - 4, 72, 14, _shade(fill.base, 0.2)))
    if kind == "bladeless":
        base_top = foot - h * 0.32
        out.append(_path(f"M{cx - 44},{foot - 8} L{cx - 38},{base_top} L{cx + 38},{base_top} L{cx + 44},{foot - 8} Z", paint))
        for i in range(6):
            y = base_top + 12 + i * (h * 0.32 - 28) / 6
            out.append(_line(f"M{cx - 30},{y:.1f} L{cx + 30},{y:.1f}", 2.2, ' stroke-opacity=".6"'))
        loop_top, loop_bot = top, base_top + 4
        mid = (loop_top + loop_bot) / 2
        ry = (loop_bot - loop_top) / 2
        out.append(_ellipse(cx, mid, 52, ry, paint, LW))
        out.append(_ellipse(cx, mid, 30, ry - 20, PAPER, LW_DETAIL))
        out.append(_highlight(f"M{cx - 44},{mid - ry * 0.4:.1f} Q{cx - 42},{mid - ry * 0.8:.1f} {cx - 20},{loop_top + 10:.1f}", 3, 0.6))
        return out
    out.append(_rect(cx - 40, top, 80, h - 6, paint, 28, LW))
    out.append(_rect(cx - 24, top + 46, 48, h - 92, _shade(fill.base, 0.45), 10, LW_DETAIL))
    n = int((h - 100) / 9)
    for i in range(n):
        y = top + 52 + i * 9
        out.append(_line(f"M{cx - 22},{y:.1f} L{cx + 22},{y:.1f}", 2.4, "", _tint(fill.base, 0.3)))
    out.append(_ellipse(cx, top + 22, 22, 8, _shade(fill.base, 0.35), LW_DETAIL))
    for i in range(3):
        out.append(_circle(cx - 10 + i * 10, top + 22, 2.4, PAPER, 0.8))
    out.append(_highlight(f"M{cx - 32},{top + 40:.1f} L{cx - 32},{foot - 30:.1f}", 3, 0.5))
    return out


def ceiling_fan(paint: str, fill: Fill, label: str | None, blades: str = "5", light: str = "no", wood: str = "no") -> list[str]:
    """A ceiling fan under its canopy and downrod, seen from a little below: ``blades``
    paddles (each ``class="blade"``) round the motor housing, and a light bowl under it."""
    n = _int(blades, 5)
    cx, cy, R, squash = 200.0, 168.0, 175.0, 0.36
    blade_fill = WOOD if _yes(wood) else paint
    out = [_line("M40,22 L360,22", 2, ' stroke-opacity=".5"')]
    out.append(_path(f"M{cx - 30},22 Q{cx},48 {cx + 30},22 Z", paint, LW_DETAIL))
    out.append(_rect(cx - 5, 40, 10, cy - 58, _shade(fill.base, 0.15), 2, LW_DETAIL))

    def blade(i: int) -> tuple[float, str]:
        a = math.radians(360 * i / n + 18)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        pts = []
        for along, half in ((40, 14), (R * 0.97, 26), (R, 18), (R, -18), (R * 0.97, -26), (40, -14)):
            x, y = along * ux + half * px, along * uy + half * py
            pts.append((cx + x, cy + y * squash))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
        iron = f"M{cx + 30 * ux:.1f},{cy + 30 * uy * squash:.1f} L{cx + 70 * ux:.1f},{cy + 70 * uy * squash:.1f}"
        return uy, (
            f'<path class="blade" d="{d}" fill="{blade_fill}" stroke="{INK}" stroke-width="{LW_DETAIL}" stroke-linejoin="round"/>'
            + _line(iron, 5, "", STEEL_DARK)
        )

    drawn = sorted((blade(i) for i in range(n)), key=lambda t: t[0])
    out += [svg for depth, svg in drawn if depth < 0]
    out.append(_ellipse(cx, cy + 6, 46, 18, _shade(fill.base, 0.25)))
    out.append(_path(f"M{cx - 46},{cy + 6} L{cx - 40},{cy - 22} Q{cx},{cy - 34} {cx + 40},{cy - 22} L{cx + 46},{cy + 6} Q{cx},{cy + 26} {cx - 46},{cy + 6} Z", paint))
    out += [svg for depth, svg in drawn if depth >= 0]
    if _yes(light):
        out.append(_path(f"M{cx - 34},{cy + 16} Q{cx - 30},{cy + 66} {cx},{cy + 68} Q{cx + 30},{cy + 66} {cx + 34},{cy + 16} Z", "#fbefc9", LW, ' class="light"'))
        out.append(_highlight(f"M{cx - 20},{cy + 30} Q{cx - 18},{cy + 52} {cx - 4},{cy + 58}", 3, 0.8))
    else:
        out.append(_ellipse(cx, cy + 22, 14, 6, _shade(fill.base, 0.2), LW_DETAIL))
    return out


def handheld_fan(paint: str, fill: Fill, label: str | None, kind: str = "handheld", blades: str = "5", fold: str = "no") -> list[str]:
    """A handheld fan: a small caged head on a handle with a power button (a hinge where it
    folds), or a neck fan: a horseshoe band seen from above, its vents along both arms."""
    cx = 200.0
    if kind == "neck":
        d = f"M{cx - 110},{120} L{cx - 110},{230} A110,110 0 0 0 {cx + 110},{230} L{cx + 110},{120}"
        out = [_shadow(cx, 362, 120)]
        out.append(_line(d, 52, "", INK))
        out.append(_line(d, 46, "", paint))
        for side in (-1, 1):
            for i in range(7):
                y = 132 + i * 15
                x = cx + side * 110
                out.append(_line(f"M{x - 12:.1f},{y} L{x + 12:.1f},{y}", 3, ' stroke-opacity=".7"'))
        out.append(_circle(cx, 340, 8, _shade(fill.base, 0.3), LW_DETAIL))
        return out
    cy, r = 135.0, 92.0
    out = [_shadow(cx, 364, 60)]
    out.append(_path(f"M{cx - 22},{cy + r - 4} L{cx - 26},{352} Q{cx},{364} {cx + 26},{352} L{cx + 22},{cy + r - 4} Z", paint))
    out.append(_circle(cx, cy + r + 50, 9, _tint(fill.base, 0.6), LW_DETAIL))
    if _yes(fold):
        out.append(_circle(cx, cy + r + 8, 12, _shade(fill.base, 0.2), LW_DETAIL))
        out.append(_line(f"M{cx - 24},{cy + r + 22} L{cx + 24},{cy + r + 22}", LW_DETAIL))
    out += _caged_head(cx, cy, r, _int(blades, 5), paint, fill)
    return out


# --------------------------------------------------------------------------
# Heaters
# --------------------------------------------------------------------------


def _knob(cx: float, cy: float, r: float = 9) -> list[str]:
    return [_circle(cx, cy, r, BLACK, LW_DETAIL), _line(f"M{cx},{cy - r + 2} L{cx},{cy - 2}", 2, "", PAPER)]


def heater(paint: str, fill: Fill, label: str | None, kind: str = "fan", fin_count: str = "9", tubes: str = "3") -> list[str]:
    """A heater by ``kind``: a fan heater's slatted box, an oil-filled radiator's ``fin_count``
    fins (each ``class="fin"``) on castors, a convector's low vented panel, a halogen heater's
    ``tubes`` glowing tubes (each ``class="tube"``), or a ceramic heater's honeycomb tower."""
    cx = 200.0
    out = [_shadow(cx, 352, 140)]
    if kind == "oil":
        n = max(_int(fin_count, 9), 3)
        width = min(300.0, 26.0 * n + 20)
        x0 = cx - width / 2
        step = width / n
        for i in range(n):
            out.append(_rect(x0 + i * step + 1.5, 96, step - 3, 222, paint, step * 0.45, LW_DETAIL, ' class="fin"'))
            out.append(_dark(f"M{x0 + i * step + step * 0.62:.1f},104 L{x0 + i * step + step - 4:.1f},104 L{x0 + i * step + step - 4:.1f},310 L{x0 + i * step + step * 0.62:.1f},310 Z", 0.12))
        out.append(_rect(x0 + width - 12, 112, 34, 64, _shade(fill.base, 0.15), 6, LW_DETAIL))
        out += _knob(x0 + width + 5, 132, 7)
        out += _knob(x0 + width + 5, 158, 7)
        for x in (x0 + step, x0 + width - step):
            out.append(_line(f"M{x:.1f},318 L{x:.1f},334", 4))
            out.append(_circle(x, 340, 8, BLACK, LW_DETAIL))
        return out
    if kind == "convector":
        out.append(_rect(56, 150, 288, 160, paint, 12))
        for i in range(22):
            x = 76 + i * 11.4
            out.append(_line(f"M{x:.1f},160 L{x:.1f},186", 3.2, ' stroke-opacity=".75"'))
        out.append(_rect(286, 206, 44, 80, _shade(fill.base, 0.15), 6, LW_DETAIL))
        out += _knob(308, 228)
        out += _knob(308, 262)
        for x in (90, 310):
            out.append(_path(f"M{x - 26},{340} Q{x},{326} {x + 26},{340} L{x + 22},{344} L{x - 22},{344} Z", BLACK, LW_DETAIL))
            out.append(_line(f"M{x},{310} L{x},{330}", 5))
        return out
    if kind == "halogen":
        n = max(_int(tubes, 3), 1)
        out.append(_rect(120, 50, 160, 290, paint, 30))
        out.append(_rect(138, 76, 124, 210, STEEL, 16, LW_DETAIL))
        gap = 210 / (n + 1)
        for i in range(n):
            y = 76 + gap * (i + 1)
            out.append(_rect(146, y - 9, 108, 18, GLOW, 9, LW_DETAIL, ' class="tube"'))
            out.append(_line(f"M152,{y - 3:.1f} L248,{y - 3:.1f}", 2.5, ' stroke-opacity=".7"', "#ffe2a8"))
        for i in range(7):
            x = 146 + i * 18
            out.append(_line(f"M{x},78 L{x},284", 1.1, ' stroke-opacity=".6"'))
        out += _knob(200, 314, 10)
        out.append(_ellipse(cx, 344, 96, 12, _shade(fill.base, 0.2)))
        return out
    if kind == "ceramic":
        out.append(_rect(140, 96, 120, 236, paint, 22))
        out.append(_rect(156, 150, 88, 150, "#5a2a1a", 10, LW_DETAIL))
        for row in range(10):
            for col in range(6):
                x = 166 + col * 14 + (row % 2) * 7
                y = 160 + row * 14
                out.append(f'<circle cx="{x}" cy="{y}" r="4.6" fill="{GLOW}" fill-opacity=".85"/>')
        out += _knob(176, 122, 8)
        out += _knob(224, 122, 8)
        out.append(_ellipse(cx, 342, 70, 11, _shade(fill.base, 0.2)))
        return out
    # fan heater
    out.append(_rect(104, 118, 192, 206, paint, 22))
    out.append(_rect(124, 170, 152, 136, _shade(fill.base, 0.5), 10, LW_DETAIL))
    for i in range(11):
        y = 180 + i * 11.6
        out.append(_line(f"M130,{y:.1f} L270,{y:.1f}", 3, "", _tint(fill.base, 0.3)))
    out += _knob(160, 144)
    out += _knob(200, 144)
    out.append(_circle(240, 144, 5, GLOW, 1))
    out.append(_rect(116, 324, 168, 14, BLACK, 6, LW_DETAIL))
    return out


# --------------------------------------------------------------------------
# Kettles and toasters
# --------------------------------------------------------------------------


def kettle(paint: str, fill: Fill, label: str | None, kind: str = "jug", material: str = "steel") -> list[str]:
    """A kettle on its power base, by ``kind``: a tall jug with a water window, a round dome
    with an arched handle, a slim gooseneck with a long spout, or a small travel jug. A glass
    body is clear and shows its water; its handle, lid and base carry the fill."""
    cx = 200.0
    glass = material == "glass"
    body = GLASS if glass else paint
    out = [_shadow(cx, 352, 120)]
    if kind == "travel":
        out.append(_ellipse(cx, 334, 70, 13, BLACK, LW_DETAIL))
        out.append(_path(f"M{cx - 56},330 L{cx - 50},200 Q{cx},188 {cx + 50},200 L{cx + 56},330 Q{cx},342 {cx - 56},330 Z", body))
        out.append(_path(f"M{cx - 50},206 L{cx - 84},196 L{cx - 52},228 Z", body, LW_DETAIL))
        out.append(_path(f"M{cx + 54},226 Q{cx + 98},232 {cx + 96},270 Q{cx + 94},300 {cx + 55},304", "none", 12, "", INK))
        out.append(_path(f"M{cx + 54},226 Q{cx + 98},232 {cx + 96},270 Q{cx + 94},300 {cx + 55},304", "none", 7, "", paint))
        out.append(_ellipse(cx, 198, 46, 9, _shade(fill.base, 0.2), LW_DETAIL))
        out.append(_highlight(f"M{cx - 38},224 L{cx - 40},312", 4, 0.5))
        return out
    if kind == "dome":
        out.append(_ellipse(cx, 336, 112, 16, BLACK, LW_DETAIL))
        out.append(_path(f"M{cx - 108},326 Q{cx - 116},196 {cx},180 Q{cx + 116},196 {cx + 108},326 Q{cx},342 {cx - 108},326 Z", body))
        out.append(_path(f"M{cx - 92},256 Q{cx - 140},226 {cx - 150},186 L{cx - 136},184 Q{cx - 122},214 {cx - 84},226 Z", body, LW_DETAIL))
        out.append(_path(f"M{cx - 70},192 Q{cx - 64},104 {cx},100 Q{cx + 64},104 {cx + 70},192", "none", 16, "", INK))
        out.append(_path(f"M{cx - 70},192 Q{cx - 64},104 {cx},100 Q{cx + 64},104 {cx + 70},192", "none", 10, "", paint))
        out.append(_ellipse(cx, 178, 34, 8, _shade(fill.base, 0.2), LW_DETAIL))
        out.append(_circle(cx, 166, 8, BLACK, LW_DETAIL))
        out.append(_highlight(f"M{cx - 80},300 Q{cx - 88},230 {cx - 40},200", 5, 0.5))
        if glass:
            out.append(_path(f"M{cx - 104},270 Q{cx},262 {cx + 104},270 L{cx + 106},326 Q{cx},340 {cx - 106},326 Z", WATER, LW_DETAIL, ' fill-opacity=".7"'))
        return out
    if kind == "gooseneck":
        out.append(_rect(cx - 88, 318, 176, 26, BLACK, 8, LW_DETAIL))
        out.append(_rect(cx - 22, 324, 44, 14, "#3a5a6a", 3, 1))
        out.append(_path(f"M{cx - 66},316 L{cx - 62},176 Q{cx},164 {cx + 62},176 L{cx + 66},316 Z", body))
        spout = f"M{cx - 62},290 Q{cx - 110},286 {cx - 112},224 Q{cx - 114},150 {cx - 158},132"
        out.append(_path(spout, "none", 13, "", INK))
        out.append(_path(spout, "none", 8, "", body))
        out.append(_path(f"M{cx + 62},196 L{cx + 100},196 L{cx + 100},290 L{cx + 64},290", "none", 14, "", INK))
        out.append(_path(f"M{cx + 62},196 L{cx + 100},196 L{cx + 100},290 L{cx + 64},290", "none", 8, "", BLACK))
        out.append(_ellipse(cx, 174, 54, 9, _shade(fill.base, 0.2), LW_DETAIL))
        out.append(_circle(cx, 160, 9, BLACK, LW_DETAIL))
        out.append(_highlight(f"M{cx - 50},196 L{cx - 52},300", 4, 0.5))
        return out
    # jug
    out.append(_ellipse(cx, 340, 104, 14, BLACK, LW_DETAIL))
    out.append(_path(f"M{cx - 84},334 L{cx - 70},120 Q{cx},108 {cx + 66},120 L{cx + 84},334 Q{cx},346 {cx - 84},334 Z", body))
    out.append(_path(f"M{cx - 70},126 L{cx - 122},104 L{cx - 116},120 L{cx - 70},170 Z", body, LW_DETAIL))
    handle = f"M{cx + 70},134 Q{cx + 140},140 {cx + 140},220 Q{cx + 140},300 {cx + 80},306"
    out.append(_path(handle, "none", 24, "", INK))
    out.append(_path(handle, "none", 18, "", paint if glass else _shade(fill.base, 0.12)))
    out.append(_ellipse(cx, 118, 66, 10, paint if glass else _shade(fill.base, 0.2), LW_DETAIL))
    if glass:
        out.append(_path(f"M{cx - 80},250 Q{cx},242 {cx + 80},250 L{cx + 83},332 Q{cx},344 {cx - 83},332 Z", WATER, LW_DETAIL, ' fill-opacity=".7"'))
        out.append(_path(f"M{cx - 80},300 L{cx + 80},300", "none", 3, ' stroke-opacity=".5"', "#4a8fd6"))
    else:
        out.append(_rect(cx - 66, 170, 18, 130, WATER, 8, LW_DETAIL))
        for i in range(4):
            out.append(_line(f"M{cx - 66},{196 + i * 26} L{cx - 58},{196 + i * 26}", 1.2))
    out.append(_highlight(f"M{cx + 40},150 L{cx + 54},310", 5, 0.45))
    return out


def toaster(paint: str, fill: Fill, label: str | None, slots: str = "2", long: str = "no") -> list[str]:
    """A toaster from above and in front: its top face holds ``slots`` slots (each
    ``class="slot"``): two in a row, four in two pairs, or long slots across the whole top;
    the front carries the browning dial and buttons, the side the lever."""
    n = max(_int(slots, 2), 1)
    lng = _yes(long)
    pairs = 1 if lng or n <= 2 else (n + 1) // 2
    rows = n if pairs == 1 else 2
    w = 210 + (pairs - 1) * 60
    x0, y_top, depth, h = 200 - w / 2 - 26, 190, 64, 140
    out = [_shadow(200, y_top + h + 10, w * 0.6)]
    out.append(_path(f"M{x0 + w},{y_top} L{x0 + w + depth},{y_top - depth} L{x0 + w + depth},{y_top - depth + h - 14} L{x0 + w},{y_top + h} Z", _shade(fill.base, 0.25)))
    out.append(_path(f"M{x0},{y_top} L{x0 + depth},{y_top - depth} L{x0 + w + depth},{y_top - depth} L{x0 + w},{y_top} Z", _tint(fill.base, 0.12)))
    out.append(_rect(x0, y_top, w, h, paint, 14))
    span = w - 40
    slot_w = (span if lng else span * 0.72) if pairs == 1 else (span - 24) / pairs * (1 if lng else 0.85)
    for p in range(pairs):
        for k in range(rows if pairs == 1 else min(2, n - 2 * p)):
            t = (k + 1) / (rows + 1)
            ox, oy = depth * t, -depth * t
            sx = x0 + 20 + (span - slot_w) / 2 * (pairs == 1) + p * (span + 24) / pairs + ox
            out.append(
                f'<path class="slot" d="M{sx:.1f},{y_top + oy - 4:.1f} L{sx + slot_w:.1f},{y_top + oy - 4:.1f} '
                f'L{sx + slot_w:.1f},{y_top + oy + 4:.1f} L{sx:.1f},{y_top + oy + 4:.1f} Z" '
                f'fill="{BLACK}" stroke="{INK}" stroke-width="1"/>'
            )
    out.append(_rect(x0 + w + depth * 0.4, y_top + 10, 14, 34, BLACK, 4, LW_DETAIL))
    out.append(_line(f"M{x0 + w + depth * 0.4 + 7},{y_top + 44} L{x0 + w + depth * 0.4 + 7},{y_top + h - 30}", 2, ' stroke-opacity=".6"'))
    out += _knob(x0 + w - 44, y_top + h - 44, 13)
    for i in range(3):
        out.append(_rect(x0 + 24 + i * 34, y_top + h - 52, 26, 14, _tint(fill.base, 0.55), 4, 1))
    out.append(_highlight(f"M{x0 + 14},{y_top + 24} L{x0 + 14},{y_top + h - 24}", 4, 0.45))
    out.append(_rect(x0 + 12, y_top + h - 4, 22, 8, BLACK, 2, 1))
    out.append(_rect(x0 + w - 34, y_top + h - 4, 22, 8, BLACK, 2, 1))
    return out


register({
    "desk_fan": desk_fan,
    "pedestal_fan": pedestal_fan,
    "tower_fan": tower_fan,
    "ceiling_fan": ceiling_fan,
    "handheld_fan": handheld_fan,
    "heater": heater,
    "kettle": kettle,
    "toaster": toaster,
})  # fmt: skip

#: The shapes this module adds, in its table's order.
SHAPES = ("desk_fan", "pedestal_fan", "tower_fan", "ceiling_fan", "handheld_fan", "heater",
          "kettle", "toaster")  # fmt: skip
