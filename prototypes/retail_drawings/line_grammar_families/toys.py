"""The toys family of the line grammar: toys (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Doll", "Soft Toy", "Toy Figure", "Toy Vehicle", "Bath Toy", "Building Set", "Jigsaw Puzzle",
    "Wooden Toy", "Role Play Toy", "Arts and Crafts Kit", "Ride-On Toy", "Card Game", "Board Game",
    "Kite", "Marble Run", "Dolls' House", "Play Kitchen", "Water Gun",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Fun", "Giggle", "Wonder", "Romp", "Skip", "Hop", "Whizz", "Zoom", "Tumble", "Frolic",
    "Bounce", "Caper", "Wobble", "Squeak", "Splash", "Imagine", "Pretend", "Explore", "Discover",
    "Adventure",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
