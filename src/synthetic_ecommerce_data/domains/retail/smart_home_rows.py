"""The Electronics department's smart home rows (gen#956): smart plugs, bulbs, doorbell cameras.

The department is ``Electronics`` (``core/departments.RETAIL``), and these types sit under
``Electronics > Smart Home``. Each type is a spec of its own (``type_specs/smart_plug.py``,
``smart_bulb.py``, ``doorbell_camera.py``) drawn by :mod:`kit_smart_home`, and each is derivable:
the scaled build draws more styles from these rows by the values their titles show. Each type has
four title patterns, each authored twice by two brands, and few enough title-shown values that it
stays inside its share of the department (``tests/test_retail_electronics_smart_home_956.py``).
Every brand is an invented Electronics brand of :mod:`electronics_rows`.

A smart bulb product is its brand, range, shape and fitting (the 2026-11-15 ruling on gen#1005:
every different product has a different picture). Its title shows the shape and the fitting
alone; its light, connection and brightness are the options of its SKUs, each priced on its own,
and each comes in packs. :data:`BULB_FITTINGS` holds the fittings each shape is really sold on,
which ``scale`` reads (:func:`real_pair`) so a derived bulb is never a GU10 candle, and
:func:`fit_bulb` gives a derived bulb the brightness and prices of the shape it ended up with.
"""

from __future__ import annotations

import zlib
from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_smart_home,  # noqa: F401 -- registers smart_plug, smart_bulb, doorbell_camera
)
from synthetic_ecommerce_data.domains.retail.electronics_rows import DEPARTMENT
from synthetic_ecommerce_data.domains.retail.furniture_rows import FurnitureRow
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, a, cw

