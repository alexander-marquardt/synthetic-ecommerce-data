"""What the Garden specs share (gen#203): the six main colors, the attribute builders and one row.

:mod:`garden_rows` (the machines and the decoys) and the specs ``hedge_trimmer``,
``garden_furniture_set`` and ``parasol`` build their rows from these, so the swatches and the
unit handling have one home. The module imports no spec: the specs import it.
"""

from __future__ import annotations

import kit_garden
from breadth_rows import Row
from variants import cw

from synthetic_ecommerce_data.core.entry import canonical

DEPARTMENT = "Garden"
#: Invented brands of the Garden department (gen#203).
V, M = "Thistle & Wren", "Fenwold Nursery"
W, H, L = "Wrenfield", "Harbour & Pine", "Larkmoor"

_HEX = kit_garden.ACCENT_HEX
RED = cw("Red", _HEX["red"])
BLUE = cw("Blue", _HEX["blue"])
GREEN = cw("Green", _HEX["green"])
YELLOW = cw("Yellow", _HEX["yellow"])
BLACK = cw("Black", _HEX["black"])
WHITE = cw("White", _HEX["white"], "solid", "#9a9ca0")


def a(key: str, name: str, v: str) -> tuple[str, str, str]:
    """A plain structured attribute."""
    return (key, name, v)


def u(key: str, name: str, v: int, unit: str) -> tuple[str, str, str, str, float]:
    """A measured attribute with its unit: the canonical value is the core's."""
    return (key, name, str(v), unit, float(canonical(str(v), unit)))


def axis(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """SKU values of a measured axis and the price at each."""
    return tuple((f"{v:g}", p) for v, p in pairs)


def row(
    code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
    shape: str, description: str, colors: tuple, attrs: tuple, sizes: tuple = (),
    size_key: str = "size", params: tuple = (),
) -> Row:  # fmt: skip
    """A Garden style."""
    return Row(code, title, brand, DEPARTMENT, path, ptype, price, shape, description, colors,
               attrs, sizes, size_key=size_key, params=params)  # fmt: skip
