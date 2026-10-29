"""The garden family of the line grammar: plants, seeds and garden goods (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Plant", "Bedding Plant", "Bulbs", "Seeds", "Growing Kit", "Christmas Tree", "BBQ",
    "Garden Furniture Set", "Lawn Mower", "Robot Mower", "Grass Trimmer", "Hedge Trimmer",
    "Parasol", "Garden Hose",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Border", "Patio", "Meadow", "Bloom", "Blossom", "Sprout", "Harvest", "Wildflower", "Trellis",
    "Terrace", "Hedgerow", "Verge", "Plot", "Pasture", "Grow", "Seedling", "Sunlit", "Cottage",
    "Allotment", "Potting",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
