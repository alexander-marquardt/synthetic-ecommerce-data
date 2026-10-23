"""Range names and the one brand that owns each (gen#623).

A range name ("Larkrise", "Harrow") is a model word. It reads as a brand when it leads the titles
of many brands, so a generated range name belongs to exactly one brand: the brand that draws it
is the brand that owns it. The pool is invented place words (a stem and an ending), dealt to the
brands in a seeded shuffle, so a name is never owned twice and the deal is the same on every run.

Two builds draw range names, each from a half of the pool: ``scale`` for the derived styles and
``grocery`` for the grocery builder. The halves are disjoint, so a brand that sells in both owns a
different set in each and no name is ever shared. A builder keeps drawing its slot (an index into
its old name list, so its random stream and its title-collision pattern stay as they were) and
:func:`Deal.owned` answers which name the brand holds at that slot.
"""

from __future__ import annotations

import random
from collections.abc import Iterable

import appliance_model_numbers as amn

#: The stems of the invented place words: no color, no product word, no brand's own word.
STEMS = (
    "Ash", "Aln", "Ark", "Bar", "Beck", "Bel", "Birk", "Bolt", "Bram", "Brack", "Brad", "Brock",
    "Bran", "Burn", "Cald", "Carr", "Chap", "Chel", "Clay", "Cleve", "Cold", "Cop", "Cor",
    "Crake", "Cress", "Cud", "Dal", "Dar", "Den", "Dew", "Dun", "Eas", "Eden", "Elm", "Eller",
    "Esk", "Fair", "Fal", "Fen", "Fern", "Flax", "Fox", "Gar", "Gil", "Glen", "Gos", "Hal",
    "Ham", "Har", "Haw", "Haz", "Hep", "Hol", "Hor", "Hul", "Ing", "Ire", "Kel", "Ken", "Kil",
    "Kirk", "Lam", "Lang", "Lea", "Lin", "Lon", "Lud", "Mal", "Mar", "Mel", "Mer", "Mid", "Mil",
    "Mor", "Nor", "Oak", "Old", "Orm", "Ot", "Ox", "Pen", "Pick", "Pil", "Pres", "Quar", "Ram",
    "Rav", "Rea", "Reed", "Rib", "Rock", "Ros", "Rud", "Rush", "Ry", "Sal", "Sand", "Sed", "Shap",
    "Shel", "Skel", "Sow", "Stan", "Stav", "Stoke", "Sut", "Swan", "Tan", "Thir", "Thorn", "Thur",
    "Tid", "Tor", "Town", "Trent", "Ulv", "Up", "Wal", "War", "Wath", "Wen", "Wes", "Whit",
    "Wig", "Win", "Wolds", "Wray", "Wyke", "Yar", "Yeld", "Zen",
)  # fmt: skip

#: The endings of the invented place words.
ENDINGS = (
    "by", "thorpe", "ley", "ford", "dale", "wick", "ham", "ton", "well", "moor", "holme",
    "combe", "mere", "hurst", "worth", "field", "stead", "bury", "gate", "beck", "fell", "wood",
    "hill", "brook", "ness", "low", "burn", "cliffe", "shaw", "den", "ington", "ingham",
    "borough", "ridge", "thwaite", "side", "bank", "croft", "mouth", "stone", "bridge", "haugh",
    "scar", "garth", "ing", "wyke",
)  # fmt: skip

SEED = "range-names:623"

#: Words no range name may be: a product or a material read as a range.
PRODUCT_WORDS = frozenset({
    "Hollow", "Oakwood", "Elmwood", "Ashwood", "Fernwood", "Garden", "Pillow", "Bramley",
})  # fmt: skip

#: Range words an authored row already carries and that the pool would otherwise deal a second
#: time (tests/test_retail_scale.py checks that no authored line is left in the pool).
AUTHORED = frozenset({
    "Ashby", "Ashlow", "Ashwell", "Brockhurst", "Dunholme", "Ellerby", "Fenbridge", "Fenby",
    "Halden", "Harwell", "Kelden", "Kenwick", "Kildale", "Kirkham", "Lindale", "Malham",
    "Mardale", "Oldstead", "Penley", "Thornby", "Winscar",
})  # fmt: skip

#: #622's appliance series: a series is its brand's word, so the pool never deals it.
SERIES_WORDS = frozenset(w for names in amn.SERIES.values() for w in names)

EXCLUDED = PRODUCT_WORDS | AUTHORED | SERIES_WORDS


def _everything() -> list[str]:
    """Every stem and ending joined, sorted and unique, excluded words still in."""
    return sorted({s + e for s in STEMS for e in ENDINGS})


def candidates() -> list[str]:
    """Every invented place word that may be a range name, sorted and unique."""
    return [n for n in _everything() if n not in EXCLUDED]


def halves() -> dict[str, list[str]]:
    """The pool split into the ``scale`` half and the ``grocery`` half, each in a seeded order.

    The shuffle and the split run over every word and the excluded ones are dropped after, so
    excluding one more word never moves another word to the other half or to another brand."""
    names = _everything()
    random.Random(SEED).shuffle(names)
    return {
        "scale": [n for n in names[0::2] if n not in EXCLUDED],
        "grocery": [n for n in names[1::2] if n not in EXCLUDED],
    }


class Deal:
    """One half of the pool dealt over a set of brands: every name has one owner.

    ``reserved`` holds the words that must not be dealt (the brands' own words and the range
    names an authored row already carries)."""

    def __init__(self, half: str, brands: Iterable[str], reserved: Iterable[str] = ()) -> None:
        self.half = half
        self.brands = sorted(set(brands))
        skip = set(reserved)
        pool = [n for n in halves()[half] if n not in skip]
        count = len(self.brands) or 1
        self._owned = {b: tuple(pool[i::count]) for i, b in enumerate(self.brands)}
        self.names = tuple(pool)

    def owned(self, brand: str, slot: int) -> str:
        """The name ``brand`` holds at ``slot``: a slot beyond its names wraps."""
        mine = self._owned[brand]
        return mine[slot % len(mine)]

    def of(self, brand: str) -> tuple[str, ...]:
        return self._owned[brand]

    def owner(self, name: str) -> str | None:
        return next((b for b, mine in self._owned.items() if name in mine), None)
