"""Brooch (gen#1113): a brooch on a pin with a safety catch, sold by metal.

It sits under ``Jewellery`` as ``Brooches``. Each SKU is a metal (the color is the metal, as for
every jewelry row since gen#207). ``motif`` is drawn by :mod:`kit_jewellery` (a flower, a bee, a
bow, a leaf, a pearl cluster, or a stone in an oval setting); a stone brooch states its ``stone``
and its drawing takes it. The rows are derivable, and a derived style keeps its template's motif
and stone (``scale_text.JEWELLERY_KEYS``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.accessory_rows import ARow
from synthetic_ecommerce_data.domains.retail.audience import WOMENS
from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    ALL_METALS,
    CALDERBY,
    CLOTHING,
    GOLD,
    HARBOUR,
    LARKMOOR,
    METALS,
    OWNED,
    SILVER,
    SKERRY,
    TIDEWELL,
    WRENFIELD,
    a,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

PATH, PTYPE = ("Womens", "Jewellery", "Brooches"), "Brooch"
#: An oval stone brooch: its stone, its price and its brand.
STONES = (
    ("Clear Crystal", 20.0, TIDEWELL), ("Sapphire", 28.0, WRENFIELD), ("Emerald", 28.0, CALDERBY),
    ("Amethyst", 26.0, LARKMOOR), ("Ruby", 28.0, SKERRY),
)  # fmt: skip


def _row(code, title, brand, price, desc, motif, kind, colors=ALL_METALS, stone=None):
    attrs = (
        a("brooch_style", "Brooch style", kind), *(a("metal", "Metal", METALS[c[0]]) for c in colors),
        *((a("stone", "Stone", stone),) if stone else ()),
        a("fastening", "Fastening", "Pin with Safety Catch"), a("audience", "Audience", WOMENS),
    )  # fmt: skip
    params = (("motif", motif), *((("stone", stone.lower()),) if motif == "stone" else ()))
    return ARow(code, title, brand, CLOTHING, PATH, PTYPE, price, "brooch", desc, colors, attrs,
                params=params, metals=tuple(METALS[c[0]] for c in colors))  # fmt: skip


SPEC = TypeSpec(
    key="brooch",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#1113)",
    rows=(
        _row("BRHFLW", "Flower Brooch", WRENFIELD, 16.0,
             "A flower brooch with six rounded lobes round a domed center, on a pin with a safety catch.", "flower", "Flower"),
        _row("BRHBEE", "Bee Brooch", LARKMOOR, 15.0,
             "A bee brooch with a striped body and open wings, on a pin with a safety catch.", "bee", "Bee"),
        _row("BRHBOW", "Bow Brooch", HARBOUR, 14.0,
             "A polished bow brooch with two loops and two tails, on a pin with a safety catch.", "bow", "Bow"),
        _row("BRHLEF", "Leaf Brooch", CALDERBY, 15.0,
             "A long leaf brooch with fine veins, worn on a coat lapel, on a pin with a safety catch.", "leaf", "Leaf"),
        _row("BRHPRL", "Pearl Cluster Brooch", SKERRY, 22.0,
             "Seven freshwater pearls in a round cluster on a metal base, on a pin with a safety catch.", "pearl", "Pearl Cluster",
             stone="Pearl"),
        *(_row(f"BRHS{i:02d}", f"{stone} Oval Brooch", brand, price,
               f"One large faceted {stone.lower()} in an oval setting with a beaded edge, on a pin with a safety catch.",
               "stone", "Stone", stone=stone)
          for i, (stone, price, brand) in enumerate(STONES, 1)),
    ),
    decoys=(
        Decoy(5, "gold brooch", "color",
              _row("BRHDGB", "Bee Brooch with Gold Tone Wings", SKERRY, 15.0,
                   "A sterling silver bee brooch whose wings carry a thin gold tone wash: the brooch itself is silver.", "bee", "Bee",
                   colors=(SILVER,))),
        Decoy(4, "pearl earrings", "category",
              _row("BRHDPE", "Pearl Brooch to Match Pearl Earrings", HARBOUR, 22.0,
                   "A pearl cluster brooch made to match a pair of pearl earrings: a brooch on a pin, not earrings.", "pearl", "Pearl Cluster",
                   colors=(GOLD,), stone="Pearl")),
    ),
)  # fmt: skip
