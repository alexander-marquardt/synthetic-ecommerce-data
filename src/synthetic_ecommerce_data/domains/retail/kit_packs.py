"""The packs a beauty line draws: a bottle, a jar or a flacon of its own (gen#748).

``bottle``, ``jar``, ``moisturiser_jar`` and ``fragrance`` each draw one pack, so the products of
a kind shared an outline. With a look in its params (:mod:`pack_looks` chooses it) each of them
draws one of the forms below under one of the tops, and a shape with no look draws as it did.

A form stands on the sheet alone: it names where its top sits, where the label panel goes and
where the emblem goes, all inside its own outline, so any form takes any top and any emblem.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    SHAPES,
    Fill,
    _highlight,
    _line,
    _panel,
    _path,
    _word,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_home import _lipstick_emblem, _text


@dataclass(frozen=True)
class Form:
    """A pack's body: its outline, the bottom of its top, the panel and the emblem's center."""

    body: str
    mouth: float
    panel: tuple[float, float, float, float]
    mark: tuple[float, float]
    gloss: str


def _rect(x: float, y: float, w: float, h: float, color: str, rx: float = 0, width: float = LW) -> str:
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{color}" stroke="{INK}" stroke-width="{width}"/>'


def _block(y: float, half: float, color: str, trim: str) -> list[str]:
    return [_rect(200 - half, y - 58, 2 * half, 58, color, 3)]


def _tall(y: float, half: float, color: str, trim: str) -> list[str]:
    return [_rect(200 - 0.7 * half, y - 82, 1.4 * half, 82, color, 3), _rect(200 - half, y - 10, 2 * half, 10, trim, 0, LW_DETAIL)]


def _ball(y: float, half: float, color: str, trim: str) -> list[str]:
    r = 1.3 * half
    return [
        _rect(200 - 0.6 * half, y - 18, 1.2 * half, 18, trim, 0, LW_DETAIL),
        f'<circle cx="200" cy="{y - 16 - r:g}" r="{r:g}" fill="{color}" stroke="{INK}" stroke-width="{LW}"/>',
    ]


def _pump(y: float, half: float, color: str, trim: str) -> list[str]:
    return [
        _rect(192, y - 50, 16, 34, trim, 0, LW_DETAIL),
        _rect(200 - half, y - 22, 2 * half, 22, color, 3),
        _path(f"M{200 - half - 4},{y - 72} L{200 + half + 8},{y - 72} L{200 + half + 42},{y - 64} L{200 + half + 42},{y - 54} L{200 + half + 4},{y - 54} L{200 + half + 4},{y - 48} L{200 - half - 4},{y - 48} Z", color),
    ]


def _dropper(y: float, half: float, color: str, trim: str) -> list[str]:
    return [
        _path(f"M186,{y - 30} L186,{y - 44} Q170,{y - 82} 200,{y - 88} Q230,{y - 82} 214,{y - 44} L214,{y - 30} Z", color),
        _rect(200 - half, y - 32, 2 * half, 32, trim, 3),
    ]


def _wide(y: float, half: float, color: str, trim: str) -> list[str]:
    return [_rect(200 - 1.8 * half, y - 34, 3.6 * half, 34, color, 8)]


def _stepped(y: float, half: float, color: str, trim: str) -> list[str]:
    return [_rect(200 - 0.6 * half, y - 62, 1.2 * half, 38, color, 3), _rect(200 - 1.2 * half, y - 28, 2.4 * half, 28, color, 3)]


#: What closes a narrow neck: a bottle's and a flacon's. ``half`` is half the neck's width.
NECK_TOPS = {"block": _block, "tall": _tall, "ball": _ball, "pump": _pump, "dropper": _dropper, "wide": _wide, "stepped": _stepped}


def _ribbed(y: float, half: float, color: str, trim: str) -> list[str]:
    ribs = " ".join(f"M{x:g},{y - 52} L{x:g},{y - 8}" for x in range(int(214 - half), int(186 + half), 10))
    return [_rect(200 - half - 8, y - 60, 2 * half + 16, 60, color, 10), _line(ribs, 1.0, ' stroke-opacity=".35"')]


def _smooth(y: float, half: float, color: str, trim: str) -> list[str]:
    return [_rect(200 - half - 8, y - 46, 2 * half + 16, 46, color, 10), _rect(200 - half - 8, y - 12, 2 * half + 16, 12, trim, 3, LW_DETAIL)]


def _dome(y: float, half: float, color: str, trim: str) -> list[str]:
    return [
        _path(f"M{200 - half - 6},{y - 14} Q{200 - half - 6},{y - 86} 200,{y - 86} Q{200 + half + 6},{y - 86} {200 + half + 6},{y - 14} Z", color),
        _rect(200 - half - 8, y - 16, 2 * half + 16, 16, trim, 3, LW_DETAIL),
    ]


def _low(y: float, half: float, color: str, trim: str) -> list[str]:
    return [_rect(200 - half - 14, y - 22, 2 * half + 28, 22, color, 11)]


def _tiered(y: float, half: float, color: str, trim: str) -> list[str]:
    return [_rect(200 - 0.6 * half, y - 58, 1.2 * half, 34, color, 6), _rect(200 - half - 8, y - 28, 2 * half + 16, 28, color, 6)]


def _knob(y: float, half: float, color: str, trim: str) -> list[str]:
    return [
        f'<circle cx="200" cy="{y - 48}" r="20" fill="{trim}" stroke="{INK}" stroke-width="{LW}"/>',
        _rect(200 - half - 8, y - 32, 2 * half + 16, 32, color, 8),
    ]


#: What closes a wide mouth: a jar's lid. ``half`` is half the mouth's width.
LIDS = {"ribbed": _ribbed, "smooth": _smooth, "dome": _dome, "low": _low, "tiered": _tiered, "knob": _knob}

BOTTLES = {
    "shouldered": Form("M142,366 L142,186 Q142,138 178,116 L180,88 L220,88 L222,116 Q258,138 258,186 L258,366 Q200,374 142,366 Z", 94, (150, 226, 100, 92), (200, 186), "M154,206 Q154,164 180,140"),
    "square": Form("M130,366 L130,152 L180,124 L180,88 L220,88 L220,124 L270,152 L270,366 Z", 94, (144, 226, 112, 92), (200, 182), "M142,206 L142,160"),
    "cone": Form("M116,366 L172,128 L180,118 L180,88 L220,88 L220,118 L228,128 L284,366 Z", 94, (152, 240, 96, 90), (200, 192), "M158,216 L176,142"),
    "waisted": Form("M134,366 Q172,250 134,150 Q138,130 180,120 L180,88 L220,88 L220,120 Q262,130 266,150 Q228,250 266,366 Z", 94, (158, 214, 84, 84), (200, 172), "M150,196 Q146,160 176,138"),
    "flask": Form("M180,88 L220,88 L220,130 Q296,150 296,250 Q296,366 200,366 Q104,366 104,250 Q104,150 180,130 Z", 94, (146, 206, 108, 92), (200, 334), "M122,226 Q124,172 172,148"),
    "squat": Form("M112,366 L112,222 Q112,190 150,180 L180,172 L180,144 L220,144 L220,172 L250,180 Q288,190 288,222 L288,366 Z", 150, (132, 232, 136, 92), (200, 204), "M126,226 Q126,204 150,194"),
    "slim": Form("M156,366 L156,128 Q156,110 180,104 L180,88 L220,88 L220,104 Q244,110 244,128 L244,366 Z", 94, (162, 206, 76, 100), (200, 166), "M168,190 L168,130"),
    "chamfered": Form("M146,366 L122,342 L122,168 L146,140 L180,130 L180,88 L220,88 L220,130 L254,140 L278,168 L278,342 L254,366 Z", 94, (146, 226, 108, 92), (200, 186), "M134,206 L134,172 L152,152"),
}
JARS = {
    "wide": Form("M104,196 L296,196 L296,316 Q296,346 266,346 L134,346 Q104,346 104,316 Z", 198, (126, 212, 148, 88), (200, 322), "M116,214 L116,320"),
    "tall": Form("M124,130 L276,130 L276,336 Q276,360 252,360 L148,360 Q124,360 124,336 Z", 132, (136, 176, 128, 104), (200, 318), "M136,146 L136,336"),
    "bowl": Form("M92,210 L308,210 Q308,350 200,350 Q92,350 92,210 Z", 212, (134, 224, 132, 74), (200, 324), "M106,226 Q114,286 148,320"),
    "taper": Form("M84,196 L316,196 L276,350 L124,350 Z", 198, (122, 212, 156, 82), (200, 322), "M102,214 L122,296"),
    "footed": Form("M112,190 L288,190 L288,318 L312,330 L312,356 L88,356 L88,330 L112,318 Z", 192, (130, 204, 140, 82), (200, 342), "M122,206 L122,306"),
    "squat": Form("M76,240 L324,240 L324,330 Q324,352 300,352 L100,352 Q76,352 76,330 Z", 242, (118, 250, 164, 64), (200, 335), "M90,254 L90,328"),
    "apothecary": Form("M140,140 L260,140 L260,156 Q322,184 322,260 Q322,352 200,352 Q78,352 78,260 Q78,184 140,156 Z", 142, (122, 206, 156, 84), (200, 322), "M94,250 Q96,204 136,176"),
}
FLACONS = {
    "block": Form("M140,124 L260,124 Q286,124 286,150 L286,326 Q286,352 260,352 L140,352 Q114,352 114,326 L114,150 Q114,124 140,124 Z", 126, (138, 196, 124, 80), (200, 314), "M126,150 L126,320"),
    "disc": Form("M82,240 A118,118 0 1 1 318,240 A118,118 0 1 1 82,240 Z", 126, (138, 196, 124, 80), (200, 312), "M100,270 Q88,190 136,156"),
    "arch": Form("M114,352 L114,216 Q114,124 200,124 Q286,124 286,216 L286,352 Z", 128, (138, 204, 124, 80), (200, 316), "M126,330 L126,216 Q128,170 156,150"),
    "hexagon": Form("M200,112 L292,164 L292,300 L200,352 L108,300 L108,164 Z", 120, (138, 196, 124, 80), (200, 312), "M120,290 L120,172"),
    "slim": Form("M142,124 L258,124 L258,352 L142,352 Z", 126, (150, 196, 100, 80), (200, 316), "M150,136 L150,186"),
    "wedge": Form("M136,124 L264,124 L304,352 L96,352 Z", 126, (136, 204, 128, 80), (200, 318), "M142,150 L122,322"),
    "shield": Form("M108,124 L292,124 L292,250 Q292,320 200,356 Q108,320 108,250 Z", 126, (140, 170, 120, 80), (200, 288), "M120,138 L120,250"),
}


@dataclass(frozen=True)
class Family:
    """One shape's looks: its forms, its tops, its top's half width, and its label's largest size."""

    forms: dict[str, Form]
    tops: dict
    half: float
    max_size: float = 44
    neck: bool = False  # a flacon's metal neck stands between its top and its form
    stamp: str | None = None  # printed on the panel under the label


