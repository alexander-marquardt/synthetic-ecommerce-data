"""The bra family of the line grammar: bras (gen#663, gen#513).

A model is a plain English word of public retail listings, an optional sub-model and a number,
then the descriptors and the kind, e.g. "Bramblewood Comfort Pro 3 Underwired Balcony Bra". No
lead is a coined brand-sounding word, a place name or a first name.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Bra",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Comfort", "Support", "Anytime", "Balance", "Contour", "Lift", "Shape", "Soft", "Poise",
    "Serene", "Haven", "Essence", "Harmony", "Petal", "Delight", "Nimbus", "Mist", "Unwind",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The numbers a model may carry.
NUMBERS = tuple(range(2, 10))
