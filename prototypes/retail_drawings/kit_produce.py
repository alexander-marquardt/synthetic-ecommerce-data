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

from kit import INK, LW_DETAIL, SHAPES, Fill, _panel, _path, _shade, register

#: Fruit -> (the kit shape that draws one, its typical weight in grams, drawn size).
FRUIT = {
    "orange": ("orange", 200, 116),
    "clementine": ("orange", 85, 96),
    "lemon": ("lemon", 110, 112),
    "apple": ("apple", 170, 112),
}
MIN_FRUIT, MAX_FRUIT = 3, 7
PACKS = ("loose", "net", "bag")

#: Count -> the fruits' centres, back row first, so nearer fruits overlap farther ones.
PILES = {
    3: ((200, 196), (150, 270), (250, 270)),
    4: ((160, 200), (240, 200), (140, 274), (260, 274)),
    5: ((165, 186), (240, 192), (120, 266), (200, 276), (280, 266)),
    6: ((150, 180), (225, 176), (290, 214), (110, 258), (190, 274), (268, 284)),
    7: ((160, 168), (240, 172), (110, 230), (200, 226), (290, 236), (150, 296), (250, 298)),
}


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
