"""Precision balls: the first breadth type declared in a module of its own (#48).

A breadth type is one :class:`...catalog.breadth.BreadthRow`, the same fields a
row file in ``data/breadth_categories/`` carries; everything else (the leaf, the
sphere drawing, the vocabulary) follows from the row.
"""

from __future__ import annotations

from ...catalog.breadth import BreadthRow
from ...catalog.typespec import TypeSpec

SPEC = TypeSpec(
    "ball_stock_precision",
    breadth=BreadthRow(
        key="ball_stock_precision",
        category=("Raw Materials", "Metals & Alloys", "Precision Balls"),
        family="motion",
        shape="sphere",
        item="Ball",
        descriptor_attr="Material",
        size_attr="Diameter",
        size_values=(
            "1/8 in",
            "3/16 in",
            "1/4 in",
            "5/16 in",
            "3/8 in",
            "1/2 in",
            "5/8 in",
            "3/4 in",
            "1 in",
        ),
        attributes={
            "Material": ("Stainless Steel", "Chrome Steel"),
            "Grade": ("G25", "G100"),
            "Finish": ("Bright",),
        },
        price_range=(3.0, 15.0),
        skus=2,
        featured_sizes=("1/2 in",),
        featured_attrs={"Material": "Stainless Steel"},
        reason=(
            "'ball' + '1/2' + 'stainless' -- the original ball-category gap example (issue body)"
        ),
    ),
)
