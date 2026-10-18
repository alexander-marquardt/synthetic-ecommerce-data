"""Quick-Disconnect Coupling with Viton O-Ring Seal: a text-match decoy for the industrial seed queries (#462).

A coupling sealed with a Viton O-ring. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "quick_disconnect_couplings",
    label="Quick-Disconnect Coupling with Viton O-Ring Seal",
    breadth=BreadthRow(
        key="quick_disconnect_couplings",
        category=(
            "Hose, Tube, Fittings & Valves",
            "Quick-Disconnect Fittings",
            "Quick-Disconnect Couplings",
        ),
        family="motion",
        shape="cylinder",
        item="Quick-Disconnect Coupling with Viton O-Ring Seal",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("1/4 in", "3/8 in", "1/2 in"),
        attributes={"Material": ("Brass",)},
        price_range=(8.0, 34.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a coupling sealed with a Viton O-ring",
    ),
)
