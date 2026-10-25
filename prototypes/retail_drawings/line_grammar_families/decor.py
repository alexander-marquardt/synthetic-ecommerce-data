"""The decor family of the line grammar: frames, clocks, candles and ornaments (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Photo Frame", "Decorative Tray", "Clock", "Christmas Decoration", "Ornament",
    "Artificial Flowers", "Scented Candle", "Wallpaper", "Paint", "Trophy", "Fridge Magnets",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Accent", "Display", "Treasure", "Memory", "Moment", "Charm", "Trinket", "Keepsake", "Festive",
    "Sparkle", "Merry", "Jolly", "Cheer", "Glee", "Fable", "Delight", "Tidings", "Yule", "Decor",
    "Showcase",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (2, 3, 4, 5, 6, 7, 8, 9)
