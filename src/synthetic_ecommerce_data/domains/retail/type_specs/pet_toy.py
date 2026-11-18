"""Pet Toy (gen#967, slice 2): dog toys by size and cat toys, each in the six main colors.

**Pets > Pet Toys > Dog Toys** holds balls, ropes, rings, bones and flying discs whose title names
the play feature and the kind, each sold Small and Large; **Cat Toys** holds wands, mice,
balls and kickers, one size. A style's SKUs are its colors (ruling 2026-10-13, gen#275) times its
sizes. :mod:`kit_pet_gear` draws the toy in its color with its feature's mark.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    ALLEY_CAT,
    BARKWELL,
    CAT_TOYS,
    DEPARTMENT,
    DOG_TOYS,
    HOUND,
    OWNERS,
    PURRSEY,
    TAILMOOR,
    WHISKERBY,
    decoy,
    gear,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_SHAPE = "pet_toy"


def _toy(animal: str, kind: str, feature: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", animal), a("toy_kind", "Toy kind", kind),
            a("play_feature", "Play feature", feature))  # fmt: skip


def _sl(small: float, large: float) -> tuple[tuple[str, float], ...]:
    return (("Small", small), ("Large", large))


ROWS = (
    gear("PTTDSB", "Squeaky Ball Dog Toy", HOUND, DOG_TOYS, "Pet Toy", _SHAPE,
         "A bouncy rubber ball with a squeaker inside, for fetch in the park or the garden.",
         _toy("Dog", "Ball", "Squeaky"), 0, _sl(4.0, 6.5)),
    gear("PTTDTR", "Tug Rope Dog Toy", BARKWELL, DOG_TOYS, "Pet Toy", _SHAPE,
         "A braided cotton rope with a knot at each end, for tug of war and chewing.",
         _toy("Dog", "Rope", "Tug"), 0, _sl(5.0, 8.5)),
    gear("PTTDFR", "Floating Ring Dog Toy", TAILMOOR, DOG_TOYS, "Pet Toy", _SHAPE,
         "A soft rubber ring that floats, for games of fetch at the beach or the lake.",
         _toy("Dog", "Ring", "Floating"), 0, _sl(6.0, 9.0)),
    gear("PTTDCB", "Chew-Resistant Bone Dog Toy", HOUND, DOG_TOYS, "Pet Toy", _SHAPE,
         "A tough nylon bone for strong chewers, textured to keep a dog busy.",
         _toy("Dog", "Bone", "Chew-Resistant"), 0, _sl(5.5, 9.5)),
    gear("PTTDGD", "Glow-in-the-Dark Flying Disc Dog Toy", BARKWELL, DOG_TOYS, "Pet Toy", _SHAPE,
         "A soft flying disc that glows after dark, gentle on a dog's mouth.",
         _toy("Dog", "Flying Disc", "Glow-in-the-Dark"), 0, _sl(6.5, 10.0)),
    gear("PTTCFW", "Feather Wand Cat Toy", WHISKERBY, CAT_TOYS, "Pet Toy", _SHAPE,
         "A cane wand with a feather lure on a string, for chasing and pouncing.",
         _toy("Cat", "Wand", "Feather"), 4.5, animal="cat"),
    gear("PTTCCM", "Catnip Mouse Cat Toy", PURRSEY, CAT_TOYS, "Pet Toy", _SHAPE,
         "A soft felt mouse filled with dried catnip, light enough to bat across the floor.",
         _toy("Cat", "Mouse", "Catnip"), 3.0, animal="cat"),
    gear("PTTCJB", "Jingle Bell Ball Cat Toy", WHISKERBY, CAT_TOYS, "Pet Toy", _SHAPE,
         "A light plastic ball with a bell inside that rings as it rolls.",
         _toy("Cat", "Ball", "Jingle Bell"), 2.5, animal="cat"),
    gear("PTTCCK", "Crinkle Kicker Cat Toy", TAILMOOR, CAT_TOYS, "Pet Toy", _SHAPE,
         "A long fabric pillow with crinkly lining, for a cat to grab and kick.",
         _toy("Cat", "Kicker", "Crinkle"), 5.5, animal="cat"),
)  # fmt: skip

SPEC = TypeSpec(
    key="pet_toy",
    department=DEPARTMENT,
    product_type="Pet Toy",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(7, "cat toy", "generic", decoy(ROWS[0], "PTTCAT", "Squeaky Ball Dog Toy, Fetch Edition",
              "A squeaky rubber ball for dogs who fetch, from the Alley Cat Provisions toy box.", ALLEY_CAT)),
        Decoy(6, "tennis ball", "generic", decoy(ROWS[1], "PTTTEN", "Tennis Club Tug Rope Dog Toy",
              "From the Tennis Club range: a braided cotton rope for tug of war.")),
    ),
)  # fmt: skip
