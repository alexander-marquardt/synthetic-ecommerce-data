"""Kayak (gen#352): sit-on-top and inflatable kayaks, for one or two, in a Sports & Outdoors group.

Sold by length in centimeters; a style states its seats and its load. The styles are templates
only (``derivable`` False). :mod:`kit_sports` draws them, with a seat for each of its seats.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from cycling_helpers import KAYAKS, _count
from sports_helpers import (
    _H,
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
    _a,
    _axis,
    _kg,
    _row,
)
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="kayak",
    department="Sports & Outdoors",
    product_type="Kayak",
    rows=(
        _row("KYKSOT", "Sit-on-Top Kayak", _L, (*KAYAKS, "Sit-on-Top Kayaks"), "Kayak", 449.0, "kayak",
             "A one-person sit-on-top kayak in rotation-molded polyethylene, with a seat back, footwells and carry handles.",
             (YELLOW, ORANGE, BLUE, GREEN),
             (_a("kayak_type", "Kayak type", "Sit-on-Top"), _count("seats", "Seats", 1), _kg("max_load_kg", "Maximum load", 120), _a("material", "Material", "Polyethylene")),
             _axis((270, 449.0), (300, 499.0)), "length_cm", (("style", "sit_on_top"), ("seats", "1"))),
        _row("KYKTND", "Tandem Sit-on-Top Kayak", _W, (*KAYAKS, "Sit-on-Top Kayaks"), "Kayak", 699.0, "kayak",
             "A two-person sit-on-top kayak with two seats, a gear well and room for a child between the paddlers.",
             (RED, WHITE, GREEN, BLACK),
             (_a("kayak_type", "Kayak type", "Sit-on-Top"), _count("seats", "Seats", 2), _kg("max_load_kg", "Maximum load", 220), _a("material", "Material", "Polyethylene")),
             _axis((370, 699.0), (390, 749.0)), "length_cm", (("style", "sit_on_top"), ("seats", "2"))),
        _row("KYKINF", "Inflatable Kayak", _H, (*KAYAKS, "Inflatable Kayaks"), "Kayak", 229.0, "kayak",
             "A one-person inflatable kayak with a rugged hull, a removable seat and a valve that fills in minutes.",
             (BLUE, YELLOW, RED, BLACK),
             (_a("kayak_type", "Kayak type", "Inflatable"), _count("seats", "Seats", 1), _kg("max_load_kg", "Maximum load", 130), _a("material", "Material", "PVC")),
             _axis((290, 229.0), (320, 259.0)), "length_cm", (("style", "inflatable"), ("seats", "1"))),
        _row("KYKINT", "Two-Person Inflatable Kayak", _L, (*KAYAKS, "Inflatable Kayaks"), "Kayak", 349.0, "kayak",
             "A two-person inflatable kayak with two seats, a skeg for tracking and a pump and bag in the box.",
             (GREEN, ORANGE, WHITE, BLUE),
             (_a("kayak_type", "Kayak type", "Inflatable"), _count("seats", "Seats", 2), _kg("max_load_kg", "Maximum load", 220), _a("material", "Material", "PVC")),
             _axis((370, 349.0), (400, 399.0)), "length_cm", (("style", "inflatable"), ("seats", "2"))),
    ),
)  # fmt: skip
