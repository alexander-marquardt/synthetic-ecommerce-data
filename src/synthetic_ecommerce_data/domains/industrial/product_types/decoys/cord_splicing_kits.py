"""O-Ring Cord Splicing Kit: a text-match decoy for the industrial seed queries (#462).

A kit that cuts and glues O-ring cord to length. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "cord_splicing_kits",
    label="O-Ring Cord Splicing Kit",
    breadth=BreadthRow(
        key="cord_splicing_kits",
        category=("Hose, Tube, Fittings & Valves", "Seals & Gaskets", "Cord Splicing Kits"),
        family="motion",
        shape="tube",
        item="O-Ring Cord Splicing Kit",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("1/8 in", "3/16 in", "1/4 in"),
        attributes={"Material": ("Nitrile",)},
        price_range=(12.0, 45.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a kit that cuts and glues O-ring cord to length",
    ),
)
