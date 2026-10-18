"""Light bulbs (gen#498, a spec by gen#351): Home > Lighting > Light Bulbs.

A shopper who types *soft white* wants the bulb a box names that way, and lighting retailers
filter bulbs by color temperature. The catalog held lamps and shades but no bulb, so the words
had nothing to match. This type is LED bulbs in the four fittings a home meets (E27 and B22
pear-shaped GLS bulbs, E14 candles, GU10 spotlights), two wattages of each, and each of those in
the four temperatures a box prints:

======  ==========  ==================================
kelvin  box name    for
======  ==========  ==================================
2700    Warm White  living rooms and bedrooms
3000    Soft White  a gentle light for the home
4000    Cool White  kitchens and hallways
6500    Daylight    workshops and task lighting
======  ==========  ==================================

A temperature is a listing of its own, as on a retailer's shelf: the box name and the kelvin
count are in the title ("LED GLS Bulb, E27, 8.5W, Warm White 2700K") and the product holds one
``color_temperature`` entry (unit KEL), the one key every light states its temperature under
(``lighting_rows``). The SKUs are the pack, one bulb or four (``units_per_pack``). The bulb is
colorless: its glass is clear or frosted, and the light's color is its temperature, which the
drawing shows as a warmer or cooler glow (:func:`kit_lighting.light_bulb`). Not derivable: the
grid is authored whole, so every fitting has every temperature. The decoys that hold a box name
without being a light (a paint, a candle, a face cream) are in :mod:`decoy_rows` (class 4).
Every brand here is invented.
"""

from __future__ import annotations

import kit_lighting  # noqa: F401 -- registers light_bulb
from type_registry import Row, TypeSpec, a, cw

_PATH = ("Home", "Lighting", "Light Bulbs")
#: kelvin -> (the name printed on a bulb box, what the light suits).
BOX = {
    2700: ("Warm White", "the glow of a traditional bulb, for living rooms and bedrooms"),
    3000: ("Soft White", "a gentle, slightly crisper light for living rooms and hallways"),
    4000: ("Cool White", "a clean, neutral light for kitchens, bathrooms and hallways"),
    6500: ("Daylight", "a bright, blue-white light for workshops, garages and reading"),
}
#: Per fitting: the glass form, the title's name for it, its cap, and the (watts, watts replaced,
#: price of one bulb) of each of its two bulbs. A GLS bulb is the household pear-shaped bulb.
_RANGE = (
    ("E27", "gls", "GLS", "an E27 screw cap", "Lanternby", ((8.5, 60, 3.5), (13.0, 100, 4.5))),
    ("E14", "candle", "Candle", "a small E14 screw cap", "Calderby & Lune",
     ((4.0, 40, 3.0), (6.0, 60, 3.8))),
    ("GU10", "spot", "Spotlight", "a GU10 two-pin cap", "Brackenmere Home",
     ((3.5, 35, 2.8), (5.0, 50, 3.4))),
    ("B22", "gls", "GLS", "a B22 bayonet cap", "Harbour & Pine",
     ((8.5, 60, 3.6), (13.0, 100, 4.6))),
)  # fmt: skip
_GLASS = cw("White", "#f3f1ea", "solid", "#9a9ca0")


def _watts(key: str, name: str, w: float) -> tuple[str, str, str, str, float]:
    """A power in watts (unit code WTT; the canonical value is the count)."""
    return (key, name, f"{w:g}", "WTT", float(w))


def _kelvin(k: int) -> tuple[str, str, str, str, float]:
    """The one color temperature entry every light states (unit KEL)."""
    return ("color_temperature", "Color temperature", str(k), "KEL", float(k))


def _row(n: int, fitting: str, form: str, noun: str, cap: str, brand: str,
         watts: float, equal: int, price: float, k: int) -> Row:  # fmt: skip
    box, suits = BOX[k]
    return Row(
        f"LB{n:02d}", f"LED {noun} Bulb, {fitting}, {watts:g}W, {box} {k}K", brand, "Home", _PATH,
        "Light Bulb", price, "light_bulb",
        f"{noun} bulb with LED light on {cap}. It uses {watts:g}W and gives the light of a "
        f"{equal}W bulb. {box} {k}K is {suits}.",
        (_GLASS,),
        (a("bulb_fitting", "Bulb fitting", fitting), a("bulb_shape", "Bulb shape", noun),
         _watts("bulb_wattage", "Bulb wattage", watts),
         _watts("equivalent_wattage", "Equivalent wattage", equal),
         _kelvin(k), a("light_source", "Light source", "LED")),
        (("1", price), ("4", round(price * 3.6, 2))), size_key="units_per_pack",
        params=(("form", form), ("fitting", fitting), ("kelvin", str(k))), colorless=True,
    )  # fmt: skip


def _rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for fitting, form, noun, cap, brand, bulbs in _RANGE:
        for watts, equal, price in bulbs:
            for k in BOX:
                n = len(out) + 1
                out.append(_row(n, fitting, form, noun, cap, brand, watts, equal, price, k))
    return tuple(out)


SPEC = TypeSpec(
    key="light_bulb",
    department="Home",
    product_type="Light Bulb",
    rows=_rows(),
)
