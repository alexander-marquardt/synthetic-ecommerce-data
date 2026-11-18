"""Weight Bench (gen#959, slice 2): Sports & Outdoors > Yoga & Fitness > Weight Benches.

A breadth type: ``derivable`` True, so the scaled build draws more weight benches by the values the titles
show (the bench type and the upholstery). The pad is the SKU's color; the bench type draws a flat pad, a raised back pad or a decline with a leg roller (:func:`kit_fitness_team.weight_bench`). Each SKU is a color in a maximum load.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import WEIGHT_BENCHES
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


def _attrs(bench_type: str, upholstery: str, grade: str) -> tuple[tuple, ...]:
    return (_a("bench_type", "Bench type", bench_type), _a("upholstery", "Upholstery", upholstery), _a("bench_grade", "Bench grade", grade))


SPEC = TypeSpec(
    key="weight_bench",
    department="Sports & Outdoors",
    product_type="Weight Bench",
    derivable=True,
    options=(Option("max_load_kg", "max_load_kg", "Maximum load", "KGM"),),
    rows=(
        _row("WBNFLV", "Home Flat Weight Bench with Vinyl Pad", _W, WEIGHT_BENCHES, "Weight Bench", 79.0, "weight_bench",
             "Flat weight bench with a vinyl pad on a steel frame, for presses, rows and step-ups at home.",
             (BLACK, RED, BLUE, WHITE), _attrs("Flat", "Vinyl", "Home"),
             _axis((150, 79.0), (250, 99.0), (300, 119.0)), "max_load_kg", (("bench_type", "flat"),)),
        _row("WBNADL", "Commercial Adjustable Weight Bench with Leatherette Pad", _H, WEIGHT_BENCHES, "Weight Bench", 149.0, "weight_bench",
             "Adjustable weight bench with a leatherette pad whose back sets at seven angles on a steel frame.",
             (BLACK, GREEN, YELLOW, RED), _attrs("Adjustable", "Leatherette", "Commercial"),
             _axis((200, 149.0), (300, 179.0)), "max_load_kg", (("bench_type", "adjustable"),)),
        _row("WBNDCV", "Commercial Decline Weight Bench with Vinyl Pad", _L, WEIGHT_BENCHES, "Weight Bench", 119.0, "weight_bench",
             "Decline weight bench with a vinyl pad and a padded leg hold, for sit-ups and decline presses.",
             (BLUE, BLACK, WHITE, YELLOW), _attrs("Decline", "Vinyl", "Commercial"),
             _axis((200, 119.0), (250, 129.0), (300, 139.0)), "max_load_kg", (("bench_type", "decline"),)),
        _row("WBNADC", "Home Adjustable Weight Bench with Canvas Pad", _L, WEIGHT_BENCHES, "Weight Bench", 129.0, "weight_bench",
             "Adjustable weight bench with a canvas pad that grips in a sweaty session, on a steel frame.",
             (GREEN, BLACK, WHITE, BLUE), _attrs("Adjustable", "Canvas", "Home"),
             _axis((150, 129.0), (250, 149.0), (300, 169.0)), "max_load_kg", (("bench_type", "adjustable"),)),
    ),
)  # fmt: skip
