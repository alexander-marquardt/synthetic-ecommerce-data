"""Fishing Reel (gen#959, slice 1): Sports & Outdoors > Fishing > Fishing Reels.

A breadth type: ``derivable`` True, so the scaled build draws more reels by the values the titles
show (the body material, the bearing count and the kind of reel). The body is the SKU's color;
the kind draws an open spool, a low baitcasting body or a closed spincast cone
(:func:`kit_fishing_golf.fishing_reel`). Each SKU is a color in a reel size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fishing_golf_rows import OWNERS, PENNYWHISTLE, REELS
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
    _L,
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


def _reel(body: str, bearings: str, kind: str) -> tuple[tuple, ...]:
    return (_a("body_material", "Body material", body), _a("ball_bearings", "Ball bearings", bearings),
            _a("reel_type", "Reel type", kind))  # fmt: skip


SPEC = TypeSpec(
    key="fishing_reel",
    department="Sports & Outdoors",
    product_type="Fishing Reel",
    derivable=True,
    owners=OWNERS,
    options=(Option("reel_size", "reel_size", "Reel size"),),
    rows=(
        _row("FRLSPN", "Aluminum 7 Bearing Spinning Fishing Reel", _H, REELS, "Fishing Reel", 34.0, "fishing_reel",
             "An aluminum spinning reel with 7 ball bearings, a folding handle and a front drag, for light lines and lures.",
             (BLACK, BLUE, RED, WHITE), _reel("Aluminum", "7", "Spinning"),
             _words(("1000", 34.0), ("2500", 36.0), ("4000", 39.0)), "reel_size", (("reel_type", "spinning"),)),
        _row("FRLBTC", "Graphite 5 Bearing Baitcasting Fishing Reel", _L, REELS, "Fishing Reel", 46.0, "fishing_reel",
             "A low-profile graphite baitcasting reel with 5 ball bearings, a star drag and a magnetic brake, for accurate casts.",
             (BLACK, GREEN, YELLOW, BLUE), _reel("Graphite", "5", "Baitcasting"),
             _words(("100", 46.0), ("150", 48.0), ("200", 51.0)), "reel_size", (("reel_type", "baitcasting"),)),
        _row("FRLSPC", "Graphite 3 Bearing Spincast Fishing Reel", PENNYWHISTLE, REELS, "Fishing Reel", 19.0, "fishing_reel",
             "A graphite spincast reel with 3 ball bearings and a push-button release under a closed cover, easy for beginners.",
             (RED, BLUE, GREEN, YELLOW), _reel("Graphite", "3", "Spincast"),
             _words(("Small", 19.0), ("Medium", 21.0), ("Large", 23.0)), "reel_size", (("reel_type", "spincast"),)),
    ),
)  # fmt: skip
