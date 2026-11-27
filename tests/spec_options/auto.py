"""Car parts and accessories: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

from ._shared import COVERAGE, VEHICLE

MOVED: dict[str, list[Option]] = {
    # a wiper blade's length in inches, the SKU axis (gen#970)
    "wiper_blade": [Option("blade_length_in", "blade_length", "Blade length", "INH")],
    # the car a trunk liner, steering wheel cover or sun shade is cut to (gen#970 slice 3)
    "trunk_liner": [VEHICLE],
    "steering_wheel_cover": [VEHICLE],
    "sun_shade": [VEHICLE],
    # how much of the seat or floor a cover or mat spans (gen#970 slice 3)
    "seat_cover": [COVERAGE],
    "floor_mat": [COVERAGE],
}
