"""Tennis Racket (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _H, _NEUTRAL, _PRIMARY, _TEAM, _W, _a, _row, _words
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="tennis_racket",
    department="Sports & Outdoors",
    product_type="Tennis Racket",
    options=(Option("grip", "grip_size", "Grip size"),),
    rows=(
        _row("TRKOPN", "Graphite Tennis Racket with Open String Pattern", _H, (*_TEAM, "Tennis Rackets"), "Tennis Racket", 54.0,
             "tennis_racket", "A graphite racket with an open string pattern for spin and power, strung and ready to play.",
             _NEUTRAL, (_a("material", "Material", "Graphite"), _a("head_size", "Head size (sq in)", "100")),
             _words(("L1", 54.0), ("L2", 54.0), ("L3", 54.0)), "grip", (("strings", "open"),)),
        _row("TRKDNS", "Aluminum Tennis Racket with Dense String Pattern", _W, (*_TEAM, "Tennis Rackets"), "Tennis Racket", 28.0,
             "tennis_racket", "A tough aluminum racket with a dense string pattern for control, a good first racket.",
             _PRIMARY, (_a("material", "Material", "Aluminum"), _a("head_size", "Head size (sq in)", "105")),
             _words(("L1", 28.0), ("L2", 28.0)), "grip", (("strings", "dense"),)),
    ),
)  # fmt: skip
