"""Series and model numbers of the large appliances (gen#622).

A brand owns its series: each series name belongs to one brand across every kind of appliance
it sells, so "Arden" never reads as a brand of its own and never sits under two brands.

A model number is a letter-and-digit code the brand's own scheme builds from its parts, the
kind, the capacity, the spin speed, the generation and the color. For Frostholm, ``FW`` (the
brand, a washing machine) + ``7`` (kg) + ``12`` (1200 rpm) + ``D`` (the generation) + ``W``
(white) is ``FW712DW``. One model number is one product: a color variant changes only the last
letter, so the code without it (the base model) names the product and every color of it.

The schemes differ by brand in the lead letters, the letter a kind takes, the separator and
whether the generation comes before or after the digits; :func:`decode` reads a code back.
"""

from __future__ import annotations

import re
from typing import NamedTuple


class Scheme(NamedTuple):
    lead: str  # what every code of the brand starts with
    shift: int  # how far the brand moves the kind letters along the alphabet
    sep: str  # between the kind letter and the rest
    generation_first: bool  # the generation letter before the digits rather than after


SCHEMES = {
    "Frostholm": Scheme("F", 0, "", False),
    "Brimwell": Scheme("BR", 3, "", True),
    "Tavorne": Scheme("TV", 7, "-", False),
    "Hollinmere": Scheme("HM", 11, "", True),
    "Cleavewick": Scheme("CW", 5, "-", True),
    "Lunden & Voss": Scheme("LV", 9, "", False),
}

#: Five series a brand, thirty in all, and no name in two lists.
SERIES = {
    "Frostholm": ("Arden", "Bexley", "Calder", "Dunmore", "Elston"),
    "Brimwell": ("Fenner", "Garrow", "Halden", "Ingram", "Jessop"),
    "Tavorne": ("Kessock", "Lawton", "Marlow", "Norbury", "Ormond"),
    "Hollinmere": ("Pelham", "Quenby", "Rowan", "Selby", "Thorne"),
    "Cleavewick": ("Ulverston", "Vellacott", "Wexcombe", "Yarrow", "Zennor"),
    "Lunden & Voss": ("Ashby", "Bramley", "Coniston", "Denby", "Eskdale"),
}  # fmt: skip

#: The ``appliance_type`` value of each kind: (its base letter, what its digits hold).
#: ``wash`` is a load in kg then the spin speed in hundreds of rpm, ``dry`` a load in kg,
#: ``litres`` the capacity in litres and ``places`` the number of place settings.
KINDS = {
    "Washing Machine": ("W", "wash"),
    "Washer Dryer": ("R", "wash"),
    "Tumble Dryer (Heat Pump)": ("H", "dry"),
    "Tumble Dryer (Condenser)": ("C", "dry"),
    "Tumble Dryer (Vented)": ("V", "dry"),
    "Fridge Freezer 70/30": ("A", "litres"),
    "Fridge Freezer 50/50": ("B", "litres"),
    "Side-by-Side": ("S", "litres"),
    "Under-Counter Fridge": ("U", "litres"),
    "Larder Fridge": ("L", "litres"),
    "Chest Freezer": ("K", "litres"),
    "Upright Freezer": ("P", "litres"),
    "Integrated Fridge": ("I", "litres"),
    "Full-Size": ("D", "places"),
    "Slimline": ("M", "places"),
    "Integrated": ("J", "places"),
    "Table-Top": ("T", "places"),
}  # fmt: skip

COLORS = {"White": "W", "Black": "B", "Silver": "S", "Red": "R", "Blue": "U", "Green": "G",
          "Yellow": "Y"}  # fmt: skip
_COLOR_OF = {v: k for k, v in COLORS.items()}
_KIND_ORDER = tuple(KINDS)
_A = ord("A")


def series_for(brand: str, kind: str) -> str:
    """The series a brand gives a kind: a brand has five and a kind takes one of them."""
    names = SERIES[brand]
    return names[_KIND_ORDER.index(kind) % len(names)]


def _kind_letter(brand: str, kind: str) -> str:
    return chr((ord(KINDS[kind][0]) - _A + SCHEMES[brand].shift) % 26 + _A)


def _digits(kind: str, capacity: int, spin: int) -> str:
    group = KINDS[kind][1]
    if group == "wash":
        return f"{capacity}{spin // 100:02d}"
    if group == "litres":
        return f"{capacity:03d}"
    if group == "places":
        return f"{capacity:02d}"
    return str(capacity)


def base_model(brand: str, kind: str, capacity: int, spin: int, generation: str) -> str:
    """The code without its color letter: it names the product, whatever color it comes in."""
    s = SCHEMES[brand]
    digits = _digits(kind, capacity, spin)
    body = generation + digits if s.generation_first else digits + generation
    return f"{s.lead}{_kind_letter(brand, kind)}{s.sep}{body}"


def encode(brand: str, kind: str, capacity: int, spin: int, generation: str, color: str) -> str:
    """The model number of one color of a product: its base model and the color's letter."""
    return base_model(brand, kind, capacity, spin, generation) + COLORS[color]


def _pattern(s: Scheme) -> re.Pattern[str]:
    rest = r"(?P<g>[A-Z])(?P<d>\d+)" if s.generation_first else r"(?P<d>\d+)(?P<g>[A-Z])"
    return re.compile(rf"{re.escape(s.lead)}(?P<k>[A-Z]){re.escape(s.sep)}{rest}(?P<c>[A-Z])")


_PATTERNS = {brand: _pattern(s) for brand, s in SCHEMES.items()}


def decode(code: str) -> dict | None:
    """Read a model number back to its brand, kind, capacity, spin speed (0 when the kind has
    none), generation and color; ``None`` when no brand's scheme builds it."""
    for brand, s in SCHEMES.items():
        if not code.startswith(s.lead):
            continue
        m = _PATTERNS[brand].fullmatch(code)
        if not m or m["c"] not in _COLOR_OF:
            return None
        base = (ord(m["k"]) - _A - s.shift) % 26
        kind = next((k for k, (letter, _) in KINDS.items() if ord(letter) - _A == base), None)
        if kind is None:
            return None
        d, group = m["d"], KINDS[kind][1]
        capacity, spin = (int(d[:-2]), int(d[-2:]) * 100) if group == "wash" else (int(d), 0)
        if _digits(kind, capacity, spin) != d:
            return None
        return {"brand": brand, "kind": kind, "capacity": capacity, "spin": spin,
                "generation": m["g"], "color": _COLOR_OF[m["c"]]}  # fmt: skip
    return None


def spec(kind: str, capacity: int, spin: int) -> str:
    """The spec a title states between the model number and the kind: ``7kg 1200 Spin``."""
    group = KINDS[kind][1]
    if group == "wash":
        return f"{capacity}kg {spin} Spin"
    if group == "dry":
        return f"{capacity}kg"
    if group == "litres":
        return f"{capacity}L"
    return f"{capacity} Place"
