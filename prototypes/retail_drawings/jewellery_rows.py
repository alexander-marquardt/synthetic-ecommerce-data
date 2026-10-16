"""The helpers the jewellery and watch specs share (gen#423): data only.

Five spec files of ``type_specs/`` (``hoop_earrings``, ``drop_earrings``, ``analog_watch``,
``digital_watch``, ``fitness_band``) build their rows from these. An earring SKU is a metal (the
color is the metal, as every jewelry row since gen#207: :class:`accessory_rows.ARow`); a watch SKU
is a strap color times a case diameter in millimetres (``case_mm``, a measured option).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_jewellery  # noqa: F401 -- registers hoop_earrings, drop_earrings, analog_watch, ...
from accessory_rows import ARow
from audience import MENS, WOMENS
from breadth_rows import Row
from variants import cw

CLOTHING = "Clothing"
#: Invented brands. The first three are already stated by other modules; the last two are new.
OWNED = (("Tidewell", "third_party"), ("Skerry & Cole", "third_party"))
WRENFIELD, LARKMOOR, CALDERBY, HARBOUR, TIDEWELL, SKERRY = (
    "Wrenfield", "Larkmoor", "Calderby & Lune", "Harbour & Pine", "Tidewell", "Skerry & Cole",
)  # fmt: skip

GOLD = cw("Gold", "#d4af37", "solid", "#8a6a22")
SILVER = cw("Silver", "#cfd5da", "solid", "#8f989f")
ROSE_GOLD = cw("Rose Gold", "#d8a28f", "solid", "#8a5a48")
METALS = {"Gold": "Gold Plated", "Silver": "Sterling Silver", "Rose Gold": "Rose Gold Plated"}
STEEL = {"Gold": "Gold Plated Stainless Steel", "Silver": "Stainless Steel", "Rose Gold": "Rose Gold Plated Stainless Steel"}  # fmt: skip
ALL_METALS = (GOLD, SILVER, ROSE_GOLD)

BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
BLUE = cw("Blue", "#3f6fb5")
RED = cw("Red", "#c8312e")
GREEN = cw("Green", "#4f7a3a")
YELLOW = cw("Yellow", "#f2c230")
BROWN = cw("Brown", "#6b4a2e")
#: The six main colors (gen#275) a strap type offers in every audience it sells to.
MAIN_SIX = (BLACK, WHITE, BLUE, RED, GREEN, YELLOW)


def a(key: str, name: str, value: str) -> tuple[str, str, str]:
    return (key, name, value)


def metres(key: str, name: str, m: int) -> tuple[str, str, str, str, float]:
    """A length in metres: the canonical value is in metres, as the core's ``MTR`` says."""
    return (key, name, str(m), "MTR", float(m))


def earrings_row(
    code: str, title: str, brand: str, price: float, desc: str, shape: str, leaf: str, ptype: str,
    style_attr: tuple, params: tuple, colors: tuple = ALL_METALS, steel: bool = False,
    stone: str | None = None, hypoallergenic: bool = True, label: str | None = None,
) -> ARow:  # fmt: skip
    """A pair of earrings: one SKU per metal, each drawn in its metal."""
    table = STEEL if steel else METALS
    attrs = (
        style_attr, *(a("metal", "Metal", table[c[0]]) for c in colors),
        *((a("stone", "Stone", stone),) if stone else ()),
        *((a("hypoallergenic", "Hypoallergenic", "Yes"),) if hypoallergenic else ()),
        a("audience", "Audience", WOMENS),
    )  # fmt: skip
    return ARow(
        code, title, brand, CLOTHING, ("Womens", "Jewellery", leaf), ptype, price, shape, desc,
        colors, attrs, params=params, metals=tuple(table[c[0]] for c in colors), label=label,
    )  # fmt: skip


def watch_row(
    code: str, title: str, brand: str, who: str, leaf: str, ptype: str, price: float, shape: str,
    desc: str, colors: tuple, strap: str, water_m: int, diameters: tuple[tuple[int, float], ...],
    params: tuple, extra: tuple = (), label: str | None = None,
) -> Row:  # fmt: skip
    """A watch: a strap color times a case diameter (``case_mm``), a strap, a water resistance."""
    assert who in (WOMENS, MENS), who
    attrs = (
        a("strap", "Strap", strap), metres("water_resistance", "Water resistance", water_m),
        *extra, a("audience", "Audience", who),
    )  # fmt: skip
    sizes = tuple((str(mm), p) for mm, p in diameters)
    return Row(
        code, title, brand, CLOTHING, (who, "Watches", leaf),
        ptype, price, shape, desc, colors, attrs, sizes, label=label, size_key="case_mm",
        params=params,
    )  # fmt: skip
