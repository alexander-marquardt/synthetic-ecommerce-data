"""SDS hammer drills (gen#191, the issue's comment): corded at 800 to 1,200 W and cordless at 18 V, with
an SDS-plus chuck, an impact energy in joules and three modes."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from type_registry import TypeSpec

ROWS = d.styles(
    (
        (
            "SDSS80",
            "800 W Corded SDS Hammer Drill",
            d.STO,
            79.0,
            "A mains SDS-plus hammer drill for masonry, with a side handle and a depth rod.",
            (*d.corded(800), *d.sds(2.6)),
            (("power", "corded"),),
        ),
        (
            "SDST11",
            "1100 W Corded SDS Hammer Drill, 3 Mode",
            d.TOR,
            119.0,
            "A mains SDS-plus hammer drill that drills, hammers and chisels.",
            (*d.corded(1100), *d.sds(3.5)),
            (("power", "corded"),),
        ),
        (
            "SDSH18",
            "18 V Cordless SDS Hammer Drill",
            d.HAR,
            149.0,
            "A cordless SDS-plus hammer drill with a side handle and a dust cap.",
            (*d.cordless(18), *d.sds(2.0)),
            (("power", "cordless"),),
        ),
        (
            "SDSB12",
            "1200 W Corded SDS Hammer Drill with Case",
            d.BRI,
            139.0,
            "A strong mains SDS-plus hammer drill with a carry case and a spare chisel.",
            (*d.corded(1200), *d.sds(4.2)),
            (("power", "corded"),),
        ),
    ),
    "SDS Hammer Drill",
    "sds_drill",
    d.DRILLS + ("SDS Drills",),
)

SPEC = TypeSpec(
    key="sds_hammer_drill",
    department=d.HOME,
    product_type="SDS Hammer Drill",
    rows=ROWS,
    decoys=d.decoys(
        ROWS[0],
        "sds hammer drill",
        ("DCSDCL", "SDS Hammer Drill, Cordless Free", "cordless sds hammer drill"),
    ),
    owners=d.OWNERS,
)
