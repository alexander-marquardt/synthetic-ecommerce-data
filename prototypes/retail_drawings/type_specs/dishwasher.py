"""Dishwashers (gen#334): full-size, slimline, integrated and table-top, six models each.

Drawn by :func:`kit_large_appliances.dishwasher`. A model's place settings, width, energy rating
and noise level are structured; its finish is the SKU's color. The word "dishwasher" is also in
the description of mugs, lunch boxes and cutlery ("Dishwasher safe"), and in the title of
dishwasher tablets, salt and rinse aid (``feature_decoys/large_appliances.py``): a category
policy routes the query to Home > Large Appliances > Dishwashers. Every brand is invented.
Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

import large_appliance_rows as lar
from breadth_rows import Row
from type_registry import TypeSpec, a

#: The dishwashers: (place settings, width cm, price, noise dB)
_DISH_KINDS = (
    ("DWF", "full", "Full-Size Dishwasher", "Full-Size", "A freestanding dishwasher",
     ((12, 60, 329, 49), (13, 60, 379, 46), (14, 60, 429, 44), (14, 60, 489, 42), (15, 60, 549, 40), (16, 60, 649, 38))),
    ("DWS", "slim", "Slimline Dishwasher", "Slimline", "A slimline dishwasher for a narrow gap",
     ((9, 45, 299, 49), (10, 45, 349, 47), (10, 45, 399, 45), (10, 45, 449, 44), (11, 45, 499, 42), (11, 45, 579, 40))),
    ("DWI", "integrated", "Integrated Dishwasher", "Integrated", "A dishwasher that hides behind a cabinet door",
     ((12, 60, 399, 46), (13, 60, 449, 44), (14, 60, 499, 43), (14, 60, 549, 42), (15, 60, 629, 40), (15, 60, 699, 38))),
    ("DWT", "tabletop", "Table-Top Dishwasher", "Table-Top", "A small dishwasher for a worktop",
     ((4, 55, 189, 52), (4, 55, 209, 51), (5, 55, 229, 50), (6, 55, 249, 49), (6, 55, 279, 48), (6, 55, 299, 47))),
)  # fmt: skip


def dishwasher_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, title, kind_name, lead, models in _DISH_KINDS:
        def make(i, models=models, lead=lead, kind_name=kind_name, pre=pre):
            places, width, price, noise = models[i]
            rating = lar.RATINGS[(i + len(pre)) % 5]
            desc = (f"{lead}. It holds {places} place settings, is {width} cm wide and runs at "
                    f"{noise} dB, energy rating {rating}.")
            attrs = (a("appliance_type", "Type", kind_name), lar.count("place_settings", "Place settings", places),
                     lar.cm(width), a("energy_rating", "Energy rating", rating), a("noise_db", "Noise level (dB)", str(noise)))
            return float(price), desc, lar.PALETTES[i % 3], attrs
        out += lar.kind_rows(pre, 6, lar.DISHWASHERS, "Dishwasher", "dishwasher", (("kind", shape),), title, make)
    return tuple(out)


SPEC = TypeSpec(
    key="dishwasher",
    department="Home",
    product_type="Dishwasher",
    owners=lar.OWNERS,
    rows=dishwasher_rows(),
)
