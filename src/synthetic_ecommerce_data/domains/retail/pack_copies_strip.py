"""A strip of packs as they are drawn, for the docs and the pull request (gen#728).

Usage::

    uv run python -m synthetic_ecommerce_data.domains.retail.pack_copies_strip \
        --out docs/images/pack-copies.svg

Each cell is one catalogue SKU's image, as the release draws it. The catalogue sells no six cans
and no Kids dress packs yet (gen#727), so those cells are a product given that pack's size.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from synthetic_ecommerce_data.domains.retail import (
    image_release,
    pack_copies,
    pack_scale_strip,
    scale,
)

SHEET = 400
GAP = 20
CAPTION = 28
ACROSS = 4

#: ``(caption, shape, a word of the title, count)``: the cells of real SKUs, in order.
SHOWN = (
    ("Socks, 5 pairs", "socks", "Socks", 5),
    ("Socks, 7 pairs", "socks", "Socks", 7),
    ("Bodysuits, 3 pack", "baby_bodysuit", "Bodysuits", 3),
    ("Knickers, 5 pack", "knickers", "Briefs", 5),
    ("Ginger beer, 6 bottles", "bottle", "Beer", 6),
    ("Yogurt, 4 pots", "tub", "Yogurt", 4),
    ("Chocolate, 4 bars", "bar", "Chocolate", 4),
    ("Eye patches, 24", "eye_patches", "Patches", 24),
    ("Tea, 40 bags", "box", "Tea", 40),
    ("Tea, 80 bags", "box", "Tea", 80),
    ("Tea, 240 bags", "box", "Tea", 240),
    ("Eye patches, 30", "eye_patches", "Patches", 30),
    ("Cable ties, 100", "cable_ties", "Ties", 100),
)
#: ``(caption, shape, a word of the title, count)``: a product given a pack it is not sold in yet.
GIVEN = (
    ("Lager, 6 cans", "tin", "Lager", 6),
    ("Kids dresses, 2 pack", "dress", "Girls", 2),
    ("Kids dresses, 3 pack", "dress", "Girls", 3),
)


def _named(recs: list[dict], shape: str, word: str) -> list[dict]:
    """The products of a shape with ``word`` in their title."""
    return [r for r in recs if r["drawing"]["shape"] == shape and word in r["title"].split()]


def _find(recs: list[dict], shape: str, word: str, n: int) -> tuple[dict, dict]:
    """The first such product and its SKU whose pack holds ``n``."""
    return next(
        (rec, sku)
        for rec in _named(recs, shape, word)
        for sku in rec["skus"]
        if pack_copies.count(rec, sku) == n
    )


def _given(recs: list[dict], shape: str, word: str, n: int) -> tuple[dict, dict]:
    """The first such product, given a pack of ``n``."""
    rec = _named(recs, shape, word)[0]
    sku = rec["skus"][0] | {"units_per_pack": n}
    return rec | {"skus": [sku]}, sku


def cells() -> list[tuple[str, bytes]]:
    """``(caption, svg)`` of every cell of the strip."""
    recs = scale.templates()
    packs = [(caption, *_find(recs, *row)) for caption, *row in SHOWN]
    packs += [(caption, *_given(recs, *row)) for caption, *row in GIVEN]
    return [(caption, image_release.render(rec, sku)) for caption, rec, sku in packs]


def strip() -> str:
    """The strip's SVG: every cell on a 400 x 400 sheet, in rows of :data:`ACROSS`."""
    drawn = cells()
    down = (len(drawn) + ACROSS - 1) // ACROSS
    width = ACROSS * (SHEET + GAP) + GAP
    height = down * (SHEET + CAPTION + GAP) + GAP
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    for i, (caption, svg) in enumerate(drawn):
        x = GAP + i % ACROSS * (SHEET + GAP)
        y = GAP + i // ACROSS * (SHEET + CAPTION + GAP)
        parts.append(pack_scale_strip._caption(caption, x, y + 20))
        parts.append(pack_scale_strip._cell(svg.decode(), x, y + CAPTION))
    parts.append("</svg>")
    return "".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pack_copies_strip.py", description=__doc__.split("\n")[0]
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(strip(), encoding="utf-8")
    print(f"{args.out}  {args.out.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
