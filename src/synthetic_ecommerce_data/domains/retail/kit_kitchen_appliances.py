"""Small kitchen appliance shapes for the retail drawing kit (gen#963): coffee makers, air fryers,
blenders.

=============  ==================================================  ==============================
shape          draws                                               params
=============  ==================================================  ==============================
coffee_maker   a drip machine with its glass carafe on a warming   kind (drip, espresso, pod,
               plate, an espresso machine with its portafilter     bean to cup, cold brew)
               and steam wand, a pod machine with its water tank,
               a bean-to-cup machine with its bean hopper, or a
               cold-brew tower with its glass jar and tap
air_fryer      a single basket fryer front on, two baskets side    kind (single basket, dual
               by side, a basket with a viewing window, or an      basket, viewing window,
               oven-style fryer whose door shows a rotisserie      rotisserie)
               spit
blender        a jug blender on its motor base, a personal         kind (jug, personal, hand)
               blender's upturned cup, or a hand blender's stick
               with its beaker
=============  ==================================================  ==============================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes its type draws what it states (gen#512). The body carries the record's fill; glass,
steel and the controls do not. No drawing prints a capacity: one image serves every size its
color sells. The drawings are original and drawn by code (ruling 2026-11-02, gen#102).
"""

# ruff: noqa: E501 -- SVG paths read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_appliances import (
    BLACK,
    GLASS,
    GLOW,
    STEEL,
    STEEL_DARK,
    _circle,
    _ellipse,
    _knob,
    _rect,
    _shadow,
)

#: Coffee in a carafe or a jar.
COFFEE = "#5a3a26"
#: The beans in a hopper.
BEAN = "#7a4a2a"


def _carafe(cx: float, top: float, bottom: float, half: float, fill: str = COFFEE) -> list[str]:
    """A glass jug ``half`` wide each side, coffee in its lower half, a black handle and lid."""
    mid = (top + bottom) / 2
    out = [_path(f"M{cx - half},{top} L{cx - half - 8},{bottom} L{cx + half + 8},{bottom} L{cx + half},{top} Z", GLASS, LW_DETAIL)]
    out.append(_path(f"M{cx - half - 4},{mid} L{cx - half - 8},{bottom} L{cx + half + 8},{bottom} L{cx + half + 4},{mid} Z", fill, LW_DETAIL))
    out.append(_rect(cx - half - 2, top - 10, 2 * half + 4, 12, BLACK, 3, LW_DETAIL))
    out.append(_path(f"M{cx + half + 4},{top + 8} L{cx + half + 26},{top + 8} L{cx + half + 26},{bottom - 12} L{cx + half + 6},{bottom - 12}", "none", 8, "", BLACK))
    return out


