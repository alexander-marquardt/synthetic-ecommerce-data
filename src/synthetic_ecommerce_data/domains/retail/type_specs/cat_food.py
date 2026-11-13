"""Cat Food (gen#967, slice 1): dry food by the bag's weight, wet food by the pack.

**Pets > Cat Food > Dry Cat Food** holds bags whose title names the life stage, the need and the
flavor; each SKU is a bag's net weight. **Pets > Cat Food > Wet Cat Food** holds packs of pouches,
trays or tins; each SKU is a pack of that many. :mod:`kit_pets` draws both.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    DEPARTMENT,
    DRY_CAT,
    FOREST,
    FURROW,
    KITTEN_MILL,
    NAVY,
    OWNERS,
    PLUM,
    PURRSEY,
    RUST,
    SKY,
    TEAL,
    WET_CAT,
    WHISKERBY,
    decoy,
    grams,
    row,
    units,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_DRY = (("animal", "cat"),)


def _dry(life: str, need: str, flavor: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", "Cat"), a("food_form", "Food form", "Dry"),
            a("life_stage", "Life stage", life), a("special_need", "Special need", need),
            a("flavor", "Flavor", flavor))  # fmt: skip


def _wet(life: str, flavor: str, fmt: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", "Cat"), a("food_form", "Food form", "Wet"),
            a("life_stage", "Life stage", life), a("flavor", "Flavor", flavor),
            a("pack_format", "Pack format", fmt))  # fmt: skip


ROWS = (
    row("CTFKIC", "Kitten Indoor Dry Cat Food with Chicken", WHISKERBY, DRY_CAT, "Cat Food", "dry_pet_food",
        "A complete dry food with small, crunchy biscuits for growing kittens.",
        _dry("Kitten", "Indoor", "Chicken"), grams((0.8, 4.5), (2, 9.0), (4, 16.0)), "net_weight_g", _DRY, PLUM),
    row("CTFASS", "Adult Sterilized Dry Cat Food with Salmon", PURRSEY, DRY_CAT, "Cat Food", "dry_pet_food",
        "A complete dry food for neutered adult cats, lower in fat to keep a healthy weight.",
        _dry("Adult", "Sterilized", "Salmon"), grams((0.8, 5.0), (2, 10.0), (4, 18.0), (7, 28.0)), "net_weight_g", _DRY, TEAL),
    row("CTFSHT", "Senior Hairball Control Dry Cat Food with Turkey", FURROW, DRY_CAT, "Cat Food", "dry_pet_food",
        "A complete dry food for older cats, with fiber to help with hairballs.",
        _dry("Senior", "Hairball Control", "Turkey"), grams((0.8, 4.5), (2, 9.5), (4, 17.0)), "net_weight_g", _DRY, NAVY),
    row("CTFAIT", "Adult Indoor Dry Cat Food with Tuna", WHISKERBY, DRY_CAT, "Cat Food", "dry_pet_food",
        "A complete dry food for adult cats who live indoors, with fewer calories for a calm day.",
        _dry("Adult", "Indoor", "Tuna"), grams((0.8, 5.0), (2, 10.0), (4, 18.0), (7, 28.0)), "net_weight_g", _DRY, SKY),
    row("CTFADD", "Adult Sensitive Dry Cat Food with Duck", PURRSEY, DRY_CAT, "Cat Food", "dry_pet_food",
        "A complete dry food for adult cats with a delicate stomach, gently cooked.",
        _dry("Adult", "Sensitive", "Duck"), grams((0.8, 5.5), (2, 11.0), (4, 19.0)), "net_weight_g", _DRY, FOREST),
    row("CTWASG", "Adult Wet Cat Food with Salmon in Gravy, Pouches", WHISKERBY, WET_CAT, "Cat Food", "wet_pet_food",
        "Tender flakes in a rich gravy, a complete meal for adult cats in single-serve packs.",
        _wet("Adult", "Salmon in Gravy", "Pouches"), units((4, 2.5), (12, 6.0), (24, 11.0), (48, 20.0)), "units_per_pack",
        (("pack_format", "pouches"), ("animal", "cat")), TEAL),
    row("CTWKCJ", "Kitten Wet Cat Food with Chicken in Jelly, Trays", PURRSEY, WET_CAT, "Cat Food", "wet_pet_food",
        "Soft morsels in jelly for growing kittens, a complete meal in a peel-lid tray.",
        _wet("Kitten", "Chicken in Jelly", "Trays"), units((6, 4.0), (12, 7.5), (24, 13.0)), "units_per_pack",
        (("pack_format", "trays"), ("animal", "cat")), PLUM),
    row("CTWSTP", "Senior Wet Cat Food with Tuna Pate, Tins", FURROW, WET_CAT, "Cat Food", "wet_pet_food",
        "A smooth pate for older cats, a complete meal in a ring-pull tin.",
        _wet("Senior", "Tuna Pate", "Tins"), units((6, 4.5), (12, 8.0), (24, 14.0)), "units_per_pack",
        (("pack_format", "tins"), ("animal", "cat")), RUST),
)  # fmt: skip

SPEC = TypeSpec(
    key="cat_food",
    department=DEPARTMENT,
    product_type="Cat Food",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(6, "dog food", "generic", decoy(ROWS[1], "CTFDOG", "Dog Rose Adult Dry Cat Food",
              "From the Dog Rose range: a complete dry food for adult cats.")),
        Decoy(7, "kitten food", "generic", decoy(ROWS[2], "CTFKIT", "Senior Hairball Control Dry Cat Food, Turkey Recipe",
              "A complete dry food for older cats from the Kitten Mill bakery.", KITTEN_MILL)),
    ),
)  # fmt: skip
