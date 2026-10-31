"""Finishing nails (gen#751): a table-driven type (#101, :mod:`...catalog.tabletype`).

**Source.** The steel rows of the table "Finishing Nails" at
https://www.mcmaster.com/finishing-nails (retrieved 2026-10-31). The table holds 25 steel rows at
several gauges per length; the five stated are the heavy end, one gauge per length from 1-1/4" to
3", the nails trim is hung with. Its Length, Shank Dia. and Head Dia. are published under those
names. The page cites no nail standard, so a record claims none. It gives no finish on a row, so
``Plain`` is the uncoated steel nail its rows are.

The price is a declared ladder, not measured (see ``tabletype``): about 3.60 USD for 100 of the
1-1/4" nail.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.industrial.nails import COLUMNS, draw, nail_spec
from synthetic_ecommerce_data.domains.industrial.tabletype import TableType, Variant

#: ``(Length, Shank Dia., Head Dia.)`` in inches, as the chart prints them.
ROWS = (
    (1.25, 0.067, 1 / 8),
    (1.5, 0.072, 1 / 8),
    (2.0, 0.091, 1 / 8),
    (2.5, 0.095, 1 / 8),
    (3.0, 0.113, 3 / 16),
)

TABLE = TableType(
    "nail_finishing",
    category=("Fasteners", "Nails", "Finishing Nails"),
    item="Finishing Nail",
    standards_family="fastener",
    standard="",
    source="supplier's finishing nail",
    columns=COLUMNS,
    rows=ROWS,
    variants=(Variant("Steel", "Plain", 1.0),),
    packs=(100, 500),
    base_price=3.60,
    size_slope=1.1,
    pack_slope=0.8,
    draw=draw,
    extent=(0.25, 3.1),
    share=0.012,
    series="FH",
    unit="in",
    compat=False,
    use_lines=(
        "A small brad head sinks below the surface of trim and can be filled over.",
        "Fixes baseboard, casing and molding where finishing nails should not show.",
    ),
)
SPEC = nail_spec(TABLE, "Finishing Nail")
