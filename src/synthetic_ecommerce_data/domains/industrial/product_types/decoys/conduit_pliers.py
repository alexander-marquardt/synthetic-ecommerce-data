"""Lock Nut Pliers: a text-match decoy for the industrial seed queries (#462).

Pliers that seat the lock nut on electrical conduit. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "conduit_pliers",
    label="Lock Nut Pliers",
    use_lines=(
        (
            "Tightens and loosens conduit lock nuts; the jaws hold the lock nut by its lugs so it "
            "seats against the box."
        ),
        "Grips the lugs of a conduit lock nut, so each nut seats tight against the box wall.",
    ),
    breadth=BreadthRow(
        key="conduit_pliers",
        category=("Hand Tools", "Pliers", "Conduit Pliers"),
        family="hand_tool",
        shape="bracket",
        item="Lock Nut Pliers",
        descriptor_attr=None,
        size_attr="Overall Length",
        size_values=("8 in", "10 in"),
        attributes={"Material": ("Alloy Steel",), "Finish": ("Black Oxide",)},
        price_range=(14.0, 48.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): pliers that seat the lock nut on "
            "electrical conduit"
        ),
    ),
)
