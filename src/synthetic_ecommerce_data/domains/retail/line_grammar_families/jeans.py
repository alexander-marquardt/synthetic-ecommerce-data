"""The jeans family of the line grammar: jeans (gen#663, gen#513).

A model is a plain word of the family alone, then the descriptors and the kind, the brand
first, e.g. "Ottery Denim Original High Rise Straight Jeans": a cut code or a sub-model read as
synthetic (#851), so ``SUBS`` and ``NUMBERS`` name no authored or derived jeans. The lead
words are plain English words of public retail listings, not coined brand-sounding ones, names
or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Jeans",)
#: The lead word of a model.
LEADS = (
    "Original", "Heritage", "Core", "Genuine", "Staple", "Standard", "Icon", "Legacy",
    "Rider", "Ranger", "Drover", "Workwear", "Frontier", "Rodeo", "Plain", "Practical", "Craft",
    "Origin", "Anchor", "Smithy", "Foundry", "Cadet",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations or cut codes a model is in.
NUMBERS = (101, 205, 312, 418, 520, 625, 731, 840)
