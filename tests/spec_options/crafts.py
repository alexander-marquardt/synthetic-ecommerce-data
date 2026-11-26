"""Crafts and sewing: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

MOVED: dict[str, list[Option]] = {
    # a fabric's cut, a fat quarter to 2 meters (gen#1118), declared by its spec from the start
    "fabric": [Option("fabric_cut", "fabric_cut", "Fabric cut")],
    # a knitting needle's and a crochet hook's size in millimeters (gen#1118, cut 2)
    "knitting_needles": [Option("needle_mm", "needle_size", "Needle size", "MMT")],
    "crochet_hook": [Option("hook_mm", "hook_size", "Hook size", "MMT")],
}
