"""The soft family of the line grammar: cushions, throws, towels and bedding (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Cushion", "Throws", "Baby Blanket", "Towel", "Beach Towel", "Tea Towels", "Duvet",
    "Duvet Cover", "Duvet Set", "Pillow", "Pillowcase", "Mattress Protector", "Mattress Topper",
    "Mattress", "Pillow Protector", "Valances", "Sofa Covers", "Apron", "Changing Mat",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Cloud", "Restful", "Snug", "Cosy", "Dream", "Drift", "Feather", "Nap", "Rest", "Hush", "Lull",
    "Slumber", "Doze", "Cuddle", "Tender", "Gentle", "Fluff", "Haze", "Calm", "Lounge",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
