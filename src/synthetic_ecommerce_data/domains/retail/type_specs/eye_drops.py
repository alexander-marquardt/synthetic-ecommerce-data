"""Eye drops (gen#968, slice 3): Health > Eye Care > Eye Drops.

A breadth type (``derivable``): the scaled build draws more eye care by swapping the pack the
title shows. A dropper bottle or a wash bottle is one SKU; single-dose vials are sold by the box
of 20 to 60 (``piece_count``). The drawing is a carton with the row's pack in front of it
(:func:`kit_health_care.eye_drop_bottle`). Over the counter only: drops for comfort, rinsing
and contact lenses, never a medicine.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_health_care,  # noqa: F401 -- registers eye_drop_bottle
)
from synthetic_ecommerce_data.domains.retail.health_rows import (
    BLUE,
    GREEN,
    HALVERING,
    OWNERS,
    QUELLMOOR,
    ROOT,
    THRENNICK,
    VELLING,
    counts,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_PATH = (ROOT, "Eye Care", "Eye Drops")


def _eye(code, title, brand, pack, desc, sizes=(), price=0.0, color=BLUE) -> object:  # noqa: ANN001
    return row(code, title, brand, _PATH, "Eye Drops", "eye_drop_bottle", desc,
               (a("eye_care_pack", "Pack", pack),), ("pack", pack.lower()), sizes, price,
               color=color)  # fmt: skip


ROWS = (
    _eye("HEDLUB", "Lubricating Eye Drops", VELLING, "Dropper Bottle",
         "A 10 ml dropper bottle of lubricating drops for eyes that feel dry after a day at a screen.", price=6.0),
    _eye("HEDCLC", "Contact Lens Comfort Drops", QUELLMOOR, "Dropper Bottle",
         "Rewetting drops for soft and hard contact lenses, in a 10 ml dropper bottle.", price=7.0, color=GREEN),
    _eye("HEDVIA", "Single-Dose Lubricating Eye Drops", HALVERING, "Single-Dose Vials",
         "Preservative-free drops in twist-off vials, one vial each time, easy to carry in a pocket.",
         counts((20, 8.0), (30, 11.0), (60, 19.0))),
    _eye("HEDSAL", "Single-Dose Saline Vials", THRENNICK, "Single-Dose Vials",
         "Sterile saline in twist-off vials for rinsing the eyes or a contact lens.",
         counts((20, 5.0), (40, 9.0)), color=GREEN),
    _eye("HEDWSH", "Eye Wash with Eye Bath", VELLING, "Eye Wash",
         "A 300 ml bottle of gentle eye wash with an eye bath cup that clips onto the cap.", price=6.5),
    _eye("HEDWST", "Travel Eye Wash", QUELLMOOR, "Eye Wash",
         "A 100 ml bottle of eye wash and an eye bath cup, sized for a wash bag.", price=4.5, color=GREEN),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's words, the fields say a dropper
#: bottle, so only a policy that reads ``eye_care_pack`` puts the real packs first.
DECOYS = (
    Decoy(6, "eye wash", "generic", decoy(
        ROWS[0], "HEDDY1", "Eye Wash Day Lubricating Eye Drops",
        "From the Eye Wash Day range: lubricating drops in a 10 ml dropper bottle.")),
    Decoy(6, "single-dose eye drops", "generic", decoy(
        ROWS[1], "HEDDY2", "Single-Dose Saturday Contact Lens Comfort Drops",
        "From the Single-Dose Saturday range: rewetting drops in a 10 ml dropper bottle.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="eye_drops",
    department="Health",
    product_type="Eye Drops",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
