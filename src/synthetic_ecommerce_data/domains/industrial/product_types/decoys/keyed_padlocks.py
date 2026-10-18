"""Hardened Steel Shackle Padlock: a text-match decoy for the industrial seed queries (#462).

A padlock with a hardened steel shackle, 50 mm. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "keyed_padlocks",
    label="Hardened Steel Shackle Padlock",
    breadth=BreadthRow(
        key="keyed_padlocks",
        category=("Safety", "Lockout & Security", "Keyed Padlocks"),
        family="hand_tool",
        shape="block",
        item="Hardened Steel Shackle Padlock",
        descriptor_attr=None,
        size_attr="Width",
        size_values=("40 mm", "50 mm", "60 mm"),
        attributes={"Material": ("Laminated Steel",), "Type": ("Keyed Alike",)},
        price_range=(9.0, 36.0),
        skus=2,
        featured_sizes=("50 mm",),
        reason=(
            "decoy for the industrial seed queries (#462): a padlock with a hardened steel "
            "shackle, 50 mm"
        ),
    ),
)
