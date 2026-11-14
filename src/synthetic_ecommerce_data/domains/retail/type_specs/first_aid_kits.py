"""First-aid kits (gen#968, slice 2): Health > First Aid > First Aid Kits.

A breadth type (``derivable``): the scaled build draws more kits by swapping the kit type the
title shows. A SKU is the kit's piece count. The drawing is a soft pouch or a hard case by the
row's ``case``, with the white cross of the first-aid sign (:func:`kit_health.first_aid_kit`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.health_rows import (
    FIRST_AID,
    GREEN,
    HALVERING,
    OWNERS,
    QUELLMOOR,
    VELLING,
    counts,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_PATH = (*FIRST_AID, "First Aid Kits")


def _kit(code, title, brand, kind, case, sizes, desc) -> object:  # noqa: ANN001
    return row(code, title, brand, _PATH, "First Aid Kits", "first_aid_kit", desc,
               (a("kit_type", "Kit type", kind), a("case", "Case", case)),
               ("case", case.lower()), sizes, color=GREEN)  # fmt: skip


ROWS = (
    _kit("HFATRV", "Travel First Aid Kit", VELLING, "Travel", "Soft Pouch", counts((30, 6.0), (60, 10.0)),
         "A zipped pouch of plasters, dressings, wipes, tape and tweezers, small enough for a day bag."),
    _kit("HFAHOM", "Home First Aid Kit", QUELLMOOR, "Home", "Hard Case", counts((60, 12.0), (100, 18.0)),
         "A hard case with a carry handle, holding plasters, bandages, dressings, gloves and scissors."),
    _kit("HFACAR", "Car First Aid Kit", HALVERING, "Car", "Soft Pouch", counts((40, 9.0), (70, 13.0)),
         "A flat zipped pouch that fits a glovebox, with plasters, bandages, gloves and a foil blanket."),
    _kit("HFASPT", "Sports First Aid Kit", VELLING, "Sports", "Soft Pouch", counts((40, 10.0), (70, 15.0)),
         "A kit-bag pouch with plasters, tape, instant cold packs, wipes and a triangular bandage."),
    _kit("HFAWRK", "Workplace First Aid Kit", QUELLMOOR, "Workplace", "Hard Case", counts((100, 22.0), (200, 35.0)),
         "A wall-mountable hard case with labeled compartments, refills and a contents list."),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: kit type, so only a policy that reads ``kit_type`` puts the real kits first.
DECOYS = (
    Decoy(6, "car first aid kit", "generic", decoy(
        ROWS[0], "HFADY1", "Racing Car Travel First Aid Kit",
        "From the Racing Car range for children: a zipped travel pouch of plasters and wipes.")),
    Decoy(6, "sports first aid kit", "generic", decoy(
        ROWS[1], "HFADY2", "Sports Day Home First Aid Kit",
        "From the Sports Day range: a hard case with plasters, bandages and dressings.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="first_aid_kits",
    department="Health",
    product_type="First Aid Kits",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
