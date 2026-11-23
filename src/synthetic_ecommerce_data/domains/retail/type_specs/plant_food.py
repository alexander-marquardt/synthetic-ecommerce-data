"""Plant food (gen#1115): Garden > Plants > Plant Food.

Feeds for the plants a shopper grows: house plants, orchids, roses, cacti, tomatoes and citrus,
as a liquid, feed sticks or granules. A breadth type: ``derivable`` True, so the scaled build
draws more styles by the plant the title shows. The ``feed_form`` is fixed per style
(``scale_text.FROZEN_KEYS``), since it decides the SKU axis: a liquid is sold by the millilitre,
granules by the gram and sticks by the count. The pack has no color a shopper picks, so the SKUs
carry none (``colorless``); the drawing takes the pack's green.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_flowers,  # noqa: F401 -- registers plant_food
)
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.outdoor_helpers import (
    DEPARTMENT,
    H,
    L,
    M,
    V,
    W,
    a,
    axis,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec
from synthetic_ecommerce_data.domains.retail.variants import cw

PATH = (DEPARTMENT, "Plants", "Plant Food")
_PT = "Plant Food"
PACK = cw("Green", "#4f8a45")
#: form -> the SKU field its sizes are stored under.
SIZE_KEY = {"Liquid": "net_volume_ml", "Granules": "net_weight_g", "Feed Sticks": "units_per_pack"}


def _food(code: str, title: str, plant: str, form: str, brand: str, desc: str, sizes: tuple) -> Row:
    attrs = (a("plant", "For", plant), a("feed_form", "Feed form", form))
    params = (("form", form.lower()), ("plant", plant.lower()))
    return Row(code, title, brand, DEPARTMENT, PATH, _PT, sizes[0][1], "plant_food", desc, (PACK,), attrs, sizes,
               colorless=True, params=params, size_key=SIZE_KEY[form])  # fmt: skip


ROWS = (
    _food("PFHPLQ", "House Plant Liquid Feed", "House Plant", "Liquid", V,
          "A liquid feed for a house plant: add one capful to a watering can every two weeks while it is growing.", axis((250, 4.5), (500, 7.0), (1000, 11.0))),
    _food("PFORLQ", "Orchid Liquid Feed", "Orchid", "Liquid", M,
          "A liquid feed for an orchid: add one capful to a watering can every two weeks while it is growing.", axis((250, 5.0), (500, 8.0))),
    _food("PFTMLQ", "Tomato Liquid Feed", "Tomato", "Liquid", W,
          "A liquid feed for a tomato: add one capful to a watering can every two weeks while it is growing.", axis((1000, 6.0), (2500, 12.0))),
    _food("PFRSGR", "Rose Feed Granules", "Rose", "Granules", H,
          "Slow-release granules for a rose: mix them into the top of the compost in spring and again in summer.", axis((750, 7.0), (1500, 11.0), (3000, 18.0))),
    _food("PFCTGR", "Citrus Tree Feed Granules", "Citrus Tree", "Granules", L,
          "Slow-release granules for a citrus tree: mix them into the top of the compost in spring and again in summer.", axis((750, 8.0), (1500, 13.0))),
    _food("PFCCST", "Cactus Feed Sticks", "Cactus", "Feed Sticks", V,
          "Feed sticks for a cactus: push one into the compost and it feeds for up to three months.", axis((20, 4.0), (40, 7.0))),
    _food("PFHPST", "House Plant Feed Sticks", "House Plant", "Feed Sticks", M,
          "Feed sticks for a house plant: push one into the compost and it feeds for up to three months.", axis((20, 4.0), (40, 6.5), (80, 11.0))),
)

SPEC = TypeSpec(
    key="plant_food",
    department=DEPARTMENT,
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
