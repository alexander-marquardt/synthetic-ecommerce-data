"""The punnet and the fruit or vegetable it holds (moved out of ``kit`` to keep it under the line cap, gen#455).

A punnet is a heap of its produce behind a clear tray (gen#1111): every item is drawn to the same
painted area whatever its own size (a bean as large as a tomato), the back row stands over the
rim, and the rest shows through the tray's film, so the produce fills more than half the product
area the house style frames. Each item carries the produce kit's gloss, and the label is a small
sticker on the tray's front that hides little of it.
"""

# ruff: noqa: E501 -- SVG literals and data rows read better whole (prototype only).

from __future__ import annotations

import functools
import math

from synthetic_ecommerce_data.domains.retail import kit_produce, sheet_cover, sheet_extent
from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _word,
    register,
)

HALF = ' stroke-opacity=".5"'


def _strawberry() -> list[str]:
    berry = (
        "M0,-24 C18,-24 24,-8 16,10 C10,22 4,30 0,32 C-4,30 -10,22 -16,10 C-24,-8 -18,-24 0,-24 Z"
    )
    return [
        _path(berry, "#d23a3a", 2),
        _path("M-12,-22 L0,-32 L12,-22 L0,-18 Z", "#4c9a3c", 1.4),
        '<g fill="#f6e27a"><circle cx="-6" cy="-6" r="1.6"/><circle cx="6" cy="2" r="1.6"/><circle cx="-2" cy="12" r="1.6"/></g>',
    ]


def _tomato() -> list[str]:
    return [
        _path(
            "M0,-22 C22,-22 28,-2 22,12 C16,26 -16,26 -22,12 C-28,-2 -22,-22 0,-22 Z", "#c8312e", 2
        ),
        _path("M-10,-20 L0,-30 L10,-20 L4,-16 L0,-20 L-4,-16 Z", "#4c9a3c", 1.4),
        _highlight("M-14,-8 Q-12,-16 -4,-17", 2, 0.6),
    ]


def _mushroom() -> list[str]:
    return [
        _path("M-9,2 L-7,26 Q0,30 7,26 L9,2 Z", "#efe9da", 2),
        _path("M-26,4 C-26,-20 -10,-28 0,-28 C10,-28 26,-20 26,4 Q0,12 -26,4 Z", "#cdb797", 2),
        _highlight("M-16,-8 Q-12,-18 -4,-20", 2, 0.5),
    ]


def _carrot() -> list[str]:
    return [
        '<g transform="rotate(-14)">',
        _path("M-8,-20 L8,-20 L3,34 L-3,34 Z", "#e07a1f", 2),
        _line("M-6,-8 L-1,-8 M2,6 L7,6 M-4,18 L0,18", 1.4),
        _path("M-6,-20 L-10,-34 L-2,-26 L0,-38 L2,-26 L10,-34 L6,-20 Z", "#4c9a3c", 1.4),
        "</g>",
    ]


def _bean() -> list[str]:
    return [
        _path(
            "M-20,22 C-24,0 -10,-16 6,-26 C12,-22 14,-18 10,-14 C0,-6 -2,6 -2,22 Z", "#5a9a3a", 2
        ),
        _line("M-12,18 C-14,2 -4,-10 4,-20", 1.2, HALF),
    ]


def _herb() -> list[str]:
    leaf = "M0,0 C-14,-8 -14,-26 0,-34 C14,-26 14,-8 0,0 Z"
    return [
        f'<g transform="rotate(-38) translate(0 -2)">{_path(leaf, "#3a8f6a", 1.6)}</g>',
        f'<g transform="rotate(38) translate(0 -2)">{_path(leaf, "#2f7d5a", 1.6)}</g>',
        f'<g transform="translate(0 4)">{_path(leaf, "#47a57a", 1.6)}</g>',
        _line("M0,0 L0,-22", 1.0, HALF),
    ]


def _pepper() -> list[str]:
    return [
        _path(
            "M-16,-16 C-26,0 -20,24 -4,28 C0,30 6,30 10,28 C24,22 26,-2 16,-16 C8,-22 -8,-22 -16,-16 Z",
            "#c8312e",
            2,
        ),
        _path("M-3,-18 L-1,-30 L4,-30 L4,-18 Z", "#4c9a3c", 1.4),
        _highlight("M-14,-6 Q-14,-14 -6,-16", 2, 0.6),
    ]


