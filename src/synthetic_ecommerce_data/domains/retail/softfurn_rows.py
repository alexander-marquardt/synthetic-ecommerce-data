"""Soft furnishings (gen#204): curtains, blinds, rugs, throws, bath mats and shower curtains.

The catalog had cushions, duvets and towels and no window dressing, no floor coverings and no
throws, so a search for a curtain, a rug or a throw found nothing or a cushion, and size,
heading, pile and room filters had nothing to narrow. Each type here is a leaf of its own under
``Home/Soft Furnishings`` (curtains, blinds, rugs, throws) or ``Home/Bathroom`` (bath mats,
shower curtains), typed by its name, with at least three styles from at least three brands, and
draws with its own shape in :mod:`kit_softfurn`.

A style's SKUs are its colors times its sizes. A size is two measured SKU fields, in centimetres
(``width_cm`` and ``drop_cm``, or ``width_cm`` and ``length_cm``), or one (``diameter_cm`` for a
round rug), so a width and a drop are each a structured attribute, never a word in a title:

==============  ======================  =============================================
type            sizes                   key attributes (each a structured entry)
==============  ======================  =============================================
Curtains        width x drop            heading, lining, material, panels
Blind           width x drop            blind type, material, blackout, cordless, fits
Rug             width x length          shape, pile, material, washable, indoor/outdoor
Throws          width x length          material, use, reversible, edge
Bath Mat        width x length          material, non-slip, quick-dry, texture
Shower Curtain  width x drop            material, waterproof, weighted hem
==============  ======================  =============================================

A drawing param is the value of the attribute that names it, lowercased, so two styles that
differ on it draw differently (``heading``, ``lined``, ``kind``, ``form``, ``pile``, ``edge``,
``texture``, ``hem``). These styles are templates only: :func:`scale.derivable` leaves them out,
as it does the sports and accessory rows, so the range grows by authored rows.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from synthetic_ecommerce_data.domains.retail import (
    kit_softfurn,  # noqa: F401 -- registers curtains, blind, rug, draped_throw, bath_mat, ...
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy
from synthetic_ecommerce_data.domains.retail.variants import cw

_SOFT = ("Home", "Soft Furnishings")
_BATH = ("Home", "Bathroom")
CURTAINS_PATH = (*_SOFT, "Curtains")
BLINDS_PATH = (*_SOFT, "Blinds")
RUGS_PATH = (*_SOFT, "Rugs")
THROWS_PATH = (*_SOFT, "Throws")
BATH_MATS_PATH = (*_BATH, "Bath Mats")
SHOWER_PATH = (*_BATH, "Shower Curtains")
HT, BM, LB = "Hearth & Table", "Brackenmere Home", "Lanternby"
CL, HP = "Calderby & Lune", "Harbour & Pine"

RED, BLUE, GREEN = cw("Red", "#c8312e"), cw("Blue", "#3f6fb5"), cw("Green", "#4f8a3a")
YELLOW, BLACK = cw("Yellow", "#f2c230"), cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
GREY, CREAM, NAVY = cw("Grey", "#9a9ca0"), cw("Cream", "#efe6cf"), cw("Navy", "#26365c")
MAIN = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


@dataclass(frozen=True)
class SoftRow(Row):
    """A style whose size is two measured SKU fields (``size_keys``), written ``"117x137"``."""

    size_keys: tuple[str, ...] = ("width_cm", "drop_cm")

    def skus(self) -> list[dict]:
        out = []
        for c in self.colors:
            for size, price in self.sizes:
                dims = dict(zip(self.size_keys, size.split("x"), strict=True))
                out.append({"color": c[0], **dims, "price": price, "in_stock": True})
        return out


def attr(key: str, name: str, value: str) -> tuple[str, str, str]:
    return (key, name, value)


def yes(key: str, name: str) -> tuple[str, str, str]:
    return (key, name, "Yes")


def params(**kw: str) -> tuple[tuple[str, str], ...]:
    return tuple(kw.items())


def stripe(name: str, accent: str):
    return cw(name, "#f6f3ea", "stripe", accent)


def gingham(name: str, accent: str):
    return cw(name, "#f6f3ea", "gingham", accent)


def row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, description: str, colors: tuple, attrs: tuple, sizes: tuple,
         prm: tuple, size_keys: tuple[str, ...] = ("width_cm", "drop_cm")) -> SoftRow:  # fmt: skip
    return SoftRow(code, title, brand, "Home", path, ptype, price, shape, description, colors,
                   attrs, sizes, params=prm, size_keys=size_keys)  # fmt: skip


def decoy(cls: int, query: str, style: SoftRow, n: int, title: str, desc: str, *, color=None,
          brand: str = "", attrs: tuple = ()) -> Decoy:  # fmt: skip
    """A text-match decoy of gen#294 for a soft furnishing: a clone of one of its styles, coded
    ``DSF<n>``. It keeps the style's leaf, shape and sizes, takes a new title and description and
    is sold in one color; its structured fields tell the truth, only the title or description
    misleads."""
    clone = replace(style, code=f"DSF{n:02d}", title=title, description=desc,
                    brand=brand or style.brand, colors=(color or style.colors[0],),
                    attrs=attrs or style.attrs)  # fmt: skip
    return Decoy(cls, query, "generic", clone)
