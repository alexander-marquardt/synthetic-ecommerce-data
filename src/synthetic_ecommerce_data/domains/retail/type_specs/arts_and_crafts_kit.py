"""Arts and Crafts Kit (Toys), registered by its spec (gen#537), a breadth type of gen#960 (slice 3).

The older craft kits stay in the shared row modules named by ``homes``, templates only. This
spec's own rows are the derivable ones (**Toys > Arts & Crafts > Craft Kits**): each title shows
the kit's theme and its craft ("Mermaid Lagoon Bead Kit"), so the scaled build draws more kits
by those two values, and the drawing follows them (:func:`kit_toys_learning.craft_tub`: the
theme on the lid, the craft's pieces in the trays). A kit is sold in four piece counts and has
no color selector: it holds pieces of every color, the exception the craft kits already declare
(ruling 2026-10-13, gen#275). Every theme is invented (ruling 2026-10-30, gen#720).
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_toys_learning,  # noqa: F401 -- registers craft_tub
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
    kind,
    sizes,
    style,
    toy_decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, Row, TypeSpec, a

_PATH = ("Toys", "Arts & Crafts", "Craft Kits")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"

#: The opening sentences: each names the theme and nothing that holds for one craft only.
_LEADS = (
    "Make a {t} picture to hang on the wall or give away.",
    "Everything for a rainy afternoon of {t} crafts is in the box.",
    "Follow the {t} guide, then make up new designs.",
    "The {t} pieces are sorted in trays that close for next time.",
)


def _kit(code: str, theme: str, craft: str, brand: str, lead: str, color, price: float) -> Row:
    """A craft kit: "<theme> <craft> Kit", sold in four piece counts, colorless."""
    toy_type = f"{craft} Kit"
    desc = (f"{lead.format(t=theme)} This {toy_type.lower()} comes in four box sizes. "
            f"Not for under 3s. For ages 6 and up.")  # fmt: skip
    return style(
        code,
        f"{theme} {toy_type}",
        brand,
        _PATH,
        "Arts and Crafts Kit",
        "craft_tub",
        desc,
        (color,),
        (a("theme", "Theme", theme), kind(toy_type), age("6+ years")),
        price,
        sizes(
            ("250", price),
            ("500", round(price * 1.6)),
            ("1000", round(price * 2.6)),
            ("2000", round(price * 4.2)),
        ),
        "piece_count",
        params=(("kind", toy_type.lower()), ("theme", theme.lower())),
        colorless=True,
    )


ROWS = (
    _kit("CRKMER", "Mermaid Lagoon", "Bead", CALDERBY, _LEADS[0], PINK, 9.0),
    _kit("CRKRAI", "Rainbow Garden", "Mosaic", LANTERNBY, _LEADS[1], GREEN, 10.0),
    _kit("CRKJUN", "Jungle Parade", "Gem Art", THISTLE, _LEADS[2], GREEN, 11.0),
    _kit("CRKUNI", "Unicorn Meadow", "Pom-Pom", FERNBY, _LEADS[3], PINK, 8.0),
    _kit("CRKSPA", "Space Explorer", "Mosaic", PUDDLE, _LEADS[0], BLUE, 10.0),
    _kit("CRKBUT", "Butterfly Garden", "Bead", CALDERBY, _LEADS[1], YELLOW, 9.0),
    _kit("CRKDIN", "Dino Valley", "Gem Art", LANTERNBY, _LEADS[2], ORANGE, 12.0),
    _kit("CRKFAI", "Fairy Castle", "Pom-Pom", THISTLE, _LEADS[3], PINK, 9.0),
    _kit("CRKSAF", "Safari Sunset", "Mosaic", FERNBY, _LEADS[0], ORANGE, 11.0),
    _kit("CRKCAN", "Candy Shop", "Bead", PUDDLE, _LEADS[1], RED, 8.0),
    _kit("CRKPET", "Pet Parade", "Pom-Pom", CALDERBY, _LEADS[2], YELLOW, 9.0),
    _kit("CRKPOL", "Polar Friends", "Gem Art", LANTERNBY, _LEADS[3], BLUE, 12.0),
    _kit("CRKROB", "Robot Factory", "Mosaic", THISTLE, _LEADS[0], RED, 11.0),
    _kit("CRKFOX", "Woodland Fox", "Bead", FERNBY, _LEADS[1], ORANGE, 10.0),
    _kit("CRKFLO", "Flower Market", "Gem Art", PUDDLE, _LEADS[2], PINK, 11.0),
    _kit("CRKOCE", "Ocean Friends", "Pom-Pom", CALDERBY, _LEADS[3], BLUE, 9.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="arts_and_crafts_kit",
    department="Toys",
    product_type="Arts and Crafts Kit",
    rows=ROWS,
    derivable=True,
    homes=(Home("toys_rows", False), Home("decoy_product_words", False)),
    decoys=(
        toy_decoy(
            6,
            "kite",
            "generic",
            ROWS[0],
            60,
            "Kite Festival Bead Kit",
            "Beads to thread a picture of a kite festival; it is a bead kit, not a kite.",
        ),
        toy_decoy(
            4,
            "glass bead kit",
            MATERIAL_CLAIM,
            ROWS[5],
            61,
            "Glass-Look Bead Kit",
            "A bead kit whose beads are polished to look like glass; they are plastic.",
        ),
    ),
)
