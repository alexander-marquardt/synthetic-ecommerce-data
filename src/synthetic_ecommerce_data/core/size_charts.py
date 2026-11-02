"""The size charts every domain reads (gen#125, slice 2 of the 2026-10-28 ruling).

A size system is a fact about the world, not about a store, like the units in
:mod:`.dimensions`: UK 5 is EU 38 and US 7 in every shop that sells a women's shoe. So the charts
live here, in core, and a domain reads a chart and never builds one of its own. One chart row is
one size in every system, ``(UK, EU, US)``; a variant states its size as the three attribute
entries :data:`KEYS`, all three from ONE row, so they can never disagree.

:func:`problems` is the standard's size rule (:func:`.standard.check_document` runs it on every
variant): a variant that carries one of :data:`KEYS` carries all three, and its three values are
a row of a chart in :data:`CHARTS`. Which sizes a product is cut in (a jean's leg lengths, a bra's
band and cup rules) is the domain's choice; the row a size reads is not.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

#: One size in each system: (UK, EU, US).
Row = tuple[str, str, str]

#: The attribute keys a size is stated in, in :data:`Row` order.
KEYS = ("size_uk", "size_eu", "size_us")


def _n(x: float) -> str:
    return f"{x:g}"


def _shoes(lo: int, hi: int, eu: int, us: int) -> dict[str, Row]:
    """Whole and half UK sizes ``lo`` to ``hi``; EU and US are UK plus a fixed step."""
    sizes = [lo + n / 2 for n in range(2 * (hi - lo) + 1)]
    return {_n(uk): (_n(uk), _n(uk + eu), _n(uk + us)) for uk in sizes}


#: Women's clothing: UK dress size -> (UK, EU, US); UK 4-26, EU = UK + 28, US = UK - 4.
WOMENS: dict[int, Row] = {uk: (str(uk), str(uk + 28), str(uk - 4)) for uk in range(4, 27, 2)}
#: Men's waist in inches -> (UK, EU, US); W28-42, odd waists to 33.
MENS_WAIST: dict[int, Row] = {
    w: (str(w), str(w + 16), str(w)) for w in (28, 29, 30, 31, 32, 33, 34, 36, 38, 40, 42)
}
#: Children's clothing by age: the EU size is the height in cm.
KIDS_AGES: dict[str, Row] = {
    uk: (uk, eu, us)
    for uk, eu, us in (
        ("3-4Y", "104", "4"), ("5-6Y", "116", "6"), ("7-8Y", "128", "8"),
        ("9-10Y", "140", "10"), ("11-12Y", "152", "12"), ("13-14Y", "164", "14"),
    )
}  # fmt: skip
#: Babywear by age in months: the EU size is the height in cm.
BABY_AGES: dict[str, Row] = {
    uk: (uk, eu, uk) for uk, eu in (
        ("0-3M", "62"), ("3-6M", "68"), ("6-12M", "80"), ("12-18M", "86"), ("18-24M", "92"),
    )
}  # fmt: skip
#: Letter sizes, the same in every system.
LETTER: dict[str, Row] = {s: (s, s, s) for s in ("XS", "S", "M", "L", "XL", "XXL")}

#: Women's shoes: UK 5 = EU 38 = US 7.
WOMENS_SHOES = _shoes(2, 9, 33, 2)
#: Men's shoes: UK 9 = EU 43 = US 10.
MENS_SHOES = _shoes(5, 14, 34, 1)
#: Kids' shoes: infant sizes run to 13, then junior sizes start again at 1; US child (C)
#: sizes, then youth (Y). Whole sizes only.
KIDS_SHOES: dict[str, Row] = {
    uk: (uk, eu, us)
    for uk, eu, us in (
        ("4 Infant", "20", "4.5C"), ("5 Infant", "21", "5.5C"), ("6 Infant", "23", "6.5C"),
        ("7 Infant", "24", "7.5C"), ("8 Infant", "25", "8.5C"), ("9 Infant", "27", "9.5C"),
        ("10 Infant", "28", "10.5C"), ("11 Infant", "29", "11.5C"),
        ("12 Infant", "30", "12.5C"), ("13 Infant", "32", "13.5C"),
        ("1 Junior", "33", "1.5Y"), ("2 Junior", "34", "2.5Y"), ("3 Junior", "35", "3.5Y"),
        ("4 Junior", "37", "4.5Y"), ("5 Junior", "38", "5.5Y"), ("6 Junior", "39", "6.5Y"),
    )
}  # fmt: skip
#: Slippers come in letter sizes, each spanning two shoe sizes per system.
SLIPPERS_WOMEN: dict[str, Row] = {"S": ("3-4", "36-37", "5-6"), "M": ("5-6", "38-39", "7-8"),
                                  "L": ("7-8", "40-41", "9-10")}  # fmt: skip
SLIPPERS_MEN: dict[str, Row] = {"M": ("7-8", "41-42", "8-9"), "L": ("9-10", "43-44", "10-11"),
                                "XL": ("11-12", "45-46", "12-13")}  # fmt: skip

#: Bra band sizes in inches (UK and US); the EU band is in cm.
BRA_BANDS: tuple[int, ...] = (28, 30, 32, 34, 36, 38, 40, 42, 44, 46)
#: UK cup, then its EU and US names (one row per cup, so the systems never disagree).
BRA_CUPS: tuple[Row, ...] = (
    ("AA", "AA", "AA"),
    ("A", "A", "A"),
    ("B", "B", "B"),
    ("C", "C", "C"),
    ("D", "D", "D"),
    ("DD", "E", "DD"),
    ("E", "F", "DDD"),
    ("F", "G", "G"),
    ("FF", "H", "H"),
    ("G", "I", "I"),
    ("GG", "J", "J"),
    ("H", "K", "K"),
    ("HH", "L", "L"),
    ("J", "M", "M"),
)
#: Every band by every cup: "34DD" -> ("34DD", "75E", "34DD"). Which pairs a bra is cut in is
#: the domain's rule, not the chart's.
BRAS: dict[str, Row] = {
    f"{band}{uk}": (f"{band}{uk}", f"{60 + (band - 28) // 2 * 5}{eu}", f"{band}{us}")
    for band in BRA_BANDS
    for uk, eu, us in BRA_CUPS
}

#: Bed and pillow sizes -> (UK, EU, US): the EU size is the mattress or pillow in cm.
BEDDING: dict[str, Row] = {
    "Single": ("Single", "90 x 200 cm", "Twin"),
    "Small Double": ("Small Double", "120 x 190 cm", "Three Quarter"),
    "Double": ("Double", "140 x 200 cm", "Full"),
    "King": ("King", "150 x 200 cm", "Queen"),
    "Super King": ("Super King", "180 x 200 cm", "King"),
    "Standard Pillow": ("Standard", "50 x 75 cm", "Standard"),
    "King Pillow": ("King", "50 x 90 cm", "King"),
    "Square Pillow": ("Square", "65 x 65 cm", "Euro"),
}

#: Every chart, by name: the rows :func:`problems` accepts.
CHARTS: dict[str, Mapping[Any, Row]] = {
    "womens": WOMENS,
    "mens_waist": MENS_WAIST,
    "kids_ages": KIDS_AGES,
    "baby_ages": BABY_AGES,
    "letter": LETTER,
    "womens_shoes": WOMENS_SHOES,
    "mens_shoes": MENS_SHOES,
    "kids_shoes": KIDS_SHOES,
    "slippers_women": SLIPPERS_WOMEN,
    "slippers_men": SLIPPERS_MEN,
    "bras": BRAS,
    "bedding": BEDDING,
}
_ROWS: frozenset[Row] = frozenset(row for chart in CHARTS.values() for row in chart.values())


def problems(where: str, attributes: Iterable[Any]) -> list[str]:
    """How one variant's size entries break the size rule; empty when they hold."""
    held = {
        e["key"]: e.get("value") for e in attributes if isinstance(e, dict) and e.get("key") in KEYS
    }
    if not held:
        return []
    missing = [k for k in KEYS if k not in held]
    if missing:
        stated = ", ".join(k for k in KEYS if k in held)
        return [f"{where}: states {stated} without {', '.join(missing)}"]
    row = tuple(held[k] for k in KEYS)
    if row not in _ROWS:
        return [f"{where}: size {row!r} (UK, EU, US) is no row of a core size chart"]
    return []