#: The top level of every path: the store's department.
ROOT = "Electronics"
PLUGS = (ROOT, "Smart Home", "Smart Plugs")
BULBS = (ROOT, "Smart Home", "Smart Bulbs")
DOORBELLS = (ROOT, "Smart Home", "Doorbell Cameras")

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (
    cw(name, hex_, "solid", "#2a2a2e" if name == "White" else "#ffffff")
    for name, hex_ in MAIN_COLORS.items()
)
#: The six main colors (gen#275), every one on every plug and doorbell template.
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        price: float, description: str, attrs: tuple[tuple, ...],
        params: tuple[tuple[str, str], ...], sizes: tuple[tuple[str, float], ...] = (),
        size_key: str = "size", colors: tuple = SIX) -> Row:  # fmt: skip
    """One smart home style: its colors (times its packs, when it has them) are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, price, shape, description,
               colors, attrs, sizes, params=params, size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, color: tuple,
          brand: str | None = None) -> Row:  # fmt: skip
    """A text-match decoy cut from ``base``: one color, and a title or description that names
    a color its structured fields do not hold (the fields tell the truth). A ``brand`` other than
    the base's keeps a decoy that draws the base's picture from being its brand's second product
    with that picture (a smart bulb's decoy: the 2026-11-15 ruling on gen#1005)."""
    return replace(base, code=code, title=title, description=description, colors=(color,),
                   brand=brand or base.brand)  # fmt: skip


#: Each smart bulb shape and the fittings it is sold on (the ruling's list): an A60 standard
#: bulb, a candle, a golf ball (P45), a large globe (G95 or G125), a reflector (R63 or R80), a
#: GU10 spot and an Edison filament bulb (ST64).
BULB_FITTINGS: dict[str, tuple[str, ...]] = {
    "A60 Standard": ("E27", "B22"), "Candle": ("E14", "E27"), "Golf Ball": ("E14", "E27"),
    "Large Globe": ("E27", "B22"), "Reflector": ("E27", "E14"), "Spot": ("GU10",),
    "Edison Filament": ("E27", "B22"),
}  # fmt: skip
#: The brightness steps (lumens) each shape is sold at, dimmest first: a candle or a spot gives
#: 470 lm, an A60 up to 1521.
BULB_LUMENS: dict[str, tuple[int, ...]] = {
    "A60 Standard": (806, 1055, 1521), "Candle": (470,), "Golf Ball": (470,),
    "Large Globe": (806, 1055), "Reflector": (470, 806), "Spot": (470,),
    "Edison Filament": (470, 806),
}  # fmt: skip
#: A single bulb's price at its shape's dimmest step, in warm white over Wi-Fi (GBP).
BULB_BASE = {
    "A60 Standard": 8.0, "Candle": 9.0, "Golf Ball": 9.0, "Large Globe": 13.0,
    "Reflector": 10.0, "Spot": 8.0, "Edison Filament": 12.0,
}  # fmt: skip
#: The price weight of a light and of a connection; each brighter step costs STEP_WEIGHT more.
LIGHT_WEIGHT = {"Warm White": 1.0, "Tunable White": 1.3, "Color Changing": 1.6}
LINK_WEIGHT = {"Bluetooth": 0.9, "Wi-Fi": 1.0, "Zigbee": 1.05}
STEP_WEIGHT = 1.15
#: The packs every bulb is sold in, and each one's price over a single bulb.
BULB_PACKS = (("Single", 1.0), ("2 pack", 1.8), ("4 pack", 3.4))


def lumens(shape: str, step: int) -> int:
    """The brightness of ``step`` (0 the dimmest) on ``shape``, its brightest when it has fewer."""
    steps = BULB_LUMENS[shape]
    return steps[min(step, len(steps) - 1)]


def bulb_price(code: str, shape: str, light: str, link: str, lm: int) -> float:
    """A single bulb's price: the shape's base, the light, the connection and the brightness
    step, times a spread of up to 6% seeded by the row and the variant (two variants of one
    weight are not one price)."""
    step = BULB_LUMENS[shape].index(lm)
    spread = 0.94 + zlib.crc32(f"{code}|{light}|{link}".encode()) % 13 / 100
    raw = BULB_BASE[shape] * LIGHT_WEIGHT[light] * LINK_WEIGHT[link] * STEP_WEIGHT**step
    return round(raw * spread * 2) / 2


def bulb_skus(code: str, shape: str, variants: tuple[tuple[str, str, int], ...]
              ) -> tuple[tuple[str, float, tuple[tuple[str, str], ...]], ...]:  # fmt: skip
    """Every SKU of a bulb: each variant (light, connection, brightness step) in each pack, as
    :class:`furniture_rows.FurnitureRow` sizes. Two variants never share a light and a
    connection, so a shape with one brightness step still sells each as its own SKU."""
    out = []
    for light, link, step in variants:
        lm = lumens(shape, step)
        single = bulb_price(code, shape, light, link, lm)
        fields = (("bulb_light", light), ("connectivity", link), ("brightness_lm", str(lm)))
        out += [(pack, round(single * k, 2), fields) for pack, k in BULB_PACKS]
    return tuple(out)


def bulb_row(code: str, brand: str, shape: str, fitting: str, description: str,
             variants: tuple[tuple[str, str, int], ...],
             attrs: tuple[tuple, ...]) -> Row:  # fmt: skip
    """One smart bulb product: its title shows the shape and the fitting alone."""
    sizes = bulb_skus(code, shape, variants)
    attrs = (a("bulb_shape", "Bulb shape", shape), a("bulb_fitting", "Bulb fitting", fitting),
             *attrs)  # fmt: skip
    params = (("bulb_shape", shape.lower()), ("bulb_fitting", fitting.lower()))
    return FurnitureRow(code, f"{shape} Smart Bulb, {fitting} Fitting", brand, DEPARTMENT, BULBS,
                        "Smart Bulb", sizes[0][1], "smart_bulb", description, (WHITE,), attrs,
                        sizes, params=params, size_key="pack_size")  # fmt: skip


def real_pair(leaf: str, values: dict[str, str]) -> bool:
    """False for a smart bulb shape on a fitting it is not sold on (a GU10 candle); True for
    every other leaf and pair. ``scale`` drops such a signature before it draws."""
    if leaf != BULBS[-1] or "bulb_shape" not in values or "bulb_fitting" not in values:
        return True
    return values["bulb_fitting"] in BULB_FITTINGS.get(values["bulb_shape"], ())


def fit_bulb(tpl: dict, rec: dict, skus: list[dict]) -> None:
    """Give a smart bulb derived to another shape that shape's brightness and prices.

    ``scale.derive`` copies the template's SKUs, so a candle derived from an A60 template kept
    its 1521 lm. Each SKU takes the step it had on the template's shape (or the brightest the
    new shape has), and its price moves by the new shape's base over the old one's.
    """
    if rec["product_type"] != "Smart Bulb":
        return
    old = next(a["value"] for a in tpl["attributes"] if a["key"] == "bulb_shape")
    new = next(a["value"] for a in rec["attributes"] if a["key"] == "bulb_shape")
    if old == new:
        return
    for s in skus:
        if "brightness_lm" not in s:
            continue
        step = BULB_LUMENS[old].index(int(s["brightness_lm"]))
        lm = lumens(new, step)
        ratio = (BULB_BASE[new] * STEP_WEIGHT ** BULB_LUMENS[new].index(lm)) / (
            BULB_BASE[old] * STEP_WEIGHT**step
        )
        s["brightness_lm"] = str(lm)
        s["price"] = round(s["price"] * ratio, 2)
