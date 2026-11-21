"""Loose and packed fruit drawn as several fruits, the count from the record (gen#125).

A pack of produce is drawn as a pile of fruits (``loose``), in a net or in a
clear bag. :func:`fruit_count` turns the record's pack count or net weight into
the number drawn, and each fruit's small offset and turn come from a hash of
the product's id (:func:`jitter`), never from a random draw, so a drawing is
the same on every build and two products' piles differ.

The pile fills its picture (gen#1111): each layout in :data:`PILES` gives its
fruits one size, and every fruit is drawn to the same painted area at that
size whatever its own shape's size, so a pile covers more than half the product
area the house style frames. Each fruit carries a gloss (a highlight up-left, a
shade down-right) and the pile stands on a ground shadow, so it reads as round.
"""

# ruff: noqa: E501 -- SVG literals and data rows read better whole (prototype only).

from __future__ import annotations

import functools
import math
import re
import zlib

from synthetic_ecommerce_data.domains.retail import (
    kit_motifs,  # noqa: F401 -- registers carrot and cherries, drawn in a pile
    sheet_cover,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW_DETAIL,
    SHAPES,
    Fill,
    _highlight,
    _line,
    _panel,
    _path,
    _shade,
    register,
)

#: Fruit -> (the kit shape that draws one, its typical weight in grams).
FRUIT = {
    "orange": ("orange", 200),
    "clementine": ("orange", 85),
    "lemon": ("lemon", 110),
    "apple": ("apple", 170),
    "lime": ("lemon", 70),
    "strawberry": ("strawberry", 20),
    "grapefruit": ("orange", 350),
    "mandarin": ("orange", 80),
    "satsuma": ("orange", 80),
    "raspberry": ("strawberry", 5),
    "blueberry": ("orange", 2),
    "blackberry": ("strawberry", 8),
    "grape": ("orange", 5),
    "tomato": ("tomato", 100),
    "onion": ("onion", 150),
    "potato": ("potato", 180),
    "carrot": ("carrot", 70),
    "banana": ("banana", 120),
    "cherry": ("cherries", 10),
}
MIN_FRUIT, MAX_FRUIT = 3, 7
PACKS = ("loose", "net", "bag")

#: Count -> (the fruits' centers, back row first so nearer fruits overlap farther ones; the
#: size each fruit is drawn at; the widest and tallest one fruit may be). One fruit stands
#: level and fills the product area; a pile overlaps its fruits so it fills it too (gen#1111).
PILES = {
    1: (((200, 196),), 330, (362, 326)),
    2: (((132, 214), (268, 184)), 240, (290, 290)),
    3: (((200, 134), (126, 252), (274, 252)), 204, (240, 240)),
    4: (((134, 138), (266, 138), (134, 258), (266, 258)), 186, (222, 222)),
    5: (((140, 126), (260, 126), (88, 250), (200, 262), (312, 250)), 168, (200, 200)),
    6: (((90, 126), (200, 116), (310, 126), (90, 252), (200, 264), (310, 252)), 158, (190, 190)),
    7: (((140, 104), (260, 104), (82, 200), (200, 194), (318, 200), (140, 286), (260, 286)), 142, (174, 174)),
}
#: A pair of fruits wider than tall (lemons, limes), one above the other.
PAIR_WIDE = (((196, 124), (204, 256)), 300, (330, 240))
#: The painted area each fruit is drawn to, as a share of its size squared: a round fruit's.
AREA = 0.72
#: Shape -> how much wider it is drawn than its own proportions: a carrot in a pile reads as
#: a chunky root and an onion as a round bulb, where at their own width a bunch of thin roots
#: or tall bulbs leaves the picture empty.
STRETCH = {"carrot": 1.8, "onion": 1.3}
#: Shape -> how much farther than a round fruit it may reach: a long or forked fruit (a banana,
#: a carrot, a pair of cherries) paints less of its box, so it is drawn longer to paint as much.
REACH = {"banana": 1.6, "carrot": 1.6, "cherries": 1.4}
#: The box the whole pile stays inside: the sheet, less a margin for the outline and the turn.
ROOM = (14.0, 20.0, 386.0, 364.0)
#: The gloss each fruit carries over its body: light up-left, shade down-right, so it reads round.
GLOSS = (
    '<radialGradient id="{0}" cx=".34" cy=".3" r=".78">'
    '<stop offset="0" stop-color="#ffffff" stop-opacity=".6"/>'
    '<stop offset=".3" stop-color="#ffffff" stop-opacity="0"/>'
    '<stop offset=".62" stop-color="#000000" stop-opacity="0"/>'
    '<stop offset="1" stop-color="#000000" stop-opacity=".3"/></radialGradient>'
)
_SVG = '<svg xmlns="http://www.w3.org/2000/svg">{}</svg>'


