"""Health's first-aid and monitor pieces (gen#968, slice 2): paths, brands, colors and rows.

Four types share them: ``type_specs/plasters.py`` and ``first_aid_kits.py`` under
``Health > First Aid``, ``type_specs/thermometers.py`` and ``blood_pressure_monitors.py`` under
``Health > Health Monitors``. Each is drawn by its shape in :mod:`kit_health`. A row's drawing
param is the lower-cased value of one of its attributes, so a derived style that swaps the value
draws what it states (gen#512). The rows are ``colorless``: the color is the drawing's only.
Every brand is invented. Velling Apothecary is already sold in Beauty; the other three are new
and owned by third parties (:data:`OWNERS`). Over the counter only, and no title or description
claims an effect (``docs/retail-health.md``).
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_health,  # noqa: F401 -- registers plaster_box, first_aid_kit, thermometer, bp_monitor
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

ROOT = "Health"
FIRST_AID = (ROOT, "First Aid")
MONITORS = (ROOT, "Health Monitors")

VELLING = "Velling Apothecary"
QUELLMOOR = "Quellmoor Care"
HALVERING = "Halvering"
THRENNICK = "Thrennick"
#: Each spec declares the owner of the brands it sells.
OWNERS = ((VELLING, "third_party"), (QUELLMOOR, "third_party"), (HALVERING, "third_party"),
          (THRENNICK, "third_party"))  # fmt: skip

WHITE = cw("White", "#f4f4f2", "solid", "#2a2a2e")
BLUE = cw("Blue", "#3f6fb5", "solid", "#ffffff")
GREEN = cw("Green", "#2f8f5b", "solid", "#ffffff")
GREY = cw("Grey", "#9aa0a8", "solid", "#2a2a2e")


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], param: tuple[str, str],
        sizes: tuple[tuple[str, float], ...] = (), price: float = 0.0,
        color: tuple = WHITE) -> Row:  # fmt: skip
    """One Health style. With ``sizes`` its SKUs are its counts (``piece_count``); without, it is
    one SKU at ``price``."""
    return Row(code, title, brand, ROOT, path, product_type, sizes[0][1] if sizes else price,
               shape, description, (color,), attrs, sizes, colorless=True, params=(param,),
               size_key="piece_count")  # fmt: skip


def counts(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A style's counts as its SKU sizes, each at its price."""
    return tuple((str(n), p) for n, p in pairs)


def decoy(base: Row, code: str, title: str, description: str) -> Row:
    """A text-match decoy cut from ``base``: its title names a range holding the query's word,
    while its fields keep ``base``'s values (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description)
