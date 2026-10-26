"""Corded (mains) drills at 450 to 710 W (gen#191), drawn with a cable and a plug and no battery."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from type_registry import TypeSpec

ROWS = d.styles(
    (
        (
            "CRDB45",
            "450 W Corded Drill",
            d.BRI,
            24.0,
            "A mains drill with a keyed chuck and a variable speed trigger.",
            d.corded(450, chuck_type="Keyed"),
            (("handle", "pistol"),),
        ),
        (
            "CRDH60",
            "600 W Corded Drill with Keyed Chuck",
            d.HAR,
            32.0,
            "A mains drill with a keyed chuck, a lock-on button and a depth stop.",
            d.corded(600, chuck_type="Keyed"),
            (("handle", "pistol"),),
        ),
        (
            "CRDS71",
            "710 W Corded Drill with Side Handle",
            d.STO,
            44.0,
            "A mains drill with a keyless chuck, a side handle and a depth stop.",
            d.corded(710, chuck_type="Keyless"),
            (("handle", "side"),),
        ),
        (
            "CRDT50",
            "500 W Corded Drill, Variable Speed",
            d.TOR,
            29.0,
            "A mains drill with a keyless chuck and a reversing switch.",
            d.corded(500, chuck_type="Keyless"),
            (("handle", "pistol"),),
        ),
    ),
    "Corded Drill",
    "corded_drill",
    d.DRILLS + ("Corded Drills",),
)

SPEC = TypeSpec(
    key="corded_drill",
    department=d.HOME,
    product_type="Corded Drill",
    rows=ROWS,
    decoys=d.decoys(
        ROWS[0], "corded drill", ("DCCDCL", "Corded Drill, Cordless Free", "cordless drill")
    ),
    owners=d.OWNERS,
)
