"""Cordless combi drills (gen#191): a drill driver with a hammer mode, drawn with a mode ring."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from type_registry import TypeSpec

ROWS = d.styles(
    (
        (
            "DRLCMB",
            "20 V Cordless Combi Drill Driver with Hammer Action",
            d.CAL,
            79.0,
            "A three-mode drill driver with a hammer setting, a keyless chuck and a fast charger.",
            d.cordless(20, modes="Drill, hammer and screwdriver"),
            (("pack", "standard"),),
        ),
        (
            "CMBT18",
            "18 V Cordless Combi Drill with Two Batteries",
            d.TOR,
            99.0,
            "A combi drill with a metal gearbox, two speeds and two batteries.",
            d.cordless(18, modes="Drill, hammer and screwdriver"),
            (("pack", "large"),),
        ),
        (
            "CMBH12",
            "12 V Compact Cordless Combi Drill",
            d.HAR,
            54.0,
            "A light combi drill for brick and wood, with a hammer mode and a work light.",
            d.cordless(12, modes="Drill, hammer and screwdriver"),
            (("pack", "compact"),),
        ),
        (
            "CMBB18",
            "18 V Brushless Cordless Combi Drill",
            d.BRI,
            119.0,
            "A brushless combi drill with 21 torque settings, a side handle and a belt clip.",
            d.cordless(18, "Brushless", modes="Drill, hammer and screwdriver"),
            (("pack", "standard"),),
        ),
    ),
    "Combi Drill",
    "combi_drill",
    d.DRILLS + ("Combi Drills",),
)

SPEC = TypeSpec(
    key="combi_drill",
    department=d.HOME,
    product_type="Combi Drill",
    rows=ROWS,
    decoys=d.decoys(
        ROWS[0], "combi drill", ("DCCBCD", "Combi Drill, Corded Free", "corded combi drill")
    ),
    owners=d.OWNERS,
)
