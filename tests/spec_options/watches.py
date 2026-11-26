"""Watches and straps: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

MOVED: dict[str, list[Option]] = {
    "analog_watch": [Option("case_mm", "case_diameter", "Case diameter", "MMT")],
    "digital_watch": [Option("case_mm", "case_diameter", "Case diameter", "MMT")],
    "fitness_band": [Option("case_mm", "case_diameter", "Case diameter", "MMT")],
    "watch_strap": [Option("lug_mm", "lug_width", "Lug width", "MMT")],
}