def coffee_maker(paint: str, fill: Fill, label: str | None, kind: str = "drip") -> list[str]:
    """A coffee maker by ``kind``, its body in the fill and its glass, steel and controls not."""
    cx = 200.0
    dark = _shade(fill.base, 0.2)
    out = [_shadow(cx, 352, 130)]
    if kind == "espresso":
        out.append(_rect(cx - 110, 120, 220, 220, paint, 14))
        out.append(_rect(cx - 110, 120, 220, 30, dark, 14, LW_DETAIL))
        out.append(_rect(cx - 78, 176, 156, 20, STEEL_DARK, 6, LW_DETAIL))
        out.append(_path(f"M{cx - 44},196 L{cx + 44},196 L{cx + 36},214 L{cx - 36},214 Z", STEEL, LW_DETAIL))
        out.append(_line(f"M{cx + 36},205 L{cx + 96},212", 9, "", BLACK))
        out.append(_line(f"M{cx - 92},180 L{cx - 96},262 L{cx - 86},270", 5, "", STEEL_DARK))
        out.append(_rect(cx - 30, 262, 60, 46, "#fbfaf6", 6, LW_DETAIL))
        out.append(_rect(cx - 90, 312, 180, 16, STEEL, 4, LW_DETAIL))
        out += _knob(cx - 70, 136, 7)
        out += _knob(cx + 70, 136, 7)
        out.append(_circle(cx, 136, 7, GLOW, 1))
        out.append(_highlight(f"M{cx - 96},160 L{cx - 96},300", 5, 0.4))
        return out
    if kind == "pod":
        out.append(_rect(cx - 70, 110, 120, 230, paint, 18))
        out.append(_rect(cx + 50, 130, 50, 190, GLASS, 10, LW_DETAIL))
        out.append(_rect(cx + 54, 200, 42, 116, "#9cc7e6", 8, 1, ' fill-opacity=".8"'))
        out.append(_rect(cx - 70, 110, 120, 44, dark, 18, LW_DETAIL))
        out.append(_rect(cx - 30, 168, 40, 18, STEEL_DARK, 4, LW_DETAIL))
        out.append(_rect(cx - 40, 286, 60, 14, STEEL, 3, LW_DETAIL))
        out.append(_path(f"M{cx - 32},246 L{cx + 12},246 L{cx + 8},284 L{cx - 28},284 Z", "#fbfaf6", LW_DETAIL))
        out.append(_circle(cx + 30, 132, 6, GLOW, 1))
        out.append(_highlight(f"M{cx - 58},160 L{cx - 58},320", 5, 0.4))
        return out
    if kind == "bean to cup":
        out.append(_rect(cx - 100, 130, 200, 210, paint, 16))
        out.append(_path(f"M{cx + 20},130 L{cx + 30},86 L{cx + 86},86 L{cx + 96},130 Z", GLASS, LW_DETAIL))
        for i in range(5):
            out.append(_ellipse(cx + 40 + i * 11, 116 - (i % 2) * 8, 5, 3.5, BEAN, 1))
        out.append(_rect(cx - 84, 146, 92, 54, "#26303a", 6, LW_DETAIL))
        out.append(_line(f"M{cx - 72},164 L{cx - 20},164 M{cx - 72},180 L{cx - 40},180", 2, "", "#9cc7e6"))
        out.append(_rect(cx - 36, 216, 72, 18, STEEL_DARK, 5, LW_DETAIL))
        out.append(_rect(cx - 26, 262, 52, 44, "#fbfaf6", 6, LW_DETAIL))
        out.append(_rect(cx - 84, 312, 168, 16, STEEL, 4, LW_DETAIL))
        out += _knob(cx + 56, 170, 10)
        out.append(_highlight(f"M{cx - 88},210 L{cx - 88},320", 5, 0.4))
        return out
    if kind == "cold brew":
        out.append(_rect(cx - 70, 70, 140, 26, paint, 8))
        out.append(_path(f"M{cx - 50},96 L{cx - 18},150 L{cx + 18},150 L{cx + 50},96 Z", GLASS, LW_DETAIL))
        out.append(_line(f"M{cx},150 L{cx},178", 4, "", STEEL_DARK))
        out += _carafe(cx, 190, 312, 44)
        out.append(_rect(cx - 90, 312, 180, 22, paint, 8))
        out.append(_line(f"M{cx - 80},70 L{cx - 80},312 M{cx + 80},70 L{cx + 80},312", 10, "", dark))
        out.append(_rect(cx + 34, 274, 22, 10, BLACK, 2, 1))
        return out
    # drip
    out.append(_path(f"M{cx - 100},336 L{cx - 100},110 Q{cx - 100},96 {cx - 86},96 L{cx + 86},96 Q{cx + 100},96 {cx + 100},110 L{cx + 100},150 L{cx - 40},150 L{cx - 40},300 L{cx + 100},300 L{cx + 100},336 Z", paint))
    out.append(_rect(cx - 30, 150, 120, 26, dark, 6, LW_DETAIL))
    out += _carafe(cx + 30, 200, 296, 40)
    out.append(_rect(cx - 40, 296, 140, 8, BLACK, 2, 1))
    out.append(_rect(cx - 88, 230, 36, 16, "#26303a", 3, 1))
    out.append(_circle(cx - 70, 270, 6, GLOW, 1))
    out.append(_highlight(f"M{cx - 88},120 L{cx - 88},320", 5, 0.4))
    return out


def _basket(x: float, w: float, top: float, bottom: float, fill: Fill, window: bool = False) -> list[str]:
    """A fryer drawer front between ``x`` and ``x + w``: its handle, and a window when asked."""
    out = [_rect(x, top, w, bottom - top, _shade(fill.base, 0.12), 10, LW_DETAIL)]
    if window:
        out.append(_rect(x + 14, top + 16, w - 28, 50, "#3a3a40", 8, LW_DETAIL))
        out.append(_ellipse(x + w / 2, top + 54, (w - 40) / 2, 8, "#d9a050", 1))
    hy = top + (80 if window else 36)
    out.append(_rect(x + w / 2 - 14, hy, 28, 54, BLACK, 6, LW_DETAIL))
    return out


