"""The sheets family of the line grammar: sheet sets (gen#963 slice 2, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places. Sheet sets are a family of their own, not the soft family's: a family's
words are dealt over the brands that sell it (``line_grammar.Deal``), so a sheet set brand new
to the soft family would re-deal its words and rename main's cushions, towels and baby goods.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Sheet Set",)
#: The lead word of a model.
LEADS = (
    "Dozy", "Snooze", "Sleepy", "Cozy", "Slumbery", "Hushed", "Sleepover", "Nightcap",
    "Eiderdown", "Coverlet", "Bedwarmer", "Snoozy", "Airy", "Drowsy", "Yawn", "Bedspread", "Kip",
    "Shuteye", "Turndown", "Hunker", "Nightfall", "Lullaby", "Bedside", "Nocturne", "Pyjama",
    "Tucked", "Starry", "Snoozer", "Bedlinen", "Comfy",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
