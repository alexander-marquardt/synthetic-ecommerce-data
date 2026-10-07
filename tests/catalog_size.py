"""The default build's size, for the tests that pin it.

Two parts, kept apart so that adding a breadth type edits nothing here:

* the **breadth** part is read from the rows. A breadth row builds exactly one
  line and :func:`.breadth.sku_count` SKUs, so a breadth type's pull request
  changes no literal in this file, and two of them cannot conflict on one.
* the **modelled** (depth) part is measured. A modelled type's line and SKU
  counts are only known by building it, so a pull request that adds or
  changes a modelled type restates these two figures by direct count of the
  documents whose ``spec_quality`` is not the breadth one. Two modelled-type
  pull requests do conflict here, which is one reason they land one at a time
  (``docs/adding-a-type.md``).
"""

from __future__ import annotations

from pathlib import Path

from synthetic_industrial_products.catalog import breadth

DEPTH_LINES = 5766
DEPTH_SKUS = 10565

SLICES = Path(__file__).parent / "data" / "golden_slices"


def depth(slices: Path = SLICES) -> tuple[int, int]:
    return DEPTH_LINES, DEPTH_SKUS

BREADTH_LINES = len(breadth.rows())
BREADTH_SKUS = sum(breadth.sku_count(row) for row in breadth.rows())

LINES = DEPTH_LINES + BREADTH_LINES
SKUS = DEPTH_SKUS + BREADTH_SKUS
