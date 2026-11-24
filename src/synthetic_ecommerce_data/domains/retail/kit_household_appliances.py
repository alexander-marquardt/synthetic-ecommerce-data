"""Household appliance shapes for the retail drawing kit (#1116): steam irons, vacuum cleaners,
microwaves.

==============  =================================================  ===========================
shape           draws                                              params
==============  =================================================  ===========================
steam_iron      an iron seen side on, its steel soleplate under    kind (standard, cordless,
                its body: a corded iron, a cordless one on its     steam generator, travel)
                charging base, one on a steam generator's water
                tank with a hose, or a small travel iron
vacuum_cleaner  an upright with its floor head and dust bin, a     kind (upright, cylinder,
                cylinder on wheels with its hose and wand, a       cordless stick, handheld,
                cordless stick with its battery, a handheld, or    robot)
                a round robot seen from above
microwave       a worktop microwave front on: its door window      kind (solo, grill,
                with a turntable plate and its control panel; a    combination)
                grill model shows its glowing element, a
                combination one its fan ring as well
==============  =================================================  ===========================

Each param's values are the lower-cased attribute values of the spec rows, so a style draws the
kind it states (gen#512). The body carries the record's fill; steel, glass and the controls do
not. The drawings are original and drawn by code (ruling 2026-11-02, gen#102).
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
    WATER,
    _circle,
    _ellipse,
    _knob,
    _rect,
    _shadow,
)

#: A vacuum's clear dust bin, with the dust in it.
DUST = "#b9b2a6"


def _iron(out: list[str], paint: str, dark: str, x0: float, x1: float, sole: float, top: float) -> None:
    """An iron's body from ``x0`` (heel) to ``x1`` (point) on a steel soleplate at ``sole``,
    its handle arching to ``top``."""
    w = x1 - x0
    out.append(_path(f"M{x0},{sole} L{x1},{sole} Q{x1 - w * 0.08},{sole - 26} {x1 - w * 0.3},{sole - 40} L{x0 + 6},{sole - 44} Z", STEEL, LW_DETAIL))
    out.append(_path(f"M{x0 + 4},{sole - 8} L{x1 - 10},{sole - 8} Q{x1 - w * 0.2},{sole - 52} {x0 + w * 0.45},{sole - 62} L{x0 + 8},{sole - 64} Z", paint))
    out.append(_path(f"M{x0 + 10},{sole - 64} Q{x0 + 4},{top} {x0 + w * 0.3},{top} L{x0 + w * 0.62},{top} Q{x0 + w * 0.74},{top + 4} {x0 + w * 0.6},{sole - 58}", "none", 16, "", dark))
    out.append(_rect(x0 + w * 0.34, sole - 50, 26, 10, BLACK, 4, 1))
    out.append(_highlight(f"M{x0 + 16},{sole - 22} L{x1 - 40},{sole - 22}", 3, 0.45))


def steam_iron(paint: str, fill: Fill, label: str | None, kind: str = "standard") -> list[str]:
    """A steam iron by ``kind``, its body in the fill and its soleplate steel."""
    cx = 200.0
    dark = _shade(fill.base, 0.25)
    out = [_shadow(cx, 352, 140)]
    if kind == "steam generator":
        out.append(_rect(cx - 140, 272, 280, 72, paint, 20))
        out.append(_rect(cx - 120, 286, 90, 44, WATER, 8, LW_DETAIL, ' fill-opacity=".8"'))
        out.append(_rect(cx + 20, 300, 40, 14, BLACK, 4, 1))
        out.append(_rect(cx + 70, 300, 40, 14, BLACK, 4, 1))
        out.append(_path(f"M{cx - 130},270 Q{cx - 170},200 {cx - 96},170", "none", 6, "", BLACK))
        _iron(out, paint, dark, cx - 100, cx + 110, 262, 156)
        return out
    if kind == "travel":
        _iron(out, paint, dark, cx - 70, cx + 70, 330, 238)
        out.append(_line(f"M{cx - 66},270 L{cx - 100},240", 6, "", STEEL_DARK))
        return out
    if kind == "cordless":
        out.append(_path(f"M{cx - 150},346 L{cx - 140},300 L{cx + 150},300 L{cx + 160},346 Z", dark))
        out.append(_rect(cx - 140, 318, 12, 8, GLOW, 2, 1))
        _iron(out, paint, dark, cx - 130, cx + 150, 300, 172)
        return out
    # standard: corded
    _iron(out, paint, dark, cx - 130, cx + 150, 330, 202)
    out.append(_path(f"M{cx - 126},300 Q{cx - 170},300 {cx - 176},340", "none", 6, "", BLACK))
    return out


def vacuum_cleaner(paint: str, fill: Fill, label: str | None, kind: str = "upright") -> list[str]:
    """A vacuum cleaner by ``kind``: the body carries the fill; the bin, hose and steel do not."""
    cx = 200.0
    dark = _shade(fill.base, 0.25)
    out = [_shadow(cx, 352, 130)]
    if kind == "robot":
        out.append(_ellipse(cx, 230, 140, 140, paint))
        out.append(_ellipse(cx, 230, 104, 104, dark, LW_DETAIL))
        out.append(_circle(cx, 150, 22, BLACK, LW_DETAIL))
        out.append(_rect(cx - 30, 210, 60, 14, BLACK, 7, 1))
        out.append(_circle(cx, 290, 10, GLOW, 1))
        out.append(_highlight(f"M{cx - 110},190 Q{cx - 90},120 {cx - 30},100", 5, 0.4))
        return out
    if kind == "handheld":
        out.append(_path(f"M{cx - 140},270 L{cx - 20},230 L{cx - 20},300 L{cx - 140},300 Z", DUST, LW_DETAIL, ' fill-opacity=".7"'))
        out.append(_rect(cx - 30, 210, 130, 100, paint, 30))
        out.append(_path(f"M{cx + 90},230 Q{cx + 160},230 {cx + 160},280 Q{cx + 160},310 {cx + 90},300", "none", 18, "", dark))
        out.append(_rect(cx + 10, 228, 60, 14, BLACK, 7, 1))
        return out
    if kind == "cylinder":
        out.append(_ellipse(cx + 60, 290, 90, 56, paint))
        out.append(_circle(cx + 20, 338, 14, BLACK, LW_DETAIL))
        out.append(_circle(cx + 110, 338, 14, BLACK, LW_DETAIL))
        out.append(_ellipse(cx + 70, 270, 40, 22, DUST, LW_DETAIL, ' fill-opacity=".7"'))
        out.append(_path(f"M{cx - 20},282 Q{cx - 80},300 {cx - 90},240 Q{cx - 100},160 {cx - 60},120", "none", 12, "", BLACK))
        out.append(_line(f"M{cx - 60},120 L{cx - 120},330", 8, "", STEEL_DARK))
        out.append(_rect(cx - 170, 330, 100, 16, dark, 6, LW_DETAIL))
        return out
    if kind == "cordless stick":
        out.append(_line(f"M{cx + 20},140 L{cx - 40},330", 10, "", STEEL_DARK))
        out.append(_rect(cx - 100, 326, 120, 22, dark, 8, LW_DETAIL))
        out.append(_rect(cx + 6, 70, 40, 120, DUST, 14, LW_DETAIL, ' fill-opacity=".7"'))
        out.append(_path(f"M{cx + 46},90 L{cx + 96},80 L{cx + 104},160 L{cx + 46},170 Z", paint))
        out.append(_path(f"M{cx + 96},80 Q{cx + 140},60 {cx + 130},120 L{cx + 104},150", "none", 14, "", dark))
        out.append(_rect(cx + 60, 176, 34, 40, BLACK, 6, LW_DETAIL))
        return out
    # upright
    out.append(_rect(cx - 110, 300, 220, 46, dark, 14))
    out.append(_rect(cx - 60, 120, 120, 190, paint, 26))
    out.append(_rect(cx - 40, 150, 80, 110, DUST, 16, LW_DETAIL, ' fill-opacity=".7"'))
    out.append(_line(f"M{cx + 44},120 L{cx + 60},40 L{cx + 20},40", 12, "", BLACK))
    out.append(_circle(cx + 90, 334, 14, BLACK, LW_DETAIL))
    out.append(_highlight(f"M{cx - 46},140 L{cx - 46},290", 4, 0.45))
    return out


def microwave(paint: str, fill: Fill, label: str | None, kind: str = "solo") -> list[str]:
    """A microwave by ``kind``: its case in the fill, its door glass and plate not."""
    cx = 200.0
    out = [_shadow(cx, 352, 170)]
    out.append(_rect(cx - 170, 120, 340, 220, paint, 16))
    out.append(_rect(cx - 150, 140, 230, 180, BLACK, 10, LW_DETAIL))
    out.append(_rect(cx - 136, 154, 202, 152, GLASS, 6, LW_DETAIL, ' fill-opacity=".35"'))
    out.append(_ellipse(cx - 35, 290, 80, 12, STEEL, LW_DETAIL))
    out.append(_rect(cx + 96, 144, 58, 40, BLACK, 4, LW_DETAIL))
    out.append(_rect(cx + 102, 152, 46, 22, GLOW, 2, 1, ' fill-opacity=".7"'))
    out += _knob(cx + 125, 220, 14)
    out += _knob(cx + 125, 268, 14)
    out.append(_rect(cx + 104, 296, 42, 14, STEEL_DARK, 4, 1))
    if kind in ("grill", "combination"):
        out.append(_path(f"M{cx - 126},166 L{cx - 96},176 L{cx - 66},166 L{cx - 36},176 L{cx - 6},166 L{cx + 24},176 L{cx + 54},166", "none", 4, "", GLOW))
    if kind == "combination":
        out.append(_circle(cx - 35, 230, 34, "none", 2))
        for dx, dy in ((0, -22), (22, 0), (0, 22), (-22, 0)):
            out.append(_line(f"M{cx - 35},230 L{cx - 35 + dx},{230 + dy}", 3, "", STEEL_DARK))
    return out


SHAPES = {"steam_iron": steam_iron, "vacuum_cleaner": vacuum_cleaner, "microwave": microwave}
register(SHAPES)
