"""The luggage family of the line grammar: suitcases, cabin cases, holdalls and travel goods
(gen#1114, gen#664, gen#513).

A model is a plain travel word of the family and an optional sub-model, then the descriptors and
the kind ("Transit Lite Hard Shell Spinner Suitcase"). It carries no number: on a suitcase or a
luggage set a number reads as its wheel or piece count. The lead words are plain English words,
not coined brand-sounding ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Suitcase", "Cabin Case", "Holdall", "Weekend Bag", "Luggage Set", "Travel Organizer",
    "Neck Pillow",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Voyage", "Transit", "Trip", "Transfer", "Gateway", "Passage", "Departure", "Layover",
    "Stopover", "Boarding", "Getaway", "Excursion", "Odyssey", "Itinerary", "Jetset", "Embark",
    "Horizon", "Route", "Wayfare", "Tourer",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Lite", "Plus", "Max", "Duo", "Pro", "Air")
#: No generation number (see the module doc).
NUMBERS = ()