def tomato(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A tomato (gen#445): a flattened round with a star-shaped green calyx."""
    calyx = "M200,138 L176,112 L194,124 L200,96 L208,124 L228,110 L212,138 L236,148 L200,152 L164,148 Z"
    return [
        _path("M96,216 C96,150 150,136 200,148 C250,136 304,150 304,216 C304,290 250,324 200,324 C150,324 96,290 96,216 Z", paint),
        _path(calyx, "#5aa24a", 2),
        _highlight("M122,192 Q130,166 160,154", 9, 0.45),
    ]


def onion(paint: str, fill: Fill, label: str | None) -> list[str]:
    """An onion (gen#445): a bulb drawn up to a dry tip, with a root tuft and papery lines."""
    bulb = "M200,70 Q214,110 252,140 Q316,196 296,264 Q270,330 200,330 Q130,330 104,264 Q84,196 148,140 Q186,110 200,70 Z"
    return [
        _path(bulb, paint),
        _line("M200,86 Q150,200 176,326 M200,86 Q250,200 224,326 M200,86 Q200,200 200,328", 1.6),
        _line("M178,330 L168,350 M200,330 L200,352 M222,330 L234,350", 2),
        _highlight("M130,214 Q136,176 168,150", 8, 0.4),
    ]


def potato(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A potato (gen#445): an uneven oval with a few eyes."""
    body = "M92,226 Q88,170 150,148 Q210,126 270,150 Q322,176 308,238 Q296,302 224,314 Q150,326 106,286 Q94,262 92,226 Z"
    eyes = ((150, 214), (214, 188), (262, 236), (188, 270), (126, 262))
    return [
        _path(body, paint),
        *[f'<path d="M{x - 7},{y} Q{x},{y - 5} {x + 7},{y}" fill="none" stroke="{INK}" stroke-width="1.6"/>' for x, y in eyes],
        _highlight("M124,196 Q136,170 172,160", 9, 0.4),
    ]


def banana(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A banana (gen#445): a crescent with a stalk at one end and a dark tip at the other."""
    body = "M92,150 Q112,296 252,326 Q304,334 326,290 Q250,300 190,244 Q146,196 140,124 Z"
    return [
        _path(body, paint),
        _path("M92,150 L100,106 L138,100 L140,124 Z", "#8a8a4a", 2),
        _path("M300,320 Q316,316 326,290 Q312,300 300,320 Z", "#3a3a2a", 2),
        _line("M130,150 Q160,270 270,312", 1.6),
        _highlight("M120,170 Q140,250 210,292", 7, 0.4),
    ]


register({"tomato": tomato, "onion": onion, "potato": potato, "banana": banana})


def fruit_count(fruit: str, grams: float | None = None, count: int | None = None) -> int:
    """How many fruits a pack shows: its count, else its weight over one fruit's, in 3-7."""
    if fruit not in FRUIT:
        raise ValueError(f"unknown fruit {fruit!r}; one of {sorted(FRUIT)}")
    if count is None:
        if grams is None:
            raise ValueError("a produce pack states its count or its weight")
        count = round(grams / FRUIT[fruit][1])
    return max(MIN_FRUIT, min(MAX_FRUIT, count))


def jitter(seed: str, i: int) -> tuple[float, float, float]:
    """Fruit ``i``'s (dx, dy, turn) for product ``seed``: a hash, never random."""
    h = zlib.crc32(f"{seed}:{i}".encode())
    return (h % 17) - 8, ((h >> 8) % 13) - 6, ((h >> 16) % 41) - 20


def pile_params(fruit: str, seed: str, pack: str = "loose", grams=None, count=None) -> dict:
    """A ``produce_pile`` drawing's params, the count derived from the record."""
    if pack not in PACKS:
        raise ValueError(f"unknown pack {pack!r}; one of {PACKS}")
    return {"fruit": fruit, "count": fruit_count(fruit, grams, count), "seed": seed, "pack": pack}


def produce_pile(
    paint: str, fill: Fill, label: str | None, fruit: str = "orange", count: int = 5,
    seed: str = "", pack: str = "loose",
) -> list[str]:  # fmt: skip
    """``count`` fruits in a pile (loose, netted or bagged); ``label`` goes on the pack's tag."""
    shape = FRUIT[fruit][0]
    centers, size, (widest, tallest) = PILES[count]
    if count == 2 and _is_wide(shape):
        centers, size, (widest, tallest) = PAIR_WIDE
    one = Fill("solid", fill.base, _shade(fill.base, 0.3))
    uid = "".join(c for c in seed if c.isalnum())
    gloss = f"gloss-{uid}"
    out = [GLOSS.format(gloss), '<ellipse class="ground" cx="200" cy="346" rx="164" ry="12" fill="#000000" fill-opacity=".14"/>']
    if pack == "bag":
        out.append(_path(BAG, "#eef6f8", LW_DETAIL, ' fill-opacity=".55"'))
    reach = REACH.get(shape, 1.0)
    box, k = _fit(shape, size, widest * reach, tallest * reach)
    body = "".join(_glossed(SHAPES[shape](fill.base, one, None), fill.base, gloss))
    fruits = _place(centers, seed, box, k, STRETCH.get(shape, 1.0), body)
    f = _room(sheet_extent.reach(_SVG.format("".join(fruits))))
    if f < 1.0:
        centers = tuple((200 + (x - 200) * f, 200 + (y - 200) * f) for x, y in centers)
        fruits = _place(centers, seed, box, k * f, STRETCH.get(shape, 1.0), body)
    out += fruits
    if pack == "bag":  # the film over the fruit: a sheen and the bag's twisted neck
        out += [
            _path(BAG, "#ffffff", LW_DETAIL, ' fill-opacity=".16"', stroke=_shade("#eef6f8", 0.45)),
            _highlight("M64,120 Q56,220 70,320 M330,112 Q344,170 340,220", 6, 0.55),
            _path("M182,64 L218,64 L210,84 L190,84 Z", "#eef6f8", LW_DETAIL),
        ]
    if pack == "net":
        mesh = " ".join(f"M{x},60 L{x + 300},380" for x in range(-300, 380, 24))
        mesh += " " + " ".join(f"M{x},60 L{x - 300},380" for x in range(20, 700, 24))
        cid = f"net-{uid}"
        net = _shade(fill.base, 0.4)
        out += [
            f'<clipPath id="{cid}"><path d="{NET}"/></clipPath>',
            f'<path d="{mesh}" fill="none" stroke="{net}" stroke-width="2" clip-path="url(#{cid})"/>',
            _path(NET, "none", LW_DETAIL, stroke=net),
            f'<rect x="174" y="48" width="52" height="28" rx="4" fill="{_shade(fill.base, 0.35)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        ]
    if label and pack != "loose":
        out += _panel(120, 318, 160, 42, label, 26)
    return out


#: The clear bag and the net, each round the whole pile.
BAG = "M50,92 Q200,72 350,92 Q368,220 362,336 Q200,364 38,336 Q32,220 50,92 Z"
NET = "M44,108 Q200,52 356,108 Q386,224 350,344 Q200,372 50,344 Q14,224 44,108 Z"


@functools.cache
def _shape_box(shape: str) -> tuple[tuple[float, float, float, float], float]:
    """The box one fruit of ``shape`` covers on its own sheet, and the share of it it paints."""
    svg = _SVG.format("".join(SHAPES[shape]("#888888", Fill("solid", "#888888", "#444444"), None)))
    box = sheet_extent.reach(svg)
    assert box is not None, shape
    return box, sheet_cover.cover(svg, box)


def _is_wide(shape: str) -> bool:
    box = _shape_box(shape)[0]
    return (box[2] - box[0]) * STRETCH.get(shape, 1.0) > 1.24 * (box[3] - box[1])


def _fit(shape: str, size: float, widest: float, tallest: float) -> tuple[tuple[float, ...], float]:
    """The box of ``shape`` and the scale that draws it to :data:`AREA` of ``size`` squared, no
    wider than ``widest`` nor taller than ``tallest`` (a banana is not drawn twice as long)."""
    box, share = _shape_box(shape)
    w, h = (box[2] - box[0]) * STRETCH.get(shape, 1.0), box[3] - box[1]
    k = min(size * math.sqrt(AREA / (share * w * h)), widest / w, tallest / h)
    return box, k


def _room(pile: tuple[float, float, float, float] | None) -> float:
    """How much a pile covering ``pile`` shrinks about the sheet's middle to stay in :data:`ROOM`
    (1 when it already does): a turned fruit at the edge of a layout reaches past it."""
    if pile is None:
        return 1.0
    low = [(200 - edge) / (200 - got) for edge, got in zip(ROOM[:2], pile[:2], strict=True) if got < edge]
    high = [(edge - 200) / (got - 200) for edge, got in zip(ROOM[2:], pile[2:], strict=True) if got > edge]
    return min([1.0, *low, *high])


def _place(
    centers: tuple[tuple[float, float], ...], seed: str, box: tuple[float, ...], k: float,
    sx: float, body: str,
) -> list[str]:  # fmt: skip
    """One ``<g class="fruit">`` per center: ``body`` (drawn in ``box``) scaled by ``k`` (``sx``
    times wider), nudged and turned by the product's :func:`jitter`. One fruit stands level."""
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    out = []
    for i, (x, y) in enumerate(centers):
        dx, dy, turn = jitter(seed, i)
        turn = turn / 2 if len(centers) > 1 else 0
        out.append(
            f'<g class="fruit" transform="translate({x + dx:.4g} {y + dy:.4g}) rotate({turn:g}) '
            f'scale({k * sx:.4g} {k:.4g}) translate({-cx:g} {-cy:g})">{body}</g>'
        )
    return out


def _glossed(parts: list[str], paint: str, gloss: str) -> list[str]:
    """``parts``, each part painted the fruit's color followed by its gloss: the same outline,
    filled with the gradient and unstroked."""
    out = []
    for part in parts:
        out.append(part)
        if f'fill="{paint}"' in part:
            over = part.replace(f'fill="{paint}"', f'fill="url(#{gloss})"')
            out.append(re.sub(r'stroke="[^"]*"', 'stroke="none"', over, count=1))
    return out


register({"produce_pile": produce_pile})
