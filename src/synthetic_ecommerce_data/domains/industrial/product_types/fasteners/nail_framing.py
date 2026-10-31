"""Framing nails (gen#751): a table-driven type (#101, :mod:`...catalog.tabletype`).

**Source.** The table "Nails (Steel, Flat head, Smooth shank)" at
https://www.mcmaster.com/common-nails (retrieved 2026-10-31). Six of its eight rows are stated,
6d (2") to 20d (4"), the sizes that frame a wall; 3d and 4d are too short for it. Its Length, Shank
Dia. and Head Dia. are published under those names. The page cites no nail standard, so a record
claims none. It gives no finish, so ``Plain`` is the uncoated steel nail its rows are.

The price is a declared ladder, not measured (see ``tabletype``): about 3.20 USD for 50 of the 2"
nail.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.industrial.nails import COLUMNS, draw, nail_spec
from synthetic_ecommerce_data.domains.industrial.tabletype import TableType, Variant

#: ``(Length, Shank Dia., Head Dia.)`` in inches, as the chart prints them.
ROWS = (
    (2.0, 0.113, 17 / 64),
    (2.5, 0.131, 9 / 32),
    (3.0, 0.148, 5 / 16),
    (3.25, 0.148, 5 / 16),
    (3.5, 0.162, 11 / 32),
    (4.0, 0.192, 13 / 32),
)

TABLE = TableType(
    "nail_framing",
    category=("Fasteners", "Nails", "Framing Nails"),
    item="Framing Nail",
    standards_family="fastener",
    standard="",
    source="supplier's common nail",
    columns=COLUMNS,
    rows=ROWS,
    variants=(Variant("Steel", "Plain", 1.0),),
    packs=(50, 250),
    base_price=3.20,
    size_slope=1.1,
    pack_slope=0.8,
    draw=draw,
    extent=(0.45, 4.1),
    share=0.012,
    series="FN",
    unit="in",
    compat=False,
    use_lines=(
        "Framing nails join studs, joists and rafters in structural work.",
        "Driven by hand with a framing hammer.",
    ),
)
SPEC = nail_spec(TABLE, "Framing Nail")
