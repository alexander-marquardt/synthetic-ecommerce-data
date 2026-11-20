"""Grooming Brush (gen#967, slice 3): dog brushes by size and cat brushes, each in the six main colors.

**Pets > Grooming > Dog Brushes** holds slicker, pin, bristle, deshedding and rubber curry brushes
whose title names the coat they are for (short, long, double, curly), each sold Small and Large;
**Cat Brushes** holds slicker, bristle and deshedding brushes and a grooming glove, one size. A
style's SKUs are its colors (ruling 2026-10-13, gen#275) times its sizes. :mod:`kit_pet_care`
draws the brush in its color with a tag of its coat.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    BARKWELL,
    CAT_BRUSHES,
    DEPARTMENT,
    DOG_BRUSHES,
    HOUND,
    OWNERS,
    PURRSEY,
    TAILMOOR,
    WHISKERBY,
    decoy,
    gear,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_SHAPE = "grooming_brush"
_TYPE = "Grooming Brush"


def _brush(animal: str, kind: str, coat: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", animal), a("brush_kind", "Brush kind", kind),
            a("coat_type", "Coat type", coat))  # fmt: skip


def _sl(small: float, large: float) -> tuple[tuple[str, float], ...]:
    return (("Small", small), ("Large", large))


ROWS = (
    gear("PGBDSL", "Long Coat Slicker Dog Brush", HOUND, DOG_BRUSHES, _TYPE, _SHAPE,
         "Fine bent wire pins that work out tangles and loose fur from a long coat.",
         _brush("Dog", "Slicker", "Long Coat"), 0, _sl(9.0, 12.0)),
    gear("PGBDPN", "Double Coat Pin Dog Brush", BARKWELL, DOG_BRUSHES, _TYPE, _SHAPE,
         "Ball-tipped steel pins on a cushioned pad that reach through a thick double coat.",
         _brush("Dog", "Pin", "Double Coat"), 0, _sl(8.0, 11.0)),
    gear("PGBDBR", "Short Coat Bristle Dog Brush", TAILMOOR, DOG_BRUSHES, _TYPE, _SHAPE,
         "Dense natural bristles that lift dust and bring out the shine in a short coat.",
         _brush("Dog", "Bristle", "Short Coat"), 0, _sl(7.0, 10.0)),
    gear("PGBDDS", "Double Coat Deshedding Dog Brush", HOUND, DOG_BRUSHES, _TYPE, _SHAPE,
         "A curved steel edge that lifts the loose undercoat before it sheds on the sofa.",
         _brush("Dog", "Deshedding", "Double Coat"), 0, _sl(16.0, 22.0)),
    gear("PGBDRC", "Short Coat Rubber Curry Dog Brush", BARKWELL, DOG_BRUSHES, _TYPE, _SHAPE,
         "Soft rubber nubs on a hand strap, for bath time and a massage that lifts loose hair.",
         _brush("Dog", "Rubber Curry", "Short Coat"), 0, _sl(6.0, 8.0)),
    gear("PGBDCS", "Curly Coat Slicker Dog Brush", TAILMOOR, DOG_BRUSHES, _TYPE, _SHAPE,
         "Long flexible pins that reach through a curly coat without pulling.",
         _brush("Dog", "Slicker", "Curly Coat"), 0, _sl(10.0, 13.0)),
    gear("PGBCSL", "Long Coat Slicker Cat Brush", WHISKERBY, CAT_BRUSHES, _TYPE, _SHAPE,
         "A small slicker with a button that pushes the collected fur off the pins.",
         _brush("Cat", "Slicker", "Long Coat"), 8.0, animal="cat"),
    gear("PGBCGG", "Short Coat Grooming Glove Cat Brush", PURRSEY, CAT_BRUSHES, _TYPE, _SHAPE,
         "A grooming glove with soft rubber tips, for a cat that likes to be stroked, not brushed.",
         _brush("Cat", "Grooming Glove", "Short Coat"), 7.0, animal="cat"),
    gear("PGBCDS", "Long Coat Deshedding Cat Brush", WHISKERBY, CAT_BRUSHES, _TYPE, _SHAPE,
         "A narrow deshedding comb that thins the undercoat to cut down on hairballs.",
         _brush("Cat", "Deshedding", "Long Coat"), 13.0, animal="cat"),
)  # fmt: skip

SPEC = TypeSpec(
    key="grooming_brush",
    department=DEPARTMENT,
    product_type=_TYPE,
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(2, "hairbrush", "category", decoy(ROWS[2], "PGBHAI", "Hairbrush Style Short Coat Bristle Dog Brush",
              "A bristle brush for a dog's coat, shaped like a hairbrush: a pet brush, not for people.")),
        Decoy(6, "toothbrush", "generic", decoy(ROWS[0], "PGBTTH", "Toothbrush Grip Long Coat Slicker Dog Brush",
              "From the Toothbrush Grip range: a slicker for a dog's coat, with no use for teeth.")),
    ),
)  # fmt: skip
