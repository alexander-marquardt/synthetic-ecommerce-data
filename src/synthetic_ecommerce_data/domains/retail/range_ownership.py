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

The scale half is dealt over an append-only :class:`Roster` (#1052): the brands dealt before it
keep their round-robin share of the half, and a brand appended later takes its own block of
:data:`ADDED_SHARE` names from :data:`ADDED_STEMS`, place words kept out of the shuffled pool. A
brand new to the build therefore moves no other brand's names, so no style in another department.
The base brands are dealt over the whole half less the roster's frozen :attr:`Roster.gaps`, and
a word reserved or excluded later only leaves its owner's names, so it moves no other brand either.
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail import appliance_model_numbers as amn

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

#: The stems of the place words a brand appended to a :class:`Roster` takes its names from
#: (#1052). Their words are in no half, so the shuffled pool never moves; append only, since a
#: stem's words go to the end of :func:`added_words` and a block already held stays put.
ADDED_STEMS = (
    "Alw", "Bix", "Blyth", "Corb", "Cran", "Elst", "Gled", "Hask", "Hest", "Ilk", "Lowd", "Pym",
    "Mox", "Nab", "Ost", "Varn", "Rans", "Scaw", "Shil", "Tebb", "Thack", "Ulp", "Wass", "Yox",
)  # fmt: skip

#: The names an appended brand holds: the base brands' share of the scale half (2,997 over 85).
ADDED_SHARE = 35

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
    return sorted(n for n in {*_everything(), *added_words()} if n not in EXCLUDED)


def added_words() -> list[str]:
    """The place words of :data:`ADDED_STEMS`, stem by stem, each stem's endings in its own
    seeded order, less any word of the shuffled pool: a new stem only appends words."""
    pool = set(_everything())
    out: list[str] = []
    for stem in ADDED_STEMS:
        words = [stem + e for e in ENDINGS]
        random.Random(f"{SEED}:{stem}").shuffle(words)
        out += [w for w in words if w not in pool]
    return out


@dataclass(frozen=True)
class Roster:
    """The brands of a deal in the order they joined it (#1052): ``base`` was dealt round-robin
    before the roster existed and keeps that deal; ``added`` is append-only, brand ``k`` holding
    block ``k`` of :func:`added_words`.

    ``gaps`` are the words of the half that were kept out when ``base`` was dealt (reserved or
    excluded then). It is frozen: the base is dealt over the whole half less ``gaps``, then a word
    skipped now is dropped from its owner's names alone, so one more reserved or excluded word
    moves no other brand (#1052 slice 2). A gap no longer skipped stays undealt."""

    base: tuple[str, ...]
    added: tuple[str, ...] = ()
    gaps: frozenset[str] = frozenset()

    def owned(self, whole: list[str], skip: set[str]) -> dict[str, tuple[str, ...]]:
        """Every rostered brand's names, present in the build or not, so a brand that leaves
        moves no other brand either. ``whole`` is the half with nothing dropped."""
        count = len(self.base)
        pool = [n for n in whole if n not in self.gaps]
        out = {
            b: tuple(n for n in pool[i::count] if n not in skip and n not in EXCLUDED)
            for i, b in enumerate(self.base)
        }
        words = added_words()
        for k, brand in enumerate(self.added):
            block = words[k * ADDED_SHARE : (k + 1) * ADDED_SHARE]
            if len(block) < ADDED_SHARE:
                raise ValueError(f"no names left for {brand!r}: append stems to ADDED_STEMS")
            out[brand] = tuple(w for w in block if w not in skip and w not in EXCLUDED)
        return out


#: The brands a derived style may carry, dealt the scale half (``scale._range_deal``). ``base``
#: is the sorted set dealt before #1052; a brand new to the scale build is appended to ``added``,
#: in the order brands join, never sorted in, or every later brand's block would move.
SCALE = Roster(
    base=(
        "Aldermist", "Ardmoor", "Barkwell", "Barrowby Kitchen", "Boltwick", "Brackenmere Home",
        "Bramblewood", "Brewhollow Roasters", "Brightwater Botanics", "Calderby & Lune",
        "Calderwick Denim", "Cindrel", "Clearbrook Household", "Clumpton", "Cobble & Kiln",
        "Cobbleway", "Copper Hill Preserves", "Crofter's Bakehouse", "Daskel", "Dovecote Lane",
        "Dunvale", "Emberly Home", "Featherlee", "Fenmere", "Fenwold Nursery", "Ferrowick Denim",
        "Freshfold", "Goldfield Farms", "Halvering", "Halvern", "Harbour & Pine", "Hearth & Table",
        "Hollin Hair", "Hollinsby", "Hollinwray Knits", "Hound & Heath", "Hushwell",
        "Kestlewood Cosmetics", "Kettleby Tea Co.", "Lanternby", "Larchwood Living", "Larkmoor",
        "Ledwick Botanics", "Little Fernby", "Marrick", "Marrowgate", "Mervane",
        "Mirefield Naturals", "Mossdown", "Mossgill Dairy", "Nimbrel", "Orrin Skin",
        "Osier & Vane", "Ottery Denim", "Pantry Mill", "Pearlbrook", "Pellbrook", "Pellimar",
        "Pewley Table", "Pinehollow", "Pipwick Toys", "Puddlecombe Toys", "Purrsey Lane",
        "Quellmoor Care", "Quillon Sleep", "Quorrin", "Ribbonvale", "Rookery Garden Co.",
        "Saltmarsh", "Soapwell", "Sorrel & Salt", "Stridewell", "Tailmoor", "Tallow Street",
        "Thistle & Wren", "Thornlea Skin", "Thrennick", "Torvane", "Treadmoor", "Veilmoor",
        "Velling Apothecary", "Wexmoor", "Wheatsheaf Lane", "Whiskerby", "Wrenfield",
    ),
    added=(),
    # The scale-half words skipped when the base was dealt: the excluded words in the half and
    # Fenmere, a brand's own word. Never edit: a word dropped later leaves its owner alone.
    gaps=frozenset({
        "Alnwick", "Ashlow", "Ashwell", "Denby", "Ellerby", "Elmwood", "Fenmere", "Fernwood",
        "Halden", "Harwell", "Hollow", "Kelden", "Malham", "Oakham", "Oldstead", "Penley",
    }),
)  # fmt: skip


def whole_halves() -> dict[str, list[str]]:
    """The pool split into the ``scale`` half and the ``grocery`` half, each in a seeded order,
    the excluded words still in."""
    names = _everything()
    random.Random(SEED).shuffle(names)
    return {"scale": names[0::2], "grocery": names[1::2]}


def halves() -> dict[str, list[str]]:
    """:func:`whole_halves` less the excluded words.

    The shuffle and the split run over every word and the excluded ones are dropped after, so
    excluding one more word never moves another word to the other half."""
    return {h: [n for n in names if n not in EXCLUDED] for h, names in whole_halves().items()}


class Deal:
    """One half of the pool dealt over a set of brands: every name has one owner.

    ``reserved`` holds the words that must not be dealt (the brands' own words and the range
    names an authored row already carries). With no ``roster`` the half is dealt round-robin over
    the sorted brands, so one brand more or one word more reserved moves every brand's names; with
    one, every brand must be on it, and neither a brand appended nor a word reserved or excluded
    later moves another brand (#1052)."""

    def __init__(
        self,
        half: str,
        brands: Iterable[str],
        reserved: Iterable[str] = (),
        roster: Roster | None = None,
    ) -> None:
        self.half = half
        self.brands = sorted(set(brands))
        skip = set(reserved)
        if roster is None:
            pool = [n for n in halves()[half] if n not in skip]
            count = len(self.brands) or 1
            self._owned = {b: tuple(pool[i::count]) for i, b in enumerate(self.brands)}
            self.names = tuple(pool)
            return
        owned = roster.owned(whole_halves()[half], skip)
        if off := [b for b in self.brands if b not in owned]:
            raise ValueError(f"{off} not on the {half} roster: append each to its added brands")
        self._owned = {b: owned[b] for b in self.brands}
        self.names = tuple(n for b in self.brands for n in self._owned[b])

    def owned(self, brand: str, slot: int) -> str:
        """The name ``brand`` holds at ``slot``: a slot beyond its names wraps."""
        mine = self._owned[brand]
        return mine[slot % len(mine)]

    def of(self, brand: str) -> tuple[str, ...]:
        return self._owned[brand]

    def owner(self, name: str) -> str | None:
        return next((b for b, mine in self._owned.items() if name in mine), None)
