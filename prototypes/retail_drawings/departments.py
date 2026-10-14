"""The closed department list of gen#125 (prototype).

A department sits where a word's meaning flips (*lemon* is food, a scent or a
cleaner), so a policy can target it. The list is shared by the retail and
industrial domains; this module only names it and refuses anything else.
Audience (womens, kids, baby) is an attribute, never a department.

Since gen#281 this list classifies the BUILD records only (brand pools, department floors,
the worn-department audience rule): no document states it, because its values mixed audience
(Clothing) with product kind (Footwear). The store's department is the top level of the
document's ``category_path`` (twelve roots, ``tests/test_retail_departments_281.py``).
"""

from __future__ import annotations

RETAIL = (
    "Clothing",
    "Footwear",
    "Lingerie & Nightwear",
    "Beauty",
    "Home",
    "Garden",
    "Gifts",
    "Toys",
    "Sports & Outdoors",
)
SHARED = (
    "Workwear & PPE",
    "Cleaning & Janitorial",
    "Furniture & Seating",
    "Food & Drink",
    "Office & Stationery",
)
INDUSTRIAL = (
    "Fasteners",
    "Cutting Tools & Abrasives",
    "Hand & Power Tools",
    "Electrical",
    "Plumbing & Fluid Power",
    "Material Handling & Storage",
    "Metalworking & Machining",
)

#: Every value a record's ``department`` may hold.
DEPARTMENTS = (*RETAIL, *SHARED, *INDUSTRIAL)


def check(values: list[str], what: str = "record") -> list[str]:
    """``values`` unchanged, or ValueError if it is empty or names an unknown department."""
    if not values:
        raise ValueError(f"{what}: no department")
    bad = [v for v in values if v not in DEPARTMENTS]
    if bad:
        raise ValueError(f"{what}: department {bad} is not on the closed list")
    return list(values)
