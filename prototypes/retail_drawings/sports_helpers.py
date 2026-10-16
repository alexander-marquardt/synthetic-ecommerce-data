"""The helpers and constants the Sports & Outdoors rows share (gen#265, gen#368): data only.

:mod:`sports_rows` (the first-increment styles, still on the legacy list) and the spec files of
``type_specs/`` (the second increment, one per type, gen#351) both build their rows from these.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_sports  # noqa: F401 -- registers tent, sleeping_bag, camp_chair, yoga_mat, ...
from breadth_rows import Row
from variants import cw

from synthetic_ecommerce_data.core.entry import canonical

DEPARTMENT = "Sports & Outdoors"
_W, _H, _L = "Wrenfield", "Harbour & Pine", "Larkmoor"
_SO = DEPARTMENT
_TENTS = (_SO, "Camping", "Tents")
_CAMP = (_SO, "Camping")
_YOGA = (_SO, "Yoga & Fitness", "Yoga")
_WEIGHTS = (_SO, "Yoga & Fitness", "Weights")
_FIT = (_SO, "Yoga & Fitness")

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
ORANGE = cw("Orange", "#e07a1f")
GREY = cw("Grey", "#9a9ca0")


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _kg(key: str, name: str, kg: int) -> tuple[str, str, str, str, float]:
    """A weight in kilograms: the canonical value is in grams, as the core's ``KGM`` says."""
    return (key, name, str(kg), "KGM", float(canonical(str(kg), "KGM")))


def _mm(key: str, name: str, mm: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(mm), "MMT", float(mm))


def _season(n: int) -> tuple[str, str, str]:
    return _a("season_rating", "Season rating", f"{n} Season")


def _axis(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """SKU values of a measured axis and the price at each."""
    return tuple((f"{v:g}", p) for v, p in pairs)


def _row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, description: str, colors: tuple, attrs: tuple, sizes: tuple = (),
         size_key: str = "size", params: tuple = ()) -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, path, ptype, price, shape, description, colors,
               attrs, sizes, size_key=size_key, params=params)  # fmt: skip


_CYCLING = (_SO, "Cycling", "Bike Pumps")
_BASEBALL = (_SO, "Baseball")
_SWIM = (_SO, "Swimming")
_TEAM = (_SO, "Team & Racket Sports")
_PRIMARY = (RED, BLUE, GREEN, YELLOW)
_NEUTRAL = (BLACK, WHITE, BLUE, GREEN)


def _cm(key: str, name: str, cm: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(cm), "CMT", float(cm * 10))


def _words(*pairs: tuple[str, float]) -> tuple[tuple[str, float], ...]:
    """A SKU axis of words (a resistance level, a grip size) and the price at each."""
    return pairs
