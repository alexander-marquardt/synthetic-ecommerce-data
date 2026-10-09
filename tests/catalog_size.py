"""The default build's size, for the tests that pin it.

Two parts, both summed per type, so that adding a type edits nothing here:

* the **breadth** part is read from the rows. A breadth row builds exactly one
  line and :func:`.breadth.sku_count` SKUs.
* the **modelled** (depth) part is measured: each type's line and SKU counts
  are read from ``golden-catalog/stats.json`` by ``type_facts.default_size``
  (#103). ``test_type_facts`` holds each type's figures to the committed
  catalog, so a change that moves one type's count names it.
"""

from __future__ import annotations

import type_facts
from synthetic_ecommerce_data.domains.industrial import breadth

_DEPTH = type_facts.default_size()
DEPTH_LINES = sum(lines for lines, _ in _DEPTH.values())
DEPTH_SKUS = sum(skus for _, skus in _DEPTH.values())

BREADTH_LINES = len(breadth.rows())
BREADTH_SKUS = sum(breadth.sku_count(row) for row in breadth.rows())

LINES = DEPTH_LINES + BREADTH_LINES
SKUS = DEPTH_SKUS + BREADTH_SKUS
