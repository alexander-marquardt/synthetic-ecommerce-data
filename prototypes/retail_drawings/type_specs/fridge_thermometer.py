"""Fridge Thermometer (gen#334): the ordinary type behind a class-8 decoy of "fridge".

One authored product, titled without the appliance word; the decoy (gen#326) is in
``feature_decoys/large_appliances.py``. Drawn by :func:`kit_large_appliances.fridge_thermometer`.
Not derivable.
"""

from __future__ import annotations

import kit_large_appliances  # noqa: F401 -- registers the shape
from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain

SPEC = TypeSpec(
    key="fridge_thermometer",
    department="Home",
    product_type="Fridge Thermometer",
    rows=(
        plain(
            "FTHPLN",
            "Hanging Dial Cold Store Thermometer",
            HOME,
            "Home",
            ("Home", "Kitchen & Dining", "Fridge Thermometers"),
            "Fridge Thermometer",
            "fridge_thermometer",
            "A dial thermometer with a safe zone marked in green, hung from a shelf bar.",
            6.0,
            (
                a("display", "Display", "Dial"),
                a("material", "Material", "Steel"),
            ),
        ),
    ),
)
