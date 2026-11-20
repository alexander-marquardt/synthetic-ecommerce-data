"""Small Pet Supply (gen#967, slice 3): fish food, aquarium gravel, and small-animal food, hay and
bedding, by the bag's or the tub's weight.

**Pets > Fish & Aquarium** holds **Fish Food** (flakes and pellets for tropical fish, goldfish
and bettas) and **Aquarium Gravel**; **Pets > Small Animal** holds **Small Animal Food** (nuggets
and pellets for rabbits, guinea pigs and hamsters), **Hay** and **Small Animal Bedding**. A title
names the formula and the animal. Each SKU is a pack's net weight, and the pack's one color is
drawn, not sold, as on a food bag. :mod:`kit_pet_care` draws a tub for fish, a bag for the rest,
with a window of what it holds, the animal's emblem and the formula's band.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    BEDDING,
    BURROWELL,
    DEPARTMENT,
    FINBROOK,
    FISH_FOOD,
    FOREST,
    GRAVEL,
    HAY,
    NAVY,
    OWNERS,
    PLUM,
    RUST,
    SAND,
    SKY,
    SMALL_FOOD,
    TAILMOOR,
    TEAL,
    decoy,
    grams,
    row,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_SHAPE = "small_pet_supply"
_TYPE = "Small Pet Supply"


def _supply(animal: str, kind: str, formula: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", animal), a("supply_kind", "Supply kind", kind),
            a("formula", "Formula", formula))  # fmt: skip


def _animal(name: str) -> tuple[tuple[str, str], ...]:
    return (("animal", name.lower()),)


ROWS = (
    row("SPSFTF", "Tropical Fish Flakes", FINBROOK, FISH_FOOD, _TYPE, _SHAPE,
        "A daily staple of thin flakes that float, then sink slowly for every level of the tank.",
        _supply("Fish", "Flakes", "Tropical"), grams((0.05, 4.5), (0.1, 7.5), (0.2, 12.0)), "net_weight_g", _animal("Fish"), TEAL),
    row("SPSFGP", "Goldfish Pellets", FINBROOK, FISH_FOOD, _TYPE, _SHAPE,
        "Small floating pellets for goldfish and pond fish, made to keep the water clearer.",
        _supply("Fish", "Pellets", "Goldfish"), grams((0.06, 4.0), (0.12, 6.5), (0.25, 11.0)), "net_weight_g", _animal("Fish"), RUST),
    row("SPSFBP", "Betta Pellets", TAILMOOR, FISH_FOOD, _TYPE, _SHAPE,
        "Tiny high-protein pellets sized for a betta's mouth.",
        _supply("Fish", "Pellets", "Betta"), grams((0.02, 3.5), (0.05, 6.0)), "net_weight_g", _animal("Fish"), PLUM),
    row("SPSGRP", "River Pebble Aquarium Gravel", FINBROOK, GRAVEL, _TYPE, _SHAPE,
        "Smooth rounded river pebbles, pre-washed, for a planted or community tank.",
        _supply("Fish", "Gravel", "River Pebble"), grams((2, 6.0), (5, 12.0), (10, 20.0)), "net_weight_g", _animal("Fish"), SAND),
    row("SPSGQS", "Quartz Sand Aquarium Gravel", TAILMOOR, GRAVEL, _TYPE, _SHAPE,
        "Fine quartz sand for bottom-dwelling fish, gentle on barbels.",
        _supply("Fish", "Gravel", "Quartz Sand"), grams((2, 5.5), (5, 11.0), (10, 18.0)), "net_weight_g", _animal("Fish"), SKY),
    row("SPSRTN", "Rabbit Nuggets with Timothy", BURROWELL, SMALL_FOOD, _TYPE, _SHAPE,
        "Single-component nuggets for adult rabbits, so a rabbit cannot pick out the sweet bits.",
        _supply("Rabbit", "Nuggets", "Timothy"), grams((1, 5.5), (2.5, 11.0), (5, 19.0)), "net_weight_g", _animal("Rabbit"), FOREST),
    row("SPSGPV", "Guinea Pig Pellets with Vitamin C", BURROWELL, SMALL_FOOD, _TYPE, _SHAPE,
        "Complete pellets with added vitamin C, which a guinea pig's body cannot make.",
        _supply("Guinea Pig", "Pellets", "Vitamin C"), grams((1, 6.0), (2.5, 12.0)), "net_weight_g", _animal("Guinea Pig"), RUST),
    row("SPSHHS", "Hamster Nuggets with Honey & Seed", TAILMOOR, SMALL_FOOD, _TYPE, _SHAPE,
        "Bite-size nuggets for hamsters and gerbils, baked with honey and sunflower seed.",
        _supply("Hamster", "Nuggets", "Honey & Seed"), grams((0.5, 3.5), (1, 6.0)), "net_weight_g", _animal("Hamster"), SAND),
    row("SPSHTH", "Timothy Hay for Rabbits", BURROWELL, HAY, _TYPE, _SHAPE,
        "Sweet-smelling second-cut timothy hay, long strands for chewing and nesting.",
        _supply("Rabbit", "Hay", "Timothy"), grams((1, 6.0), (2.5, 12.0), (5, 20.0)), "net_weight_g", _animal("Rabbit"), FOREST),
    row("SPSHMG", "Meadow Hay for Guinea Pigs", TAILMOOR, HAY, _TYPE, _SHAPE,
        "Soft meadow hay with grasses and herbs, dust-extracted for small lungs.",
        _supply("Guinea Pig", "Hay", "Meadow"), grams((1, 5.0), (2.5, 10.0)), "net_weight_g", _animal("Guinea Pig"), TEAL),
    row("SPSBPU", "Unscented Paper Bedding for Rabbits", BURROWELL, BEDDING, _TYPE, _SHAPE,
        "Soft, absorbent recycled paper bedding that holds odors and stays low in dust.",
        _supply("Rabbit", "Paper Bedding", "Unscented"), grams((1, 7.0), (2.5, 14.0)), "net_weight_g", _animal("Rabbit"), SKY),
    row("SPSBWL", "Lavender Wood Shavings for Hamsters", TAILMOOR, BEDDING, _TYPE, _SHAPE,
        "Kiln-dried aspen shavings with a light lavender scent, for burrowing and nesting.",
        _supply("Hamster", "Wood Shavings", "Lavender"), grams((0.5, 4.0), (1, 6.5), (2.5, 12.0)), "net_weight_g", _animal("Hamster"), NAVY),
)  # fmt: skip

SPEC = TypeSpec(
    key="small_pet_supply",
    department=DEPARTMENT,
    product_type=_TYPE,
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(2, "cat litter", "category", decoy(ROWS[10], "SPSLIT", "Litter Corner Unscented Paper Bedding for Rabbits",
              "Paper bedding for a rabbit's litter corner: small-animal bedding, not a cat litter.")),
        Decoy(6, "tea", "generic", decoy(ROWS[8], "SPSTEA", "Tea Time Timothy Hay for Rabbits",
              "From the Tea Time range: a bale of fragrant timothy hay for rabbits, not a tea.")),
    ),
)  # fmt: skip
