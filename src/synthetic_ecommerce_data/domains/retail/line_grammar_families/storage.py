"""The storage family of the line grammar: baskets, boxes, hangers and hooks (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Storage Basket", "Storage Boxes", "Storage Box", "Garment Bags", "Hanger", "Clothes Hangers",
    "Wash Bags", "Nursery Storage", "Laundry Basket", "Drying Racks", "Clothes Airer",
    "Wall Hooks", "Door Stop", "Car Boot Organiser", "Cup Holder", "Nappy Caddy", "Money Box",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Tidy", "Stow", "Neat", "Order", "Stack", "Tuck", "Sort", "Keep", "Fold", "Hold", "Haul",
    "Carry", "Shelve", "Clear", "Space", "Nook", "Cache", "Locker", "Handy", "Utility",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
