"""The baby gear family of the line grammar: strollers, car seats and high chairs (gen#965).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind, the brand first: "Calderby & Lune Rover Lie-Flat Full-Size Stroller".
The lead words are plain English words of going out and about, not coined brand-sounding ones,
names or places. The three kinds have a family of their own because the soft family's words
(gen#664) are all dealt to its brands, and a stroller named "Doze" reads as bedding.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Stroller", "Car Seat", "High Chair")
#: The lead word of a model.
LEADS = (
    "Journey", "Amble", "Saunter", "Rove", "Hike", "Scoot", "Jaunt", "Outing", "Promenade",
    "Tour", "Venture", "Pathway", "Compass", "Perch", "Pip", "Bud", "Acorn", "Sail", "Rover",
    "Voyager",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
