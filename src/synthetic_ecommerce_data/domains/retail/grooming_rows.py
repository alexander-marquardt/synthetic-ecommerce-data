"""Oral care and shaving's shared pieces (gen#957, slice 2): their paths and brands.

The Beauty department had no toothbrush, toothpaste or razor, so a search for ``toothbrush``,
``whitening toothpaste`` or ``5 blade razor`` found nothing. Three types fix that, each a spec of
its own (``type_specs/toothbrush.py``, ``toothpaste.py``, ``razor.py``) drawn by
:mod:`kit_grooming`. A toothbrush and a razor are sold in the six main colors (gen#275) and
built by :func:`hair_rows.row`; a toothpaste is colorless, as a shampoo is. The brands are the
department's invented brands; every name here is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    hair_rows,  # noqa: F401 -- registers the department's brands' owners
    kit_grooming,  # noqa: F401 -- registers toothbrush, toothpaste, razor
)
from synthetic_ecommerce_data.domains.retail.hair_rows import DEPARTMENT

TOOTHBRUSHES = (DEPARTMENT, "Dental", "Toothbrushes")
TOOTHPASTE = (DEPARTMENT, "Dental", "Toothpaste")
RAZORS = (DEPARTMENT, "Shaving", "Razors")

#: The brands the three types' templates are sold under, all owned by a third party.
OWNED = (
    ("Thornlea Skin", "third_party"), ("Aldermist", "third_party"),
    ("Pearlbrook", "third_party"), ("Sorrel & Salt", "third_party"),
)  # fmt: skip