def air_fryer(paint: str, fill: Fill, label: str | None, kind: str = "single basket") -> list[str]:
    """An air fryer front on by ``kind``, its body in the fill: one drawer, two side by side, a
    drawer with a window, or an oven-style box whose glass door shows a rotisserie spit."""
    cx = 200.0
    out = [_shadow(cx, 352, 140)]
    if kind == "rotisserie":
        out.append(_rect(cx - 130, 110, 260, 226, paint, 16))
        out.append(_rect(cx - 112, 150, 180, 160, "#3a3a40", 8, LW_DETAIL))
        out.append(_line(f"M{cx - 104},228 L{cx + 60},228", 4, "", STEEL))
        out.append(_ellipse(cx - 22, 228, 46, 30, "#c9843a", LW_DETAIL))
        out.append(_rect(cx - 112, 150, 180, 160, GLASS, 8, 1, ' fill-opacity=".25"'))
        out.append(_rect(cx + 80, 150, 36, 60, "#26303a", 4, 1))
        out += _knob(cx + 98, 240, 10)
        out += _knob(cx + 98, 280, 10)
        out.append(_rect(cx - 112, 126, 180, 12, BLACK, 4, 1))
        return out
    if kind == "dual basket":
        out.append(_rect(cx - 140, 120, 280, 216, paint, 18))
        out.append(_rect(cx - 60, 132, 120, 26, "#26303a", 6, 1))
        out += _basket(cx - 128, 120, 176, 324, fill)
        out += _basket(cx + 8, 120, 176, 324, fill)
        out.append(_highlight(f"M{cx - 128},140 L{cx - 128},166", 5, 0.4))
        return out
    out.append(_path(f"M{cx - 100},336 L{cx - 108},150 Q{cx - 106},104 {cx},100 Q{cx + 106},104 {cx + 108},150 L{cx + 100},336 Z", paint))
    out.append(_rect(cx - 40, 120, 80, 30, "#26303a", 6, 1))
    out.append(_circle(cx, 135, 6, GLOW, 1))
    out += _basket(cx - 84, 168, 170, 324, fill, window=kind == "viewing window")
    out.append(_highlight(f"M{cx - 92},170 L{cx - 88},320", 5, 0.4))
    return out


def blender(paint: str, fill: Fill, label: str | None, kind: str = "jug") -> list[str]:
    """A blender by ``kind``: a jug on its motor base, a personal blender's upturned cup on its
    base, or a hand blender's stick beside its beaker. The motor body carries the fill."""
    cx = 200.0
    out = [_shadow(cx, 352, 110)]
    if kind == "hand":
        out.append(_path(f"M{cx + 30},336 L{cx + 24},226 L{cx + 116},226 L{cx + 110},336 Z", GLASS, LW_DETAIL))
        out.append(_path(f"M{cx + 28},290 L{cx + 112},290 L{cx + 110},336 L{cx + 30},336 Z", "#e8a0b0", LW_DETAIL))
        out.append(_rect(cx - 66, 70, 52, 130, paint, 22))
        out.append(_rect(cx - 52, 92, 24, 10, BLACK, 4, 1))
        out.append(_rect(cx - 50, 200, 20, 110, STEEL, 4, LW_DETAIL))
        out.append(_path(f"M{cx - 66},310 Q{cx - 40},290 {cx - 14},310 L{cx - 22},326 L{cx - 58},326 Z", STEEL, LW_DETAIL))
        out.append(_highlight(f"M{cx - 56},90 L{cx - 56},186", 4, 0.45))
        return out
    if kind == "personal":
        out.append(_path(f"M{cx - 48},230 L{cx - 38},86 L{cx + 38},86 L{cx + 48},230 Z", GLASS, LW_DETAIL))
        out.append(_path(f"M{cx - 44},170 L{cx - 40},96 L{cx + 40},96 L{cx + 44},170 Z", "#8bc34a", LW_DETAIL, ' fill-opacity=".85"'))
        out.append(_rect(cx - 52, 226, 104, 20, BLACK, 4, LW_DETAIL))
        out.append(_path(f"M{cx - 56},246 L{cx + 56},246 L{cx + 66},336 L{cx - 66},336 Z", paint))
        out.append(_circle(cx, 296, 12, BLACK, LW_DETAIL))
        out.append(_highlight(f"M{cx - 30},104 L{cx - 36},220", 4, 0.5))
        return out
    # jug
    out.append(_path(f"M{cx - 64},226 L{cx - 76},80 L{cx + 76},80 L{cx + 64},226 Z", GLASS, LW_DETAIL))
    out.append(_path(f"M{cx - 68},170 L{cx - 72},120 L{cx + 72},120 L{cx + 68},170 L{cx + 64},226 L{cx - 64},226 Z", "#f2c94c", LW_DETAIL, ' fill-opacity=".8"'))
    out.append(_rect(cx - 80, 70, 160, 14, BLACK, 4, LW_DETAIL))
    out.append(_path(f"M{cx + 72},100 L{cx + 110},104 L{cx + 108},200 L{cx + 66},204", "none", 10, "", BLACK))
    out.append(_path(f"M{cx - 90},230 L{cx + 90},230 L{cx + 100},336 L{cx - 100},336 Z", paint))
    out.append(_rect(cx - 70, 226, 140, 10, BLACK, 3, 1))
    out += _knob(cx, 286, 18)
    out.append(_highlight(f"M{cx - 54},96 L{cx - 46},216", 5, 0.5))
    return out


SHAPES = {"coffee_maker": coffee_maker, "air_fryer": air_fryer, "blender": blender}
register(SHAPES)
