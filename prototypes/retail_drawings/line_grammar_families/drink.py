"""The drink family of the line grammar: tea, coffee, juice and the soft drinks (gen#665,
gen#513).

The model shape is the pantry's (see :mod:`line_grammar_families.pantry`): a plain lead word, an
optional sub-model and a number, then the product, e.g. "Brisk Batch 3 Green Tea".
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
SUBS = ("Batch", "Special", "Reserve", "Edition", "Series", "Deluxe")
NUMBERS = tuple(range(2, 10))
#: The lead word alone is a model, the decoy-friendly short title.
BARE = True
#: The title leads with its brand in two of three draws (``line_grammar.brand_led``).
MIXED_BRAND = True
