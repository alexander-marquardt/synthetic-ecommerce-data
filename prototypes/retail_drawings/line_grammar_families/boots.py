"""The boots family of the line grammar: boots (gen#663, gen#513).

A model is a plain English word of public retail listings, an optional sub-model and a number,
then the descriptors and the kind, e.g. "Ottery Denim Original 101 High Rise Straight Jeans". No
lead is a coined brand-sounding word, a place name or a first name.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Walking Boots", "Chelsea Boots", "Ankle Boots", "Chukka Boots", "Knee High Boots", "Wellies",
    "Safety Boots",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Summit", "Ascent", "Alpine", "Grit", "Rugged", "Hammer", "Timber", "Bedrock", "Granite",
    "Puddle", "Drizzle", "Storm", "Gale", "Hardy", "Sturdy", "Trek", "Wander", "Roam", "Ramble",
    "Scout", "Pioneer", "Forager", "Stomp", "Boulder",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The numbers a model may carry.
NUMBERS = tuple(range(2, 10))
