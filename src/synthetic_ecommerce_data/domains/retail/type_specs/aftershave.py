"""Aftershave (gen#214, widened by gen#957): fragrance family and concentration are attributes, the size in ml is the SKU.

The range grows by authored rows (``derivable`` stays False, ``tests/test_retail_beauty_214.py``):
gen#957 adds an aromatic balm, a smoky splash and a herbal eau de toilette to the three of gen#214.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from synthetic_ecommerce_data.domains.retail.beauty_depth import (
    PACK_INK,
    PACK_SAGE,
    PACK_SAND,
    PACK_SKY,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Fragrance", "Aftershave"), ptype="Aftershave")

ROWS = (
    _row("ASHWDY", "Cedar Woods Aftershave", "Thornlea Skin", 14.0, "aftershave",
        "A calming splash of cedar and oak moss for freshly shaved skin.",
        (a("fragrance_family", "Fragrance family", "Woody"), a("concentration", "Concentration", "Aftershave Splash")), (("30", 9.0), ("50", 14.0), ("100", 22.0)), "net_volume_ml", (("cap", "stopper"),), (PACK_INK,)),
    _row("ASHFRS", "Ocean Fresh Eau de Toilette for Men", "Aldermist", 24.0, "aftershave",
        "A clean, salty eau de toilette with sea notes and a crisp finish.",
        (a("fragrance_family", "Fragrance family", "Aquatic"), a("concentration", "Concentration", "Eau de Toilette")), (("30", 16.0), ("50", 24.0), ("100", 36.0)), "net_volume_ml", (("cap", "spray"),), (PACK_SKY,)),
    _row("ASHSPC", "Black Pepper Eau de Cologne", "Pearlbrook", 18.0, "aftershave",
        "A warm, spicy cologne with pepper and amber for evenings out.",
        (a("fragrance_family", "Fragrance family", "Spicy"), a("concentration", "Concentration", "Eau de Cologne")), (("30", 12.0), ("50", 18.0), ("100", 28.0)), "net_volume_ml", (("cap", "stopper"),), (PACK_SAND,)),
    _row("ASHLAV", "Rosemary and Cedar Aftershave Balm", "Sorrel & Salt", 16.0, "aftershave",
        "A cooling, alcohol-free balm with rosemary and cedar that soothes razor burn.",
        (a("fragrance_family", "Fragrance family", "Aromatic"), a("concentration", "Concentration", "Aftershave Balm")), (("30", 10.0), ("50", 16.0), ("100", 24.0)), "net_volume_ml", (("cap", "spray"),), (PACK_SAGE,)),
    _row("ASHVET", "Vetiver and Clove Aftershave", "Fenmere", 20.0, "aftershave",
        "A dry, smoky splash of vetiver root and clove for the close of a shave.",
        (a("fragrance_family", "Fragrance family", "Smoky"), a("concentration", "Concentration", "Aftershave Splash")), (("30", 13.0), ("50", 20.0), ("100", 30.0)), "net_volume_ml", (("cap", "stopper"),), (PACK_INK,)),
    _row("ASHMAR", "Sea Salt and Juniper Eau de Toilette for Men", "Veilmoor", 26.0, "aftershave",
        "A bright, mineral eau de toilette of sea salt and juniper that lasts the working day.",
        (a("fragrance_family", "Fragrance family", "Herbal"), a("concentration", "Concentration", "Eau de Toilette")), (("30", 17.0), ("50", 26.0), ("100", 39.0)), "net_volume_ml", (("cap", "spray"),), (PACK_SKY,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="aftershave",
    department="Beauty",
    product_type="Aftershave",
    rows=ROWS,
    decoys=(
        Decoy(4, "citrus aftershave", "vocabulary", decoy("ASD1", "Citrus Stopper Woody Aftershave", "A woody aftershave with a citrus-green stopper.", ROWS[0])),
        Decoy(6, "citrus aftershave", "generic", decoy("ASD2", "Citrus Bay Woody Aftershave", "From the Citrus Bay range: a woody aftershave.", ROWS[0])),
        Decoy(7, "citrus aftershave", "generic", decoy("ASD3", "Woody Aftershave", "A woody aftershave splash.", ROWS[0], brand="Citrus Heron")),
    ),
    owners=(("Aldermist", "third_party"), ("Citrus Heron", "third_party"), ("Fenmere", "third_party"), ("Pearlbrook", "third_party"), ("Sorrel & Salt", "third_party"), ("Thornlea Skin", "third_party"), ("Veilmoor", "third_party"),),
)  # fmt: skip
