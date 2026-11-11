"""Ordinary products whose text holds a common misspelling of their own product word (gen#944).

The retail-and-industrial demo shows the spelling suggestion: a search that finds the literal
word serves its hits, and offers "You may also consider searching for <common spelling>" only
when it has 3 or fewer Best results (the Engine's ``did_you_mean_head_hit_threshold``) and the
common spelling is at least 5 times more common. For the demo to show both sides, two words
here are on 3 products (the hits and the suggestion show) and two on 7 to 10 (hits only):

==========  ========  ===============  ===================================
Word        Products  Common spelling  The demo shows
==========  ========  ===============  ===================================
choocolate  3         chocolate        the hits and the suggestion
bannana     3         banana           the hits and the suggestion
leggins     8         leggings         hits only
cardigen    8         cardigan         hits only
==========  ========  ===============  ===================================

These are no decoys: each row is a real product of its word's own type and category (a milk
chocolate bar, a pack of five bananas, leggings, a cardigan), so every structured field tells the
truth. The misspelling is product text only: an invented brand (``Choocolate Factory``,
``Bannana Bros``, ``Leggins Lab``, ``Cardigen & Co``; :mod:`misspelled_brands`), a product
name in the title (``High-Rise Gym Leggins``), or, on two rows, the description alone. No
category node, product type or attribute holds one. ``tests/test_retail_misspelled_words_944.py``
counts each word's products and checks both rules.

``pliars`` (pliers), the issue's fifth word, is an industrial product and is not built here.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    misspelled_brands,  # noqa: F401 -- owners and house styles
)
from synthetic_ecommerce_data.domains.retail.decoy_kind import Kind

_UK = ("6", "8", "10", "12", "14", "16")

#: misspelling -> (the common spelling, how many products carry it).
WORDS = {
    "choocolate": ("chocolate", 3),
    "bannana": ("banana", 3),
    "leggins": ("leggings", 8),
    "cardigen": ("cardigan", 8),
}

#: The true types, each the common word's own type in its own category.
KINDS = {
    "ms944_milk_bar": Kind("Food & Drink", ("Food & Drink", "Chocolate & Sweets", "Chocolate", "Chocolate Bars", "Milk Chocolate Bars"),
                           "Chocolate Bar", "bar", "Pantry Mill", 2.2, colorless=True),
    "ms944_bananas": Kind("Food & Drink", ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Bananas"), "Fresh Fruit",
                          "produce_pile", "Goldfield Farms", 1.3, params=(("fruit", "banana"), ("pack", "loose")), colorless=True,
                          units_per_pack=5),
    "ms944_leggings": Kind("Clothing", ("Womens", "Leggings"), "Leggings", "leggings", "Larkmoor", 18.0, sizes=_UK,
                           size_range="regular", params=(("length", "full"), ("rise", "high"))),
    "ms944_cardigan": Kind("Clothing", ("Womens", "Knitwear", "Cardigans"), "Cardigan", "cardigan", "Larkmoor", 34.0, sizes=_UK,
                           size_range="regular", params=(("neckline", "crew"), ("sleeve", "long")),
                           extra=(("sleeve_length", "Sleeve length", "Long"),)),
}  # fmt: skip

_CF, _BB, _LS, _CC = misspelled_brands.BRANDS

#: Rows of (number, kind, title, description, color, the misspelling, brand or None for the kind's).
_ROWS = (
    # choocolate: 3 products, one in each place
    (9441, "ms944_milk_bar", "Choocolate Factory Milk Chocolate Bar", "Smooth milk chocolate in a bar of twelve squares.", "Brown", "choocolate", _CF),
    (9442, "ms944_milk_bar", "Choocolate Crunch Milk Bar", "Milk chocolate with crisped rice, in a bar of twelve squares.", "Brown", "choocolate", None),
    (9443, "ms944_milk_bar", "Hazelnut Milk Chocolate Bar", "Whole roasted hazelnuts in creamy milk choocolate.", "Brown", "choocolate", None),
    # bannana: 3 products, two by the brand and one by name
    (9444, "ms944_bananas", "Bannana Bros Fairtrade Bananas", "Five ripe Fairtrade bananas, ready to eat.", "Yellow", "bannana", _BB),
    (9445, "ms944_bananas", "Bannana Bros Baby Bananas", "Five small, sweet bananas for a lunch box.", "Yellow", "bannana", _BB),
    (9446, "ms944_bananas", "Big Bannana Bunch", "Five large bananas, ripened in the store.", "Yellow", "bannana", None),
    # leggins: 8 products, three by the brand, four by name, one in the description
    (9447, "ms944_leggings", "Leggins Lab High-Rise Leggings", "Full length leggings with a high, wide waistband.", "Black", "leggins", _LS),
    (9448, "ms944_leggings", "Leggins Lab Yoga Leggings", "Soft stretch leggings for yoga and the studio.", "Navy", "leggins", _LS),
    (9449, "ms944_leggings", "Leggins Lab Ribbed Leggings", "Ribbed jersey leggings with a high waist.", "Grey", "leggins", _LS),
    (9450, "ms944_leggings", "High-Rise Gym Leggins", "Squat-proof leggings with a high waistband.", "Black", "leggins", None),
    (9451, "ms944_leggings", "Seamless Sports Leggins", "Seamless knit leggings that move with you.", "Blue", "leggins", None),
    (9452, "ms944_leggings", "Everyday Stretch Leggins", "Cotton stretch leggings for every day.", "Grey", "leggins", None),
    (9453, "ms944_leggings", "Soft Lounge Leggins", "Brushed jersey leggings for the sofa.", "Pink", "leggins", None),
    (9454, "ms944_leggings", "Jersey Waistband Leggings", "Soft stretch jersey leggins with a wide waistband.", "Black", "leggins", None),
    # cardigen: 8 products, four by the brand and four by name
    (9455, "ms944_cardigan", "Cardigen & Co Ribbed Cardigan", "A ribbed knit cardigan with a crew neck.", "Cream", "cardigen", _CC),
    (9456, "ms944_cardigan", "Cardigen & Co Cable Cardigan", "A cable knit cardigan with four buttons.", "Navy", "cardigen", _CC),
    (9457, "ms944_cardigan", "Cardigen & Co Soft Cardigan", "A soft knit cardigan to layer over a dress.", "Grey", "cardigen", _CC),
    (9458, "ms944_cardigan", "Cardigen & Co Fine Knit Cardigan", "A fine knit cardigan for the office.", "Black", "cardigen", _CC),
    (9459, "ms944_cardigan", "Chunky Knit Cardigen", "A chunky knit cardigan with a crew neck.", "Cream", "cardigen", None),
    (9460, "ms944_cardigan", "Button Front Cardigen", "A button front cardigan in a soft knit.", "Pink", "cardigen", None),
    (9461, "ms944_cardigan", "Longline Cardigen", "A long knit cardigan that reaches the hip.", "Green", "cardigen", None),
    (9462, "ms944_cardigan", "Everyday Cardigen", "A light knit cardigan for every day.", "Red", "cardigen", None),
)  # fmt: skip


def word_rows(d):
    """The rows, made with the class-8 table's row maker. No row is a decoy, so none names a
    query, a noun or a fixing policy, and the decoy contract (:mod:`decoy_contract`) skips them."""
    rows = []
    for n, kind, title, desc, color, _word, brand in _ROWS:
        own = {"brand": brand} if brand else {}
        rows.append(d(n, kind, title, desc, color, "", "", "", decoy=False, **own))
    return tuple(rows)


def product_ids() -> frozenset[str]:
    """The product ids of the rows (``PLT-DY<number>``)."""
    return frozenset(f"PLT-DY{n:02d}" for n, *_ in _ROWS)
