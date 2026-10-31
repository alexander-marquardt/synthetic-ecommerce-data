"""Series and model numbers of the bicycles (gen#625, scheme of gen#622; ten brands, gen#718).

A brand owns its series: each series name belongs to one brand, and a brand gives each kind of
bike it sells one of its own. Its series are the kinds it sells: the three house brands sell all
four, and the seven bicycle-only brands fewer, a mountain specialist and an e-bike brand among
them. A model number is a letter-and-digit code the brand's scheme builds
from the bike's parts: the kind, the wheel size in inches, the number of gears and the model
year. For Wrenfield, ``RD`` (a road bike) + ``28`` (inch wheels) + ``18`` (gears) + ``26`` (the
2026 model year) is ``RD28-18-26``.

One model number is one product, whatever its color or frame size: the frame size (or a kids'
bike's wheel size) is what the SKU sells by, so it is the SKU's own attribute, not a part of the
code. A kids' bike's code therefore has no wheel digits.

The schemes differ by brand in the lead letters, the order of the parts and the separators, so
no code is two brands'; :func:`decode` reads a code back.
"""

from __future__ import annotations

import re

#: The ``bike_type`` value of each kind and the two letters it takes in a code.
KINDS = {"Road": "RD", "Mountain": "MT", "Electric": "EB", "Kids": "KD"}
_KIND_OF = {v: k for k, v in KINDS.items()}

#: Each brand's scheme: ``t`` the kind letters, ``w`` the wheel inches (empty for a kids' bike,
#: sold by wheel size), ``g`` the gears in two digits and ``y`` the model year's last two digits.
SCHEMES = {
    "Wrenfield": "{t}{w}-{g}-{y}",
    "Harbour & Pine": "HP{y}{t}{w}{g}",
    "Larkmoor": "LM{t}-{y}{w}{g}",
    "Gorsecliff": "GC{y}{t}-{w}-{g}",
    "Rindlemoor": "RM-{t}{g}-{w}{y}",
    "Tolvaney": "TV{w}{t}{g}.{y}",
    "Ostlebury": "OB{g}-{t}{w}-{y}",
    "Wattlebrook": "WB{t}{w}.{g}.{y}",
    "Pipkinford": "PK-{t}{w}{y}{g}",
    "Hessenby": "HB{y}-{g}{t}{w}",
}

#: The kinds a brand sells, each in a series of its own, and no name in two brands.
SERIES = {
    "Wrenfield": {
        "Road": "Aero Elite", "Mountain": "Aero Max",
        "Electric": "Aero Plus", "Kids": "Aero Lite",
    },
    "Harbour & Pine": {
        "Road": "Velocity Elite", "Mountain": "Velocity Max",
        "Electric": "Velocity Plus", "Kids": "Velocity Lite",
    },
    "Larkmoor": {
        "Road": "Rapid Elite", "Mountain": "Rapid Max",
        "Electric": "Rapid Plus", "Kids": "Rapid Lite",
    },
    "Gorsecliff": {"Mountain": "Scree"},
    "Rindlemoor": {"Road": "Longstride", "Mountain": "Stonebrake"},
    "Tolvaney": {"Road": "Fleetline"},
    "Ostlebury": {"Road": "Meridian", "Electric": "Meridian Assist"},
    "Wattlebrook": {"Electric": "Currentline"},
    "Pipkinford": {"Kids": "First Spin"},
    "Hessenby": {"Mountain": "Ridgeway", "Electric": "Ridgeway Assist", "Kids": "Ridgeway Junior"},
}  # fmt: skip

#: The model year every bike of the range is sold as.
MODEL_YEAR = 2026

_PARTS = {
    "t": r"(?P<t>[A-Z]{2})",
    "w": r"(?P<w>\d{2})?",
    "g": r"(?P<g>\d{2})",
    "y": r"(?P<y>\d{2})",
}
_PATTERNS = {
    brand: re.compile("".join(_PARTS.get(p, re.escape(p)) for p in re.split(r"\{(\w)\}", s)))
    for brand, s in SCHEMES.items()
}


def series_for(brand: str, kind: str) -> str:
    """The series a brand sells a kind of bike in."""
    return SERIES[brand][kind]


def encode(brand: str, kind: str, wheel: int | None, gears: int, year: int = MODEL_YEAR) -> str:
    """The model number of a bike: ``wheel`` is ``None`` for a kids' bike (its SKU axis)."""
    if kind not in SERIES[brand]:
        raise ValueError(f"{brand} sells no {kind} bike")
    if (wheel is None) != (kind == "Kids"):
        raise ValueError(f"{kind}: only a kids' bike leaves its wheel size out of the code")
    w = "" if wheel is None else f"{wheel:02d}"
    return SCHEMES[brand].format(t=KINDS[kind], w=w, g=f"{gears:02d}", y=f"{year % 100:02d}")


def decode(code: str) -> dict | None:
    """Read a model number back to its brand, kind, wheel inches (``None`` for a kids' bike),
    gears and model year; ``None`` when no brand's scheme builds it."""
    for brand, pattern in _PATTERNS.items():
        m = pattern.fullmatch(code)
        if not m or m["t"] not in _KIND_OF:
            continue
        kind, wheel = _KIND_OF[m["t"]], m["w"]
        if (wheel is None) != (kind == "Kids") or kind not in SERIES[brand]:
            continue
        return {"brand": brand, "kind": kind, "wheel": None if wheel is None else int(wheel),
                "gears": int(m["g"]), "year": 2000 + int(m["y"])}  # fmt: skip
    return None


def spec(gears: int, wheel: int | None) -> str:
    """The spec a title states between the model number and the bike: ``28in 18 Speed``."""
    speed = "Single Speed" if gears == 1 else f"{gears} Speed"
    return speed if wheel is None else f"{wheel}in {speed}"
