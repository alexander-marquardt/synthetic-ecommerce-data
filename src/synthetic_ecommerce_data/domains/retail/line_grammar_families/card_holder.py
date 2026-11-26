"""The card holder family of the line grammar (gen#1114, gen#513).

A family of its own, so the models of :mod:`bags` and :mod:`bags_carry` keep their names. A model
is a plain word of the paper office and an optional sub-model, then the descriptors and the kind,
the brand first ("Brand Vellum Leather Slim Card Holder"). It carries no number: on a card holder a
number reads as a count of card slots. The lead words are plain English words no other template's
text uses, so no lead leaves another family's deal.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Card Holder",)
#: The lead word of a model.
LEADS = (
    "Vellum", "Ledger", "Almanac", "Codex", "Charter", "Docket", "Dossier", "Rubric", "Gazette",
    "Lexicon", "Quire", "Folium", "Frontispiece", "Inkwell", "Scrivener", "Archive", "Missive",
    "Postscript", "Colophon", "Escritoire", "Memorandum", "Epistle",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Duo", "Lux")
#: No generation number (see the module doc).
NUMBERS = ()
