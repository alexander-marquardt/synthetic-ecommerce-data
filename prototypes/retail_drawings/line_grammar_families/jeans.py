"""The jeans family of the line grammar: jeans (gen#663, gen#513).

A model is a plain English word of public retail listings, an optional sub-model and a number,
then the descriptors and the kind, e.g. "Ottery Denim Original 101 High Rise Straight Jeans". No
lead is a coined brand-sounding word, a place name or a first name.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Jeans",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Original", "Heritage", "Core", "Authentic", "Staple", "Standard", "Icon", "Legacy", "Rider",
    "Ranger", "Drover", "Workwear", "Frontier", "Rodeo", "Plain", "Practical", "Craft", "Origin",
    "Anchor", "Smithy", "Foundry", "Cadet",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The numbers a model may carry.
NUMBERS = (101, 205, 312, 418, 520, 625, 731, 840)
