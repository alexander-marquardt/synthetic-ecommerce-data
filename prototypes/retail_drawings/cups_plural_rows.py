"""Lingerie that names its cups in the plural (gen#508): data only."""

from __future__ import annotations

from class_model import Style

STYLES: tuple[Style, ...] = ()


def docs() -> list[dict]:
    """Every style's catalog document."""
    return [s.doc() for s in STYLES]


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"PLT-{s.code}" for s in STYLES)
