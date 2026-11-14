"""Board Game (Toys), registered by its spec (gen#537); a breadth type since gen#960.

**Toys > Games > Board Games.** The older styles stay in ``toys_rows`` as templates only (the
``homes`` entry). The rows here are ``derivable``: each title shows the game's theme and its kind
("Pirate Island Strategy Board Game"), so the scaled build draws more board games by those two
values, and the drawing follows the kind (:func:`kit_toys.board_game`: a track for a family
game, a hex board for a strategy game, a sand timer for a party game). The players, the play
time and the age range stay with the template (``scale_text.FROZEN_KEYS``). A board game has no
color selector; its SKUs are the editions.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_toys,  # noqa: F401 -- registers board_game
)
from synthetic_ecommerce_data.domains.retail.toys_play_common import (
    BLUE,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    ORANGE,
    PINK,
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
from synthetic_ecommerce_data.domains.retail.type_registry import Home, Row, TypeSpec, a

_PATH = ("Toys", "Games", "Board Games")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"


def _game(code: str, theme: str, game: str, brand: str, lo: int, hi: int, minutes: int,
          years: int, lead: str, color, price: float) -> Row:  # fmt: skip
    """A board game: "<theme> <kind> Board Game"; ``lead`` is the opening sentence, which
    names the theme ({t}), and the second names the kind, as the swap of a derived style needs."""
    toy_type = f"{game} Board Game"
    desc = (f"{lead.format(t=theme)} A {toy_type.lower()} for {lo} to {hi} players in about {minutes} minutes. "
            f"For ages {years} and up. The travel edition packs into a small tin; the deluxe "
            f"edition adds a second board.")  # fmt: skip
    return style(
        code,
        f"{theme} {toy_type}",
        brand,
        _PATH,
        "Board Game",
        "board_game",
        desc,
        (color,),
        (
            a("theme", "Theme", theme),
            kind(toy_type),
            count("min_players", "Minimum players", lo),
            count("max_players", "Maximum players", hi),
            a("play_time", "Play time (minutes)", str(minutes)),
            age(f"{years}+ years"),
        ),
        price,
        sizes(("Standard", price), ("Travel", round(price * 0.6)), ("Deluxe", price + 15.0)),
        "edition",
        params=(("kind", toy_type.lower()), ("theme", theme.lower())),
        colorless=True,
    )


#: The opening sentences: each names the board by its theme and nothing else, so a derived
#: style that swaps the theme or the kind reads true.
_LEADS = (
    "Take turns across the {t} board and be the first to reach the final square.",
    "Every space on the {t} board holds a surprise, and the first player home wins.",
    "Collect a token from each corner of the {t} board before the others do.",
    "Plan each move on the {t} board and keep one step ahead of the other players.",
)

ROWS = (
    _game("BGMPIR", "Pirate Island", "Family", PUDDLE, 2, 6, 30, 6, _LEADS[0], RED, 20.0),
    _game("BGMDIN", "Dinosaur Valley", "Family", FERNBY, 2, 4, 25, 5, _LEADS[1], GREEN, 18.0),
    _game("BGMJUN", "Jungle Temple", "Strategy", PUDDLE, 2, 4, 60, 10, _LEADS[2], GREEN, 30.0),
    _game("BGMHAU", "Haunted Manor", "Party", THISTLE, 4, 10, 40, 10, _LEADS[3], PINK, 22.0),
    _game("BGMROC", "Rocket Station", "Strategy", CALDERBY, 2, 5, 75, 12, _LEADS[0], BLUE, 35.0),
    _game("BGMDRA", "Dragon Mountain", "Family", LANTERNBY, 2, 5, 35, 7, _LEADS[1], ORANGE, 22.0),
    _game("BGMREE", "Treasure Reef", "Party", THISTLE, 3, 8, 30, 8, _LEADS[2], BLUE, 20.0),
    _game("BGMFOR", "Wildwood Forest", "Strategy", THISTLE, 2, 4, 90, 12, _LEADS[3], GREEN, 38.0),
    _game("BGMARC", "Arctic Expedition", "Family", FERNBY, 2, 6, 30, 6, _LEADS[0], BLUE, 19.0),
    _game("BGMCAR", "Desert Caravan", "Strategy", LANTERNBY, 2, 4, 60, 10, _LEADS[1], YELLOW, 32.0),
    _game("BGMROB", "Robot Factory", "Party", CALDERBY, 4, 12, 45, 12, _LEADS[2], ORANGE, 24.0),
    _game("BGMWIZ", "Wizard Academy", "Family", PUDDLE, 2, 4, 40, 8, _LEADS[3], PINK, 21.0),
    _game("BGMVOY", "Ocean Voyage", "Strategy", LANTERNBY, 2, 5, 80, 12, _LEADS[0], BLUE, 34.0),
    _game("BGMVOL", "Volcano Quest", "Party", FERNBY, 3, 8, 30, 8, _LEADS[1], RED, 18.0),
    _game("BGMFAR", "Farmyard Frolic", "Family", LANTERNBY, 2, 4, 20, 4, _LEADS[2], YELLOW, 15.0),
    _game("BGMCAS", "Castle Siege", "Strategy", PUDDLE, 2, 4, 75, 12, _LEADS[3], RED, 33.0),
    _game("BGMCAN", "Candy Kingdom", "Family", CALDERBY, 2, 4, 25, 5, _LEADS[0], PINK, 17.0),
    _game("BGMMER", "Mermaid Lagoon", "Party", LANTERNBY, 3, 8, 30, 7, _LEADS[1], BLUE, 19.0),
    _game("BGMSAF", "Safari Trail", "Family", THISTLE, 2, 6, 35, 6, _LEADS[2], YELLOW, 20.0),
    _game("BGMVIK", "Viking Harbour", "Strategy", FERNBY, 2, 4, 70, 12, _LEADS[3], RED, 34.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="board_game",
    department="Toys",
    product_type="Board Game",
    rows=ROWS,
    derivable=True,
    decoys=(
        toy_decoy(6, "jigsaw", "generic", ROWS[0], 40, "Jigsaw Junction Family Board Game",
                  "From the Jigsaw Junction range, named after a railway crossing; it is a board "
                  "game, and there are no puzzle pieces in the box.", color=GREEN),
        toy_decoy(4, "wooden board game", MATERIAL_CLAIM, ROWS[4], 41,
                  "Wooden-Look Strategy Board Game",
                  "A strategy board game in a box printed to look like oak; the board and pieces "
                  "are card and plastic.", color=ORANGE),
    ),
    homes=(Home("toys_rows", False),),
)  # fmt: skip