FAMILIES = {
    "bottle": Family(BOTTLES, NECK_TOPS, 24),
    "jar": Family(JARS, LIDS, 92, 52),
    "moisturiser_jar": Family(JARS, LIDS, 92, 30),
    "fragrance": Family(FLACONS, NECK_TOPS, 30, 28, neck=True, stamp="EAU DE PARFUM"),
}


def _top(family: Family, form: Form, top: str, color: str, trim: str) -> list[str]:
    half = min(family.half, form.panel[2] * 0.62)
    if not family.neck:
        return family.tops[top](form.mouth, half, color, trim)
    collar = _rect(184, form.mouth - 22, 32, 24, trim, 0, LW_DETAIL)
    return [*family.tops[top](form.mouth - 20, half, color, trim), collar]


def _printed(family: Family, form: Form, label: str | None) -> list[str]:
    x, y, w, h = form.panel
    if family.stamp is None:
        return _panel(x, y, w, h, label, family.max_size)
    words = [_word(label, x + w / 2, y + h * 0.37, w - 14, family.max_size)] if label else []
    return [*_panel(x, y, w, h, None), *words, _text(x + w / 2, y + h * 0.82, family.stamp, 9, INK, ' letter-spacing="1.5"')]


def _pack(family: Family, paint: str, fill: Fill, label: str | None, form: str, top: str, top_color: str, emblem: str, trim: str) -> list[str]:
    drawn = family.forms[form]
    return [
        _path(drawn.body, paint),
        *_top(family, drawn, top, top_color, trim),
        _highlight(drawn.gloss, 5, 0.5),
        *_printed(family, drawn, label),
        *_lipstick_emblem(emblem, *drawn.mark, trim),
    ]


def _looked(shape: str):
    """``shape``'s drawing, which draws a pack of its family when its params carry a look."""
    plain, family = SHAPES[shape], FAMILIES[shape]

    def draw(paint: str, fill: Fill, label: str | None, **look: str) -> list[str]:
        return _pack(family, paint, fill, label, **look) if look else plain(paint, fill, label)

    return draw


register({shape: _looked(shape) for shape in FAMILIES})
