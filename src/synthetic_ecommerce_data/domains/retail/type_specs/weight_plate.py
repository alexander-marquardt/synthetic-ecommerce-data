"""Weight Plate (gen#959, slice 2): Sports & Outdoors > Yoga & Fitness > Weights > Weight Plates.

A breadth type: ``derivable`` True, so the scaled build draws more weight plates by the values the titles
show (the material and the bore). The face is the SKU's color; the material draws a raised rim, three grip holes or a steel hub (:func:`kit_fitness_team.weight_plate`). Each SKU is a color in a weight.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import WEIGHT_PLATES
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
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec


def _attrs(material: str, bore: str, grip: str) -> tuple[tuple, ...]:
    return (_a("material", "Material", material), _a("bore", "Bore", bore), _a("plate_grip", "Grip", grip))


SPEC = TypeSpec(
    key="weight_plate",
    department="Sports & Outdoors",
    product_type="Weight Plate",
    derivable=True,
    options=(Option("weight_kg", "weight", "Weight", "KGM"),),
    rows=(
        _row("WPLCIO", "Cast Iron Olympic Tri-Grip Weight Plate", _W, WEIGHT_PLATES, "Weight Plate", 12.0, "weight_plate",
             "Cast iron Olympic weight plate, sold singly, with a machined centre hole that slides onto a bar.",
             (BLACK, BLUE, RED, GREEN), _attrs("Cast Iron", "Olympic", "Tri-Grip"),
             _axis((2.5, 12.0), (5, 19.0), (10, 34.0), (20, 62.0)), "weight_kg", (("material", "cast iron"),)),
        _row("WPLRCS", "Rubber Coated Standard Solid Weight Plate", _H, WEIGHT_PLATES, "Weight Plate", 10.0, "weight_plate",
             "Rubber coated standard weight plate, sold singly, that is quiet on the floor and kind to a bar.",
             (BLACK, RED, BLUE, YELLOW), _attrs("Rubber Coated", "Standard", "Solid"),
             _axis((1.25, 6.0), (2.5, 10.0), (5, 17.0), (10, 30.0)), "weight_kg", (("material", "rubber coated"),)),
        _row("WPLURO", "Urethane Olympic Dual-Grip Weight Plate", _L, WEIGHT_PLATES, "Weight Plate", 24.0, "weight_plate",
             "Urethane Olympic weight plate, sold singly, with a tough face that keeps its look in a busy gym.",
             (WHITE, BLACK, GREEN, RED), _attrs("Urethane", "Olympic", "Dual-Grip"),
             _axis((2.5, 24.0), (5, 39.0), (10, 69.0), (20, 119.0)), "weight_kg", (("material", "urethane"),)),
        _row("WPLRCO", "Rubber Coated Olympic Tri-Grip Weight Plate", _L, WEIGHT_PLATES, "Weight Plate", 14.0, "weight_plate",
             "Rubber coated Olympic weight plate, sold singly, with a face that is easy to grip and load.",
             (BLACK, YELLOW, GREEN, BLUE), _attrs("Rubber Coated", "Olympic", "Tri-Grip"),
             _axis((2.5, 14.0), (5, 23.0), (10, 40.0), (20, 72.0)), "weight_kg", (("material", "rubber coated"),)),
    ),
)  # fmt: skip
