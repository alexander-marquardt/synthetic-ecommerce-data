"""The casual family of the line grammar: casual shoes (gen#663, gen#513).

A model is a plain word of the family, an optional sub-model and a number or a code, then the
descriptors and the kind, the brand first, e.g. "Brand Siesta 2 Cork Wedges". The lead words are
plain English words of public retail listings, not coined brand-sounding ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Espadrilles", "Slippers", "Wedges", "Mules", "Sandals", "Clogs", "Jelly Shoes")
#: The lead word of a model.
LEADS = (
    "Siesta", "Fiesta", "Sorbet", "Languid", "Toasty", "Nestle", "Plush", "Lazy", "Sunset",
    "Sunrise", "Poolside", "Lido", "Parasol", "Gelato", "Barbecue", "Hammock", "Tropic",
    "Carnival", "Flutter", "Twirl", "Swish", "Bliss", "Tang", "Jolly",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations or cut codes a model is in.
NUMBERS = tuple(range(2, 10))
