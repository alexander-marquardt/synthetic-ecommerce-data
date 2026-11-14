"""The Cleaning department's paper goods (gen#962): their paths, colors, packs and rows.

Toilet paper, paper towels and facial tissues sit under ``Cleaning > Paper Goods``. The build
record's department is ``Cleaning & Janitorial`` (:mod:`departments`), which keys the brand
pools. Each type is a spec of its own (``type_specs/toilet_paper.py``, ``paper_towels.py``,
``facial_tissues.py``) drawn by :mod:`kit_paper`. A SKU is a pack (``pack_size``), so a pack of
twelve rolls is drawn as twelve rolls (:mod:`pack_copies`). A roll of paper is white and sold
without a color (``colorless``); a tissue box is sold in the six main colors (gen#275). Every
brand here is invented (ruling 2026-10-30, gen#720).
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_paper,  # noqa: F401 -- registers toilet_roll, paper_towel_roll, tissue_box
)
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, a, cw

#: The build record's department, from the closed list of :mod:`departments`.
DEPARTMENT = "Cleaning & Janitorial"
#: The top level of every path: the store's department (``core/departments.RETAIL``).
ROOT = "Cleaning"
TOILET = (ROOT, "Paper Goods", "Toilet Paper")
TOWELS = (ROOT, "Paper Goods", "Paper Towels")
TISSUES = (ROOT, "Paper Goods", "Facial Tissues")

#: The invented paper brands, each new to the catalogue, and their owner.
FEATHERLEE = "Featherlee"
MOSSDOWN = "Mossdown"
HOLLINSBY = "Hollinsby"
OWNERS = ((FEATHERLEE, "third_party"), (MOSSDOWN, "third_party"), (HOLLINSBY, "third_party"))

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (
    cw(name, hex_, "solid", "#2a2a2e" if name == "White" else "#ffffff")
    for name, hex_ in MAIN_COLORS.items()
)
#: The six main colors (gen#275): a tissue box comes in every one.
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)
#: A roll's paper: drawn white, sold without a color.
PAPER_WHITE = (WHITE,)


def packs(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A style's packs as its SKU sizes: ``Single`` or ``<n> pack``, each at its price."""
    return tuple(("Single" if n == 1 else f"{n} pack", p) for n, p in pairs)


def roll(finish: str, ply: str, roll_size: str) -> tuple[tuple, ...]:
    """A toilet roll's attributes: its finish, its ply and its roll size."""
    return (a("finish", "Finish", finish), a("ply", "Ply", ply),
            a("roll_size", "Roll size", roll_size))  # fmt: skip


def towel(finish: str, sheet: str, roll_size: str) -> tuple[tuple, ...]:
    """A paper towel roll's attributes: its finish, its sheet and its roll size."""
    return (a("finish", "Finish", finish), a("sheet", "Sheet", sheet),
            a("roll_size", "Roll size", roll_size))  # fmt: skip


def tissue(finish: str, ply: str, box: str) -> tuple[tuple, ...]:
    """A box of tissues' attributes: its finish, its ply and its box."""
    return (a("finish", "Finish", finish), a("ply", "Ply", ply), a("box", "Box", box))


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        params: tuple[tuple[str, str], ...], colors: tuple = PAPER_WHITE) -> Row:  # fmt: skip
    """One paper style: its packs are its SKUs, times its colors when it has them (a tissue box);
    a roll of white paper carries no color."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape, description,
               colors, attrs, sizes, params=params, size_key="pack_size",
               colorless=colors == PAPER_WHITE)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, colors: tuple | None = None,
          attrs: tuple[tuple, ...] | None = None) -> Row:  # fmt: skip
    """A text-match decoy cut from ``base``: a title or description that holds the shopper's
    word, while its structured fields tell the truth."""
    return replace(base, code=code, title=title, description=description,
                   colors=base.colors if colors is None else colors,
                   attrs=base.attrs if attrs is None else attrs)  # fmt: skip
