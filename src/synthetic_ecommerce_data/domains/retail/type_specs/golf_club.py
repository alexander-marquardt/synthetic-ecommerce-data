"""Golf Club (gen#959, slice 1): Sports & Outdoors > Golf > Golf Clubs.

A breadth type: ``derivable`` True, so the scaled build draws more clubs by the values the titles
show (the shaft material and the club). The head is the SKU's color; the club draws a wood, an
iron, a wedge or a putter (:func:`kit_fishing_golf.golf_club`). Each SKU is a color for a right-
or a left-handed player.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fishing_golf_rows import CLUBS, LARCHMERE, OWNERS
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
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec


def _club(shaft: str, club: str) -> tuple[tuple, ...]:
    return (_a("shaft_material", "Shaft material", shaft), _a("club_type", "Club type", club))


def _hands(price: float) -> tuple[tuple[str, float], ...]:
    return _words(("Right Handed", price), ("Left Handed", price))


SPEC = TypeSpec(
    key="golf_club",
    department="Sports & Outdoors",
    product_type="Golf Club",
    derivable=True,
    owners=OWNERS,
    options=(Option("handedness", "handedness", "Handedness"),),
    rows=(
        _row("GCLDRV", "Graphite Driver Golf Club", LARCHMERE, CLUBS, "Golf Club", 149.0, "golf_club",
             "A 460cc driver with a graphite shaft and a forgiving face, for long, straight tee shots.",
             (BLACK, BLUE, RED, WHITE), _club("Graphite", "Driver"), _hands(149.0), "handedness",
             (("club_type", "driver"),)),
        _row("GCLFWD", "Graphite Fairway Wood Golf Club", _H, CLUBS, "Golf Club", 99.0, "golf_club",
             "A fairway wood with a graphite shaft and a shallow face that lifts the ball cleanly off the grass.",
             (BLACK, GREEN, YELLOW, WHITE), _club("Graphite", "Fairway Wood"), _hands(99.0), "handedness",
             (("club_type", "fairway wood"),)),
        _row("GCLIRN", "Steel 7 Iron Golf Club", _W, CLUBS, "Golf Club", 69.0, "golf_club",
             "A cavity-back 7 iron with a steel shaft, for approach shots that hold the green.",
             (BLACK, BLUE, RED, GREEN), _club("Steel", "7 Iron"), _hands(69.0), "handedness",
             (("club_type", "7 iron"),)),
        _row("GCLWDG", "Steel Sand Wedge Golf Club", _L, CLUBS, "Golf Club", 59.0, "golf_club",
             "A 56 degree sand wedge with a steel shaft and deep grooves, for bunker shots and short pitches.",
             (BLACK, WHITE, YELLOW, BLUE), _club("Steel", "Sand Wedge"), _hands(59.0), "handedness",
             (("club_type", "sand wedge"),)),
        _row("GCLPTR", "Steel Putter Golf Club", LARCHMERE, CLUBS, "Golf Club", 79.0, "golf_club",
             "A blade putter with a steel shaft and a milled face, for a true roll on the green.",
             (BLACK, RED, GREEN, WHITE), _club("Steel", "Putter"), _hands(79.0), "handedness",
             (("club_type", "putter"),)),
    ),
)  # fmt: skip
