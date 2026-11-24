"""The home baking set's shared pieces (gen#1119): its paths, colors and rows.

A brownie mix and a brownie tin are what the book title ``How to Make Brownies`` collides with
(``books_rows.COLLISIONS``). The mix sits in Food & Drink's baking cupboard beside the flour, the
tin in Home's bakeware beside the cake cases, and the brands are existing ones of each department.
Each type is a spec of its own (``type_specs/brownie_mix.py``, ``brownie_tin.py``) drawn by
:mod:`kit_baking`. Neither is sold by color: a carton's print and a tin's finish are drawn.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_baking,  # noqa: F401 -- registers the set's shapes
)
from synthetic_ecommerce_data.domains.retail.breadth_row import Row

MIXES = ("Food & Drink", "Food Cupboard", "Baking", "Baking Mixes")
TINS = ("Home", "Kitchen & Dining", "Bakeware", "Brownie Tins")


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        size_key: str, color: tuple, params: tuple[tuple[str, str], ...],
        label: str | None = None) -> Row:  # fmt: skip
    """One style: its sizes are its SKUs, and its one color is drawn, not sold."""
    return Row(code, title, brand, path[0], path, product_type, sizes[0][1], shape, description,
               (color,), attrs, sizes, label=label, colorless=True, size_key=size_key,
               params=params)  # fmt: skip
