"""Coffee Pods (gen#964, slice 1): single-serve pods by the box.

**Food & Drink > Drinks > Coffee Pods** holds boxes whose title names the beans' origin, the
roast and the brew style; each SKU is a box of that many pods. The box is drawn (``box``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pantry_rows import (
    BREWHOLLOW,
    DEPARTMENT,
    FOREST,
    HEARTH,
    NAVY,
    OWNERS,
    PANTRY_MILL,
    PLUM,
    RUST,
    SAND,
    SKY,
    TEAL,
    decoy,
    row,
    units,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

PATH = (DEPARTMENT, "Drinks", "Coffee Pods")


def _pod(origin: str, roast: str, style: str) -> tuple[tuple, ...]:
    return (a("origin", "Origin", origin), a("roast", "Roast", roast),
            a("brew_style", "Brew style", style))  # fmt: skip


def _row(code: str, origin: str, roast: str, style: str, brand: str, desc: str,
         sizes: tuple[tuple[str, float], ...], color: tuple) -> object:  # fmt: skip
    return row(code, f"{origin} {roast} Roast {style} Coffee Pods", brand, PATH, "Coffee Pods",
               "box", desc, _pod(origin, roast, style), sizes, "units_per_pack", color,
               "Pods")  # fmt: skip


_SMALL = units((10, 3.0), (20, 5.5), (30, 7.5))
_LARGE = units((10, 3.5), (20, 6.5), (30, 9.0), (50, 14.0))

ROWS = (
    _row("CPDCOL", "Colombian", "Medium", "Lungo", BREWHOLLOW,
         "Single-serve pods, ground and sealed within a day of roasting, for a machine that takes standard pods.", _LARGE, RUST),
    _row("CPDETH", "Ethiopian", "Light", "Americano", BREWHOLLOW,
         "Whole beans from one growing region, ground and sealed in a single-serve pod to keep them fresh.", _LARGE, SKY),
    _row("CPDSUM", "Sumatran", "Dark", "Ristretto", BREWHOLLOW,
         "Single-serve pods for a standard pod machine, each sealed in nitrogen to keep the aroma in.", _LARGE, NAVY),
    _row("CPDBRA", "Brazilian", "Medium", "Espresso", PANTRY_MILL,
         "An everyday single-serve pod from our own range, ground and sealed after roasting.", _SMALL, SAND),
    _row("CPDGUA", "Guatemalan", "Dark", "Espresso", PANTRY_MILL,
         "Beans from a single growing region, roasted in small batches and sealed in single-serve pods.", _SMALL, PLUM),
    _row("CPDKEN", "Kenyan", "Light", "Lungo", HEARTH,
         "Single-serve pods from one growing region, for a quick cup from a standard pod machine.", _SMALL, FOREST),
    _row("CPDPER", "Peruvian", "Medium", "Americano", HEARTH,
         "Single-serve pods of shade-grown beans, ground and sealed fresh after roasting.", _SMALL, TEAL),
    _row("CPDCRI", "Costa Rican", "Dark", "Lungo", PANTRY_MILL,
         "Single-serve pods for a standard machine, from beans bought direct from a growers' cooperative.", _SMALL, RUST),
    _row("CPDHON", "Honduran", "Medium", "Ristretto", BREWHOLLOW,
         "Small-batch roasted beans in single-serve pods, sealed to keep each cup fresh.", _LARGE, FOREST),
    _row("CPDMEX", "Mexican", "Light", "Espresso", HEARTH,
         "Single-serve pods of high-grown beans, ground and sealed within a day of roasting.", _SMALL, NAVY),
)  # fmt: skip

SPEC = TypeSpec(
    key="coffee_pods",
    department=DEPARTMENT,
    product_type="Coffee Pods",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(6, "vanilla coffee pods", "generic", decoy(ROWS[3], "CPDVAN", "Vanilla Wharf Brazilian Medium Roast Espresso Coffee Pods",
              "From the Vanilla Wharf range: an unflavored espresso in a single-serve pod.")),
        Decoy(6, "caramel coffee pods", "generic", decoy(ROWS[0], "CPDCAR", "Caramel Quay Colombian Medium Roast Lungo Coffee Pods",
              "From the Caramel Quay range: an unflavored long cup in a single-serve pod.")),
    ),
)  # fmt: skip
