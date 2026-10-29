"""The kitchen family of the line grammar: utensils, pans and small kitchen goods (gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Kitchen Utensil", "Kitchen Knife", "Chopping Board", "Colander", "Saucepan", "Frying Pan",
    "Kettle", "Toaster", "Kitchen Scales", "Kitchen Bin", "Kitchen Roll", "Cupcake Cases",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Chef", "Cook", "Bake", "Simmer", "Whisk", "Sizzle", "Stir", "Roast", "Larder", "Prep",
    "Galley", "Brew", "Steam", "Poach", "Braise", "Saute", "Knead", "Zest", "Spice", "Season",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: A kitchen code is lettered so that no count noun after it reads as a count ("16 Color Coded").
NUMBERS = ("K11", "K12", "K13", "K14", "K15", "K16", "K17", "K18")
