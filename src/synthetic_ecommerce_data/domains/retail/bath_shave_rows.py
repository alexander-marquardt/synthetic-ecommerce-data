"""Beauty's bath and shaving depth (gen#1112, slice 3): the paths, colors and the row helper.

Two new types under ``Beauty > Shaving`` (``type_specs/razor_cartridges.py`` and
``shave_gel.py``) and Shower Gel's body wash rows (``type_specs/shower_gel.py``) are built here,
each drawn by its shape in :mod:`kit_bath_shave`. A style's SKUs are its pack counts
(``piece_count``) or volumes (``net_volume_ml``), and its title shows the values the scaled build
swaps, so the build draws more styles than the templates. Each drawing param is an attribute's
key and its lower-cased value, so a derived style draws what it states (gen#512). The rows are
``colorless``: the pack's color is the drawing's only. The brands are the Beauty template brands
of :mod:`skin_rows`, with the department's own labels on derived styles.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_bath_shave,  # noqa: F401 -- registers body_wash_bottle, razor_cartridge_pack, shave_gel_can
)
from synthetic_ecommerce_data.domains.retail.skin_rows import OWNED
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

ROOT = "Beauty"
SHAVING = (ROOT, "Shaving")
SHOWER_GEL = (ROOT, "Bath & Body", "Shower Gel")

THORNLEA, ALDERMIST, PEARLBROOK = "Thornlea Skin", "Aldermist", "Pearlbrook"
SORREL, VEILMOOR, FENMERE = "Sorrel & Salt", "Veilmoor", "Fenmere"
#: Every brand above is a third party's (:data:`skin_rows.OWNED`).
OWNERS = OWNED

NAVY = cw("Navy", "#2f3a4a", "solid", "#ffffff")
SLATE = cw("Slate", "#5e6b78", "solid", "#ffffff")
TEAL = cw("Teal", "#2a7f80", "solid", "#ffffff")
CREAM = cw("Cream", "#efe8d8", "solid", "#2a2a2e")
BLUSH = cw("Blush", "#e9c3c6", "solid", "#2a2a2e")
FERN = cw("Fern", "#9bb08f", "solid", "#ffffff")


def sizes(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A style's pack counts or volumes as its SKU sizes, each at its price."""
    return tuple((str(n), p) for n, p in pairs)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], skus: tuple[tuple[str, float], ...],
        size_key: str, color: tuple, label: str) -> Row:  # fmt: skip
    """One style under ``path``: its SKUs are ``skus``, and each attribute is a drawing param of
    the same key with its lower-cased value."""
    params = tuple((k, str(v).lower()) for k, _n, v in attrs)
    return Row(code, title, brand, ROOT, path, product_type, skus[0][1], shape, description,
               (color,), attrs, skus, label, colorless=True, params=params,
               size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str) -> Row:
    """A text-match decoy cut from ``base``: its title names a range holding the query's word,
    while its fields keep ``base``'s values (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description)
