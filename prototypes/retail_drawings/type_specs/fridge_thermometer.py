"""Fridge Thermometer (gen#334): the ordinary type behind a class-8 decoy of "fridge".

One authored product, titled without the appliance word; the class-8 decoy (gen#326) is the
spec's own `decoys`. Drawn by :func:`kit_large_appliances.fridge_thermometer`.
Not derivable.
"""

from __future__ import annotations

import kit_large_appliances  # noqa: F401 -- registers the shape
from type_registry import TypeSpec, a
from word_decoy_types import HOME, plain, word_decoy

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
    decoys=(
        word_decoy(
            33, "Fridge Thermometer",
            "A dial thermometer that hangs on a shelf and shows the temperature inside.",
            "Grey", HOME, "Home", ("Home", "Kitchen & Dining", "Fridge Thermometers"),
            "Fridge Thermometer", "fridge_thermometer", 7.0, "fridge", "category",
        ),
    ),
)
