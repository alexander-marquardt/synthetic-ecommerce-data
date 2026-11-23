"""Tampons (gen#1112, slice 1): Health > Feminine Care > Tampons.

A breadth type (``derivable``): the title shows the absorbency (Light to Super Plus) and the
applicator (plastic, cardboard, or none), and the scaled build draws more packs by swapping them.
A SKU is a box of 16 to 48 tampons (``piece_count``). The drawing is a carton with one tampon in
front as the pack sells it and one drop per absorbency step (:func:`kit_health_feminine.tampon_box`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.feminine_care_rows import PURPLE, TEAL, row
from synthetic_ecommerce_data.domains.retail.health_rows import (
    HALVERING,
    OWNERS,
    QUELLMOOR,
    THRENNICK,
    VELLING,
    counts,
    decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _tampons(code, title, brand, absorbency, applicator, sizes, desc, color=None) -> object:  # noqa: ANN001
    attrs = (a("tampon_absorbency", "Tampon absorbency", absorbency),
             a("tampon_applicator", "Applicator", applicator))
    extra = {"color": color} if color else {}
    return row(code, title, brand, "Tampons", "tampon_box", desc, attrs, sizes, **extra)


ROWS = (
    _tampons("HFTRPL", "Regular Plastic Applicator Tampons", VELLING, "Regular", "Plastic Applicator",
             counts((16, 2.5), (32, 4.5), (48, 6.25)), "Each tampon is wrapped on its own, with a rounded tip and a ringed grip."),
    _tampons("HFTSCA", "Super Cardboard Applicator Tampons", QUELLMOOR, "Super", "Cardboard Applicator",
             counts((16, 2.25), (32, 4.0)), "Tampons in card tubes that go in the bin with the wrapper, in a recyclable box."),
    _tampons("HFTLNA", "Light Non-Applicator Tampons", HALVERING, "Light", "Non-Applicator",
             counts((16, 1.5), (24, 2.0), (32, 2.75)), "Compact tampons inserted with a fingertip, in a pocket-sized box."),
    _tampons("HFTSPP", "Super Plus Plastic Applicator Tampons", THRENNICK, "Super Plus", "Plastic Applicator",
             counts((16, 2.75), (32, 5.0)), "Fuller tampons with a smooth barrel and a grip that pulls out short for a handbag.", PURPLE),
    _tampons("HFTRNA", "Regular Non-Applicator Tampons", QUELLMOOR, "Regular", "Non-Applicator",
             counts((16, 1.6), (32, 2.9), (48, 4.0)), "Small cotton tampons with a stitched cord, each one sealed in film."),
    _tampons("HFTLCA", "Light Cardboard Applicator Tampons", VELLING, "Light", "Cardboard Applicator",
             counts((18, 2.25), (36, 4.0)), "Slim tampons in paper-wrapped card tubes, in a flip-top carton.", TEAL),
    _tampons("HFTSPC", "Super Plus Cardboard Applicator Tampons", HALVERING, "Super Plus", "Cardboard Applicator",
             counts((16, 2.6), (32, 4.75), (48, 6.5)), "Fuller tampons in sturdy card tubes, in a box that opens from the side."),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: absorbency or applicator, so only a policy that reads ``tampon_absorbency`` or
#: ``tampon_applicator`` puts the real boxes first.
DECOYS = (
    Decoy(6, "super tampons", "generic", decoy(
        ROWS[2], "HFTDY1", "Super Soft Light Non-Applicator Tampons",
        "From the Super Soft range: compact tampons inserted with a fingertip.")),
    Decoy(6, "plastic applicator tampons", "generic", decoy(
        ROWS[1], "HFTDY2", "Plastic Free Super Cardboard Applicator Tampons",
        "From the Plastic Free range: tampons in card tubes, in a recyclable box.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="tampons",
    department="Health",
    product_type="Tampons",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
