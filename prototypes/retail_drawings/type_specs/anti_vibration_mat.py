"""Anti-Vibration Mat (gen#334): the ordinary type behind a class-8 decoy of "washing machine".

One authored product, titled without the appliance word; the class-8 decoy (gen#326) is the
spec's own `decoys`. Drawn by :func:`kit_large_appliances.anti_vibration_mat`.
Not derivable.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped.

from __future__ import annotations

import kit_large_appliances  # noqa: F401 -- registers the shape
from type_registry import Decoy, Row, TypeSpec, a
from variants import cw

SPEC = TypeSpec(
    key="anti_vibration_mat",
    department="Cleaning & Janitorial",
    product_type="Anti-Vibration Mat",
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
                a("pack_size", "Pack size", "4 pack"),
            ),
            colorless=True,
        ),
    ),
    decoys=(
        Decoy(8, "washing machine", "category", Row(
            "DT34", "Washing Machine Anti-Vibration Mat", "Pantry Mill", "Cleaning & Janitorial",
            ("Cleaning", "Laundry", "Anti-Vibration Mats"), "Anti-Vibration Mat", 16.0,
            "anti_vibration_mat", "Four rubber pads that stop a machine from walking across the floor.",
            (cw("Black", "#2d2d33"),), (), colorless=True)),
    ),
)
