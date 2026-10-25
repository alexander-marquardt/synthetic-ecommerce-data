"""The gifts family of the line grammar: keyrings, gift sets, cards and paper (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Keyring", "Gift Bag", "Gift Set", "Gift Hamper", "Gift Card", "Greeting Card",
    "Wrapping Paper", "Notebook", "Diary", "Bouquet",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Present", "Surprise", "Token", "Treat", "Wish", "Greeting", "Regards", "Thanks", "Blessing",
    "Occasion", "Celebrate", "Party", "Parcel", "Ribbon", "Jubilee", "Milestone", "Gesture",
    "Wrap", "Offering", "Hello",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
