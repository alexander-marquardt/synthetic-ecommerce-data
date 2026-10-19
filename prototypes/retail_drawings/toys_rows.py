"""Toy templates for the scaled retail catalog (gen#201): data only.

The Toys department sold five kinds (soft toys, bath toys, toy vehicles, figures and night
lights), so a search for a building set, a jigsaw, a board game, a doll, a play kitchen,
a craft kit or a balance bike found nothing, and no toy carried an age range. Each type
here is a leaf with its own drawing (:mod:`kit_toys`) and its shopper attributes as
structured entries:

- ``age_range`` on every style, one key across the types ("6+ years", "18+ months"), and
  the row's ``audience`` (exported as ``age_group``): baby, toddler or kids. A 1000 piece
  jigsaw is for adults;
- ``toy_type`` names the kind inside a type (a Play Kitchen or a Tool Bench, a Balance
  Bike or a Trike), one key across the types, so a toy-type facet lists them all;
- ``theme`` names what a building set or a jigsaw shows; a craft kit sells each theme as
  a SKU, as its box prints no theme;
- ``line`` is one of four invented character ranges, each sold by one brand across several
  kinds, so a range name alone finds its jigsaw, its building set and its scooter. The
  drawing carries the range's mark (``character``, a motif of :mod:`motifs`).

A set's pieces come from its :class:`Contents`, the one source of its ``piece_count``,
its title and its first sentence, and the drawing shows each piece (``class="piece"``);
a jigsaw draws its pieces as a grid of exactly that many tiles. A building set sells its
sizes as SKUs (``piece_count`` per SKU) on one shared box drawing, which prints no count.
These styles are templates only: :func:`scale.derivable` leaves them out, as it does the
shirts, so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from dataclasses import dataclass

import kit_toys  # noqa: F401 -- registers building_set, jigsaw, board_game, doll, ...
from breadth_rows import Contents, Row, paint_range
from variants import cw

from synthetic_ecommerce_data.core.entry import canonical

_T = "Toys"
_P, _L, _K = "Pipwick Toys", "Little Fernby", "Puddlecombe Toys"
BABY, TODDLER, KIDS, ADULT = "baby", "toddler", "kids", "adult"

#: The invented character ranges: line -> (its one brand, the motif that marks it).
RANGES = {
    "Moonmoth Rangers": (_P, "star"),
    "Rumblesaur Ridge": (_P, "dinosaur"),
    "Bramblewood Owls": (_L, "bird"),
    "Driftwhistle Bay": (_K, "whale"),
}


@dataclass(frozen=True)
class TRow(Row):
    """A toy row. ``finish_by_color``: a wooden toy's Natural colorway is unpainted, every
    other colorway painted, so each SKU's ``finish`` follows its color."""

    finish_by_color: bool = False

    def skus(self) -> list[dict]:
        out = super().skus()
        if self.finish_by_color:
            for sku in out:
                sku["finish"] = "Natural" if sku["color"] == "Natural" else "Painted"
        return out


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _count(key: str, name: str, n: int) -> tuple[str, str, str, str]:
    return (key, name, str(n), "C62")


def _age(v: str) -> tuple[str, str, str]:
    return _a("age_range", "Age range", v)


def _kind(v: str) -> tuple[str, str, str]:
    return _a("toy_type", "Toy type", v)


def _line(name: str, brand: str) -> tuple[tuple[str, str, str], ...]:
    if RANGES[name][0] != brand:
        raise ValueError(f"{name!r} is {RANGES[name][0]}'s range, not {brand}'s")
    return (_a("line", "Line", name),)


def _char(name: str | None) -> tuple[tuple[str, str], ...]:
    return (("character", RANGES[name][1]),) if name else ()


def _counts(kit: Contents) -> tuple[str, str]:
    """The drawing's ``counts`` param: each line's quantity, in order, so the kit draws
    every piece of every line (``class="piece"``) and no more."""
    return ("counts", ",".join(str(q) for q, _ in kit))


def _yes(v: bool) -> str:
    return "Yes" if v else "No"


RED = cw("Red", "#c8312e", "solid", "#f4f1ea")
BLUE = cw("Blue", "#3f6fb5", "solid", "#f4f1ea")
NAVY = cw("Navy", "#26365c", "solid", "#f2d14b")
GREEN = cw("Green", "#5f9a4a", "solid", "#f4f1ea")
YELLOW = cw("Yellow", "#f2c94c", "solid", "#2f2f35")
PINK = cw("Pink", "#f2a1b8", "solid", "#2f2f35")
LILAC = cw("Lilac", "#b9a3d0", "solid", "#2f2f35")
PURPLE = cw("Purple", "#7b4fa0", "solid", "#f4f1ea")
TEAL = cw("Teal", "#1c7c7d", "solid", "#f4f1ea")
GREY = cw("Grey", "#9a9ca0", "solid", "#2f2f35")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
ORANGE = cw("Orange", "#e07a1f", "solid", "#2f2f35")
NATURAL = cw("Natural", "#d9b98a", "solid", "#8a6a44")

