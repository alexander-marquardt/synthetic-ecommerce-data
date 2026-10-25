"""The trainers family of the line grammar: trainers (gen#663, gen#513).

A model is a plain word of the family, an optional sub-model and a number or a code, then the
descriptors and the kind, the brand first, e.g. "Brand Court Max 4 Leather Trainers". The lead
words are plain English words of public retail listings, not coined brand-sounding ones, names or
places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Trainers", "Platform Trainers", "Plimsolls", "Barefoot Shoes")
#: The lead word of a model.
LEADS = (
    "Dash", "Cruise", "Baseline", "Pitch", "Flex", "Sprint", "Rebound", "Rally", "Volley", "Skim",
    "Orbit", "Pulse", "Blaze", "Apex", "Vector", "Stealth", "Jump", "Hoop", "Lunge", "Switch",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations or cut codes a model is in.
NUMBERS = tuple(range(2, 10))
