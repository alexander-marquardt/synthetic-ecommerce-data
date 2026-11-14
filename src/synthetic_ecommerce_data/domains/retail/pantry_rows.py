"""The shared parts of the pantry-staple types of Food & Drink (gen#964).

Coffee Pods, Granola and Flour (``type_specs/coffee_pods.py``, ``granola.py``, ``flour.py``)
sell the department's existing invented brands, so each already has a house style. A style is
colorless food: its pack color is drawn, not sold, as Tea and Coffee are (:mod:`breadth_food`).
Its SKUs are its pack sizes: the pods in a box (``units_per_pack``) or the bag's net weight in
grams (``net_weight_g``).
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import grocery_rows
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

DEPARTMENT = "Food & Drink"

#: The brands: each already sells food in the catalogue and has its house style.
BREWHOLLOW = "Brewhollow Roasters"
PANTRY_MILL = "Pantry Mill"
HEARTH = "Hearth & Table"
CRUNCHWORTH = "Crunchworth"
GOLDFIELD = "Goldfield Farms"
WHEATSHEAF = "Wheatsheaf Lane"
CROFTER = "Crofter's Bakehouse"

#: Who makes each brand, as the grocery build states it (:data:`grocery_rows.OWNERS`): a spec
#: row needs its owner before the grocery build has run.
OWNERS = tuple((b, grocery_rows.OWNERS[b]) for b in (
    BREWHOLLOW, PANTRY_MILL, HEARTH, CRUNCHWORTH, GOLDFIELD, WHEATSHEAF, CROFTER))  # fmt: skip

#: The pack colors: a box's or a bag's print, which the drawing takes as its fill.
RUST = cw("Rust", "#b5522f", "solid", "#ffffff")
FOREST = cw("Forest", "#2f6b45", "solid", "#ffffff")
NAVY = cw("Navy", "#26406b", "solid", "#ffffff")
PLUM = cw("Plum", "#6e3b6e", "solid", "#ffffff")
TEAL = cw("Teal", "#1f7a7a", "solid", "#ffffff")
SAND = cw("Sand", "#d9c08c", "solid", "#2a2a2e")
SKY = cw("Sky", "#7fb2d9", "solid", "#2a2a2e")


def grams(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """A bag's weights in kilograms as its SKU sizes: the net weight in grams, at its price."""
    return tuple((str(round(kg * 1000)), p) for kg, p in pairs)


def units(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A box's counts as its SKU sizes: the pods in each, at its price."""
    return tuple((str(n), p) for n, p in pairs)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        size_key: str, color: tuple, label: str) -> Row:  # fmt: skip
    """One pantry style: its sizes are its SKUs, and its one pack color is drawn, not sold."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape,
               description, (color,), attrs, sizes, label=label, colorless=True,
               size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str) -> Row:
    """A text-match decoy cut from ``base``: a title and a description that hold a word its
    structured fields do not (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description)
