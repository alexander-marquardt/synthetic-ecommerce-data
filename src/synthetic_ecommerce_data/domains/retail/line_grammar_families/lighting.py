"""The lighting family of the line grammar: lamps, shades and bulbs (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Lampshade", "Ceiling Light", "Floor Lamp", "Table Lamp", "Wall Light", "Desk Lamp",
    "Night Light", "Light Bulb",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Glow", "Beam", "Halo", "Lumen", "Spark", "Bright", "Gleam", "Flare", "Shimmer", "Shine",
    "Dusk", "Morning", "Ember", "Aura", "Glint", "Lustre", "Sheen", "Flicker", "Twilight",
    "Radiant",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (200, 300, 400, 500, 600, 700, 800, 900)
