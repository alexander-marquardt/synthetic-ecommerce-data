"""Pet Bed (gen#967, slice 2): dog beds and cat beds by size, each in the six main colors.

**Pets > Pet Beds > Dog Beds** holds donut, bolster, orthopedic and cushion beds whose title names
the cover and the style, sold Small, Medium and Large; **Cat Beds** holds cave, donut and
radiator beds, one size. A style's SKUs are its colors (ruling 2026-10-13, gen#275) times its sizes.
:mod:`kit_pet_gear` draws the bed in its color with a swatch of its cover.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    BARKWELL,
    CAT_BEDS,
    DEPARTMENT,
    DOG_BEDS,
    HOUND,
    KITTEN_MILL,
    OWNERS,
    PURRSEY,
    TAILMOOR,
    WHISKERBY,
    decoy,
    gear,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_SHAPE = "pet_bed"


def _bed(animal: str, style: str, cover: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", animal), a("bed_style", "Bed style", style),
            a("cover", "Cover", cover))  # fmt: skip


def _dog(small: float, medium: float, large: float) -> tuple[tuple[str, float], ...]:
    return (("Small", small), ("Medium", medium), ("Large", large))


ROWS = (
    gear("PTBDFD", "Faux Fur Donut Dog Bed", HOUND, DOG_BEDS, "Pet Bed", _SHAPE,
         "A round calming bed with a raised rim to rest a head on, in soft faux fur.",
         _bed("Dog", "Donut", "Faux Fur"), 0, _dog(25.0, 35.0, 49.0)),
    gear("PTBDCB", "Corduroy Bolster Dog Bed", BARKWELL, DOG_BEDS, "Pet Bed", _SHAPE,
         "A rectangular bed with a bolster on three sides and a removable, washable cover.",
         _bed("Dog", "Bolster", "Corduroy"), 0, _dog(29.0, 39.0, 55.0)),
    gear("PTBDQO", "Quilted Orthopedic Dog Bed", TAILMOOR, DOG_BEDS, "Pet Bed", _SHAPE,
         "A memory foam mattress that supports older joints, with a quilted cover.",
         _bed("Dog", "Orthopedic", "Quilted"), 0, _dog(39.0, 55.0, 75.0)),
    gear("PTBDWC", "Waterproof Cushion Dog Bed", HOUND, DOG_BEDS, "Pet Bed", _SHAPE,
         "A flat cushion with a wipe-clean waterproof cover, for the car or the crate.",
         _bed("Dog", "Cushion", "Waterproof"), 0, _dog(19.0, 26.0, 34.0)),
    gear("PTBCFC", "Faux Fur Cave Cat Bed", WHISKERBY, CAT_BEDS, "Pet Bed", _SHAPE,
         "A covered bed with a round opening, for a cat that likes to hide and stay warm.",
         _bed("Cat", "Cave", "Faux Fur"), 24.0, animal="cat"),
    gear("PTBCVD", "Velvet Donut Cat Bed", PURRSEY, CAT_BEDS, "Pet Bed", _SHAPE,
         "A small round bed with a soft raised rim, in a plush velvet cover.",
         _bed("Cat", "Donut", "Velvet"), 19.0, animal="cat"),
    gear("PTBCSR", "Sherpa Radiator Cat Bed", TAILMOOR, CAT_BEDS, "Pet Bed", _SHAPE,
         "A hammock on a steel frame that hooks over a radiator, lined with sherpa fleece.",
         _bed("Cat", "Radiator", "Sherpa"), 17.0, animal="cat"),
)  # fmt: skip

SPEC = TypeSpec(
    key="pet_bed",
    department=DEPARTMENT,
    product_type="Pet Bed",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(2, "sofa", "category", decoy(ROWS[1], "PTBSOF", "Sofa Style Corduroy Bolster Dog Bed",
              "A bolster bed shaped like a little sofa for a dog to curl up on: a pet bed, not a sofa.")),
        Decoy(7, "kitten bed", "generic", decoy(ROWS[0], "PTBKIT", "Faux Fur Donut Dog Bed, Calming",
              "A calming donut bed for dogs, from the Kitten Mill workshop.", KITTEN_MILL)),
    ),
)  # fmt: skip
