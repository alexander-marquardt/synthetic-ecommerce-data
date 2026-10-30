"""Series and model numbers of the small machines (gen#622, in the scheme of gen#625).

Kettles, toasters, the garden machines and the drill drivers carry a model number on the box, as
the large appliances and the bicycles do. A brand owns its series: each series name belongs to
one brand, and its lead word is the brand's across every kind. Each series is a model of its
kind's family in :mod:`line_grammar`, so the words a brand authors here are out of the deal its
derived styles draw from.

A model number is a letter-and-digit code the brand's scheme builds from the machine's parts: the
kind, a letter for its variant, two or three digits for its measure and the model year. For
Hearth & Table, ``KT`` (a kettle) + ``30`` (3000 W) + ``S`` (a standard kettle) + ``26`` (the 2026
model year) is ``HTKT30S-26``.

One model number is one product, whatever its color or size: the color and the size are what the
SKU sells by, so they are the SKU's own attributes, not parts of the code. The schemes differ by
brand in the lead letters, the order of the parts and the separators, so no code is two brands';
:func:`decode` reads a code back.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import replace
from typing import NamedTuple

from synthetic_ecommerce_data.domains.retail.breadth_rows import Row


class Kind(NamedTuple):
    letters: str  # what a code calls the kind
    variant: str  # the attribute the code's variant letter holds
    variants: dict[str, str]  # the attribute's value -> its letter
    measure: str  # the attribute the code's digits hold
    step: int  # what one in the digits counts of the measure
    spec: str  # what a title states, given the measure; empty when the title opens on it


#: A mower's spec spells its liters out: ``40L`` in a title would read as a net volume
#: (:data:`net_volume.TITLE_VOLUME`), and a grass box is not what the mower holds for sale.
_POWER = {"Cordless Battery": "B", "Petrol": "P", "Corded Electric": "E"}

#: product type -> how a code reads it.
KINDS = {
    "Kettle": Kind(
        "KT", "kettle_type", {"Standard": "S", "Quiet Boil": "Q", "Temperature Control": "T", "Travel": "V"},
        "wattage", 100, "{}W",
    ),
    "Toaster": Kind("TS", "finish", {"Gloss": "G", "Brushed": "B", "Matte": "M"}, "browning_settings", 1, "{} Setting"),
    "Lawn Mower": Kind("LM", "power_source", _POWER, "grass_box_capacity", 1, "{} Liter Box"),
    "Robot Mower": Kind("RM", "boundary", {"Wire": "W", "Wire-Free GPS": "G"}, "max_slope", 1, "{}% Slope"),
    "Grass Trimmer": Kind("GT", "power_source", _POWER, "shaft_length", 1, "{}cm Shaft"),
    "Hedge Trimmer": Kind("HG", "power_source", _POWER, "tooth_gap", 1, "{}mm Tooth Gap"),
    "Drill Driver": Kind("DD", "motor_type", {"Brushed": "B", "Brushless": "L"}, "voltage_v", 1, ""),
}  # fmt: skip
_KIND_OF = {k.letters: name for name, k in KINDS.items()}

#: Each brand's scheme: ``t`` the kind letters, ``d`` the measure's digits, ``v`` the variant
#: letter and ``y`` the model year's last two digits.
SCHEMES = {
    "Hearth & Table": "HT{t}{d}{v}-{y}",
    "Calderby & Lune": "CL-{t}{y}{v}{d}",
    "Emberly Home": "EM{t}{v}{d}{y}",
    "Lanternby": "LB{y}{t}{d}{v}",
    "Larchwood Living": "LW{t}-{d}{v}{y}",
    "Cobble & Kiln": "CK{d}{t}{v}-{y}",
    "Thistle & Wren": "TW{t}{v}-{d}-{y}",
    "Fenwold Nursery": "FN{y}{t}{v}{d}",
    "Harbour & Pine": "HP{y}{t}{d}{v}",
    "Wrenfield": "{t}{d}-{v}-{y}",
    "Torvane Tools": "TT{t}{d}{v}{y}",
    "Harkwell Works": "HK-{t}{v}{d}-{y}",
    "Marlowick": "MW{y}-{t}{d}{v}",
}

#: The series a brand sells each kind in: one lead word a brand, and no name in two brands.
SERIES = {
    "Hearth & Table": {"Kettle": "Brew Max", "Toaster": "Brew Duo"},
    "Calderby & Lune": {"Kettle": "Steam Pro", "Toaster": "Steam Duo", "Drill Driver": "Torque Pro"},
    "Emberly Home": {"Kettle": "Galley Plus", "Toaster": "Galley Duo"},
    "Lanternby": {"Kettle": "Simmer Lite"},
    "Larchwood Living": {"Kettle": "Larder Max", "Toaster": "Larder Lite"},
    "Cobble & Kiln": {"Kettle": "Prep Mini"},
    "Thistle & Wren": {"Lawn Mower": "Verge Pro", "Robot Mower": "Verge Max", "Grass Trimmer": "Verge Lite", "Hedge Trimmer": "Verge Duo"},
    "Fenwold Nursery": {"Lawn Mower": "Terrace Pro", "Robot Mower": "Terrace Max"},
    "Harbour & Pine": {"Lawn Mower": "Pasture Pro", "Robot Mower": "Pasture Max", "Grass Trimmer": "Pasture Lite", "Hedge Trimmer": "Pasture Duo"},
    "Wrenfield": {"Lawn Mower": "Hedgerow Pro", "Grass Trimmer": "Hedgerow Lite", "Hedge Trimmer": "Hedgerow Duo"},
    "Torvane Tools": {"Drill Driver": "Drive Pro"},
    "Harkwell Works": {"Drill Driver": "Anvil Pro"},
    "Marlowick": {"Drill Driver": "Forge Mini"},
}  # fmt: skip

#: The model year every machine of the range is sold as.
MODEL_YEAR = 2026

_PARTS = {
    "t": r"(?P<t>[A-Z]{2})",
    "d": r"(?P<d>\d{2,3})",
    "v": r"(?P<v>[A-Z])",
    "y": r"(?P<y>\d{2})",
}
_PATTERNS = {
    brand: re.compile("".join(_PARTS.get(p, re.escape(p)) for p in re.split(r"\{(\w)\}", s)))
    for brand, s in SCHEMES.items()
}


def encode(brand: str, kind: str, variant: str, measure: int, year: int = MODEL_YEAR) -> str:
    """The model number of a machine: ``variant`` and ``measure`` are its attributes' values."""
    k = KINDS[kind]
    return SCHEMES[brand].format(
        t=k.letters, v=k.variants[variant], d=f"{measure // k.step:02d}", y=f"{year % 100:02d}"
    )


