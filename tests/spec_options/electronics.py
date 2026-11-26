"""Electronics: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

from ._shared import LENGTH, RAM, SCREEN, STORAGE

MOVED: dict[str, list[Option]] = {
    # a new phone is sold unlocked or carrier-locked, its third SKU axis (gen#1117)
    "smartphone": [STORAGE, Option("network_lock", "network_lock", "Network lock")],
    "tablet": [STORAGE],
    "e_reader": [STORAGE],
    "laptop": [STORAGE, RAM, SCREEN],
    "desktop": [STORAGE, RAM],
    "cable": [LENGTH],
    "laptop_sleeve": [SCREEN],
    "monitor": [SCREEN],
    # a smart bulb's light, connection and brightness (#956)
    "smart_bulb": [
        Option("bulb_light", "bulb_light", "Light"),
        Option("connectivity", "connectivity", "Connectivity"),
        Option("brightness_lm", "brightness", "Brightness (lm)"),
    ],
}
