"""Hedge trimmer (gen#203, a spec by gen#351): cordless, corded electric and petrol.

**Garden > Lawn Care > Hedge Trimmers**: three styles from three invented brands, one per power
source, drawn by :func:`kit_outdoor.hedge_trimmer`. The SKUs are a color times a blade length in
centimetres (the measured axis the export states with its unit); the tooth gap is a structured
entry in millimetres and a cordless style adds its battery voltage. The six main colors are
offered across the type (gen#275). Not derivable: the department grows by authored rows. The
type's text-match decoys (gen#294) are in :mod:`garden_rows`, with the other machines'.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_outdoor  # noqa: F401 -- registers hedge_trimmer
from outdoor_helpers import BLACK, BLUE, GREEN, RED, WHITE, YELLOW, H, V, W, a, axis, row, u
from type_registry import TypeSpec

_PATH = ("Garden", "Lawn Care", "Hedge Trimmers")

SPEC = TypeSpec(
    key="hedge_trimmer",
    department="Garden",
    product_type="Hedge Trimmer",
    rows=(
        row("HDGCRD", "Cordless Hedge Trimmer", V, _PATH, "Hedge Trimmer", 89.0, "hedge_trimmer",
            "A light hedge trimmer that runs on a rechargeable battery, with a dual-action blade "
            "and a rear handle, for tidying a garden hedge without a cable.",
            (GREEN, RED, BLACK, YELLOW),
            (a("power_source", "Power source", "Cordless Battery"), u("tooth_gap", "Tooth gap", 16, "MMT"),
             u("battery_voltage", "Battery voltage", 18, "VLT"), a("battery_included", "Battery included", "Yes")),
            axis((45, 89.0), (52, 109.0), (60, 129.0)), "blade_length_cm", (("power", "cordless"),)),
        row("HDGELC", "Corded Electric Hedge Trimmer", W, _PATH, "Hedge Trimmer", 49.0, "hedge_trimmer",
            "A mains hedge trimmer with a ten metre cable, a hand guard and a double-sided blade, "
            "for a medium hedge close to the house.",
            (BLUE, YELLOW, WHITE, GREEN),
            (a("power_source", "Power source", "Corded Electric"), u("tooth_gap", "Tooth gap", 20, "MMT")),
            axis((50, 49.0), (55, 59.0), (60, 69.0)), "blade_length_cm", (("power", "electric"),)),
        row("HDGPET", "Petrol Hedge Trimmer", H, _PATH, "Hedge Trimmer", 229.0, "hedge_trimmer",
            "A two-stroke hedge trimmer with a pull-start and a wide tooth gap, for thick growth "
            "and long hedges far from a socket.",
            (RED, BLACK, WHITE, BLUE),
            (a("power_source", "Power source", "Petrol"), u("tooth_gap", "Tooth gap", 28, "MMT")),
            axis((60, 229.0), (75, 279.0)), "blade_length_cm", (("power", "petrol"),)),
    ),
)  # fmt: skip
