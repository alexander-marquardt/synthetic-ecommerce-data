"""Masonry nails (gen#751): a table-driven type (#101, :mod:`...catalog.tabletype`).

**Source.** The table of zinc-plated steel nails at https://www.mcmaster.com/masonry-nails
(retrieved 2026-10-31), all six rows, 3/4" to 2-1/2". Its Length, Shank Dia. and Head Dia. are
published under those names. The page's search listing cites no nail standard, so a record claims
none.

The price is a declared ladder, not measured (see ``tabletype``): about 4.50 USD for 25 of the 3/4"
nail.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.industrial.nails import COLUMNS, draw, nail_spec
from synthetic_ecommerce_data.domains.industrial.tabletype import TableType, Variant

#: ``(Length, Shank Dia., Head Dia.)`` in inches, as the chart prints them.
ROWS = (
    (0.75, 0.13, 3 / 8),
    (1.0, 0.16, 7 / 16),
    (1.25, 0.19, 1 / 2),
    (1.5, 0.25, 9 / 16),
    (2.0, 0.25, 9 / 16),
    (2.5, 0.25, 9 / 16),
)

TABLE = TableType(
    "nail_masonry",
    category=("Fasteners", "Nails", "Masonry Nails"),
    item="Masonry Nail",
    standards_family="fastener",
    standard="",
    source="supplier's masonry nail",
    columns=COLUMNS,
    rows=ROWS,
    variants=(Variant("Steel", "Zinc Plated", 1.0),),
    packs=(25, 100),
    base_price=4.50,
    size_slope=1.1,
    pack_slope=0.8,
    draw=draw,
    extent=(0.6, 2.6),
    share=0.012,
    series="MN",
    unit="in",
    compat=False,
    use_lines=(
        "Fixes furring strips and plates to brick, block and mortar joints.",
        "Masonry nails take a heavy hammer; wear eye protection when driving them.",
    ),
)
SPEC = nail_spec(TABLE, "Masonry Nail")
