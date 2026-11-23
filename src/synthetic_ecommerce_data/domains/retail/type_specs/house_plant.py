"""House plant (gen#1115): Garden > Plants > House Plants.

Ten live house plants (an orchid, a succulent, a cactus, monstera-style foliage and more), each
sold in a pot. A breadth type: ``derivable`` True, so the scaled build draws more styles by the
pot material the title shows and the pot's color. The plant is fixed per style: ``plant_kind``,
``light_needs`` and ``pet_safe`` are facts of the plant (``scale_text.FROZEN_KEYS``), so a derived
monstera is never pet safe. ``pet_safe`` follows the ASPCA's list of plants toxic and non-toxic
to cats and dogs. Each SKU is a pot color times a pot size in centimetres, and every style offers
the six main colors (gen#275): the color is the pot's.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_flowers,  # noqa: F401 -- registers house_plant
)
from synthetic_ecommerce_data.domains.retail.outdoor_helpers import (
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    H,
    L,
    M,
    V,
    W,
    a,
    axis,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

PATH = ("Garden", "Plants", "House Plants")
_PT = "House Plant"
SIX = (WHITE, BLACK, GREEN, BLUE, RED, YELLOW)
BRIGHT, LOW, SUN = "Bright Indirect Light", "Low Light", "Full Sun"


def _plant(code: str, name: str, plant: str, pot: str, light: str, pet_safe: bool, brand: str,
           desc: str, sizes: tuple) -> object:  # fmt: skip
    attrs = (
        a("plant_kind", "Plant", plant),
        a("pot_material", "Pot material", pot),
        a("light_needs", "Light needs", light),
        a("pet_safe", "Pet safe", "Yes" if pet_safe else "No"),
    )
    params = (("kind", plant.lower()), ("pot", pot.lower()))
    return row(code, f"{name} in {pot} Pot", brand, PATH, _PT, sizes[0][1], "house_plant", desc, SIX,
               attrs, sizes, "pot_size_cm", params)  # fmt: skip


ROWS = (
    _plant("HPORPH", "Phalaenopsis Orchid", "Orchid", "Ceramic", BRIGHT, True, V,
           "A moth orchid with two flower spikes, staked, in a Ceramic pot. Non-toxic to cats and dogs.", axis((9, 22.0), (12, 32.0))),
    _plant("HPECHV", "Echeveria Succulent", "Echeveria", "Ceramic", SUN, True, M,
           "A rosette succulent for a sunny sill, in a Ceramic pot. Water every two weeks. Non-toxic to cats and dogs.", axis((6, 6.0), (9, 9.0), (12, 14.0))),
    _plant("HPXMCC", "Christmas Cactus", "Christmas Cactus", "Plastic", BRIGHT, True, W,
           "A trailing cactus that flowers in winter, in a Plastic pot. Non-toxic to cats and dogs.", axis((9, 10.0), (12, 16.0))),
    _plant("HPMNST", "Monstera Deliciosa", "Monstera", "Ceramic", BRIGHT, False, H,
           "A Swiss cheese plant with split leaves, in a Ceramic pot. Keep away from cats and dogs.", axis((12, 18.0), (17, 32.0), (21, 55.0))),
    _plant("HPPCLY", "Peace Lily", "Peace Lily", "Plastic", LOW, False, L,
           "A peace lily with white flowers that copes with a shady room, in a Plastic pot. Keep away from cats and dogs.", axis((12, 14.0), (17, 24.0))),
    _plant("HPSNKE", "Snake Plant", "Snake Plant", "Metal", LOW, False, V,
           "An upright snake plant that needs little water, in a Metal pot. Keep away from cats and dogs.", axis((12, 16.0), (17, 28.0), (21, 45.0))),
    _plant("HPPTHS", "Golden Pothos", "Pothos", "Metal", LOW, False, M,
           "A trailing pothos for a shelf, in a Metal pot. Keep away from cats and dogs.", axis((12, 12.0), (17, 22.0))),
    _plant("HPCLTH", "Calathea Prayer Plant", "Calathea", "Ceramic", BRIGHT, True, W,
           "A calathea with striped leaves that fold up at night, in a Ceramic pot. Non-toxic to cats and dogs.", axis((12, 16.0), (17, 28.0))),
    _plant("HPSPDR", "Spider Plant", "Spider Plant", "Plastic", BRIGHT, True, H,
           "A spider plant with arching striped leaves and plantlets, in a Plastic pot. Non-toxic to cats and dogs.", axis((9, 8.0), (12, 12.0), (17, 20.0))),
    _plant("HPALOE", "Aloe Vera", "Aloe Vera", "Metal", SUN, False, L,
           "An aloe vera for a sunny sill, in a Metal pot. Keep away from cats and dogs.", axis((9, 9.0), (12, 14.0))),
)

SPEC = TypeSpec(
    key="house_plant",
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
    options=(Option("pot_size_cm", "pot_size", "Pot size", "CMT"),),
)
