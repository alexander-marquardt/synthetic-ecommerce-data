"""Leash & Collar (gen#967, slice 3): dog leashes, collars and harnesses, and cat collars.

**Pets > Leashes & Collars** holds **Dog Leashes**, **Retractable Leashes**, **Dog Collars** and
**Dog Harnesses**, each sold Small, Medium and Large, and **Cat Collars**, one size. A title
names the material (nylon, leather, rope, padded, reflective) and the kind. A style's SKUs are its
colors (ruling 2026-10-13, gen#275) times its sizes. :mod:`kit_pet_care` draws the gear in its
color with a swatch of its material.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    BARKWELL,
    CAT_COLLARS,
    DEPARTMENT,
    DOG_COLLARS,
    DOG_LEASHES,
    HARNESSES,
    HOUND,
    OWNERS,
    PURRSEY,
    RETRACTABLE,
    TAILMOOR,
    WHISKERBY,
    decoy,
    gear,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_SHAPE = "pet_leash"
_TYPE = "Leash & Collar"


def _gear(animal: str, kind: str, material: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", animal), a("gear_kind", "Gear kind", kind),
            a("material", "Material", material))  # fmt: skip


def _sml(small: float, medium: float, large: float) -> tuple[tuple[str, float], ...]:
    return (("Small", small), ("Medium", medium), ("Large", large))


ROWS = (
    gear("PLCDNL", "Nylon Dog Leash", HOUND, DOG_LEASHES, _TYPE, _SHAPE,
         "A flat woven nylon leash with a padded handle loop and a swivel clip.",
         _gear("Dog", "Leash", "Nylon"), 0, _sml(9.0, 11.0, 13.0)),
    gear("PLCDLL", "Leather Dog Leash", TAILMOOR, DOG_LEASHES, _TYPE, _SHAPE,
         "A stitched leather leash that softens with use, with a solid brass clip.",
         _gear("Dog", "Leash", "Leather"), 0, _sml(19.0, 23.0, 27.0)),
    gear("PLCDRL", "Rope Dog Leash", BARKWELL, DOG_LEASHES, _TYPE, _SHAPE,
         "A braided climbing-rope leash, strong and easy to grip on long walks.",
         _gear("Dog", "Leash", "Rope"), 0, _sml(14.0, 17.0, 20.0)),
    gear("PLCDRT", "Reflective Retractable Dog Leash", BARKWELL, RETRACTABLE, _TYPE, _SHAPE,
         "A retractable tape leash with a brake button and a reflective strip for walks after dark.",
         _gear("Dog", "Retractable", "Reflective"), 0, _sml(18.0, 24.0, 30.0)),
    gear("PLCDNC", "Nylon Dog Collar", HOUND, DOG_COLLARS, _TYPE, _SHAPE,
         "An adjustable nylon collar with a quick-release buckle and a ring for a name tag.",
         _gear("Dog", "Collar", "Nylon"), 0, _sml(7.0, 8.5, 10.0)),
    gear("PLCDLC", "Leather Dog Collar", TAILMOOR, DOG_COLLARS, _TYPE, _SHAPE,
         "A buckled leather collar with a metal D-ring, lined for comfort.",
         _gear("Dog", "Collar", "Leather"), 0, _sml(14.0, 17.0, 20.0)),
    gear("PLCDPH", "Padded Dog Harness", BARKWELL, HARNESSES, _TYPE, _SHAPE,
         "A padded chest harness that spreads the pull, with a clip on the back for the leash.",
         _gear("Dog", "Harness", "Padded"), 0, _sml(18.0, 22.0, 27.0)),
    gear("PLCDRH", "Reflective Dog Harness", HOUND, HARNESSES, _TYPE, _SHAPE,
         "A step-in harness with reflective trim and two adjustable straps.",
         _gear("Dog", "Harness", "Reflective"), 0, _sml(16.0, 20.0, 24.0)),
    gear("PLCCRC", "Reflective Cat Collar", WHISKERBY, CAT_COLLARS, _TYPE, _SHAPE,
         "A slim breakaway collar with reflective stitching and a small bell.",
         _gear("Cat", "Collar", "Reflective"), 6.0, animal="cat"),
    gear("PLCCNC", "Nylon Cat Collar", PURRSEY, CAT_COLLARS, _TYPE, _SHAPE,
         "A soft nylon breakaway collar that opens if it catches, with a bell.",
         _gear("Cat", "Collar", "Nylon"), 5.0, animal="cat"),
)  # fmt: skip

SPEC = TypeSpec(
    key="leash_collar",
    department=DEPARTMENT,
    product_type=_TYPE,
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(2, "seat belt", "category", decoy(ROWS[0], "PLCSEA", "Seat Belt Buckle Nylon Dog Leash",
              "A nylon dog leash with a buckle like a seat belt's: a leash, not a car seat belt.")),
        Decoy(6, "chain", "generic", decoy(ROWS[6], "PLCCHN", "Chain Link Padded Dog Harness",
              "From the Chain Link range: a padded chest harness with no metal chain in it.")),
    ),
)  # fmt: skip
