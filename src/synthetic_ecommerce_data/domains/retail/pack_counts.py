"""What each counted title draws: title N against the items its image shows (gen#728).

Usage::

    uv run python -m synthetic_ecommerce_data.domains.retail.pack_counts

prints, for the ceiling build, one row per product type, the count its title states (``Set of
4``, ``6 Pack``, ``16 Piece``: :func:`pack_copies.title_count`) and the SKU's own pack count, the
count its image draws and how it draws it:

- ``copies``: the layout's copies of the item (:func:`pack_copies.layout`), read off the
  ``pack-copy`` uses;
- ``outer box``: above 24, the outer box with the count on its front;
- ``own drawing``: the shape draws its own count (:func:`pack_copies.shown`): a suit's pieces, a
  nest of tables, a craft kit's contents;
- ``printed``: the count printed on the image (:func:`pack_copies.count_tag`), for a piece set
  whose drawing shows its parts rather than N items, or a count above 24;
- ``one item``: none of these, so one.

``tests/test_retail_set_counts_728.py`` fails on any row whose drawn count is not the title's.
"""

from __future__ import annotations

import re
import sys
from typing import NamedTuple

from synthetic_ecommerce_data.domains.retail import image_release, pack_copies

_PRINTED = re.compile(r'class="pack-tag" data-count="(\d+)"')
_BOX = re.compile(r'class="pack-box" data-count="(\d+)"')
_PACK = re.compile(r'class="pack" data-count="(\d+)"')


class Row(NamedTuple):
    """One (type, title N, SKU count): what its first SKU's image draws."""

    product_type: str
    title_n: int
    sku_count: int
    drawn: int
    how: str
    uses: int
    shape: str
    title: str


def drawn(rec: dict, sku: dict) -> tuple[int, str, int]:
    """The count the SKU's image draws, how it draws it, and the ``pack-copy`` uses in it."""
    svg = image_release.render(rec, sku).decode()
    uses = svg.count('class="pack-copy"')
    for pattern, how in ((_PRINTED, "printed"), (_BOX, "outer box"), (_PACK, "copies")):
        found = pattern.search(svg)
        if found:
            return int(found[1]), how, uses
    shown = pack_copies.shown(rec)
    return (shown, "own drawing", uses) if shown is not None else (1, "one item", uses)


def rows(records: list[dict]) -> list[Row]:
    """One row per (type, title N, SKU count) of ``records``, from the first SKU met."""
    seen: dict[tuple[str, int, int], tuple[dict, dict]] = {}
    for rec in records:
        n = pack_copies.title_count(rec["title"])
        if n is None:
            continue
        for sku in rec["skus"]:
            seen.setdefault((rec["product_type"], n, pack_copies.count(rec, sku)), (rec, sku))
    return [
        Row(ptype, n, counted, *drawn(rec, sku), rec["drawing"]["shape"], rec["title"])
        for (ptype, n, counted), (rec, sku) in sorted(seen.items())
    ]


def table(found: list[Row]) -> str:
    """``found`` as a Markdown table, a row per (type, title N)."""
    lines = ["| Type | Title N | Drawn | How | Example |", "|---|---:|---:|---|---|"]
    lines += [
        f"| {r.product_type} | {r.title_n} | {r.drawn} | {r.how} | {r.title} |" for r in found
    ]
    return "\n".join(lines)


def main() -> int:
    from synthetic_ecommerce_data.domains.retail import retail_figures

    found = rows(retail_figures.ceiling().records)
    print(table(found))
    wrong = [r for r in found if r.drawn != r.title_n]
    print(f"\n{len(found)} rows, {len(wrong)} drawn with another count", file=sys.stderr)
    return 1 if wrong else 0


if __name__ == "__main__":
    raise SystemExit(main())
