"""The bags family of the line grammar: crossbody, shoulder and clutch bags (gen#1114, gen#513).

A model is a plain word of going out and an optional sub-model, then the descriptors and the kind,
the brand first ("Brand Boulevard Leather Saddle Crossbody Bag"). It carries no number: on a bag a
number reads as a size or a pocket count. The lead words are plain English words no other
template's text uses, so no lead leaves another family's deal.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Crossbody Bag", "Shoulder Bag", "Clutch Bag")
#: The lead word of a model.
LEADS = (
    "Boulevard", "Matinee", "Rendezvous", "Vignette", "Colonnade", "Esplanade", "Overture",
    "Interlude", "Cabaret", "Serenade", "Debut", "Piazza", "Atelier", "Mezzanine", "Recital",
    "Rotunda", "Cameo", "Sonnet", "Cadenza", "Masquerade", "Quartet", "Premiere",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Duo", "Lux")
#: No generation number (see the module doc).
NUMBERS = ()
