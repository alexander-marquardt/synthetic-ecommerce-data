"""The tee family of the line grammar: tees (gen#663, gen#513).

A model is a plain word of the family, an optional sub-model and a number or a code, then the
descriptors and the kind, the brand first, e.g. "Brand Weekend Pro 3 Crew Neck Tee". The lead
words are plain English words of public retail listings, not coined brand-sounding ones, names or
places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Tee", "T-Shirt")
#: The lead word of a model.
LEADS = (
    "Regular", "Casual", "Weekend", "Laidback", "Relaxed", "Fresh", "Zephyr", "Dayoff",
    "Saturday", "Studio", "Campus", "Varsity", "Retro", "Hoodie", "Downtown", "Skate", "Surf",
    "Camp", "Field", "Garage", "Social", "Club", "Chill", "Basecamp",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations or cut codes a model is in.
NUMBERS = tuple(range(2, 10))
