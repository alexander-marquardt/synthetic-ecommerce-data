"""The ingredient or claim a food title may end on, read from its own recipe (gen#729).

A food model is a lead word and at most one style word (:mod:`line_grammar`), so past those words
a brand's titles stay distinct by what the product is made of, as a shelf label says it: "Finest
Greek Style Yogurt with Live Cultures", "Prime Oat Drink with No Added Sugar".

Every word here is true of the product and of all its variants, so :func:`true_words` reads each
variant's label list. An ingredient phrase needs its ingredient in every list; a claim needs its
refused words in none; and a word a flavor or the title already says stays out, because a shared
title never names a value of the variant axis. A family with no label list (fresh produce, wine,
the spirits) has nothing to read, so it gains no word.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from synthetic_ecommerce_data.domains.retail.grocery_ingredients import facet_value

#: The bakes, sweets and spreads, whose labels sell on what goes into them.
_SWEET = frozenset({
    "Biscuit", "Biscuits", "Cake", "Cereal Bar", "Chocolate Bar", "Chocolate Box", "Cookies",
    "Doughnut", "Festive Bake", "Free From Snack", "Hot Chocolate", "Ice Cream", "Jam",
    "Snack Bar", "Spread", "Sweets",
})  # fmt: skip
#: The savory and everyday packed foods.
_SAVORY = frozenset({
    "Baby Food", "Bread", "Cereal", "Chutney", "Crisps", "Nuts & Popcorn", "Pasta", "Pickle",
    "Pizza", "Porridge", "Ready Meal", "Rice & Grains", "Sauce", "Seasoning", "Tinned Food",
    "World Food", "Yogurt",
})  # fmt: skip
#: The drinks with a label list that are not alcohol.
_DRINK = frozenset({"Coffee", "Juice", "Plant Milk", "Soft Drink", "Tea"})
_PACKED = _SWEET | _SAVORY | _DRINK

#: (phrase, the label values that back it, the kinds a shelf label says it on).
INGREDIENTS: tuple[tuple[str, frozenset[str], frozenset[str]], ...] = (
    ("Real Butter", frozenset({"butter"}), _SWEET | _SAVORY),
    ("Real Sugar", frozenset({"sugar"}), _SWEET),
    ("Real Vanilla", frozenset({"vanilla extract"}), _SWEET),
    ("Real Cream", frozenset({"cream", "double cream"}), _SWEET),
    ("Real Egg", frozenset({"egg", "pasteurised egg"}), _SWEET),
    ("Real Tomato", frozenset({"tomato", "tomatoe"}), _SAVORY),
    ("Real Garlic", frozenset({"garlic"}), _SAVORY),
    ("Real Ginger", frozenset({"ginger"}), _SAVORY),
    ("Cocoa Butter", frozenset({"cocoa butter"}), _SWEET),
    ("Rolled Oats", frozenset({"rolled oat"}), _SWEET | _SAVORY),
    ("Sea Salt", frozenset({"sea salt"}), _PACKED),
    ("Black Pepper", frozenset({"black pepper"}), _SAVORY),
    ("Rapeseed Oil", frozenset({"rapeseed oil"}), _SAVORY),
    ("Sunflower Oil", frozenset({"sunflower oil"}), _SAVORY),
    ("Whole Milk", frozenset({"whole milk"}), frozenset({"Yogurt"})),
    ("Live Cultures", frozenset({"live yoghurt culture"}), frozenset({"Yogurt"})),
    ("Natural Flavoring", frozenset({"natural flavoring"}), _SWEET | _DRINK),
    ("Natural Colors", frozenset({"color (anthocyanins)", "color (carotenes)"}), _SWEET),
    ("Added Vitamin C", frozenset({"vitamin c"}), _DRINK | {"Baby Food"}),
    ("Added Vitamin D", frozenset({"vitamin d3", "vitamin d"}), _DRINK | {"Milk", "Baby Food"}),
    ("Added Vitamin A", frozenset({"vitamin a"}), frozenset({"Milk"})),
    ("Added Calcium", frozenset({"calcium", "calcium carbonate"}), _DRINK | {"Milk"}),
    ("Added Riboflavin", frozenset({"riboflavin"}), frozenset({"Milk"})),
    ("Added Vitamins", frozenset({"vitamins (b12, d2)", "vitamins (niacin, b6, folic acid)"}),
     _DRINK | {"Cereal"}),
    ("Added Iron", frozenset({"iron"}), frozenset({"Baby Food", "Pasta"})),
)  # fmt: skip

_NOT_NATURAL = (
    "preservative|color|sweetener|stabiliser|antioxidant|acidity regulator|emulsifier|"
    "(?<!natural )flavoring"
)
#: (phrase, the pattern no label value of any variant may match, the kinds it is said on).
CLAIMS: tuple[tuple[str, re.Pattern[str], frozenset[str]], ...] = (
    ("No Added Sugar", re.compile(r"sugar|syrup|honey|glucose|molasses|treacle|caramel"),
     _SAVORY - {"Pasta", "Rice & Grains", "Seasoning"} | {"Juice", "Plant Milk", "Soft Drink"}),
    ("No Palm Oil", re.compile(r"palm"),
     _SWEET - {"Festive Bake", "Jam"} | {"Crisps", "Pizza", "Ready Meal"}),
    ("No Preservatives", re.compile(r"preservative"), _PACKED | {"Milk"}),
    ("No Artificial Colors", re.compile(r"color"), _PACKED),
    ("No Artificial Flavors", re.compile(r"(?<!natural )flavoring"), _PACKED),
    ("No Artificial Ingredients", re.compile(_NOT_NATURAL), _PACKED),
)  # fmt: skip


def _stems(text: str) -> set[str]:
    """``text``'s words, a plural and its singular as one ("Oats" and "Oat")."""
    return {w.casefold().rstrip("es") for w in re.findall(r"[\w']+", text)}


def _names(phrase: str) -> set[str]:
    """The words of ``phrase`` a title could say already: "Real Butter" says butter."""
    return _stems(phrase) - _stems("Real Added")


def true_words(kind: str, title: str, axis: Iterable[str], lists: Sequence[list[str]]) -> list[str]:
    """The endings true of a product of ``kind`` whose variants carry the label ``lists``, for a
    ``title`` that has none yet and the variant values ``axis``: "with Real Butter". A title with
    a "with" of its own ("Chopped Tomatoes with Basil") takes no second one."""
    if " with " in title or not lists or not all(lists):
        return []
    labels = [{facet_value(item) for item in items} for items in lists]
    said = _stems(title).union(*(_stems(value) for value in axis))
    found = [
        phrase
        for phrase, backing, kinds in INGREDIENTS
        if kind in kinds and all(backing & label for label in labels) and not _names(phrase) & said
    ]
    found += [
        phrase
        for phrase, refused, kinds in CLAIMS
        if kind in kinds and not any(refused.search(v) for label in labels for v in label)
    ]
    return [f"with {phrase}" for phrase in found]
