"""Thermometers (gen#968, slice 2): Health > Health Monitors > Thermometers.

A breadth type (``derivable``): the scaled build draws more thermometers by swapping the kind
and the display the title shows. Each style is one SKU. The drawing is a slim stick, an ear
probe or a flat forehead head by the row's kind (:func:`kit_health.thermometer`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.health_rows import (
    BLUE,
    HALVERING,
    MONITORS,
    OWNERS,
    QUELLMOOR,
    THRENNICK,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_PATH = (*MONITORS, "Thermometers")


def _thermo(code, title, brand, kind, display, price, desc, color=WHITE) -> object:  # noqa: ANN001
    return row(code, title, brand, _PATH, "Thermometers", "thermometer", desc,
               (a("thermometer_type", "Thermometer type", kind), a("display", "Display", display)),
               ("kind", kind.lower()), price=price, color=color)  # fmt: skip


ROWS = (
    _thermo("HTHSTK", "Digital Stick Thermometer", THRENNICK, "Digital Stick", "Plain", 5.0,
            "A slim thermometer for under the tongue or the arm that beeps when the reading is ready."),
    _thermo("HTHSTB", "Backlit Digital Stick Thermometer", QUELLMOOR, "Digital Stick", "Backlit", 7.0,
            "A slim thermometer with a display you can read in the dark, in a clip-shut case.", BLUE),
    _thermo("HTHEAR", "Ear Thermometer", THRENNICK, "Ear", "Backlit", 22.0,
            "A one-second reading, a memory of the last nine readings and 20 probe covers."),
    _thermo("HTHFHD", "Forehead Thermometer", HALVERING, "Forehead", "Backlit", 18.0,
            "A no-touch reading in one second, with a silent mode for a sleeping child."),
    _thermo("HTHFHQ", "Plain Forehead Thermometer", QUELLMOOR, "Forehead", "Plain", 14.0,
            "A no-touch reading in one second, switched by a single button.", BLUE),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say a
#: digital stick, so only a policy that reads ``thermometer_type`` puts the real ones first.
DECOYS = (
    Decoy(6, "ear thermometer", "generic", decoy(
        ROWS[0], "HTHDY1", "Ear & Brow Digital Stick Thermometer",
        "From the Ear & Brow range: a slim thermometer that beeps when the reading is ready.")),
    Decoy(6, "forehead thermometer", "generic", decoy(
        ROWS[1], "HTHDY2", "Forehead Friends Backlit Digital Stick Thermometer",
        "From the Forehead Friends range for children: a slim thermometer with a lit display.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="thermometers",
    department="Health",
    product_type="Thermometers",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
