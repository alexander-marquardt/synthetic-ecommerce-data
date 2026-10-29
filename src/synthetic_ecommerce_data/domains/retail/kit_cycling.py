"""Cycling accessory shapes for the retail drawing kit (gen#625).

The accessories a shopper finds next to the bikes on a search for ``bicycle`` or ``bike``: each
is drawn as what it is, so a saddle or a pair of pedals never reads as a bike. Outlines are the
kit's ink, and the record's fill (color and pattern) paints the main surface.

===============  =============================================  ==========================
shape            draws                                          params
===============  =============================================  ==========================
chain_lube       a squeeze bottle with a long drip nozzle, or   style (drip, spray)
                 a spray can with a straw
bike_bottle      a sports bottle with a push-pull valve, slim   style (squeeze, insulated)
                 or with an insulated double wall
bike_saddle      a saddle seen from the side on its rails,      style (road, comfort)
                 narrow and long or wide and padded
bike_pedals      two pedals on their spindles, flat platforms   style (flat, clipless)
                 with pins or small clipless bodies
===============  =============================================  ==========================

A drawing never prints a volume or a size: a style's SKUs share one image per colorway. Every
param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import POLE, _ell, _label, _rect


def chain_lube(paint: str, fill: Fill, label: str | None, style: str = "drip") -> list[str]:
    """Chain lube: a ``drip`` squeeze bottle with a long nozzle, or a ``spray`` can and straw."""
    dark = _shade(fill.base, 0.35)
    if style.lower() == "spray":
        return _label([
            _rect(150, 130, 100, 230, paint, 14),
            _rect(166, 96, 68, 36, POLE, 8),
            _rect(184, 74, 32, 24, dark, 5),
            _line("M216,84 L300,62", 4),
            _rect(150, 220, 100, 60, dark, 0),
            _highlight("M166,150 L166,340", 6, 0.5),
        ], label)
    return _label([
        _path("M146,366 L146,190 Q146,150 182,140 L218,140 Q254,150 254,190 L254,366 Q200,374 146,366 Z", paint),
        _rect(176, 112, 48, 30, dark, 6),
        _path("M190,112 L196,40 L204,40 L210,112 Z", POLE),
        _rect(146, 230, 108, 70, dark, 0),
        _highlight("M162,196 L162,350", 6, 0.5),
    ], label)


def bike_bottle(paint: str, fill: Fill, label: str | None, style: str = "squeeze") -> list[str]:
    """A bike bottle: a ``squeeze`` bottle with a waist grip, or an ``insulated`` straight wall."""
    dark = _shade(fill.base, 0.35)
    if style.lower() == "insulated":
        body = "M138,368 L138,140 Q138,118 160,114 L240,114 Q262,118 262,140 L262,368 Q200,378 138,368 Z"
        bands = [_line("M138,150 L262,150", 3), _line("M138,340 L262,340", 3)]
    else:
        body = "M140,368 L140,140 Q140,118 162,114 L238,114 Q260,118 260,140 L260,210 Q244,240 260,270 L260,368 Q200,378 140,368 Z"
        bands = [_line("M142,216 Q200,232 258,216", 3), _line("M142,264 Q200,248 258,264", 3)]
    return _label([
        _path(body, paint),
        *bands,
        _rect(158, 82, 84, 34, dark, 8),
        _rect(186, 52, 28, 32, POLE, 6),
        _highlight("M156,150 L156,350", 6, 0.5),
    ], label)


def bike_saddle(paint: str, fill: Fill, label: str | None, style: str = "road") -> list[str]:
    """A saddle from the side: ``road`` (long and narrow) or ``comfort`` (wide, deep padding)."""
    dark = _shade(fill.base, 0.4)
    if style.lower() == "comfort":
        top = "M70,190 Q80,140 170,150 Q260,160 330,170 Q352,180 340,206 Q300,236 200,232 Q100,232 76,214 Q64,204 70,190 Z"
        springs = [_line(f"M{x},236 L{x + 6},290", 4) for x in (110, 300)]
    else:
        top = "M40,196 Q60,170 150,176 L300,180 Q352,184 364,198 Q356,214 300,214 L120,216 Q52,216 40,196 Z"
        springs = []
    return _label([
        _path(top, paint),
        _line("M90,226 Q200,262 320,226", 5, stroke=POLE),
        *springs,
        _rect(186, 240, 28, 110, POLE, 6),
        _path("M80,206 Q200,224 330,206", dark, 2.4),
        _highlight("M90,178 Q180,160 300,176", 5, 0.5),
    ], label)


def bike_pedals(paint: str, fill: Fill, label: str | None, style: str = "flat") -> list[str]:
    """A pair of pedals: ``flat`` platforms with pins, or small ``clipless`` bodies with a cleat bar."""
    dark = _shade(fill.base, 0.35)
    out: list[str] = []
    for x in (60, 220):
        out.append(_rect(x + 46, 196, 60, 14, POLE, 5))
        if style.lower() == "clipless":
            out.append(_ell(x + 60, 204, 54, 62, paint))
            out.append(_rect(x + 30, 194, 60, 20, dark, 6))
        else:
            out.append(_rect(x, 120, 120, 170, paint, 14))
            out.append(_rect(x + 22, 144, 76, 122, dark, 10))
            out += [_ell(x + px, y, 5, 5, POLE, 1.6) for px in (12, 108) for y in (140, 205, 270)]
    out.append(_highlight("M76,136 L76,276", 5, 0.5))
    return _label(out, label)


SHAPES = {"chain_lube": chain_lube, "bike_bottle": bike_bottle, "bike_saddle": bike_saddle,
          "bike_pedals": bike_pedals}  # fmt: skip
register(SHAPES)
