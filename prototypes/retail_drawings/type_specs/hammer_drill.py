"""Hammer drills (gen#191), cordless at 18 and 40 V and corded at 550 to 1,100 W.

The drawing shows a battery for a cordless one and a cable and plug for a corded one
(:func:`kit_drills.hammer_drill`)."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from type_registry import TypeSpec

ROWS = d.styles(
    (
        (
            "DRLHMR",
            "40 V Cordless Brushless Hammer Drill",
            d.CAL,
            129.0,
            "A brushless hammer drill with a side handle, a depth rod and a rapid charger.",
            d.cordless(40, "Brushless"),
            (("power", "cordless"),),
        ),
        (
            "HMDT18",
            "18 V Cordless Hammer Drill, 2 Speed",
            d.TOR,
            89.0,
            "A cordless hammer drill for brick and concrete, with a side handle and a depth rod.",
            d.cordless(18),
            (("power", "cordless"),),
        ),
        (
            "HMDH71",
            "710 W Corded Hammer Drill",
            d.HAR,
            59.0,
            "A mains hammer drill with a variable speed trigger, a side handle and a depth rod.",
            d.corded(710),
            (("power", "corded"),),
        ),
        (
            "HMDS11",
            "1100 W Corded Hammer Drill with Depth Rod",
            d.STO,
            94.0,
            "A heavy mains hammer drill for masonry, with a side handle and a depth rod.",
            d.corded(1100),
            (("power", "corded"),),
        ),
        (
            "HMDB55",
            "550 W Corded Hammer Drill",
            d.BRI,
            39.0,
            "A light mains hammer drill for brick walls, with a side handle.",
            d.corded(550),
            (("power", "corded"),),
        ),
    ),
    "Hammer Drill",
    "hammer_drill",
    d.DRILLS + ("Hammer Drills",),
)

SPEC = TypeSpec(
    key="hammer_drill",
    department=d.HOME,
    product_type="Hammer Drill",
    rows=ROWS,
    decoys=d.decoys(
        ROWS[2], "hammer drill", ("DCHDCL", "Hammer Drill, Cordless Free", "cordless hammer drill")
    ),
    owners=d.OWNERS,
)
