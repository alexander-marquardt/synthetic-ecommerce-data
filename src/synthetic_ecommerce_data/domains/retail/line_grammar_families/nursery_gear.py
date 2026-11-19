"""The nursery gear family of the line grammar: cribs and baby monitors (gen#965, slice 3).

A model is a plain word of the family, an optional sub-model and a number, then the descriptors
and the kind, the brand first: "Cobble & Kiln Starling Wipe-Clean Standard Crib". The lead
words are plain English words of a quiet room at night, not coined brand-sounding ones, names or
places. The two kinds are a family of their own, not kinds of the baby gear family
(``baby_gear.py``): a family's words are dealt over its brands, so a kind added there re-deals
them and renames the strollers, car seats and high chairs already sold.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Crib", "Baby Monitor")
#: The lead word of a model.
LEADS = (
    "Moonbeam", "Starlight", "Twinkle", "Clover", "Bramble", "Sparrow", "Puffin", "Dewdrop",
    "Harebell", "Thimble", "Button", "Firefly", "Hushaby", "Nightjar", "Starling", "Glimmer",
    "Feather", "Bunting", "Catkin", "Hollow",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
