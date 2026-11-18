"""Plasters (gen#968, slice 2): Health > First Aid > Plasters.

A breadth type (``derivable``): the scaled build draws more boxes by swapping the plaster type
the title shows. A SKU is a box of 20, 40 or 80 (``piece_count``). The drawing is a carton with
one plaster of the row's type in front of it (:func:`kit_health.plaster_box`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.health_rows import (
    BLUE,
    FIRST_AID,
    HALVERING,
    OWNERS,
    QUELLMOOR,
    VELLING,
    counts,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_PATH = (*FIRST_AID, "Plasters")


def _plaster(code, title, brand, kind, sizes, desc, color=BLUE) -> object:  # noqa: ANN001
    return row(code, title, brand, _PATH, "Plasters", "plaster_box", desc,
               (a("plaster_type", "Plaster type", kind),), ("plaster", kind.lower()), sizes,
               color=color)  # fmt: skip


ROWS = (
    _plaster("HPLFAB", "Fabric Plasters", VELLING, "Fabric", counts((20, 2.0), (40, 3.5), (80, 6.0)),
             "Flexible fabric strips in mixed sizes for knees, elbows and fingers, in a flip-top box."),
    _plaster("HPLWTP", "Waterproof Plasters", QUELLMOOR, "Waterproof", counts((20, 2.5), (40, 4.0)),
             "Thin strips that stay on in the shower and the pool, in mixed sizes."),
    _plaster("HPLCLR", "Clear Plasters", HALVERING, "Clear", counts((20, 2.5), (40, 4.5)),
             "See-through strips that are barely there on the skin, in mixed sizes."),
    _plaster("HPLBLS", "Blister Plasters", VELLING, "Blister", counts((6, 4.0), (12, 7.0)),
             "Cushioned gel pads shaped for heels and toes, for walking shoes and new boots."),
    _plaster("HPLSNS", "Sensitive Plasters", QUELLMOOR, "Sensitive", counts((20, 2.5), (40, 4.5)),
             "Soft strips with a gentle adhesive that peels away cleanly, in mixed sizes."),
    _plaster("HPLFBX", "Fabric Fingertip Plasters", HALVERING, "Fabric", counts((20, 2.5), (40, 4.0)),
             "Shaped fabric strips that wrap a fingertip or a knuckle, in a flip-top box."),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: plaster type, so only a policy that reads ``plaster_type`` puts the real boxes first.
DECOYS = (
    Decoy(6, "waterproof plasters", "generic", decoy(
        ROWS[0], "HPLDY1", "Waterproof Walker Fabric Plasters",
        "From the Waterproof Walker range: fabric strips in mixed sizes.")),
    Decoy(6, "blister plasters", "generic", decoy(
        ROWS[2], "HPLDY2", "Blister Brook Clear Plasters",
        "From the Blister Brook range: see-through strips in mixed sizes.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="plasters",
    department="Health",
    product_type="Plasters",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
