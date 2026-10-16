"""Card game (gen#424): family, party and strategy card games, sold as editions.

**Toys > Games > Card Games**: six styles from three invented brands, drawn by
:func:`kit_toys_play.card_game`. The players (a minimum and a maximum count, so "for 4
players" is a range filter), the play time in minutes, the kind and the age range are
structured entries; the SKUs are the editions. A card game has no color selector. The older
card games of Board Games keep their leaf. Not derivable: authored rows only.
"""

from __future__ import annotations

import kit_toys_play  # noqa: F401 -- registers card_game
from toys_play_common import EIGHT, FERNBY, PIPWICK, PUDDLE, age, count, kind, sizes, style
from type_registry import Row, TypeSpec, a

_PATH = ("Toys", "Games", "Card Games")


def _game(code: str, title: str, brand: str, shape_kind: str, lo: int, hi: int, minutes: int,
          years: str, desc: str, price: float, travel: float) -> Row:  # fmt: skip
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
            kind(f"{shape_kind.title()} Card Game"),
            count("min_players", "Minimum players", lo),
            count("max_players", "Maximum players", hi),
            a("play_time", "Play time (minutes)", str(minutes)),
            age(years),
        ),
        price,
        sizes(("Standard", price), ("Travel", travel), ("Deluxe", price + 6.0)),
        "edition",
        params=(("kind", shape_kind),),
        colorless=True,
    )


SPEC = TypeSpec(
    key="card_game",
    department="Toys",
    product_type="Card Game",
    rows=(
        _game("CGMFA1", "Snap Along Family Card Game", PIPWICK, "family", 2, 6, 20, "5+ years",
              "Match the pictures and shout snap. A family card game for 2 to 6 players in "
              "about 20 minutes. For ages 5 and up.", 8.0, 5.0),
        _game("CGMFA2", "Hedgehog Hurry Family Card Game", FERNBY, "family", 2, 4, 15, "8+ years",
              "Race to empty your hand and keep your hedgehogs out of the puddle. A family "
              "card game for 2 to 4 players in about 15 minutes. For ages 8 and up.", 9.0, 6.0),
        _game("CGMPA1", "Giggle Pile Party Card Game", PUDDLE, "party", 4, 10, 30, "12+ years",
              "Pull a card, read it out and keep a straight face. A party card game for 4 to "
              "10 players in about 30 minutes. For ages 12 and up.", 14.0, 9.0),
        _game("CGMPA2", "Dare or Doodle Party Card Game", PIPWICK, "party", 3, 8, 25, "10+ years",
              "Draw it, mime it or hum it before the card runs out. A party card game for 3 to "
              "8 players in about 25 minutes. For ages 10 and up.", 12.0, 8.0),
        _game("CGMST1", "Saltmarsh Gambit Strategy Card Game", PUDDLE, "strategy", 2, 4, 45,
              "12+ years", "Build a trade route card by card and block your rivals. A strategy "
              "card game for 2 to 4 players in about 45 minutes. For ages 12 and up.", 16.0, 11.0),
        _game("CGMST2", "Lantern Court Strategy Card Game", FERNBY, "strategy", 2, 5, 60,
              "14+ years", "Draft, bluff and trade favours at court. A strategy card game for 2 "
              "to 5 players in about an hour. For ages 14 and up.", 18.0, 12.0),
    ),
)  # fmt: skip
