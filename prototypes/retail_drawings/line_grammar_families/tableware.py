"""The tableware family of the line grammar: plates, mugs, cups and dinner sets (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Plate", "Bowl", "Mug", "Cup", "Cup Set", "Cutlery", "Cutlery Set", "Dinner Set", "Glassware",
    "Tumbler", "Travel Cup", "Measuring Cup", "Paper Cup", "Party Cup", "Sippy Cup",
    "Baby Beakers", "Casserole Dish", "Storage Jar", "Lunch Box",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Supper", "Feast", "Brunch", "Banquet", "Serve", "Dine", "Savour", "Relish", "Gather", "Toast",
    "Buffet", "Picnic", "Dessert", "Starter", "Platter", "Sip", "Taste", "Entertain", "Everyday",
    "Spread",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
