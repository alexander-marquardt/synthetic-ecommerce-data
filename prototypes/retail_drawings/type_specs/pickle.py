"""Pickles (gen#445, a spec by gen#351): Food & Drink > Food Cupboard > Sauces & Condiments.

One real pickle, so the type is registered through a spec. The class 9 plural decoys of
:mod:`decoy_rows` (a jar of pickled onions or preserved lemons) share the type and sit in the same
leaf; they are decoys, not spec rows. Every name here is invented.
"""

from __future__ import annotations

from type_registry import Row, TypeSpec, a, cw

SPEC = TypeSpec(
    key="pickle",
    department="Food & Drink",
    product_type="Pickle",
    derivable=False,
    owners=(("Olivar Grove", "third_party"),),
    rows=(
        Row(
            code="PKLJAR",
            title="Sweet Gherkin Pickle",
            brand="Olivar Grove",
            department="Food & Drink",
            path=("Food & Drink", "Food Cupboard", "Sauces & Condiments"),
            product_type="Pickle",
            price=2.3,
            shape="jar",
            description="Small gherkins pickled in a sweet spiced vinegar, in a glass jar.",
            colors=(cw("Green", "#6a8a3a", "solid", "#ffffff"),),
            attrs=(a("ingredient", "Ingredient", "Gherkins"),),
            sizes=(("340g", 2.3), ("680g", 3.7)),
            colorless=True,
        ),
    ),
)
