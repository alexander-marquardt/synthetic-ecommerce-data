"""Laundry Pods (gen#962 slice 3): Cleaning > Laundry > Laundry Pods.

A breadth type: ``derivable`` True, so the scaled build draws more tubs from these four by the
values their titles show (the formula, the scent and the loads). A tub of pods is sold without a
color (``colorless``), the declared exception to the six main colors of gen#275 that a roll of
white paper takes in slice 1. Each SKU is a pack of 1, 2 or 3 tubs.
:func:`kit_cleaning_care.pod_tub` draws the tub and one pod before it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bags_wrap_rows import lowered
from synthetic_ecommerce_data.domains.retail.cleaning_care_rows import PODS, pod
from synthetic_ecommerce_data.domains.retail.paper_rows import (
    DEPARTMENT,
    FEATHERLEE,
    HOLLINSBY,
    MOSSDOWN,
    OWNERS,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _packs(base: float) -> tuple[tuple[str, float], ...]:
    """Packs of 1, 2 and 3 tubs, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in ((1, 1.0), (2, 1.9), (3, 2.7))))


def _params(formula: str, scent: str, loads: str) -> tuple[tuple[str, str], ...]:
    return lowered(("formula", formula), ("scent", scent), ("loads", loads))


ROWS = (
    row("LPDCSR", "Deep Clean Laundry Pods, Spring Rain, 42 Loads", HOLLINSBY, PODS, "Laundry Pods", "pod_tub",
        "Deep Clean Laundry Pods, a tub of 42 Loads, in Spring Rain. Put the pods in the drum before the clothes.",
        pod("Deep Clean", "Spring Rain", "42 Loads"), _packs(9.0), _params("Deep Clean", "Spring Rain", "42 Loads")),
    row("LPSSUN", "Sensitive Skin Laundry Pods, Unscented, 24 Loads", MOSSDOWN, PODS, "Laundry Pods", "pod_tub",
        "Sensitive Skin Laundry Pods, a tub of 24 Loads, in Unscented. Keep the tub closed and out of reach of children.",
        pod("Sensitive Skin", "Unscented", "24 Loads"), _packs(6.5), _params("Sensitive Skin", "Unscented", "24 Loads")),
    row("LPOBCB", "Oxi Boost Laundry Pods, Clean Breeze, 64 Loads", FEATHERLEE, PODS, "Laundry Pods", "pod_tub",
        "Oxi Boost Laundry Pods, a tub of 64 Loads, in Clean Breeze. The pods dissolve in hot or cold water.",
        pod("Oxi Boost", "Clean Breeze", "64 Loads"), _packs(15.0), _params("Oxi Boost", "Clean Breeze", "64 Loads")),
    row("LPDCCB", "Deep Clean Laundry Pods, Clean Breeze, 24 Loads", MOSSDOWN, PODS, "Laundry Pods", "pod_tub",
        "Deep Clean Laundry Pods, a tub of 24 Loads, in Clean Breeze. The pods dissolve in hot or cold water.",
        pod("Deep Clean", "Clean Breeze", "24 Loads"), _packs(6.0), _params("Deep Clean", "Clean Breeze", "24 Loads")),
)

SPEC = TypeSpec(
    key="laundry_pods",
    department=DEPARTMENT,
    product_type="Laundry Pods",
    derivable=True,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "fabric softener", "vocabulary", decoy(ROWS[0], "LPNOFS", "Softener Free Deep Clean Laundry Pods, Spring Rain, 42 Loads",
              "Deep clean laundry pods with no fabric softener in them.")),
        Decoy(6, "sensitive skin laundry pods", "generic", decoy(ROWS[2], "LPSNBY", "Sensitive Bay Oxi Boost Laundry Pods, Clean Breeze, 64 Loads",
              "From the Sensitive Bay range: Oxi Boost pods, not the gentle formula.")),
    ),
)  # fmt: skip
