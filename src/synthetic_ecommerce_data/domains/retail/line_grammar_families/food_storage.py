"""The food storage family of the line grammar: food storage containers (gen#963 slice 2, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places. Food storage containers are a family of their own, not the storage
family's: a family's words are dealt over the brands that sell it (``line_grammar.Deal``), so a
kitchen brand new to the storage family would re-deal its words and rename main's baskets,
boxes and hooks.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Food Storage Container",)
#: The lead word of a model.
LEADS = (
    "Seal", "Lidded", "Keeper", "Crate", "Tub", "Vault", "Nestable", "Leftover", "Sealable",
    "Bento", "Brimful", "Stowaway", "Hoard", "Keepsafe", "Freezer", "Batchcook", "Batch", "Portion",
    "Stockpile", "Cupboard", "Fridge", "Saver", "Canister", "Thrifty", "Frugal", "Tiffin",
    "Stockup", "Pantryful", "Mealtime", "Snackbox",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
