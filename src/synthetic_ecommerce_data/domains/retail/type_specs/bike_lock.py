"""Bike Lock (gen#959, slice 3): Sports & Outdoors > Cycling > Bike Locks.

A breadth type: ``derivable`` True, so the scaled build draws more bike locks by the values the titles
show (the grade, the type and the opening). The body is the SKU's color; the type draws a steel shackle, a run of chain links, folded plates or a coiled cable (:func:`kit_outdoor_winter.bike_lock`). Each SKU is a color in a length.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.outdoor_winter_rows import BIKE_LOCKS
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    _a,
    _axis,
    _row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec


def _attrs(lock_grade: str, lock_type: str, lock_opening: str) -> tuple[tuple, ...]:
    return (
        _a("lock_grade", "Lock grade", lock_grade),
        _a("lock_type", "Lock type", lock_type),
        _a("lock_opening", "Lock opening", lock_opening),
    )


SPEC = TypeSpec(
    key="bike_lock",
    department="Sports & Outdoors",
    product_type="Bike Lock",
    derivable=True,
    rows=(
        _row("BLKHSK", "Heavy-Duty Shackle Bike Lock with Key", _W, BIKE_LOCKS, "Bike Lock", 45.0, "bike_lock",
             "Hardened steel U-shaped shackle lock with two keys and a frame bracket, for locking up in town.",
             (BLACK, RED, YELLOW, BLUE), _attrs("Heavy-Duty", "Shackle", "Key"),
             _axis((23, 42.0), (30, 45.0)), "length_cm", (("lock_type", "shackle"),)),
        _row("BLKSCC", "Standard Chain Bike Lock with Combination", _H, BIKE_LOCKS, "Bike Lock", 35.0, "bike_lock",
             "Steel chain lock in a fabric sleeve that guards the frame, closed by a four-digit combination.",
             (BLUE, GREEN, BLACK, WHITE), _attrs("Standard", "Chain", "Combination"),
             _axis((90, 32.0), (110, 35.0), (150, 42.0)), "length_cm", (("lock_type", "chain"),)),
        _row("BLKHFK", "Heavy-Duty Folding Bike Lock with Key", _L, BIKE_LOCKS, "Bike Lock", 69.0, "bike_lock",
             "Folding lock of riveted steel plates that folds into a frame holster, with two keys.",
             (YELLOW, RED, BLACK, GREEN), _attrs("Heavy-Duty", "Folding", "Key"),
             _axis((78, 65.0), (100, 69.0)), "length_cm", (("lock_type", "folding"),)),
        _row("BLKLCC", "Lightweight Cable Bike Lock with Combination", _L, BIKE_LOCKS, "Bike Lock", 15.0, "bike_lock",
             "Coiled steel cable lock with a vinyl coat and a resettable combination, for a quick stop.",
             (WHITE, RED, BLUE, YELLOW), _attrs("Lightweight", "Cable", "Combination"),
             _axis((120, 13.0), (180, 15.0), (240, 18.0)), "length_cm", (("lock_type", "cable"),)),
    ),
)  # fmt: skip
