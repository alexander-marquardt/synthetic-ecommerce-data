"""A retail attribute that repeats the product type is not published (gen#497).

The authored rows keep the keys they were written with: the drawing params, the scaler's value
pools and ``FROZEN_KEYS`` read them. What a shopper and a downstream catalogue see is the
published document, so :func:`clean` (called by ``export._product_attributes``) drops, from
each entry list, an entry a retailer would not print because the title and the category
already say it: a key in :data:`RESTATING` whose value is the product type itself.

- ``storage_type`` "Storage Box" on a Storage Box;
- ``tracker_type`` "Fitness band" on a Fitness Band;
- a ``type`` equal to the type.

A real sub-kind of the same key (a nursery storage's Basket, Cube or Hanging Organizer) stays.

The rest of #497's retail half (the same-concept merges, the ``style`` fold, the value fixes)
is not here: it renames keys that about thirty test modules read by their authored name, so it
goes in later slices.
"""

from __future__ import annotations

from typing import Any

#: Keys the review found carrying the product type as their value (#497, "Remove").
RESTATING = frozenset({"storage_type", "tracker_type", "type"})


def restates_the_type(entry: dict[str, Any], product_type: str) -> bool:
    """Whether ``entry`` says only what the product type already says."""
    return False


def clean(entries: list[dict[str, Any]], product_type: str) -> list[dict[str, Any]]:
    """``entries`` as published."""
    return entries
