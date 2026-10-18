"""Printable surfaces for the retail drawing kit (gen#125, motif prints).

The products a motif print goes on that the kit did not draw yet: a
sweatshirt, pyjamas, a fitted sheet, a cushion, a tea towel, an apron, a mug
and a roll of wrapping paper. Each paints its main surface with ``paint``, so
a print's ``<pattern>`` (or its ground, for a placement print) shows on it.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _tint, register
from kit_garments import top, trousers


def sweatshirt(paint: str, fill: Fill, label: str | None, neckline: str = "crew") -> list[str]:
    """A sweatshirt or jumper (crew neck unless ``neckline`` says otherwise): the kit's jumper
    with long sleeves and rib bands."""
    return top(paint, fill, label, neckline=neckline, sleeve="long", kind="jumper")


def pyjamas(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A pyjama set: a long-sleeved top beside its trousers, both in the record's fill."""
    shirt = top(paint, fill, None, neckline="v_neck", sleeve="long")
    legs = trousers(paint, fill, None, fit="straight", rise="mid")
    return [
        f'<g transform="translate(-12 70) scale(.6)">{"".join(shirt)}</g>',
        f'<g transform="translate(160 70) scale(.62)">{"".join(legs)}</g>',
    ]


def sheet(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A folded fitted sheet: a stack with its elasticated corner showing."""
    return [
        _path("M70,250 L330,250 L330,320 Q200,334 70,320 Z", _shade(fill.base, 0.12) if fill.base.startswith("#") else paint),
        _path("M70,130 L330,130 L330,250 L70,250 Z", paint),
        _path("M70,130 Q200,112 330,130 L330,150 Q200,134 70,150 Z", paint, LW_DETAIL),
        _line("M70,250 Q200,262 330,250", 1.4, ' stroke-dasharray="5 4"'),
        _highlight("M84,140 L300,140", 4, 0.35),
    ]


def cushion(paint: str, fill: Fill, label: str | None, trim: str = "") -> list[str]:
    """A scatter cushion; ``trim`` (a hex color) draws a contrasting piping round its edge."""
    d = "M86,96 Q200,82 314,96 Q328,206 314,316 Q200,330 86,316 Q72,206 86,96 Z"
    return [
        '<ellipse cx="200" cy="334" rx="120" ry="9" fill="#000000" fill-opacity=".08"/>',
        _path(d, paint),
        *([_path(d, "none", 7, "", trim)] if trim else []),
        _path(d, "none", 1.2, ' transform="translate(200 206) scale(.94) translate(-200 -206)" stroke-dasharray="5 4"'),
        _line("M86,96 L104,114 M314,96 L296,114 M86,316 L104,298 M314,316 L296,298", 1.4),
    ]


def tea_towel(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A tea towel hanging from its loop, hemmed, with two woven bands."""
    return [
        _line("M200,58 Q184,38 200,30 Q216,38 200,58", 2),
        _path("M112,58 L288,58 L288,350 L112,350 Z", paint),
        f'<rect x="112" y="300" width="176" height="10" fill="{_shade(fill.base, 0.3)}" stroke="{INK}" stroke-width="1"/>',
        f'<rect x="112" y="318" width="176" height="6" fill="{_shade(fill.base, 0.3)}" stroke="{INK}" stroke-width="1"/>',
        _line("M118,64 L282,64 M118,344 L282,344", 1.0, ' stroke-dasharray="4 3"'),
    ]


def apron(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M156,96 L244,96 L248,160 Q302,166 304,186 L314,352 Q200,366 86,352 L96,186 Q98,166 152,160 Z"
    return [
        _line("M156,96 Q150,52 200,44 Q250,52 244,96", LW),
        _line("M100,196 Q60,214 52,250 M300,196 Q340,214 348,250", LW),
        _path(body, paint),
        _path("M150,250 L250,250 L248,304 L152,304 Z", paint, LW_DETAIL),
        _line("M200,250 L200,304", 1.2, ' stroke-dasharray="4 3"'),
    ]


def mug(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M270,170 Q336,170 336,230 Q336,292 268,292 L268,266 Q310,266 310,230 Q310,196 270,196 Z", _tint(fill.base, 0.1) if fill.base.startswith("#") else paint),
        _path("M100,120 L270,120 L270,318 Q270,344 244,344 L126,344 Q100,344 100,318 Z", paint),
        f'<ellipse cx="185" cy="120" rx="85" ry="16" fill="#f4f1ea" stroke="{INK}" stroke-width="{LW}"/>',
        _highlight("M114,146 L114,312", 6, 0.35),
    ]


def wrapping_paper(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A roll of wrapping paper with a length unrolled toward the viewer."""
    return [
        _path("M96,206 L304,206 L346,348 L54,348 Z", paint),
        _path("M80,110 L320,110 L320,206 L80,206 Z", paint),
        f'<ellipse cx="320" cy="158" rx="22" ry="48" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<ellipse cx="320" cy="158" rx="9" ry="20" fill="#e2c9a0" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _line("M96,206 L304,206", LW),
        _highlight("M92,124 L300,124", 5, 0.35),
    ]


register(
    {"sweatshirt": sweatshirt, "pyjamas": pyjamas, "sheet": sheet, "cushion": cushion,
     "tea_towel": tea_towel, "apron": apron, "mug": mug, "wrapping_paper": wrapping_paper},
    {"sweatshirt": 6},
)  # fmt: skip
