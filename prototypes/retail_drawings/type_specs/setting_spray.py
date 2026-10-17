"""Setting Spray (gen#214): finish and skin type are attributes, the size in ml is the SKU.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK_ROSE, PACK_SAND, PACK_SKY, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Make-Up", "Face", "Setting Sprays"), ptype="Setting Spray")

ROWS = (
    _row("SSPMAT", "Matte Finish Setting Spray", "Veilmoor", 12.0, "setting_spray",
        "A fine mist that locks make-up in place with a shine-free finish for oily skin.",
        (a("finish", "Finish", "Matte"), a("skin_type", "Skin type", "Oily")), (("50", 12.0), ("100", 18.0)), "net_volume_ml", (("nozzle", "mist"),), (PACK_SAND,)),
    _row("SSPDEW", "Dewy Setting Spray", "Fenmere", 13.0, "setting_spray",
        "A hydrating mist that sets make-up and leaves a fresh, glowing look on dry skin.",
        (a("finish", "Finish", "Dewy"), a("skin_type", "Skin type", "Dry")), (("50", 13.0), ("100", 19.0)), "net_volume_ml", (("nozzle", "pump"),), (PACK_ROSE,)),
    _row("SSPLNG", "Long Wear Setting Spray", "Sorrel & Salt", 11.0, "setting_spray",
        "A weightless spray that keeps a natural look in place for sixteen hours.",
        (a("finish", "Finish", "Natural"), a("skin_type", "Skin type", "Combination")), (("50", 11.0), ("100", 17.0), ("150", 23.0)), "net_volume_ml", (("nozzle", "mist"),), (PACK_SKY,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="setting_spray",
    department="Beauty",
    product_type="Setting Spray",
    rows=ROWS,
    decoys=(
        Decoy(4, "dewy setting spray", "vocabulary", decoy("SSD1", "Dewy Pink Cap Setting Spray", "A matte setting spray with a pink cap.", ROWS[0])),
        Decoy(6, "dewy setting spray", "generic", decoy("SSD2", "Dewy Orchard Setting Spray", "From the Dewy Orchard range: a matte setting spray.", ROWS[0])),
        Decoy(7, "dewy setting spray", "generic", decoy("SSD3", "Matte Setting Spray", "A matte setting spray for oily skin.", ROWS[0], brand="Dewy Finch")),
    ),
    owners=(("Dewy Finch", "third_party"), ("Fenmere", "third_party"), ("Sorrel & Salt", "third_party"), ("Veilmoor", "third_party"),),
)  # fmt: skip