def decode(code: str) -> dict | None:
    """Read a model number back to its brand, kind, variant, measure and model year; ``None`` when
    no brand's scheme builds it."""
    for brand, pattern in _PATTERNS.items():
        m = pattern.fullmatch(code)
        if not m or m["t"] not in _KIND_OF:
            continue
        kind = _KIND_OF[m["t"]]
        variant = next((v for v, letter in KINDS[kind].variants.items() if letter == m["v"]), None)
        if variant is None:
            continue
        return {"brand": brand, "kind": kind, "variant": variant,
                "measure": int(m["d"]) * KINDS[kind].step, "year": 2000 + int(m["y"])}  # fmt: skip
    return None


def spec(kind: str, measure: int) -> str:
    """The spec a title states between the model number and the machine: ``3000W``."""
    return KINDS[kind].spec.format(measure)


def numbered(rows: Iterable[Row]) -> tuple[Row, ...]:
    """``rows`` under their brand's series and model number: the title reads brand, series, model
    number, spec, then the row's own title, "Hearth & Table Brew Max HTKT30S-26 3000W Rapid Boil
    Jug Kettle", and every color's SKU states the one code."""
    return tuple(_numbered(row) for row in rows)


def _numbered(row: Row) -> Row:
    k = KINDS[row.product_type]
    attrs = {a[0]: a[2] for a in row.attrs}
    measure = int(attrs[k.measure])
    code = encode(row.brand, row.product_type, attrs[k.variant], measure)
    series = SERIES[row.brand][row.product_type]
    head = (row.brand, series, code, spec(row.product_type, measure), row.title)
    return replace(
        row, title=" ".join(p for p in head if p),
        attrs=(*row.attrs, ("model_number", "Model number", code), ("model_year", "Model year", str(MODEL_YEAR))),
        product_line=series, color_codes=tuple((c[0], code) for c in row.colors),
    )  # fmt: skip
