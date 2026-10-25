"""The alcohol family of the line grammar: wine, beer, cider and the spirits (gen#665, gen#513).

The model shape is the pantry's (see :mod:`line_grammar_families.pantry`): a plain lead word, an
optional sub-model and a number, then the product, e.g. "Cellar Reserve 2 Merlot".
"""

from __future__ import annotations

KINDS = (
    "Wine", "Beer", "Cider", "Perry", "Mead", "Gin", "Vodka", "Rum", "Tequila", "Whisky",
    "Champagne", "Fortified Wine",
)  # fmt: skip
#: The lead words of the scale build.
LEADS = (
    "Sovereign", "Merchant", "Vintner", "Landlord", "Hogshead", "Founders", "Taproom", "Regal",
)  # fmt: skip
#: The lead words of the grocery build: disjoint from ``LEADS`` (gen#642).
GROCERY_LEADS = (
    "Cellar", "Grand", "Master", "Imperial", "Royal", "Crown", "Tavern", "Fireside", "Gantry",
    "Cask",
)  # fmt: skip
SUBS = ("Reserve", "Special", "Edition", "Batch", "Series", "Deluxe")
NUMBERS = tuple(range(2, 10))
#: The lead word alone is a model, the decoy-friendly short title.
BARE = True
#: The title leads with its brand in two of three draws (``line_grammar.brand_led``).
MIXED_BRAND = True
