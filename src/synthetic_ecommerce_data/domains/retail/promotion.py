"""The keyword ``promotion``, shopper label "Sale", that replaced the boolean ``offer`` (gen#189).

One source for the values, read by every producer of a was-price (:mod:`class_model`,
:mod:`footwear_rows`) and checked at every layer by ``tests/test_retail_promotion_189.py``:

- a product with a ``was_price`` carries :data:`ON_SALE`, whichever campaign it is in, so
  clicking "On sale" finds every reduced product;
- a product in the seeded campaign (:data:`CAMPAIGN`) also carries its name, so clicking the
  campaign finds only that campaign; the name never replaces :data:`ON_SALE`;
- a product with no ``was_price`` has no ``promotion`` key (there is no "no" value).

A new campaign is a new value in the same field and needs no remapping. Multi-buy is out of
scope: it becomes its own field later.
"""

from __future__ import annotations

import zlib

ON_SALE = "On sale"
#: The one seeded campaign, on a subset of the reduced products so the demo shows both values.
CAMPAIGN = "Christmas promotion"
#: One reduced product in this many is in the campaign, picked by a hash of its id.
CAMPAIGN_ONE_IN = 3


def values(product_id: str) -> list[str]:
    """The ``promotion`` values of a REDUCED product (one with a ``was_price``).

    A product with no ``was_price`` gets no ``promotion`` key, so callers do not ask."""
    in_campaign = zlib.crc32(product_id.encode()) % CAMPAIGN_ONE_IN == 0
    return [ON_SALE, CAMPAIGN] if in_campaign else [ON_SALE]
