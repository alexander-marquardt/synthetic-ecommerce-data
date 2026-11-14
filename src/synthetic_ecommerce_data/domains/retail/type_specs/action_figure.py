"""Action Figure (Toys), a breadth type of gen#960 (slice 2).

**Toys > Figures & Playsets > Action Figures.** Each title shows the figure's character and its
kind ("Captain Comet Space Action Figure"), so the scaled build draws more action figures by
those two values, and the drawing follows them (:func:`kit_toys_figures.action_figure`: a cape
for a superhero, a helmet for a space figure, a hat for an adventure figure, the character on
the card). Every template is sold in the six main colors of the suit (ruling 2026-10-13,
gen#275) and is for ages 4 and up, so a derived style keeps its age. Every character is
invented (ruling 2026-10-30, gen#720).
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_toys_figures,  # noqa: F401 -- registers action_figure
)
from synthetic_ecommerce_data.domains.retail.toys_play_common import (
    BLACK,
    BLUE,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PUDDLE,
    RED,
    WHITE,
    YELLOW,
    age,
    kind,
    style,
    toy_decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, a

_PATH = ("Toys", "Figures & Playsets", "Action Figures")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)

#: The opening sentences: each names the character and nothing that holds for one kind only.
_LEADS = (
    "{c} is ready for the next mission.",
    "{c} leads the team into every adventure.",
    "Pose {c} for a battle on the rug or for the display shelf.",
    "{c} comes with a spare pair of hands and a display stand.",
)


def _figure(code: str, character: str, series: str, brand: str, lead: str, price: float) -> Row:
    """An action figure: "<character> <series> Action Figure", in the six main colors."""
    toy_type = f"{series} Action Figure"
    desc = (f"{lead.format(c=character)} This {toy_type.lower()} has twelve points of "
            f"articulation. For ages 4 and up.")  # fmt: skip
    return style(
        code,
        f"{character} {toy_type}",
        brand,
        _PATH,
        "Action Figure",
        "action_figure",
        desc,
        SIX,
        (a("character", "Character", character), kind(toy_type), age("4+ years")),
        price,
        params=(("kind", toy_type.lower()), ("character", character.lower())),
    )


ROWS = (
    _figure("ACFCOM", "Captain Comet", "Space", CALDERBY, _LEADS[0], 12.0),
    _figure("ACFBAD", "Night Badger", "Superhero", LANTERNBY, _LEADS[1], 10.0),
    _figure("ACFOTT", "Storm Otter", "Adventure", THISTLE, _LEADS[2], 9.0),
    _figure("ACFRAN", "Lightning Lancer", "Superhero", FERNBY, _LEADS[3], 11.0),
    _figure("ACFGOL", "Mossback Golem", "Adventure", PUDDLE, _LEADS[0], 14.0),
    _figure("ACFVIP", "Volt Viper", "Space", CALDERBY, _LEADS[1], 13.0),
    _figure("ACFKNI", "Tidal Knight", "Superhero", LANTERNBY, _LEADS[2], 12.0),
    _figure("ACFHAW", "Swift Hawk", "Adventure", THISTLE, _LEADS[3], 10.0),
    _figure("ACFLYN", "Frost Lynx", "Space", FERNBY, _LEADS[0], 11.0),
    _figure("ACFMAN", "Mantis Prime", "Superhero", PUDDLE, _LEADS[1], 15.0),
    _figure("ACFRAY", "Rocket Ray", "Space", LANTERNBY, _LEADS[2], 9.0),
    _figure("ACFMOT", "Dusk Moth", "Adventure", CALDERBY, _LEADS[3], 8.0),
    _figure("ACFCMD", "Quartz Commander", "Space", THISTLE, _LEADS[0], 16.0),
    _figure("ACFTOR", "Thunder Tortoise", "Superhero", FERNBY, _LEADS[1], 9.0),
    _figure("ACFWOL", "Echo Wolf", "Adventure", PUDDLE, _LEADS[2], 12.0),
    _figure("ACFSTA", "Solar Stag", "Superhero", CALDERBY, _LEADS[3], 13.0),
    _figure("ACFMET", "Major Meteor", "Space", LANTERNBY, _LEADS[0], 14.0),
    _figure("ACFGIZ", "Professor Gizmo", "Adventure", THISTLE, _LEADS[1], 11.0),
    _figure("ACFPAN", "Nova Panther", "Superhero", FERNBY, _LEADS[2], 12.0),
    _figure("ACFSPK", "Sergeant Sparrow", "Space", PUDDLE, _LEADS[3], 10.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="action_figure",
    department="Toys",
    product_type="Action Figure",
    rows=ROWS,
    derivable=True,
    decoys=(
        toy_decoy(6, "kite", "generic", ROWS[0], 50, "Kite Flyer Space Action Figure",
                  "From the Kite Flyer range, named after a hero who glides between rooftops; "
                  "it is an action figure and does not fly.", color=BLUE),
        toy_decoy(4, "metal action figure", MATERIAL_CLAIM, ROWS[1], 51,
                  "Metal-Look Superhero Action Figure",
                  "A superhero action figure painted to look like brushed steel; the figure "
                  "is plastic.", color=BLACK),
    ),
)  # fmt: skip
