"""The bra family of the line grammar: bras (gen#663, gen#513).

A model is a plain word of the family, an optional sub-model and a number or a code, then the
descriptors and the kind, the brand first, e.g. "Bramblewood Comfort Pro 3 Underwired Balcony
Bra". The lead words are plain English words of public retail listings, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Bra",)
#: The lead word of a model.
LEADS = (
    "Comfort", "Support", "Anytime", "Balance", "Contour", "Lift", "Shape", "Soft", "Poise",
    "Serene", "Haven", "Essence", "Harmony", "Petal", "Delight", "Nimbus", "Mist", "Unwind",
    "Cushion", "Smooth",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations or cut codes a model is in.
NUMBERS = tuple(range(2, 10))
