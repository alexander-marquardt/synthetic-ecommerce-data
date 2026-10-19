"""Anti-Vibration Mat (gen#334): the ordinary type behind a class-8 decoy of "washing machine".

One authored product, titled without the appliance word; the decoy (gen#326) is in
``feature_decoys/large_appliances.py``. Drawn by :func:`kit_large_appliances.anti_vibration_mat`.
Not derivable.
"""

from __future__ import annotations

import kit_large_appliances  # noqa: F401 -- registers the shape
from type_registry import Row, TypeSpec, a
from variants import cw

SPEC = TypeSpec(
    key="anti_vibration_mat",
    department="Cleaning & Janitorial",
    product_type="Anti-Vibration Mat",
    owners=(("Pantry Mill", "own"),),
    rows=(
        Row(
            "AVMPLN",
            "Rubber Floor Pads for Laundry Machines, Set of 4",
            "Pantry Mill",
            "Cleaning & Janitorial",
            ("Cleaning", "Laundry", "Anti-Vibration Mats"),
            "Anti-Vibration Mat",
            14.0,
            "anti_vibration_mat",
            "Thick rubber pads that sit under the feet of a laundry machine and damp its shake.",
            (cw("Black", "#2d2d33"),),
            (
                a("material", "Material", "Rubber"),
                a("pack_size", "Pack size", "4"),
            ),
            colorless=True,
        ),
    ),
)
