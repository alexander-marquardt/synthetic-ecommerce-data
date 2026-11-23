"""Beauty's cotton pieces (gen#1112, slice 2): the path, colors, brands and the row helpers.

Three types share them, each a spec under ``Beauty > Cotton``: ``type_specs/cotton_pads.py``,
``cotton_buds.py`` and ``cotton_wool.py``. Each is drawn by its shape in
:mod:`kit_beauty_cotton`. A style's SKUs are its pack counts (``piece_count``) or, for cotton
wool, its weight in grams (``net_weight_g``), and its title shows two values the scaled build
swaps (a pad's shape and texture, a bud's stem and tip, the wool's form and grade), so the build
draws more packs than the templates. Each drawing param is an attribute's key and its lower-cased
value, so a derived style draws what it states (gen#512). The rows are ``colorless``: the pack's
color is the drawing's only. The brands are Beauty template brands, with the department's own
labels on derived styles (``department_rates/beauty.py``).
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_beauty_cotton,  # noqa: F401 -- registers cotton_pad_pack, cotton_bud_tub, cotton_wool_bag
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

ROOT = "Beauty"
COTTON = (ROOT, "Cotton")

ALDERMIST, FENMERE, SORREL, VEILMOOR = "Aldermist", "Fenmere", "Sorrel & Salt", "Veilmoor"
OWNERS = tuple((b, "third_party") for b in (ALDERMIST, FENMERE, SORREL, VEILMOOR))

SKY = cw("Sky", "#8fb8d8", "solid", "#ffffff")
ROSE = cw("Rose", "#e3a5b4", "solid", "#ffffff")
SAGE = cw("Sage", "#9bb08f", "solid", "#ffffff")
LILAC = cw("Lilac", "#b7a3d6", "solid", "#2a2a2e")


def counts(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A style's pack counts or weights as its SKU sizes, each at its price."""
    return tuple((str(n), p) for n, p in pairs)


def row(code: str, title: str, brand: str, product_type: str, shape: str, description: str,
        attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...], size_key: str,
        color: tuple = SKY) -> Row:  # fmt: skip
    """One cotton style under ``Beauty > Cotton > <product_type>``: its SKUs are its sizes, and
    each attribute is a drawing param of the same key with its lower-cased value."""
    params = tuple((k, str(v).lower()) for k, _n, v in attrs)
    return Row(code, title, brand, ROOT, (*COTTON, product_type), product_type,
               sizes[0][1], shape, description, (color,), attrs, sizes, colorless=True,
               params=params, size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str) -> Row:
    """A text-match decoy cut from ``base``: its title names a range holding the query's word,
    while its fields keep ``base``'s values (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description)
