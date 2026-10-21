"""Yoga Mat (gen#265, moved to a spec by gen#351 and gen#455): Yoga & Fitness: a mat's thickness is the SKU axis.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _H, _L, _YOGA, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="yoga_mat",
    department="Sports & Outdoors",
    product_type="Yoga Mat",
    rows=(
        _row("YGMFLT", "Non-Slip Yoga Mat", _L, (*_YOGA, "Yoga Mats"), "Yoga Mat", 16.0, "yoga_mat",
             "A grippy mat with a textured top that stays put through a long flow, in a choice of "
             "thickness.",
             (BLUE, GREEN, RED, YELLOW),
             (_a("material", "Material", "PVC"), _a("surface", "Surface", "Non-Slip")),
             _axis((4, 16.0), (6, 20.0), (8, 25.0)), "thickness_mm", (("state", "flat"),)),
        _row("YGMTRV", "Foldable Travel Yoga Mat", _H, (*_YOGA, "Yoga Mats"), "Yoga Mat", 22.0,
             "yoga_mat", "A thin mat that rolls up small and fits in a bag, for the studio and "
             "for holidays.",
             (BLACK, WHITE, BLUE, GREEN),
             (_a("material", "Material", "Natural Rubber"), _a("surface", "Surface", "Suede")),
             _axis((1, 22.0), (2, 26.0)), "thickness_mm", (("state", "rolled"),)),
    ),
)  # fmt: skip
