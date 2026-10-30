"""The drink family of the line grammar: tea, coffee, juice and the soft drinks (gen#665,
gen#513).

The model shape is the pantry's (see :mod:`line_grammar_families.pantry`): a plain lead word and
an optional style word of the kind, then the product, e.g. "Brisk Whole Leaf Tea".
"""

from __future__ import annotations

KINDS = (
    "Tea", "Coffee", "Juice", "Soft Drink", "Milk", "Plant Milk", "Hot Chocolate", "Ginger Beer",
    "Root Beer",
)  # fmt: skip
#: The lead words of the scale build.
LEADS = (
    "Elevenses", "Teatime", "Poolside", "Winter", "Autumn", "Perky", "Breezy", "Vivid",
)  # fmt: skip
#: The lead words of the grocery build: disjoint from ``LEADS`` (gen#642).
GROCERY_LEADS = (
    "Brisk", "Lively", "Evening", "Crisp", "Zesty", "Refresh", "Vital", "Balanced",
    "Lunchtime", "Cheery", "Cheerful", "Fizz", "Bubbly", "Quench",
)  # fmt: skip
_FIZZY = (
    "Sparkling", "Lightly Sparkling", "Traditional", "Old Fashioned", "Extra Fizzy", "Craft Made",
    "Signature Recipe", "Refreshing", "Light", "Small Batch", "Botanical", "Hand Crafted",
)  # fmt: skip
#: Kind -> the style words a model of it may carry after its lead word: see the pantry's.
STYLES = {
    "Tea": (
        "Single Estate", "Extra Strong", "Afternoon", "Mellow Blend", "Signature Blend",
        "Long Leaf",
        "Whole Leaf", "Hand Picked", "High Grown", "Smooth Blend", "Rich Blend", "Everyday Blend",
    ),
    "Coffee": (
        "Single Origin", "Freshly Roasted", "Slow Roasted", "Small Batch", "Smooth Blend",
        "Rich Blend", "Barista Style", "Hand Roasted", "Roastery Style",
    ),
    "Juice": (
        "Cold Pressed", "Freshly Pressed", "Pure", "Breakfast", "Not From Concentrate",
        "Sun Ripened", "Just Squeezed", "Orchard Pressed",
    ),
    "Soft Drink": _FIZZY,
    "Milk": (
        "Filtered", "Farm Fresh", "Single Herd", "Grass Fed", "Family Farm", "Extra Fresh",
        "Everyday Fresh", "Pasture Raised",
    ),
    "Plant Milk": (
        "Creamy", "Extra Creamy", "Silky", "Toasted", "Everyday Blend", "Frothy", "Silky Smooth",
    ),
    "Hot Chocolate": (
        "Luxury", "Rich", "Velvety", "Indulgent", "Extra Rich", "Instant", "Belgian Style",
        "Cafe Style", "Creamy",
    ),
    "Ginger Beer": _FIZZY,
    "Root Beer": _FIZZY,
}  # fmt: skip
SUBS = tuple(dict.fromkeys(word for row in STYLES.values() for word in row))
NUMBERS = ()
#: The lead word alone is a model, the decoy-friendly short title.
BARE = True
#: The title leads with its brand in two of three draws (``line_grammar.brand_led``).
MIXED_BRAND = True
