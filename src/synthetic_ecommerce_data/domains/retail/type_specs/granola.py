"""Granola (gen#964, slice 1): baked oat and grain clusters by the bag's weight.

**Food & Drink > Breakfast > Granola** holds bags whose title names the texture, the grain and
the flavor; each SKU is a bag's net weight. The bag is drawn (``bag``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pantry_rows import (
    CRUNCHWORTH,
    DEPARTMENT,
    FOREST,
    GOLDFIELD,
    HEARTH,
    NAVY,
    OWNERS,
    PANTRY_MILL,
    PLUM,
    RUST,
    SAND,
    SKY,
    TEAL,
    decoy,
    grams,
    row,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

PATH = (DEPARTMENT, "Breakfast", "Granola")


def _attrs(texture: str, grain: str, flavor: str) -> tuple[tuple, ...]:
    return (a("texture", "Texture", texture), a("grain", "Grain", grain),
            a("flavor", "Flavor", flavor))  # fmt: skip


def _row(code: str, texture: str, grain: str, flavor: str, brand: str, desc: str,
         sizes: tuple[tuple[str, float], ...], color: tuple) -> object:  # fmt: skip
    return row(code, f"{texture} {grain} Granola with {flavor}", brand, PATH, "Granola", "bag",
               desc, _attrs(texture, grain, flavor), sizes, "net_weight_g", color, "Granola")  # fmt: skip


_SMALL = grams((0.4, 2.5), (0.5, 3.0), (0.75, 4.2))
_LARGE = grams((0.5, 3.2), (0.75, 4.5), (1.0, 5.6))

ROWS = (
    _row("GRNCOH", "Crunchy", "Oat", "Honey & Almond", CRUNCHWORTH,
         "Baked slowly until golden, for a bowl with cold milk or a spoonful over yogurt.", _LARGE, SAND),
    _row("GRNCLF", "Clustered", "Oat", "Fruit & Nut", CRUNCHWORTH,
         "Wholegrain granola baked in small batches, high in fiber.", _LARGE, RUST),
    _row("GRNTSM", "Toasted", "Spelt", "Maple & Pecan", PANTRY_MILL,
         "Granola baked with a little rapeseed oil, a source of fiber, in a resealable bag.", _SMALL, PLUM),
    _row("GRNCBA", "Crunchy", "Buckwheat", "Apple & Cinnamon", PANTRY_MILL,
         "Wholegrain granola for breakfast or a snack, baked until crisp.", _SMALL, FOREST),
    _row("GRNCSC", "Clustered", "Spelt", "Coconut & Cashew", HEARTH,
         "Granola baked in small batches in our own bakery, in a resealable bag.", _LARGE, TEAL),
    _row("GRNTOT", "Toasted", "Oat", "Tropical Fruit", HEARTH,
         "Wholegrain granola for a bowl with milk, with no artificial colors or flavorings.", _SMALL, SKY),
    _row("GRNCOM", "Crunchy", "Oat", "Mixed Seed", GOLDFIELD,
         "Wholegrain granola baked slowly, lower in sugar than our classic recipe.", _SMALL, NAVY),
    _row("GRNCBH", "Clustered", "Buckwheat", "Honey & Almond", GOLDFIELD,
         "Granola baked in small batches from wholegrain, high in fiber, in a resealable bag.", _LARGE, SAND),
    _row("GRNTSA", "Toasted", "Spelt", "Apple & Cinnamon", CRUNCHWORTH,
         "Slow-baked granola for milk, yogurt or a fruit bowl.", _SMALL, RUST),
    _row("GRNCOF", "Crunchy", "Oat", "Fruit & Nut", PANTRY_MILL,
         "Wholegrain granola baked until crisp, a source of fiber.", _LARGE, FOREST),
)  # fmt: skip

SPEC = TypeSpec(
    key="granola",
    department=DEPARTMENT,
    product_type="Granola",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(6, "peanut granola", "generic", decoy(ROWS[1], "GRNPNT", "Peanut Row Clustered Oat Granola with Fruit & Nut",
              "From the Peanut Row range: wholegrain granola made without peanuts.")),
        Decoy(6, "protein granola", "generic", decoy(ROWS[4], "GRNPRO", "Protein Hill Clustered Spelt Granola with Coconut & Cashew",
              "From the Protein Hill range: granola baked in small batches.")),
    ),
)  # fmt: skip
