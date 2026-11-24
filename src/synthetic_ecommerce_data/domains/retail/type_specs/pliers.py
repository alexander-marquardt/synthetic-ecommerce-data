"""Pliers (gen#1130): Home > DIY & Tools > Pliers, eight plain pairs in the six main colors.

They are the common spelling of the Pliars card game's name
(:mod:`feature_decoys.misspelled_words_944`): the Engine offers "pliers" for "pliars" only when
at least 5 times more titles hold it. Each style names the kind of pliers, and its drawing is that
jaw (:mod:`kit_pliers`); a SKU is a handle color.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    diy_tools as d,
)
from synthetic_ecommerce_data.domains.retail import (
    kit_pliers,  # noqa: F401 -- registers pliers
)
from synthetic_ecommerce_data.domains.retail.outdoor_helpers import u
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec, a

_PT = "Pliers"


def _pair(code, words, brand, price, jaw, size, mm, desc):
    return (
        code,
        f"{words} Pliers",
        brand,
        price,
        desc,
        (a("jaw_type", "Jaw type", words), u("plier_length", "Length", mm, "MMT")),
        (("jaw", jaw), ("size", size)),
    )


ROWS = d.styles(
    (
        _pair("PLRCM1", "Combination", d.TOR, 16.0, "combination", "standard", 180, "Combination pliers that grip, bend and cut, with soft two-tone handles."),
        _pair("PLRLN1", "Long Nose", d.BRI, 14.0, "long_nose", "standard", 170, "Long nose pliers for reaching into tight spaces and shaping fine wire."),
        _pair("PLRSC1", "Side Cutter", d.HAR, 15.0, "side_cutter", "short", 160, "Side cutter pliers that cut wire flush, with a spring that opens the jaw."),
        _pair("PLRWP1", "Water Pump", d.STO, 18.0, "pump", "long", 250, "Water pump pliers with an adjustable jaw for pipes and nuts."),
        _pair("PLRSJ1", "Slip Joint", d.CAL, 13.0, "slip_joint", "standard", 200, "Slip joint pliers with a two-position pivot for wide and narrow work."),
        _pair("PLRLK1", "Locking", d.TOR, 22.0, "locking", "long", 225, "Locking pliers that hold fast on a worn nut until the lever is released."),
        _pair("PLRCM2", "Heavy Duty Combination", d.HAR, 24.0, "combination", "long", 225, "Heavy duty combination pliers with a bolt cutter notch at the hinge."),
        _pair("PLRLN2", "Mini Long Nose", d.BRI, 11.0, "long_nose", "short", 120, "Mini long nose pliers for jewellery and electronics repairs."),
    ),
    _PT,
    "pliers",
    (*d.DIY, "Pliers"),
)  # fmt: skip

SPEC = TypeSpec(
    key="pliers",
    department=d.HOME,
    product_type=_PT,
    rows=ROWS,
    decoys=d.decoys(
        ROWS[0],
        "combination pliers",
        ("PLRDY1", "Combination Pliers with Wire Stripper", "pliers with wire stripper"),
    ),
)
