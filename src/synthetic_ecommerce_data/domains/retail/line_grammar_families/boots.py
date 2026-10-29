"""The boots family of the line grammar: boots (gen#663, gen#513).

A model is a plain word of the family, an optional sub-model and a number or a code, then the
descriptors and the kind, the brand first, e.g. "Brand Summit 3 Waterproof Walking Boots". The
lead words are plain English words of public retail listings, not coined brand-sounding ones,
names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Walking Boots", "Chelsea Boots", "Ankle Boots", "Chukka Boots", "Knee High Boots",
    "Wellies", "Safety Boots",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Summit", "Ascent", "Alpine", "Grit", "Rugged", "Hammer", "Timber", "Bedrock", "Granite",
    "Puddle", "Drizzle", "Storm", "Gale", "Hardy", "Sturdy", "Trek", "Wander", "Roam", "Ramble",
    "Scout", "Pioneer", "Forager", "Stomp", "Boulder",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations or cut codes a model is in.
NUMBERS = tuple(range(2, 10))
