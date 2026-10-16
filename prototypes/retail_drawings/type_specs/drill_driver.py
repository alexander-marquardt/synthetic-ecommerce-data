"""Cordless drill drivers at 12, 18 and 20 V (gen#191): the product type names the tool, not a plain drill.

Five styles from four brands over the 12, 18 and 20 V packs; the drawing's battery follows the voltage
(:func:`kit_drills.drill_driver`). The two oldest rows were typed Cordless Drill in ``breadth_rows``."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from type_registry import TypeSpec

ROWS = d.styles(
    (
        (
            "DRLCRD",
            "18 V Cordless Drill Driver with Two Batteries",
            d.CAL,
            59.0,
            "A two-speed drill driver with a keyless chuck, a work light and a fast charger.",
            d.cordless(18),
            (("pack", "standard"),),
        ),
        (
            "DRLCMP",
            "12 V Compact Cordless Drill Driver",
            d.CAL,
            39.0,
            "A light one-hand drill driver with a keyless chuck, a work light and a one-hour charger.",
            d.cordless(12),
            (("pack", "compact"),),
        ),
        (
            "DRLDD20",
            "20 V Cordless Drill Driver, 2 Speed",
            d.TOR,
            69.0,
            "A two-speed drill driver with a 13 mm keyless chuck and a battery gauge.",
            d.cordless(20),
            (("pack", "large"),),
        ),
        (
            "DRLDD18",
            "18 V Brushless Cordless Drill Driver",
            d.HAR,
            89.0,
            "A brushless drill driver with 21 torque settings and a belt clip.",
            d.cordless(18, "Brushless"),
            (("pack", "standard"),),
        ),
        (
            "DRLDD12",
            "12 V Cordless Drill Driver with Light",
            d.BRI,
            34.0,
            "A small drill driver for shelves and flat packs, with a work light.",
            d.cordless(12),
            (("pack", "compact"),),
        ),
    ),
    "Drill Driver",
    "drill_driver",
    d.DRILLS + ("Cordless Drills",),
)

SPEC = TypeSpec(
    key="drill_driver",
    department=d.HOME,
    product_type="Drill Driver",
    rows=ROWS,
    decoys=d.decoys(
        ROWS[0],
        "drill driver",
        ("DCDDHM", "Drill Driver, Hammer Action Free", "hammer drill driver"),
    ),
    owners=d.OWNERS,
)
