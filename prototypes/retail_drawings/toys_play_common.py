"""Shared helpers of the six toy types of gen#424.

A module beside the specs, so the registry walk does not meet it.
"""

from __future__ import annotations

from dataclasses import replace

from type_registry import Decoy, Row, a
from variants import cw

from synthetic_ecommerce_data.core.entry import canonical

PIPWICK, FERNBY, PUDDLE = "Pipwick Toys", "Little Fernby", "Puddlecombe Toys"
#: The policy a class 4 decoy (a material or feature named but absent) is repaired by (gen#311).
MATERIAL_CLAIM = "special: material claim"

RED = cw("Red", "#c8312e", "solid", "#f4f1ea")
BLUE = cw("Blue", "#3f6fb5", "solid", "#f4f1ea")
GREEN = cw("Green", "#5f9a4a", "solid", "#f4f1ea")
YELLOW = cw("Yellow", "#f2c94c", "solid", "#2f2f35")
BLACK = cw("Black", "#2a2a2e", "solid", "#f4f1ea")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
ORANGE = cw("Orange", "#e07a1f", "solid", "#2f2f35")
PINK = cw("Pink", "#f2a1b8", "solid", "#2f2f35")
#: The six main colors (gen#275) and two more, for a type that varies by color.
EIGHT = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE, ORANGE, PINK)


def age(v: str) -> tuple[str, str, str]:
    return a("age_range", "Age range", v)


def kind(v: str) -> tuple[str, str, str]:
    return a("toy_type", "Toy type", v)


def measured(key: str, name: str, v: float, unit: str) -> tuple[str, str, str, str, float]:
    """A measured entry: the value in its unit, the canonical value beside it."""
    text = f"{v:g}"
    return (key, name, text, unit, canonical(text, unit))


def count(key: str, name: str, n: int) -> tuple[str, str, str, str]:
    return (key, name, str(n), "C62")


def yes(v: bool) -> str:
    return "Yes" if v else "No"


def sizes(*pairs: tuple[object, float]) -> tuple[tuple[str, float], ...]:
    return tuple((f"{n:g}" if isinstance(n, float) else str(n), p) for n, p in pairs)


def style(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, shape: str,
          desc: str, colors: tuple, attrs: tuple, price: float, sz: tuple = (),
          size_key: str = "size", audience: str = "kids", params: tuple = (),
          colorless: bool = False) -> Row:  # fmt: skip
    """One style of a toy type in the Toys department."""
    return Row(
        code,
        title,
        brand,
        "Toys",
        path,
        ptype,
        price,
        shape,
        desc,
        colors,
        attrs,
        sz,
        audience=audience,
        colorless=colorless,
        params=params,
        size_key=size_key,
    )


def toy_decoy(cls: int, query: str, policy: str, row: Row, n: int, title: str, desc: str,
              *, brand: str = "", color=None) -> Decoy:  # fmt: skip
    """A text-match decoy of gen#294 for a toy type: a clone of one of its styles, coded ``DT<n>``.

    It keeps the style's leaf, structured entries and shape, takes a new short title and
    description (and, for class 7, a new brand) and is sold in the one ``color``, which a
    colorless type only draws. A decoy is never derived; its structured fields tell the truth.
    """
    clone = replace(
        row, code=f"DT{n:02d}", title=title, description=desc, brand=brand or row.brand,
        colors=(color or row.colors[0],),
    )  # fmt: skip
    return Decoy(cls, query, policy, clone)
