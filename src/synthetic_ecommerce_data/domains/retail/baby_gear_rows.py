"""The baby gear of Kids > Baby's shared pieces (gen#965): its paths, brands, colors and rows.

Kids > Baby sold clothing only. Its gear is under two new nodes: ``Diapering`` (diapers and baby
wipes) and ``Feeding`` (baby bottles, beside the Beakers already there). Each type is a spec of
its own (``type_specs/diapers.py``, ``baby_wipes.py``, ``baby_bottle.py``) drawn by
:mod:`kit_baby_gear`. The build record's ``department`` is ``Home``, as for the nursery types
and the baby beakers (:mod:`babywear_rows`), which keys the brand pools; the store's department
is the top level of the path, ``Kids``. Diapers and wipes carry no color (``colorless``): their
one color is the pack's, and the drawing takes it. A bottle is sold in a color, and its collar
takes it. The brands are the invented baby and nursery brands already on the catalogue.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_baby_gear,  # noqa: F401 -- registers diaper_pack, wipes_pack, baby_bottle
)
from synthetic_ecommerce_data.domains.retail.babywear_rows import (
    BLACK,
    BLUE,
    GREEN,
    GREY,
    PINK,
    RED,
    WHITE,
    YELLOW,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

#: The build record's department, from the closed list of :mod:`departments`.
DEPARTMENT = "Home"
BABY = ("Kids", "Baby")
DIAPERS = (*BABY, "Diapering", "Diapers")
WIPES = (*BABY, "Diapering", "Baby Wipes")
BOTTLES = (*BABY, "Feeding", "Baby Bottles")

LITTLE_FERNBY = "Little Fernby"
FENWOLD = "Fenwold Nursery"
HUSHWELL = "Hushwell"
THISTLE = "Thistle & Wren"
QUILLON = "Quillon Sleep"
MIREFIELD = "Mirefield Naturals"
CALDERBY = "Calderby & Lune"
LANTERNBY = "Lanternby"

#: The pack colors of the colorless types: a pack's print, which the drawing takes as its fill.
SKY = cw("Sky", "#9cc6e8", "solid", "#2a2a2e")
MINT = cw("Mint", "#a9dcc4", "solid", "#2a2a2e")
LILAC = cw("Lilac", "#c7b5e2", "solid", "#2a2a2e")
PEACH = cw("Peach", "#f4c3a3", "solid", "#2a2a2e")
LEMON = cw("Lemon", "#f3e08c", "solid", "#2a2a2e")
NAVY = cw("Navy", "#2f4a78", "solid", "#ffffff")

__all__ = [
    "BABY", "BLACK", "BLUE", "BOTTLES", "CALDERBY", "DEPARTMENT", "DIAPERS", "FENWOLD", "GREEN",
    "GREY", "HUSHWELL", "LANTERNBY", "LEMON", "LILAC", "LITTLE_FERNBY", "MINT", "MIREFIELD",
    "NAVY", "PEACH", "PINK", "QUILLON", "RED", "SKY", "THISTLE", "WHITE", "WIPES", "YELLOW",
    "decoy", "packs", "row",
]  # fmt: skip


def packs(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A style's packs as its SKU sizes: ``Single`` or ``<n> pack``, each at its price."""
    return tuple(("Single" if n == 1 else f"{n} pack", p) for n, p in pairs)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        size_key: str, params: tuple[tuple[str, str], ...], colors: tuple,
        colorless: bool = False) -> Row:  # fmt: skip
    """One baby gear style: its sizes (times its colors, unless ``colorless``) are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape, description,
               colors, attrs, sizes, audience="baby", colorless=colorless, params=params,
               size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, colors: tuple | None = None) -> Row:
    """A text-match decoy cut from ``base``: a title or description that holds a word its
    structured fields do not (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description,
                   colors=colors or base.colors[:1])  # fmt: skip
