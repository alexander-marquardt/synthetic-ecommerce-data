"""Dog Food (gen#967, slice 1): dry food by the bag's weight, wet food by the pack.

**Pets > Dog Food > Dry Dog Food** holds bags whose title names the life stage, the breed size
and the flavor; each SKU is a bag's net weight. **Pets > Dog Food > Wet Dog Food** holds packs of
pouches, trays or tins; each SKU is a pack of that many. :mod:`kit_pets` draws both.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    ALLEY_CAT,
    BARKWELL,
    DEPARTMENT,
    DRY_DOG,
    FOREST,
    FURROW,
    HOUND,
    NAVY,
    OWNERS,
    PLUM,
    RUST,
    SAND,
    TEAL,
    WET_DOG,
    decoy,
    grams,
    row,
    units,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_DRY = (("animal", "dog"),)


def _dry(life: str, breed: str, flavor: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", "Dog"), a("food_form", "Food form", "Dry"),
            a("life_stage", "Life stage", life), a("breed_size", "Breed size", breed),
            a("flavor", "Flavor", flavor))  # fmt: skip


def _wet(life: str, flavor: str, fmt: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", "Dog"), a("food_form", "Food form", "Wet"),
            a("life_stage", "Life stage", life), a("flavor", "Flavor", flavor),
            a("pack_format", "Pack format", fmt))  # fmt: skip


ROWS = (
    row("DGFPSC", "Puppy Small Breed Dry Dog Food with Chicken & Rice", HOUND, DRY_DOG, "Dog Food", "dry_pet_food",
        "A complete dry food with small kibble for growing puppies, made with real meat and no artificial colors.",
        _dry("Puppy", "Small Breed", "Chicken & Rice"), grams((1.5, 7.0), (4, 15.0), (7, 24.0)), "net_weight_g", _DRY, RUST),
    row("DGFAML", "Adult Medium Breed Dry Dog Food with Lamb & Rice", BARKWELL, DRY_DOG, "Dog Food", "dry_pet_food",
        "A complete dry food for active adult dogs, gently cooked for easy digestion.",
        _dry("Adult", "Medium Breed", "Lamb & Rice"), grams((2, 9.0), (6, 21.0), (12, 36.0), (15, 42.0)), "net_weight_g", _DRY, FOREST),
    row("DGFSLS", "Senior Large Breed Dry Dog Food with Salmon & Potato", FURROW, DRY_DOG, "Dog Food", "dry_pet_food",
        "A complete dry food with joint care for older dogs, with omega 3 for a healthy coat.",
        _dry("Senior", "Large Breed", "Salmon & Potato"), grams((2, 10.0), (6, 23.0), (12, 39.0), (15, 46.0)), "net_weight_g", _DRY, NAVY),
    row("DGFALT", "Adult Large Breed Dry Dog Food with Turkey & Sweet Potato", HOUND, DRY_DOG, "Dog Food", "dry_pet_food",
        "A grain-free dry food for big adult dogs, with large kibble to crunch.",
        _dry("Adult", "Large Breed", "Turkey & Sweet Potato"), grams((2, 11.0), (6, 25.0), (12, 42.0), (15, 49.0)), "net_weight_g", _DRY, SAND),
    row("DGFASD", "Adult Small Breed Dry Dog Food with Duck & Pea", BARKWELL, DRY_DOG, "Dog Food", "dry_pet_food",
        "A complete dry food with small kibble for little adult dogs with big appetites.",
        _dry("Adult", "Small Breed", "Duck & Pea"), grams((1.5, 8.0), (4, 17.0), (7, 27.0)), "net_weight_g", _DRY, PLUM),
    row("DGFSMB", "Senior Medium Breed Dry Dog Food with Beef & Vegetable", FURROW, DRY_DOG, "Dog Food", "dry_pet_food",
        "A complete dry food for older dogs, lower in fat to help keep a healthy weight.",
        _dry("Senior", "Medium Breed", "Beef & Vegetable"), grams((2, 9.0), (6, 20.0), (12, 34.0), (15, 40.0)), "net_weight_g", _DRY, TEAL),
    row("DGWACG", "Adult Wet Dog Food with Chicken in Gravy, Pouches", HOUND, WET_DOG, "Dog Food", "wet_pet_food",
        "Tender chunks in a rich gravy, a complete meal for adult dogs in single-serve packs.",
        _wet("Adult", "Chicken in Gravy", "Pouches"), units((6, 5.0), (12, 9.0), (24, 16.0), (48, 29.0)), "units_per_pack",
        (("pack_format", "pouches"), ("animal", "dog")), RUST),
    row("DGWPBJ", "Puppy Wet Dog Food with Beef in Jelly, Trays", BARKWELL, WET_DOG, "Dog Food", "wet_pet_food",
        "Soft chunks in jelly for growing puppies, a complete meal in a peel-lid tray.",
        _wet("Puppy", "Beef in Jelly", "Trays"), units((6, 6.0), (12, 11.0), (24, 19.0)), "units_per_pack",
        (("pack_format", "trays"), ("animal", "dog")), FOREST),
    row("DGWSLL", "Senior Wet Dog Food with Lamb in Loaf, Tins", FURROW, WET_DOG, "Dog Food", "wet_pet_food",
        "A smooth meaty loaf for older dogs, a complete meal in a ring-pull tin.",
        _wet("Senior", "Lamb in Loaf", "Tins"), units((6, 6.5), (12, 12.0), (24, 21.0)), "units_per_pack",
        (("pack_format", "tins"), ("animal", "dog")), NAVY),
)  # fmt: skip

SPEC = TypeSpec(
    key="dog_food",
    department=DEPARTMENT,
    product_type="Dog Food",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(7, "cat food", "generic", decoy(ROWS[1], "DGFCAT", "Adult Medium Breed Dry Dog Food with Lamb & Rice",
              "A complete dry food for adult dogs from the Alley Cat Larder kitchen.", ALLEY_CAT)),
        Decoy(6, "puppy food", "generic", decoy(ROWS[2], "DGFPUP", "Puppy Hill Senior Dry Dog Food",
              "From the Puppy Hill range: a gentle dry food for older dogs.")),
    ),
)  # fmt: skip