#: What a punnet holds, by the ``produce`` param (a punnet of strawberries when it is absent):
#: (one item drawn about its own center, the color its body is painted and glossed in).
PRODUCE = {
    "strawberry": (_strawberry, "#d23a3a"),
    "tomato": (_tomato, "#c8312e"),
    "mushroom": (_mushroom, "#cdb797"),
    "carrot": (_carrot, "#e07a1f"),
    "bean": (_bean, "#5a9a3a"),
    "herb": (_herb, "#47a57a"),
    "pepper": (_pepper, "#c8312e"),
}
#: Where the items lie, back row first so nearer items overlap farther ones: the back row stands
#: over the rim and the rest fill the tray behind its film.
HEAP = (
    (92, 140), (164, 134), (236, 134), (308, 140),
    (76, 196), (138, 190), (200, 188), (262, 190), (324, 196),
    (100, 248), (166, 244), (234, 244), (300, 248),
    (134, 298), (200, 296), (266, 298),
)  # fmt: skip
#: The painted area each item is drawn to, in sheet units squared, whatever its own size, and
#: the longest it may be, so a long item stays inside the tray.
ITEM_AREA, ITEM_LONGEST = 6000.0, 108.0
#: Produce -> how much wider it is drawn than its own proportions: a baby carrot or a bean is a
#: chunky one, where at its own width a heap of thin ones leaves the tray empty.
STRETCH = {"carrot": 2.2, "bean": 1.4}
#: Produce -> the longest it may be, past :data:`ITEM_LONGEST`: a heap of baby carrots lies
#: tilted in the tray, so a longer root still stays inside it.
LONGEST = {"carrot": 130.0}
#: The tray: its outline, the rim's line, and the sticker the label goes on.
TRAY = "M34,178 L366,178 L338,356 L62,356 Z"
STICKER = (136, 314, 128, 34)
_SVG = '<svg xmlns="http://www.w3.org/2000/svg">{}</svg>'


@functools.cache
def _scale(produce: str) -> str:
    """The ``scale`` that draws one ``produce`` item to :data:`ITEM_AREA`, no longer than
    :data:`ITEM_LONGEST` (or its :data:`LONGEST`), :data:`STRETCH` times wider."""
    sx = STRETCH.get(produce, 1.0)
    svg = _SVG.format(f'<g transform="scale({sx:g} 1)">{"".join(PRODUCE[produce][0]())}</g>')
    painted = sheet_cover.cover(svg, (-60, -60, 60, 60), step=1.0) * 120**2
    box = sheet_extent.reach(svg)
    assert box is not None, produce
    longest = LONGEST.get(produce, ITEM_LONGEST)
    k = min(math.sqrt(ITEM_AREA / painted), longest / max(box[2] - box[0], box[3] - box[1]))
    return f"scale({k * sx:.4g} {k:.4g})"


def punnet(paint: str, fill: Fill, label: str | None, produce: str = "strawberry") -> list[str]:
    """A punnet heaped with ``produce`` (one of :data:`PRODUCE`): the fruit or vegetable it is named for."""
    item, color = PRODUCE[produce]
    body = "".join(kit_produce._glossed(item(), color, "gloss-punnet"))
    k = _scale(produce)
    items = [
        f'<g class="fruit" transform="translate({x} {y}) rotate({(i * 37) % 31 - 15}) {k}">{body}</g>'
        for i, (x, y) in enumerate(HEAP)
    ]
    slots = " ".join(f"M{x},196 L{x + (x - 200) * -0.1:.1f},344" for x in range(64, 346, 28))
    sx, sy, sw, sh = STICKER
    out = [
        kit_produce.GLOSS.format("gloss-punnet"),
        '<ellipse class="ground" cx="200" cy="356" rx="160" ry="10" fill="#000000" fill-opacity=".14"/>',
        _path(TRAY, "#dfeef2"),
        *items,
        _path(TRAY, "#eef6f8", 3, ' fill-opacity=".3"'),
        _line(slots, 1.0, HALF),
        _line("M30,178 L370,178", 5),
    ]
    if label:
        out.append(
            f'<g class="label"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="5" fill="{paint}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            f"{_word(label, sx + sw / 2, sy + sh / 2, sw - 12, 24, '#ffffff')}</g>"
        )
    return out


register({"punnet": punnet})
