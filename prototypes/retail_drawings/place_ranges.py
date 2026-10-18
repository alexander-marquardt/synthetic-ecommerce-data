"""Range names of the class 6 apparel decoys (gen#446): a place that starts with a product word.

A range name is never a color: "Womens Red Tarn Jumper" read as a red jumper although it is not
red, and a title may not claim a color the product lacks (the rule of #444). Each range here is a
place whose first word is the word a shopper may type (``kettle``), a word no clothing type
borrows or is, so the decoy fools a plain text match on that word and nothing else.
"""

from __future__ import annotations

#: (the range name, what it is named for); the first word is the word the decoy targets.
PLACE_RANGES = (
    ("Kettle Hill", "a hill above the old mill"),
    ("Lantern Row", "a terrace by the quay"),
    ("Cushion Common", "a common beside the village"),
    ("Teapot Lane", "a lane by a tea room"),
    ("Candle Wood", "a wood of tall pines"),
    ("Basket Hollow", "a dip where willows grow"),
)


def place_range(index: int) -> tuple[str, str, str]:
    """The range, what it is named for and its first word (lower case), by cycling ``index``."""
    name, gloss = PLACE_RANGES[index % len(PLACE_RANGES)]
    return name, gloss, name.split()[0].lower()
