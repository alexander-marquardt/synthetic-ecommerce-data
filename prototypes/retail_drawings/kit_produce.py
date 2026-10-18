"""Loose and packed fruit drawn as several fruits, the count from the record (gen#125).

A pack of produce is drawn as a small pile of 3 to 7 fruits (``loose``), in a
net or in a clear bag. :func:`fruit_count` turns the record's pack count or
net weight into the number drawn, and each fruit's small offset and turn come
from a hash of the product's id (:func:`jitter`), never from a random draw, so
a drawing is the same on every build and two products' piles differ.
"""

# ruff: noqa: E501 -- SVG literals and data rows read better whole (prototype only).

from __future__ import annotations

import zlib

import kit_motifs  # noqa: F401 -- registers carrot and cherries, drawn in a pile
from kit import INK, LW_DETAIL, SHAPES, Fill, _highlight, _line, _panel, _path, _shade, register

#: Fruit -> (the kit shape that draws one, its typical weight in grams, drawn size).
FRUIT = {
    "orange": ("orange", 200, 116),
    "clementine": ("orange", 85, 96),
    "lemon": ("lemon", 110, 112),
    "apple": ("apple", 170, 112),
    "lime": ("lemon", 70, 100),
    "strawberry": ("strawberry", 20, 84),
    "grapefruit": ("orange", 350, 128),
    "mandarin": ("orange", 80, 92),
    "satsuma": ("orange", 80, 92),
    "raspberry": ("strawberry", 5, 60),
    "blueberry": ("orange", 2, 44),
    "blackberry": ("strawberry", 8, 64),
    "grape": ("orange", 5, 56),
    "tomato": ("tomato", 100, 110),
    "onion": ("onion", 150, 110),
    "potato": ("potato", 180, 120),
    "carrot": ("carrot", 70, 130),
    "banana": ("banana", 120, 130),
    "cherry": ("cherries", 10, 90),
}
MIN_FRUIT, MAX_FRUIT = 3, 7
PACKS = ("loose", "net", "bag")

#: Count -> the fruits' centers, back row first, so nearer fruits overlap farther ones.
PILES = {
    3: ((200, 196), (150, 270), (250, 270)),
    4: ((160, 200), (240, 200), (140, 274), (260, 274)),
    5: ((165, 186), (240, 192), (120, 266), (200, 276), (280, 266)),
    6: ((150, 180), (225, 176), (290, 214), (110, 258), (190, 274), (268, 284)),
    7: ((160, 168), (240, 172), (110, 230), (200, 226), (290, 236), (150, 296), (250, 298)),
}


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
    shape, _, size = FRUIT[fruit]
    one = Fill("solid", fill.base, _shade(fill.base, 0.3))
    out = []
    if pack == "bag":
        out.append(_path("M86,120 Q200,104 314,120 L330,336 Q200,356 70,336 Z", "#eef6f8", extra=' fill-opacity=".6"'))
    for i, (x, y) in enumerate(PILES[count]):
        dx, dy, turn = jitter(seed, i)
        body = "".join(SHAPES[shape](fill.base, one, None))
        out.append(
            f'<g class="fruit" transform="translate({x + dx:g} {y + dy:g}) rotate({turn:g}) '
            f'scale({size / 400:.4g}) translate(-200 -210)">{body}</g>'
        )
    if pack == "net":
        hull = "M84,150 Q200,104 316,150 Q350,250 306,338 Q200,362 94,338 Q50,250 84,150 Z"
        mesh = " ".join(f"M{x},100 L{x + 240},360" for x in range(-160, 360, 22))
        mesh += " " + " ".join(f"M{x},100 L{x - 240},360" for x in range(40, 560, 22))
        cid = "net-" + "".join(c for c in seed if c.isalnum())
        net = _shade(fill.base, 0.4)
        out += [
            f'<clipPath id="{cid}"><path d="{hull}"/></clipPath>',
            f'<path d="{mesh}" fill="none" stroke="{net}" stroke-width="1.6" clip-path="url(#{cid})"/>',
            _path(hull, "none", LW_DETAIL, stroke=net),
            f'<rect x="176" y="96" width="48" height="26" rx="4" fill="{_shade(fill.base, 0.35)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        ]
    if label and pack != "loose":
        out += _panel(120, 330, 160, 44, label, 26)
    return out


register({"produce_pile": produce_pile})
