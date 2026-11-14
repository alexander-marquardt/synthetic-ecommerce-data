"""Card game (gen#424): family, party and strategy card games, sold as editions.

**Toys > Games > Card Games**: six named styles and sixteen themed ones ("Pixel Pets Party Card
Game", the theme on the box) from five invented brands, drawn by
:func:`kit_toys_play.card_game`. The players (a minimum and a maximum count, so "for 4
players" is a range filter), the play time in minutes, the kind and the age range are
structured entries; the SKUs are the editions. A card game has no color selector. The older
card games of Board Games keep their leaf. A breadth type since gen#960: ``derivable``, so the
scaled build draws more card games by the values their titles show (the kind, and a themed
row's theme); the players, the play time and the age range stay the template's.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_toys_play,  # noqa: F401 -- registers card_game
)
from synthetic_ecommerce_data.domains.retail.toys_play_common import (
    BLUE,
    EIGHT,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PUDDLE,
    RED,
    YELLOW,
    age,
    count,
    kind,
    sizes,
    style,
    toy_decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, a

_PATH = ("Toys", "Games", "Card Games")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"


def _game(code: str, title: str, brand: str, shape_kind: str, lo: int, hi: int, minutes: int,
          years: str, desc: str, price: float, travel: float, theme: str = "") -> Row:  # fmt: skip
    return style(
        code,
        title,
        brand,
        _PATH,
        "Card Game",
        "card_game",
        desc,
        EIGHT[:1],
        (
            *((a("theme", "Theme", theme),) if theme else ()),
            kind(f"{shape_kind.title()} Card Game"),
            count("min_players", "Minimum players", lo),
            count("max_players", "Maximum players", hi),
            a("play_time", "Play time (minutes)", str(minutes)),
            age(years),
        ),
        price,
        sizes(("Standard", price), ("Travel", travel), ("Deluxe", price + 6.0)),
        "edition",
        params=(("kind", f"{shape_kind} card game"), *((("theme", theme.lower()),)[: bool(theme)])),
        colorless=True,
    )


def _themed(code: str, theme: str, brand: str, shape_kind: str, lo: int, hi: int, minutes: int,
            years: int, price: float) -> Row:  # fmt: skip
    """A themed card game, "<theme> <kind> Card Game": the text names the theme and the kind
    and nothing that holds only for one of them, so a derived style that swaps either reads
    true."""
    desc = (f"Every card in the {theme} deck counts, so play each one with care. A {shape_kind} "
            f"card game for {lo} to {hi} players in about {minutes} minutes. For ages {years} "
            "and up.")  # fmt: skip
    title = f"{theme} {shape_kind.title()} Card Game"
    return _game(code, title, brand, shape_kind, lo, hi, minutes, f"{years}+ years", desc, price,
                 round(price * 0.65), theme)  # fmt: skip


_ROWS = (
    _game("CGMFA1", "Snap Along Family Card Game", THISTLE, "family", 2, 6, 20, "5+ years",
          "Match the pictures and shout snap. A family card game for 2 to 6 players in "
          "about 20 minutes. For ages 5 and up.", 8.0, 5.0),
    _game("CGMFA2", "Hedgehog Hurry Family Card Game", FERNBY, "family", 2, 4, 15, "8+ years",
          "Race to empty your hand and keep your hedgehogs out of the puddle. A family "
          "card game for 2 to 4 players in about 15 minutes. For ages 8 and up.", 9.0, 6.0),
    _game("CGMPA1", "Giggle Pile Party Card Game", PUDDLE, "party", 4, 10, 30, "12+ years",
          "Pull a card, read it out and keep a straight face. A party card game for 4 to "
          "10 players in about 30 minutes. For ages 12 and up.", 14.0, 9.0),
    _game("CGMPA2", "Dare or Doodle Party Card Game", CALDERBY, "party", 3, 8, 25, "10+ years",
          "Draw it, mime it or hum it before the card runs out. A party card game for 3 to "
          "8 players in about 25 minutes. For ages 10 and up.", 12.0, 8.0),
    _game("CGMST1", "Quayside Gambit Strategy Card Game", PUDDLE, "strategy", 2, 4, 45,
          "12+ years", "Build a trade route card by card and block your rivals. A strategy "
          "card game for 2 to 4 players in about 45 minutes. For ages 12 and up.", 16.0, 11.0),
    _game("CGMST2", "Lantern Court Strategy Card Game", FERNBY, "strategy", 2, 5, 60,
          "14+ years", "Draft, bluff and trade favours at court. A strategy card game for 2 "
          "to 5 players in about an hour. For ages 14 and up.", 18.0, 12.0),
    *(
        _themed(*r)
        for r in (
            ("CGMTH01", "Cosmic Comets", CALDERBY, "family", 2, 6, 20, 7, 9.0),
            ("CGMTH02", "Pixel Pets", THISTLE, "party", 3, 8, 25, 8, 11.0),
            ("CGMTH03", "Royal Banquet", LANTERNBY, "strategy", 2, 4, 45, 12, 15.0),
            ("CGMTH04", "Monster Mash", CALDERBY, "party", 4, 10, 30, 10, 12.0),
            ("CGMTH05", "Sunken Ship", CALDERBY, "strategy", 2, 5, 40, 10, 14.0),
            ("CGMTH06", "Fairy Glen", THISTLE, "family", 2, 4, 15, 5, 8.0),
            ("CGMTH07", "Racing Snails", LANTERNBY, "family", 2, 6, 20, 6, 9.0),
            ("CGMTH08", "Ninja Kittens", THISTLE, "family", 2, 5, 15, 7, 10.0),
            ("CGMTH09", "Robot Rumble", CALDERBY, "party", 3, 8, 30, 9, 12.0),
            ("CGMTH10", "Jungle Parade", THISTLE, "strategy", 2, 4, 50, 12, 16.0),
            ("CGMTH11", "Ice Kingdom", LANTERNBY, "party", 4, 12, 35, 12, 13.0),
            ("CGMTH12", "Market Day", LANTERNBY, "strategy", 2, 4, 40, 10, 15.0),
            ("CGMTH13", "Garden Gnomes", CALDERBY, "family", 2, 5, 20, 6, 9.0),
            ("CGMTH14", "Penguin Picnic", THISTLE, "party", 3, 9, 25, 7, 11.0),
            ("CGMTH15", "Dragon Eggs", LANTERNBY, "strategy", 2, 4, 45, 10, 14.0),
            ("CGMTH16", "Treehouse Club", FERNBY, "family", 2, 6, 20, 6, 9.0),
        )
    ),
)  # fmt: skip
_BRAND = "Dewhatch"

SPEC = TypeSpec(
    key="card_game",
    department="Toys",
    product_type="Card Game",
    rows=_ROWS,
    derivable=True,
    decoys=(
        toy_decoy(6, "kite", "generic", _ROWS[0], 20, "Kite Field Card Game",
                  "From the Kite Field range, named after a windy meadow; it is a game of cards "
                  "and does not fly.", color=RED),
        toy_decoy(6, "marble run", "generic", _ROWS[1], 21, "Marble Run Dene Card Game",
                  "From the Marble Run Dene range, named after a valley of round stones; it is "
                  "a game of cards.", color=GREEN),
        toy_decoy(4, "foil card game", MATERIAL_CLAIM, _ROWS[2], 22, "Foil-Look Card Game",
                  "A card game in a box printed to shine like foil; there is no foil on it.",
                  color=YELLOW),
        toy_decoy(7, "water gun", "generic", _ROWS[3], 23, "Dewhatch Water Gun Card Game",
                  "A party card game from Dewhatch; the water gun is only in the title, "
                  "nothing in the box squirts.", brand=_BRAND, color=BLUE),
    ),
    owners=((_BRAND, "own"),),
)  # fmt: skip