# --------------------------------------------------------------------------
# Building sets: the theme is the box art; the sizes are SKUs by piece count.
# --------------------------------------------------------------------------

_BLD = (_T, "Building & Construction", "Building Sets")
STANDARD, LARGE = "Standard Bricks", "Large Bricks"


def _bld(theme: str, age: str, system: str, line: str | None = None, brand: str = _P) -> tuple:
    return (_a("theme", "Theme", theme), _age(age), _a("compatible_system", "Compatible system",
            system), *(_line(line, brand) if line else ()))  # fmt: skip


def _pcs(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    return tuple((str(n), p) for n, p in pairs)


BUILDING_SETS = (
    TRow("BLDMMR", "Moonmoth Rangers Space Base Building Set", _P, _T, _BLD, "Building Set",
         15.0, "building_set", "Build the Rangers' moon base, its launch pad and a rocket "
         "that seats two minifigures. Fits every standard brick. For ages 6 and up. In three "
         "sizes: 150, 420 and 880 pieces.",
         (NAVY,), _bld("Space", "6+ years", STANDARD, "Moonmoth Rangers"),
         _pcs((150, 15.0), (420, 35.0), (880, 70.0)), audience=KIDS, colorless=True,
         params=(("theme", "space"), *_char("Moonmoth Rangers")), size_key="piece_count"),
    TRow("BLDRUM", "Rumblesaur Ridge Volcano Building Set", _P, _T, _BLD, "Building Set", 25.0,
         "building_set", "A smoking volcano, a rope bridge and a big dinosaur with a jaw that "
         "opens. Fits every standard brick. For ages 7 and up. In 260 and 640 pieces.",
         (GREEN,), _bld("Dinosaurs", "7+ years", STANDARD, "Rumblesaur Ridge"),
         _pcs((260, 25.0), (640, 55.0)), audience=KIDS, colorless=True,
         params=(("theme", "dinosaurs"), *_char("Rumblesaur Ridge")), size_key="piece_count"),
    TRow("BLDCST", "Clifftop Castle Building Set", _K, _T, _BLD, "Building Set", 30.0,
         "building_set", "A castle with a drawbridge that winds up, two towers and a knight "
         "on horseback. Fits every standard brick. For ages 8 and up. In 380 and 1050 pieces.",
         (GREY,), _bld("Castle", "8+ years", STANDARD), _pcs((380, 30.0), (1050, 85.0)),
         audience=KIDS, colorless=True, params=(("theme", "castle"),), size_key="piece_count"),
    TRow("BLDCTY", "City Fire Station Building Set", _L, _T, _BLD, "Building Set", 18.0,
         "building_set", "A fire station with a roll-up door, a fire engine and a ladder that "
         "turns. Fits every standard brick. For ages 5 and up. In 190 and 410 pieces.",
         (RED,), _bld("City", "5+ years", STANDARD), _pcs((190, 18.0), (410, 38.0)),
         audience=KIDS, colorless=True, params=(("theme", "city"),), size_key="piece_count"),
    TRow("BLDOWL", "Bramblewood Owls Treehouse Building Set", _L, _T, _BLD, "Building Set",
         12.0, "building_set", "A treehouse with a rope swing, a nest box and three owl "
         "friends from the Bramblewood stories. Fits every standard brick. For ages 4 and up. "
         "In 120 and 300 pieces.",
         (GREEN,), _bld("Animals", "4+ years", STANDARD, "Bramblewood Owls", _L),
         _pcs((120, 12.0), (300, 28.0)), audience=KIDS, colorless=True,
         params=(("theme", "animals"), *_char("Bramblewood Owls")), size_key="piece_count"),
    TRow("BLDFRM", "Farmyard Animals Large Brick Set", _K, _T, _BLD, "Building Set", 15.0,
         "building_set", "Big, easy-grip bricks for little hands, with a barn, a tractor and "
         "farm animals to build. For ages 18 months and up. In 40 and 85 pieces.",
         (YELLOW,), _bld("Animals", "18+ months", LARGE), _pcs((40, 15.0), (85, 28.0)),
         audience=TODDLER, colorless=True, params=(("theme", "farm"), ("bricks", "large")),
         size_key="piece_count"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Jigsaws: one picture and piece count per style; the grid draws every piece.
# --------------------------------------------------------------------------

_JIG = (_T, "Puzzles", "Jigsaw Puzzles")


def _cm(key: str, name: str, v: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(v), "CMT", float(v * 10))  # canonical length is millimeters


def _jig(n: int, theme: str, age: str, size: tuple[int, int], line: str | None = None,
         brand: str = _P):  # fmt: skip
    """A jigsaw's finished size is its length and width, two ``CMT`` entries a filter or a
    sort can use (gen#261), and the text a shopper reads ("49 x 36 cm"), from the same two."""
    length, width = size
    return (_count("piece_count", "Piece count", n), _a("theme", "Theme", theme), _age(age),
            _a("finished_size", "Finished size", f"{length} x {width} cm"),
            _cm("item_length", "Item length", length), _cm("item_width", "Item width", width),
            *(_line(line, brand) if line else ()))  # fmt: skip


def _jp(n: int, theme: str, line: str | None = None) -> tuple[tuple[str, str], ...]:
    return (("pieces", str(n)), ("theme", theme), *_char(line))


JIGSAWS = (
    TRow("JIG024", "Driftwhistle Bay 24 Piece Floor Puzzle", _K, _T, _JIG, "Jigsaw Puzzle",
         10.0, "jigsaw", "Big, thick pieces that make a harbour scene with the Driftwhistle "
         "Bay whale, sized for the floor. For ages 3 and up.",
         (TEAL,), _jig(24, "Seaside", "3+ years", (60, 40), "Driftwhistle Bay", _K),
         audience=KIDS, colorless=True, params=_jp(24, "seaside", "Driftwhistle Bay")),
    TRow("JIG035", "Rumblesaur Ridge 35 Piece Jigsaw Puzzle", _P, _T, _JIG, "Jigsaw Puzzle",
         8.0, "jigsaw", "The Rumblesaur Ridge gang by their volcano, in sturdy card pieces. "
         "For ages 4 and up.",
         (GREEN,), _jig(35, "Dinosaurs", "4+ years", (40, 28), "Rumblesaur Ridge"),
         audience=KIDS, colorless=True, params=_jp(35, "dinosaurs", "Rumblesaur Ridge")),
    TRow("JIG048", "Moonmoth Rangers 48 Piece Jigsaw Puzzle", _P, _T, _JIG, "Jigsaw Puzzle",
         9.0, "jigsaw", "The Rangers' rocket over a cratered moon, with a poster of the "
         "finished picture in the box. For ages 5 and up.",
         (NAVY,), _jig(48, "Space", "5+ years", (48, 34), "Moonmoth Rangers"),
         audience=KIDS, colorless=True, params=_jp(48, "space", "Moonmoth Rangers")),
    TRow("JIG100", "World Map 100 Piece Jigsaw Puzzle", _L, _T, _JIG, "Jigsaw Puzzle", 11.0,
         "jigsaw", "A bright map of the continents and oceans with the animals that live "
         "there. For ages 6 and up.",
         (BLUE,), _jig(100, "Maps", "6+ years", (49, 36)), audience=KIDS, colorless=True,
         params=_jp(100, "maps")),
    TRow("JIG500", "Harbour Village 500 Piece Jigsaw Puzzle", _K, _T, _JIG, "Jigsaw Puzzle",
         14.0, "jigsaw", "Painted cottages around a busy harbour at sunset, cut in a classic "
         "grid. For ages 10 and up.",
         (ORANGE,), _jig(500, "Landscapes", "10+ years", (49, 36)), audience=KIDS,
         colorless=True, params=_jp(500, "landscapes")),
    TRow("JIG1KA", "Alpine Lake 1000 Piece Jigsaw Puzzle", _P, _T, _JIG, "Jigsaw Puzzle",
         16.0, "jigsaw", "Snowy peaks reflected in a still lake, on thick blue-backed board "
         "with a linen finish. For ages 12 and up.",
         (BLUE,), _jig(1000, "Landscapes", "12+ years", (68, 49)), audience=ADULT,
         colorless=True, params=_jp(1000, "landscapes")),
    TRow("JIG1KB", "Night Sky 1000 Piece Jigsaw Puzzle", _L, _T, _JIG, "Jigsaw Puzzle", 16.0,
         "jigsaw", "Stars, planets and a crescent moon on a deep blue sky, a slow, absorbing "
         "puzzle. For ages 12 and up.",
         (NAVY,), _jig(1000, "Space", "12+ years", (68, 49)), audience=ADULT,
         colorless=True, params=_jp(1000, "space")),
)  # fmt: skip

# --------------------------------------------------------------------------
# Board games: the kind is drawn (a track, a hex board, a fan of cards, a timer); the
# editions are SKUs on the one box.
# --------------------------------------------------------------------------

_GAM = (_T, "Games", "Board Games")


def _game(kind: str, lo: int, hi: int, minutes: int, age: str, line: str | None = None,
          brand: str = _P) -> tuple:  # fmt: skip
    """A game's kind, its players (a count each end, so "for 4 players" is a range filter)
    and its play time: a plain number, its unit in its name, as a percent's is."""
    return (_kind(kind), _count("min_players", "Minimum players", lo),
            _count("max_players", "Maximum players", hi),
            _a("play_time", "Play time (minutes)", str(minutes)), _age(age),
            *(_line(line, brand) if line else ()))  # fmt: skip


def _ed(*pairs: tuple[str, float]) -> tuple[tuple[str, float], ...]:
    return tuple(pairs)


BOARD_GAMES = (
    TRow("GAMFAM", "Hedgerow Hop Family Board Game", _L, _T, _GAM, "Board Game", 18.0,
         "board_game", "Race your hedgehog round the hedgerow, dodge the puddles and hop the "
         "shortcuts. A family game for 2 to 6 players that takes about half an hour. For ages "
         "6 and up. The travel edition folds into a pocket-sized tin.",
         (RED,), _game("Family Game", 2, 6, 30, "6+ years"),
         _ed(("Standard", 18.0), ("Travel", 10.0)), audience=KIDS, colorless=True,
         params=(("kind", "family"),), size_key="edition"),
    TRow("GAMSTR", "Saltmarsh Traders Strategy Board Game", _K, _T, _GAM, "Board Game", 35.0,
         "board_game", "Build ports, trade salt and silk, and outwit your rivals across a "
         "board of hex tiles. A strategy game for 2 to 4 players, about 90 minutes. For ages "
         "10 and up. The deluxe edition has wooden pieces.",
         (NAVY,), _game("Strategy Game", 2, 4, 90, "10+ years"),
         _ed(("Standard", 35.0), ("Deluxe", 55.0)), audience=KIDS, colorless=True,
         params=(("kind", "strategy"),), size_key="edition"),
    TRow("GAMCRD", "Thimblewhip Card Game", _P, _T, _GAM, "Board Game", 8.0, "board_game",
         "A fast matching game: spot the pair, slap the pile, keep the cards. A card game for "
         "2 to 8 players in about 20 minutes. For ages 7 and up.",
         (YELLOW,), _game("Card Game", 2, 8, 20, "7+ years"),
         _ed(("Standard", 8.0), ("Travel", 6.0)), audience=KIDS, colorless=True,
         params=(("kind", "card"),), size_key="edition"),
    TRow("GAMPTY", "Muddle & Mime Party Game", _P, _T, _GAM, "Board Game", 22.0, "board_game",
         "Draw, act or hum the word on the card before the sand runs out. A party game for 4 "
         "to 12 players, about 45 minutes. For ages 12 and up.",
         (PURPLE,), _game("Party Game", 4, 12, 45, "12+ years"), _ed(("Standard", 22.0),),
         audience=KIDS, colorless=True, params=(("kind", "party"),), size_key="edition"),
    TRow("GAMMMR", "Moonmoth Rangers Race to the Moon Board Game", _P, _T, _GAM, "Board Game",
         15.0, "board_game", "Roll, fly and dodge the comets to land the Rangers' rocket on "
         "the moon first. A family game for 2 to 4 players in about 25 minutes. For ages 5 "
         "and up.",
         (NAVY,), _game("Family Game", 2, 4, 25, "5+ years", "Moonmoth Rangers"),
         _ed(("Standard", 15.0), ("Travel", 9.0)), audience=KIDS, colorless=True,
         params=(("kind", "family"), *_char("Moonmoth Rangers")), size_key="edition"),
    TRow("GAMOWL", "Bramblewood Owls Memory Card Game", _L, _T, _GAM, "Board Game", 7.0,
         "board_game", "Turn two cards and find the matching owls. A first card game for 1 to "
         "4 players in about 15 minutes. For ages 3 and up.",
         (GREEN,), _game("Card Game", 1, 4, 15, "3+ years", "Bramblewood Owls", _L),
         _ed(("Standard", 7.0),), audience=KIDS, colorless=True,
         params=(("kind", "card"), *_char("Bramblewood Owls")), size_key="edition"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Dolls: the kind is drawn, in the outfit's color; each accessory is drawn beside it.
# --------------------------------------------------------------------------

_DOL = (_T, "Dolls & Accessories", "Dolls")


def _doll(kind: str, cm: int, accessories: int, age: str, line: str | None = None,
          brand: str = _P) -> tuple:  # fmt: skip
    return (_kind(kind), ("item_height", "Item height", str(cm), "CMT", cm * 10.0),
            _count("accessory_count", "Accessory count", accessories), _age(age),
            *(_line(line, brand) if line else ()))  # fmt: skip


def _dp(kind: str, accessories: int, line: str | None = None) -> tuple[tuple[str, str], ...]:
    return (("kind", kind), ("accessories", str(accessories)), *_char(line))


_FIGS = Contents((2, "grown-up figures"), (2, "child figures"))

DOLLS = (
    TRow("DOLFSH", "Fashion Doll with Wardrobe Accessories", _P, _T, _DOL, "Doll", 15.0, "doll",
         "A poseable fashion doll with long brushable hair. Comes with a handbag, a sun hat, "
         "a pair of shoes and a hairbrush. For ages 3 and up.",
         (PINK, BLUE, PURPLE), _doll("Fashion Doll", 30, 4, "3+ years"), audience=KIDS,
         params=_dp("fashion", 4)),
    TRow("DOLBBY", "Soft-Bodied Baby Doll with Bottle", _L, _T, _DOL, "Doll", 20.0, "doll",
         "A cuddly baby doll with a soft body, a vinyl head and eyes that close. Comes with a "
         "feeding bottle and a blanket. For ages 18 months and up.",
         (LILAC, YELLOW, WHITE), _doll("Baby Doll", 36, 2, "18+ months"), audience=TODDLER,
         params=_dp("baby", 2)),
    TRow("DOLBTH", "Bath-Time Baby Doll", _P, _T, _DOL, "Doll", 14.0, "doll",
         "An all-vinyl baby doll that can go in the bath. Comes with a sponge, a hooded towel "
         "and a duck. For ages 2 and up.",
         (PINK, BLUE), _doll("Baby Doll", 30, 3, "2+ years"), audience=TODDLER,
         params=_dp("baby", 3)),
    TRow("DOLRAG", "Bramblewood Owls Rag Doll", _L, _T, _DOL, "Doll", 18.0, "doll",
         "A soft rag doll with yarn hair, stitched eyes and an owl patch on her dress, safe "
         "from birth. Machine washable at 30 degrees.",
         (GREEN, RED), _doll("Rag Doll", 40, 0, "0+ months", "Bramblewood Owls", _L),
         audience=BABY, params=_dp("rag", 0, "Bramblewood Owls")),
    TRow("DOLDWB", "Driftwhistle Bay Sailor Rag Doll", _K, _T, _DOL, "Doll", 16.0, "doll",
         "A rag doll in a striped sailor's top, from the harbour town of Driftwhistle Bay. "
         "Comes with a sailor's hat. For ages 3 and up.",
         (NAVY, RED), _doll("Rag Doll", 30, 1, "3+ years", "Driftwhistle Bay", _K),
         audience=KIDS, params=_dp("rag", 1, "Driftwhistle Bay")),
    TRow("DOLHSE", _FIGS.title("Doll's House Family Figures"), _K, _T, _DOL, "Doll", 12.0,
         "doll", _FIGS.text("Bendy figures that sit, stand and fit any doll's house. "
                            "For ages 3 and up."),
         (BLUE, RED), (*_doll("Doll's House Figures", 12, 0, "3+ years"), *_FIGS.attrs),
         audience=KIDS, params=(("kind", "house"), _counts(_FIGS))),
)  # fmt: skip

# --------------------------------------------------------------------------
# Wooden toys: the Natural colorway is unpainted, the others painted (``finish``).
# --------------------------------------------------------------------------

_WDN = (_T, "Baby & Toddler", "Wooden Toys")


def _wood(kind: str, age: str, fsc: bool, line: str | None = None, brand: str = _P) -> tuple:
    return (_kind(kind), _age(age), ("material", "Material", "Wooden"),
            _a("fsc_certified", "FSC certified", _yes(fsc)), *(_line(line, brand) if line else ()))  # fmt: skip


_RINGS = Contents((5, "rings"), (1, "base with a peg"))
_SORTER = Contents((1, "sorting cube"), (6, "shapes"))
_TRAIN = Contents((1, "engine"), (2, "carriages"), (6, "track pieces"))
_PUZZLE = Contents((6, "animal pieces"))

WOODEN_TOYS = (
    TRow("WDNSTK", _RINGS.title("Wooden Stacking Rings"), _L, _T, _WDN, "Wooden Toy", 12.0,
         "wooden_toy", _RINGS.text("Smooth rings that stack biggest to smallest, a first "
                                   "lesson in size. For ages 12 months and up."),
         (NATURAL, RED, BLUE), (*_wood("Stacking Rings", "12+ months", True), *_RINGS.attrs),
         audience=TODDLER, params=(("kind", "stacking"), _counts(_RINGS)),
         finish_by_color=True),
    TRow("WDNSRT", _SORTER.title("Wooden Shape Sorter Cube"), _K, _T, _WDN, "Wooden Toy", 16.0,
         "wooden_toy", _SORTER.text("Post each chunky shape through its hole, then lift "
                                    "the lid to start again. For ages 12 months and up."),
         (NATURAL, YELLOW), (*_wood("Shape Sorter", "12+ months", True), *_SORTER.attrs),
         audience=TODDLER, params=(("kind", "sorter"), _counts(_SORTER)),
         finish_by_color=True),
    TRow("WDNTRN", _TRAIN.title("Wooden Train Set"), _P, _T, _WDN, "Wooden Toy", 22.0,
         "wooden_toy", _TRAIN.text("Magnetic couplings and grooved track that joins the "
                                   "common wooden railways. For ages 3 and up."),
         (RED, NATURAL), (*_wood("Train Set", "3+ years", True), *_TRAIN.attrs),
         audience=KIDS, params=(("kind", "train"), _counts(_TRAIN)),
         finish_by_color=True),
    TRow("WDNPZL", _PUZZLE.title("Wooden Farm Animal Peg Puzzle"), _L, _T, _WDN, "Wooden Toy",
         10.0, "wooden_toy", _PUZZLE.text("Each piece has a peg to lift it out and a "
                                          "picture under it to match. For ages 18 months and "
                                          "up."),
         (NATURAL, GREEN), (*_wood("Wooden Puzzle", "18+ months", False), *_PUZZLE.attrs),
         audience=TODDLER, params=(("kind", "puzzle"), _counts(_PUZZLE)),
         finish_by_color=True),
    TRow("WDNPUL", "Driftwhistle Bay Pull-Along Whale", _K, _T, _WDN, "Wooden Toy", 14.0,
         "wooden_toy", "A wooden whale on wheels with a flapping tail and a long pull cord, for "
         "new walkers. For ages 12 months and up.",
         (BLUE, NATURAL), _wood("Pull-Along Toy", "12+ months", True, "Driftwhistle Bay", _K),
         audience=TODDLER, params=(("kind", "pull_along"), *_char("Driftwhistle Bay")),
         finish_by_color=True),
    TRow("WDNDOG", "Wooden Pull-Along Dachshund", _P, _T, _WDN, "Wooden Toy", 15.0,
         "wooden_toy", "A long dog in jointed sections that wiggles as it rolls, on a pull "
         "cord. For ages 12 months and up.",
         (NATURAL, RED), _wood("Pull-Along Toy", "12+ months", False), audience=TODDLER,
         params=(("kind", "pull_along"), ("animal", "dog")), finish_by_color=True),
)  # fmt: skip

# --------------------------------------------------------------------------
# Role play: the kind is drawn in the record's color; a tea set draws every piece.
# --------------------------------------------------------------------------

_RPL = (_T, "Pretend Play", "Role Play Toys")


def _rp(kind: str, age: str, material: str, line: str | None = None, brand: str = _P) -> tuple:
    return (_kind(kind), _age(age), ("material", "Material", material),
            *(_line(line, brand) if line else ()))  # fmt: skip


_TEA = Contents((1, "teapot"), (4, "cups"), (4, "saucers"), (1, "milk jug"))

ROLE_PLAY = (
    TRow("RPLKIT", "Wooden Play Kitchen with Oven and Sink", _L, _T, _RPL, "Role Play Toy",
         90.0, "role_play", "A play kitchen with a hob that clicks, an oven door that opens, a "
         "sink with a tap that turns and a shelf for pans. For ages 3 and up.",
         (WHITE, BLUE, PINK), _rp("Play Kitchen", "3+ years", "Wooden"), audience=KIDS,
         params=(("kind", "kitchen"),)),
    TRow("RPLKTP", "Compact Play Kitchen with Sounds", _P, _T, _RPL, "Role Play Toy", 45.0,
         "role_play", "A small play kitchen that fits a corner, with a sizzling hob, a "
         "microwave and a fridge door. Wipe clean. For ages 2 and up.",
         (RED, GREY), _rp("Play Kitchen", "2+ years", "Plastic"), audience=TODDLER,
         params=(("kind", "kitchen"),)),
    TRow("RPLTLB", "Kids' Wooden Tool Bench", _K, _T, _RPL, "Role Play Toy", 40.0, "role_play",
         "A sturdy workbench with a vice that winds, a saw, a hammer and nuts and bolts that "
         "twist on. For ages 3 and up.",
         (NATURAL, BLUE), _rp("Tool Bench", "3+ years", "Wooden"), audience=KIDS,
         params=(("kind", "tool_bench"),)),
    TRow("RPLDOC", "Doctor's Kit in a Carry Case", _P, _T, _RPL, "Role Play Toy", 15.0,
         "role_play", "A carry case with a stethoscope, a thermometer, a syringe and a "
         "bandage, ready for a teddy check-up. For ages 3 and up.",
         (RED, BLUE), _rp("Doctor's Kit", "3+ years", "Plastic"), audience=KIDS,
         params=(("kind", "doctor"),)),
    TRow("RPLTIL", "Toy Shop Till with Scanner", _L, _T, _RPL, "Role Play Toy", 25.0,
         "role_play", "A shop till with a scanner that beeps, a cash drawer that pops open and "
         "a set of play coins and notes. For ages 3 and up.",
         (YELLOW, BLUE), _rp("Shop Till", "3+ years", "Plastic"), audience=KIDS,
         params=(("kind", "shop_till"),)),
    TRow("RPLTEA", _TEA.title("Driftwhistle Bay Wooden Tea Set"), _K, _T, _RPL,
         "Role Play Toy", 20.0, "role_play",
         _TEA.text("Painted with the Driftwhistle Bay boats, for teddy bear picnics. For ages "
                   "3 and up."),
         (BLUE, PINK), (*_rp("Tea Set", "3+ years", "Wooden", "Driftwhistle Bay", _K),
                        *_TEA.attrs),
         audience=KIDS, params=(("kind", "tea_set"), _counts(_TEA),
                                *_char("Driftwhistle Bay"))),
)  # fmt: skip

# --------------------------------------------------------------------------
# Arts and crafts: the kit's contents are drawn, piece by piece; the theme is a SKU.
# --------------------------------------------------------------------------

_CRF = (_T, "Arts & Crafts", "Craft Kits")


def _craft(kind: str, age: str, line: str | None = None, brand: str = _P) -> tuple:
    return (_kind(kind), _age(age), *(_line(line, brand) if line else ()))


def _themes(price: float, *themes: str) -> tuple[tuple[str, float], ...]:
    return tuple((t, price) for t in themes)


_PAINT15 = Contents((12, "paint colors"), (2, "brushes"), (1, "water pot"))
_PAINT9 = Contents((6, "paint colors"), (2, "brushes"), (1, "water pot"))
_BEADS = Contents((8, "tubs of beads"), (4, "elastic cords"), (1, "sorting tray"))
_SLIME = Contents((6, "tubs of slime base"), (3, "glitter pots"), (1, "mixing cup"))
_KNIT = Contents((2, "knitting needles"), (3, "balls of yarn"), (1, "pattern booklet"))
_COLOR = Contents((24, "colored pencils"), (1, "sharpener"), (1, "coloring book"))


def _cp(kind: str, kit: Contents, line: str | None = None) -> tuple[tuple[str, str], ...]:
    return (("kind", kind), _counts(kit), *_char(line))


CRAFT_KITS = (
    TRow("CRFPNT", _PAINT15.title("Watercolor Painting Set"), _L, _T, _CRF,
         "Arts and Crafts Kit", 12.0, "craft_kit",
         _PAINT15.text("Bright pans of watercolor in a tin with a mixing lid, and a pad of "
                       "pictures to paint. For ages 5 and up."),
         (BLUE,), (*_craft("Painting Set", "5+ years"), *_PAINT15.attrs),
         _themes(12.0, "Unicorns", "Dinosaurs", "Space"), audience=KIDS, colorless=True,
         params=_cp("painting", _PAINT15), size_key="theme"),
    TRow("CRFOWL", _PAINT9.title("Bramblewood Owls First Painting Set"), _L, _T, _CRF,
         "Arts and Crafts Kit", 8.0, "craft_kit",
         _PAINT9.text("Chunky brushes and washable paints, with owl pictures to fill in. For "
                      "ages 3 and up."),
         (GREEN,), (*_craft("Painting Set", "3+ years", "Bramblewood Owls", _L),
                    *_PAINT9.attrs),
         _themes(8.0, "Animals"), audience=KIDS, colorless=True,
         params=_cp("painting", _PAINT9, "Bramblewood Owls"), size_key="theme"),
    TRow("CRFBED", _BEADS.title("Bead Jewelry Making Kit"), _P, _T, _CRF, "Arts and Crafts Kit",
         14.0, "craft_kit",
         _BEADS.text("Over 600 beads sorted by color, to thread bracelets and necklaces. "
                     "Not for under 3s. For ages 6 and up."),
         (PINK,), (*_craft("Bead Kit", "6+ years"), *_BEADS.attrs),
         _themes(14.0, "Mermaids", "Rainbows"), audience=KIDS, colorless=True,
         params=_cp("bead", _BEADS), size_key="theme"),
    TRow("CRFSLM", _SLIME.title("Slime Making Kit"), _K, _T, _CRF, "Arts and Crafts Kit",
         13.0, "craft_kit",
         _SLIME.text("Mix, stretch and sparkle: glue-free slime base with glitter to stir "
                     "in. Adult supervision needed. For ages 8 and up."),
         (TEAL,), (*_craft("Slime Kit", "8+ years"), *_SLIME.attrs),
         _themes(13.0, "Space", "Unicorns"), audience=KIDS, colorless=True,
         params=_cp("slime", _SLIME), size_key="theme"),
    TRow("CRFKNT", _KNIT.title("Learn to Knit Kit"), _L, _T, _CRF, "Arts and Crafts Kit", 15.0,
         "craft_kit",
         _KNIT.text("Short bamboo needles, soft chunky yarn and step-by-step pictures to knit "
                    "a first scarf. For ages 8 and up."),
         (LILAC,), (*_craft("Knitting Kit", "8+ years"), *_KNIT.attrs),
         _themes(15.0, "Rainbows", "Animals"), audience=KIDS, colorless=True,
         params=_cp("knitting", _KNIT), size_key="theme"),
    TRow("CRFCOL", _COLOR.title("Moonmoth Rangers Coloring Set"), _P, _T, _CRF,
         "Arts and Crafts Kit", 10.0, "craft_kit",
         _COLOR.text("Soft-lead pencils in a tin, and a book of Rangers adventures to color. "
                     "For ages 4 and up."),
         (NAVY,), (*_craft("Coloring Set", "4+ years", "Moonmoth Rangers"), *_COLOR.attrs),
         _themes(10.0, "Space"), audience=KIDS, colorless=True,
         params=_cp("coloring", _COLOR, "Moonmoth Rangers"), size_key="theme"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Ride-ons: the kind is drawn with its wheels, in the record's color.
# --------------------------------------------------------------------------

_RID = (_T, "Outdoor Toys", "Ride-On Toys")


def _ride(kind: str, age: str, kg: int, inches: int | None, wheels: int,
          line: str | None = None, brand: str = _P) -> tuple:  # fmt: skip
    """A ride-on's attributes. ``inches`` is a fixed wheel size (a scooter's, a ride-on car's);
    a bike or a trike sells its wheel size as a SKU axis instead (:func:`_wheel_sizes`), so
    it passes ``None`` and the size is stated once."""
    fixed = (("wheel_size", "Wheel size", str(inches), "INH", canonical(str(inches), "INH")),
             ) if inches else ()  # fmt: skip
    return (_kind(kind), _age(age), ("max_weight_kg", "Maximum weight", str(kg), "KGM",
            canonical(str(kg), "KGM")), *fixed,
            _count("wheel_count", "Wheel count", wheels), *(_line(line, brand) if line else ()))  # fmt: skip


def _rpm(kind: str, wheels: int, line: str | None = None,
         inches: int | None = None) -> tuple[tuple[str, str], ...]:
    """The drawing's params; a bike or a trike names its default wheel size, which each SKU's
    own ``wheel_size_in`` replaces, so each size is its own picture."""
    return (("kind", kind), ("wheels", str(wheels)), *_char(line),
            *((("wheel_size_in", str(inches)),) if inches else ()))  # fmt: skip


def _wheel_sizes(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A bike's or a trike's SKU sizes: wheel diameter in inches, and the price at it."""
    return tuple((str(n), p) for n, p in pairs)


_FIXED_WOOD = "natural birch plywood, left unpainted: the wood is the color"
_FIXED_RANGE = "the range livery: the Moonmoth Rangers navy and badge are what mark the range"

RIDE_ONS = (
    TRow("RIDBAL", "Balance Bike with Air Tires", _P, _T, _RID, "Ride-On Toy", 50.0, "ride_on",
         "A light balance bike with no pedals, so a child learns to steer and balance first. "
         "Air tires and a seat that rises as they grow. In three wheel sizes: 10, 12 and 14 "
         "inch. For ages 2 and up.",
         paint_range(RED, BLUE, GREEN), _ride("Balance Bike", "2+ years", 25, None, 2),
         _wheel_sizes((10, 45.0), (12, 50.0), (14, 58.0)), audience=TODDLER,
         params=_rpm("balance_bike", 2, inches=12), size_key="wheel_size_in"),
    TRow("RIDWDB", "Wooden Balance Bike", _L, _T, _RID, "Ride-On Toy", 60.0, "ride_on",
         "A birch plywood balance bike with rubber tires and a padded seat. In three wheel "
         "sizes: 10, 12 and 14 inch. For ages 3 and up.", (NATURAL,),
         _ride("Balance Bike", "3+ years", 30, None, 2),
         _wheel_sizes((10, 55.0), (12, 60.0), (14, 68.0)), audience=KIDS,
         params=_rpm("balance_bike", 2, inches=12), size_key="wheel_size_in",
         fixed_color=_FIXED_WOOD),
    TRow("RIDSC3", "Three-Wheel Kids' Scooter with Light-Up Wheels", _K, _T, _RID,
         "Ride-On Toy", 30.0, "ride_on",
         "Two wheels at the front for a steady ride, lean-to-steer, and wheels that glow as "
         "they roll. Folds flat. For ages 3 and up.",
         paint_range(PINK, BLUE, GREEN), _ride("Scooter", "3+ years", 50, 5, 3), audience=KIDS,
         params=_rpm("scooter", 3)),
    TRow("RIDSC2", "Moonmoth Rangers Folding Scooter", _P, _T, _RID, "Ride-On Toy", 35.0,
         "ride_on", "A two-wheel scooter with an adjustable bar, a rear brake and the "
         "Rangers' badge on the deck. Folds flat. For ages 5 and up.",
         (NAVY,), _ride("Scooter", "5+ years", 50, 6, 2, "Moonmoth Rangers"), audience=KIDS,
         params=_rpm("scooter", 2, "Moonmoth Rangers"), fixed_color=_FIXED_RANGE),
    TRow("RIDTRK", "Toddler Trike with Push Handle", _L, _T, _RID, "Ride-On Toy", 55.0,
         "ride_on", "A trike with a parent push handle that comes off as the child learns to "
         "pedal, a seat belt and a storage bin. In two wheel sizes: 10 and 12 inch. For ages "
         "18 months and up.",
         paint_range(RED, TEAL), _ride("Trike", "18+ months", 20, None, 3),
         _wheel_sizes((10, 55.0), (12, 62.0)), audience=TODDLER,
         params=_rpm("trike", 3, inches=10), size_key="wheel_size_in"),
    TRow("RIDCAR", "Push-Along Ride-On Car with Horn", _K, _T, _RID, "Ride-On Toy", 35.0,
         "ride_on", "A low ride-on car that little feet push along, with a horn that toots and "
         "a storage space under the seat. For ages 12 months and up.",
         paint_range(RED, PINK, YELLOW), _ride("Ride-On Car", "12+ months", 25, 6, 4),
         audience=TODDLER, params=_rpm("car", 4)),
)  # fmt: skip

ROWS = (*BUILDING_SETS, *JIGSAWS, *BOARD_GAMES, *DOLLS, *WOODEN_TOYS, *ROLE_PLAY, *CRAFT_KITS,
        *RIDE_ONS)  # fmt: skip


def docs() -> list[dict]:
    """Every toy row's catalog document."""
    return [r.doc() for r in ROWS]
