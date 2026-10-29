"""The soft furnishings family of the line grammar: curtains, blinds, rugs, mats (gen#204, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Curtains", "Blind", "Rug", "Bath Mat", "Shower Curtain")
#: The lead word of a model.
LEADS = (
    "Drape", "Pleat", "Weave", "Loom", "Tuft", "Pile", "Tassel", "Shade", "Veil", "Panel",
    "Fringe", "Hem", "Stitch", "Braid", "Thread", "Woven", "Knot", "Sheer", "Lattice", "Hanging",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
