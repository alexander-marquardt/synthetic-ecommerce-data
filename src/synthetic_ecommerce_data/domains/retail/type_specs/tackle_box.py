"""Tackle Box (gen#959, slice 1): Sports & Outdoors > Fishing > Tackle Boxes.

A breadth type: ``derivable`` True, so the scaled build draws more boxes by the values the titles
show (the tray count and the kind of box). The shell is the SKU's color; the kind draws fanned
cantilever trays, three drawer fronts or a hip roof of clear trays
(:func:`kit_fishing_golf.tackle_box`). Each SKU is a color in a size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fishing_golf_rows import (
    OWNERS,
    PENNYWHISTLE,
    TACKLE_BOXES,
)
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
    _row,
    _words,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec


def _box(trays: str, kind: str) -> tuple[tuple, ...]:
    return (_a("trays", "Trays", trays), _a("tackle_type", "Box type", kind),
            _a("material", "Material", "Polypropylene"))  # fmt: skip


SPEC = TypeSpec(
    key="tackle_box",
    department="Sports & Outdoors",
    product_type="Tackle Box",
    derivable=True,
    owners=OWNERS,
    rows=(
        _row("TCKCNT", "3 Tray Cantilever Tackle Box", _W, TACKLE_BOXES, "Tackle Box", 24.0, "tackle_box",
             "A cantilever tackle box with 3 trays that fan open as the lid lifts, and a deep base for reels and spools.",
             (GREEN, BLACK, BLUE, RED), _box("3", "Cantilever"),
             _words(("Medium", 24.0), ("Large", 29.0)), "size", (("tackle_type", "cantilever"),)),
        _row("TCKDRW", "4 Tray Drawer Tackle Box", PENNYWHISTLE, TACKLE_BOXES, "Tackle Box", 36.0, "tackle_box",
             "A drawer tackle box with 4 trays that slide out from the front, a top lid for tools and a carry handle.",
             (BLACK, GREEN, YELLOW, WHITE), _box("4", "Drawer"),
             _words(("Medium", 36.0), ("Large", 42.0)), "size", (("tackle_type", "drawer"),)),
        _row("TCKHIP", "2 Tray Hip Roof Tackle Box", _L, TACKLE_BOXES, "Tackle Box", 18.0, "tackle_box",
             "A hip roof tackle box with 2 clear trays that open from the middle, so every lure is in sight at once.",
             (BLUE, RED, YELLOW, WHITE), _box("2", "Hip Roof"),
             _words(("Small", 18.0), ("Medium", 21.0)), "size", (("tackle_type", "hip roof"),)),
        _row("TCKCN5", "5 Tray Cantilever Tackle Box", _H, TACKLE_BOXES, "Tackle Box", 39.0, "tackle_box",
             "A large cantilever tackle box with 5 trays on steel arms and a lockable latch, for a full kit of lures and hooks.",
             (RED, BLACK, YELLOW, BLUE), _box("5", "Cantilever"),
             _words(("Large", 39.0), ("Extra Large", 46.0)), "size", (("tackle_type", "cantilever"),)),
    ),
)  # fmt: skip
