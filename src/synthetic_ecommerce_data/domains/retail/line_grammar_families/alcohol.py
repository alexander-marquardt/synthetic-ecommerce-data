"""The alcohol family of the line grammar: wine, beer, cider and the spirits (gen#665, gen#513).

The model shape is the pantry's (see :mod:`line_grammar_families.pantry`): a plain lead word and
an optional style word of the kind, then the product, e.g. "Cellar Oak Aged Merlot Red Wine".
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
_ORCHARD = (
    "Farm Pressed", "Orchard Pressed", "Cloudy", "Craft Pressed", "Slow Fermented", "Traditional",
    "Small Batch", "Hand Crafted", "Barrel Aged", "Naturally Fermented",
)  # fmt: skip
#: Kind -> the style words a model of it may carry after its lead word: see the pantry's.
STYLES = {
    "Wine": (
        "Single Vineyard", "Oak Aged", "Barrel Aged", "Hillside", "Late Picked", "Hand Harvested",
        "Vineyard Selection", "Cool Climate", "Small Lot", "Sun Drenched",
    ),
    "Beer": (
        "Craft Brewed", "Small Batch", "Slow Brewed", "Bottle Conditioned", "Dry Hopped",
        "Double Hopped", "Brewery Fresh", "Hand Crafted", "Traditional", "Unfiltered",
        "Cold Filtered",
    ),
    "Cider": _ORCHARD,
    "Perry": _ORCHARD,
    "Mead": ("Slow Fermented", "Small Batch", "Hand Crafted", "Barrel Aged", "Aged", "Oak Aged"),
    "Gin": (
        "Small Batch", "Hand Crafted", "Copper Distilled", "Botanical", "Signature Blend",
        "Pot Distilled",
        "Slow Distilled", "Hand Bottled",
    ),
    "Vodka": (
        "Small Batch", "Charcoal Filtered", "Hand Crafted", "Ultra Smooth", "Ice Filtered",
        "Cold Filtered", "Silky Smooth", "Copper Still",
    ),
    "Rum": (
        "Small Batch", "Aged", "Barrel Aged", "Oak Aged", "Pot Distilled", "Hand Crafted",
        "Caribbean Style", "Slow Distilled",
    ),
    "Tequila": (
        "Small Batch", "Hand Crafted", "Oak Aged", "Barrel Rested", "Slow Cooked", "Pot Distilled",
        "Traditional", "Hand Harvested",
    ),
    "Whisky": (
        "Small Batch", "Oak Aged", "Barrel Aged", "Pot Distilled", "Peated", "Mellow",
        "Hand Crafted", "Slow Distilled", "Copper Distilled",
    ),
    "Champagne": (
        "Vintage", "Single Vineyard", "Grower", "Prestige Cuvee", "Hillside", "Hand Harvested",
        "Bottle Aged", "Small Lot",
    ),
    "Fortified Wine": (
        "Aged", "Barrel Aged", "Oak Aged", "Solera Style", "Small Lot", "Slow Matured",
        "Traditional", "Bodega Style",
    ),
}  # fmt: skip
SUBS = tuple(dict.fromkeys(word for row in STYLES.values() for word in row))
NUMBERS = ()
#: The lead word alone is a model, the decoy-friendly short title.
BARE = True
#: The title leads with its brand in two of three draws (``line_grammar.brand_led``).
MIXED_BRAND = True
