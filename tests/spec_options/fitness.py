"""Fitness: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

from ._shared import THICKNESS, WEIGHT

MOVED: dict[str, list[Option]] = {
    "resistance_band": [Option("resistance", "resistance_level", "Resistance level")],
    # The options the shared table still held that no shared source's row carries (#413).
    "yoga_mat": [THICKNESS],
    "dumbbell": [WEIGHT],
    "kettlebell": [WEIGHT],
}
