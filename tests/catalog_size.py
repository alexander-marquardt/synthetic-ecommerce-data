"""The default build's size, for the tests that pin it.

Two parts, both summed per type, so that adding a type edits nothing here:

* the **breadth** part is read from the rows. A breadth row builds exactly one
  line and :func:`.breadth.sku_count` SKUs.
* the **modelled** (depth) part is measured. A modelled type's line and SKU
  counts are only known by building it, so each type states its own:
  ``default_lines`` and ``default_skus`` on its ``TypeSpec``, or its row of
  ``type_facts.SHARED_SIZE`` while it is declared in the shared tables
  (#61). ``test_type_facts`` holds each type's figures to the committed
  catalog, so a change that moves one type's count names it.
"""

from __future__ import annotations

import type_facts
from synthetic_ecommerce_data.catalog import breadth

_DEPTH = type_facts.default_size()
DEPTH_LINES = sum(lines for lines, _ in _DEPTH.values())
DEPTH_SKUS = sum(skus for _, skus in _DEPTH.values())

BREADTH_LINES = len(breadth.rows())
BREADTH_SKUS = sum(breadth.sku_count(row) for row in breadth.rows())

LINES = DEPTH_LINES + BREADTH_LINES
SKUS = DEPTH_SKUS + BREADTH_SKUS
