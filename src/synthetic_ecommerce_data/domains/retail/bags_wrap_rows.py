"""The Cleaning department's bags and wraps (gen#962 slice 2): their paths and attributes.

Trash bags, food storage bags and food wrap sit under ``Cleaning > Bags & Wraps``. Each type is a
spec of its own (``type_specs/trash_bags.py``, ``food_storage_bags.py``, ``food_wrap.py``) drawn by
:mod:`kit_bags_wrap`. The department, the brands, the six main colors, ``packs()``, ``row()`` and
``decoy()`` are slice 1's (:mod:`paper_rows`). A trash bag is sold in the six main colors
(gen#275); a clear food bag and a roll of wrap are sold without a color (``colorless``), as a roll
of white paper is. Every brand here is invented (ruling 2026-10-30, gen#720).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_bags_wrap,  # noqa: F401 -- registers trash_bag, zip_bag, wrap_box
)
from synthetic_ecommerce_data.domains.retail.paper_rows import ROOT
from synthetic_ecommerce_data.domains.retail.type_registry import a

TRASH = (ROOT, "Bags & Wraps", "Trash Bags")
FOOD_BAGS = (ROOT, "Bags & Wraps", "Food Storage Bags")
WRAP = (ROOT, "Bags & Wraps", "Food Wrap")


def lowered(*pairs: tuple[str, str]) -> tuple[tuple[str, str], ...]:
    """A row's drawing params: each attribute's value, lower-cased, as its shape reads it."""
    return tuple((k, v.lower()) for k, v in pairs)


def trash(strength: str, closure: str, use: str) -> tuple[tuple, ...]:
    """A trash bag's attributes: its strength, its closure and the bin it is sized for."""
    return (a("strength", "Strength", strength), a("closure", "Closure", closure),
            a("use", "Use", use))  # fmt: skip


def food_bag(closure: str, kind: str, size: str) -> tuple[tuple, ...]:
    """A food storage bag's attributes: its closure, its kind and its size."""
    return (a("closure", "Closure", closure), a("kind", "Kind", kind),
            a("bag_size", "Bag size", size))  # fmt: skip


def wrap(grade: str, material: str, roll: str) -> tuple[tuple, ...]:
    """A food wrap's attributes: its grade, its material and its roll."""
    return (a("grade", "Grade", grade), a("material", "Material", material),
            a("roll", "Roll", roll))  # fmt: skip
