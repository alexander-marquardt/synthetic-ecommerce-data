"""Facial cleansers, deodorants and nail polish's shared pieces (gen#957): their paths and brands.

The Beauty department had no facial cleanser, deodorant or nail polish, so a search for
``foaming face wash``, ``roll-on deodorant`` or ``red nail polish`` found nothing. Three types fix
that, each a spec of its own (``type_specs/facial_cleanser.py``, ``deodorant.py``,
``nail_polish.py``) drawn by :mod:`kit_skin`. A nail polish is sold in the six main colors
(gen#275) and built by :func:`hair_rows.row`; a cleanser and a deodorant are colorless, as a
toothpaste is. The brands are the department's invented brands; every name here is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    hair_rows,  # noqa: F401 -- registers the department's brands' owners
    kit_skin,  # noqa: F401 -- registers facial_cleanser, deodorant, nail_polish
)
from synthetic_ecommerce_data.domains.retail.hair_rows import DEPARTMENT

CLEANSERS = (DEPARTMENT, "Skincare", "Cleansers")
DEODORANTS = (DEPARTMENT, "Body Care", "Deodorants")
NAIL_POLISH = (DEPARTMENT, "Nails", "Nail Polish")

#: The brands the three types' templates are sold under, all owned by a third party.
OWNED = (
    ("Thornlea Skin", "third_party"), ("Aldermist", "third_party"),
    ("Pearlbrook", "third_party"), ("Sorrel & Salt", "third_party"),
    ("Veilmoor", "third_party"), ("Fenmere", "third_party"),
)  # fmt: skip
