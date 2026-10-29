"""Short-titled foods that are not olive oil, for the query "olive oil" (gen#686).

The failure, seen on public grocery sites: a search for ``olive oil`` returns pesto, tinned fish
and fries cooked in olive oil near the top. The title holds both words of the query and is as
short as an olive oil's, so a plain text match ranks it beside the oils. Each row is an ordinary
supermarket food with olive oil as an ingredient (class 10 of :mod:`decoy_rows`, like the red wine
vinegar of gen#500), filed, typed and drawn as what it is: a jar of pesto, a tin of sardines, a
bag of fries. None sits under Food Cupboard > Olive Oil.

With interpretation on, the query is exactly one category label (Olive Oil), and the whole-query
category policy of prism-retail-and-industrial (R&I#325) reads it as that node, so the oils lead.

The codes are a DY block of their own, Y6860 to Y6866 (product ids PLT-DY6860 to PLT-DY6866).
No brand is a real one.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.decoy_kind import Kind

_Q = "olive oil"

KINDS = {
    "olive_oil_crisps": Kind("Food & Drink", ("Food & Drink", "Biscuits & Snacks", "Crisps"),
                             "Crisps", "crisps_bag", "Copper Hill Preserves", 1.2, colorless=True),
}

_ROWS = (
    ("Y6860", "pasta_sauce", "Pesto with Olive Oil", "Basil pesto for pasta, made with olive oil.",
     "Green", 960, ("basil (35%)", "olive oil (30%)", "cheese", "pine nuts", "garlic", "salt")),
    ("Y6861", "frozen_veg", "Fries Cooked in Olive Oil", "Frozen chips for the oven, cooked in olive oil.",
     "Gold", 950, ("potatoes (95%)", "olive oil (5%)")),
    ("Y6862", "tinned", "Sardines in Olive Oil", "Whole sardines in a tin, packed in olive oil.",
     "Grey", 940, ("sardines (75%)", "olive oil (24%)", "salt")),
    ("Y6863", "tinned", "Tuna in Olive Oil", "Skipjack tuna chunks in a tin, in olive oil.",
     "Pink", 930, ("skipjack tuna (70%)", "olive oil (29%)", "salt")),
    ("Y6864", "pickle", "Sun-Dried Tomatoes in Olive Oil", "Sun-dried tomato pieces in a jar of olive oil.",
     "Red", 920, ("sun-dried tomatoes (60%)", "olive oil (35%)", "garlic", "oregano", "salt")),
    ("Y6865", "spread", "Olive Oil Spread", "A soft spread for bread, made with olive oil.",
     "Yellow", 910, ("vegetable oils", "olive oil (21%)", "water", "salt", "emulsifier (sunflower lecithin)")),
    ("Y6866", "olive_oil_crisps", "Crisps Cooked in Olive Oil", "Thin potato crisps, cooked in olive oil.",
     "Gold", 900, ("potatoes", "olive oil (30%)", "sea salt")),
)


def decoy_rows(d):
    return tuple(
        d(code, kind, title, desc, color, 10, _Q, sold, ingredients=ingredients)
        for code, kind, title, desc, color, sold, ingredients in _ROWS
    )
