"""High Chairs (gen#965, slice 2): Kids > Baby > Feeding > High Chairs.

A breadth type: ``derivable`` True, so the scaled build draws more high chairs from these six by
the values their titles show (the feature and the frame: wooden, folding or pedestal). The SKU is
a color, which the seat pad takes; the frame draws the chair (:func:`kit_baby_gear.high_chair`):
four splayed beech legs, a folding X-frame on wheels, or one pedestal on a round foot.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baby_gear_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    DEPARTMENT,
    GREEN,
    GREY,
    HIGH_CHAIRS,
    HUSHWELL,
    LANTERNBY,
    LITTLE_FERNBY,
    MIREFIELD,
    PINK,
    RED,
    THISTLE,
    WHITE,
    YELLOW,
    decoy,
    gear_row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _chair(feature: str, frame: str) -> tuple[tuple, ...]:
    return (a("feature", "Feature", feature), a("frame", "Frame", frame))


def _drawn(frame: str) -> tuple[tuple[str, str], ...]:
    return (("frame", frame.lower()),)


def _row(code: str, feature: str, frame: str, brand: str, price: float, colors: tuple, rest: str):
    return gear_row(code, f"{feature} {frame} High Chair", brand, HIGH_CHAIRS, "High Chair", "high_chair",
                    f"A {feature.lower()} {frame.lower()} high chair {rest}",
                    _chair(feature, frame), price, _drawn(frame), colors)  # fmt: skip


ROWS = (
    _row("HCHAHW", "Adjustable Height", "Wooden", THISTLE, 149.0, (WHITE, GREY, GREEN),
         "with a removable tray, a five-point harness and a footrest, from six months."),
    _row("HCHCVW", "Convertible", "Wooden", MIREFIELD, 179.0, (WHITE, BLUE, YELLOW),
         "with a removable tray, a five-point harness and a footrest, that becomes a junior chair at the table."),
    _row("HCHSSF", "Space-Saving", "Folding", LITTLE_FERNBY, 69.0, (GREY, RED, BLUE, BLACK),
         "with a removable tray, a five-point harness and a footrest, that stands on its own when put away."),
    _row("HCHRCF", "Reclining", "Folding", HUSHWELL, 99.0, (GREY, PINK, GREEN),
         "with a removable tray, a five-point harness, a footrest and locking wheels."),
    _row("HCHECP", "Easy Clean", "Pedestal", LANTERNBY, 189.0, (WHITE, BLACK, RED),
         "with a removable dishwasher-safe tray, a five-point harness and a footrest, in one wipeable moulded seat."),
    _row("HCHPDP", "Padded", "Pedestal", CALDERBY, 219.0, (WHITE, YELLOW, GREY),
         "with a removable tray, a five-point harness and a footrest, on a seat that swivels."),
)  # fmt: skip

SPEC = TypeSpec(
    key="high_chair",
    department=DEPARTMENT,
    product_type="High Chair",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(2, "baby bottle", "category", decoy(ROWS[4], "HCHBBH", "Easy Clean Pedestal High Chair with Baby Bottle Holder",
              "An easy clean pedestal high chair with a cup and bottle holder in its tray: no baby bottle is included.")),
        Decoy(6, "yellow high chair", "generic", decoy(ROWS[2], "HCHYFN", "Yellow Finch Space-Saving Folding High Chair",
              "From the Yellow Finch range: a grey space-saving folding high chair with a removable tray and a five-point harness.", (GREY,))),
    ),
)  # fmt: skip
