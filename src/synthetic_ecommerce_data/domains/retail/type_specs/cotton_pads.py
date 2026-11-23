"""Cotton pads (gen#1112, slice 2): Beauty > Cotton > Cotton Pads.

A breadth type (``derivable``): the title shows the pad's shape (round, oval, square) and its
texture (quilted, smooth, exfoliating), and the scaled build draws more packs by swapping them. A
SKU is a bag of 50 to 150 pads (``piece_count``). The drawing is a clear bag with a stack of pads
seen through its front (:func:`kit_beauty_cotton.cotton_pad_pack`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.cotton_rows import (
    ALDERMIST,
    FENMERE,
    LILAC,
    OWNERS,
    ROSE,
    SORREL,
    VEILMOOR,
    counts,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _pads(code, title, brand, shape, texture, sizes, desc, color=None) -> object:  # noqa: ANN001
    attrs = (a("pad_shape", "Pad shape", shape), a("pad_texture", "Texture", texture))
    extra = {"color": color} if color else {}
    return row(
        code,
        title,
        brand,
        "Cotton Pads",
        "cotton_pad_pack",
        desc,
        attrs,
        sizes,
        "piece_count",
        **extra,
    )


ROWS = (
    _pads("CTPRQU", "Round Quilted Cotton Pads", ALDERMIST, "Round", "Quilted",
          counts((80, 1.0), (120, 1.4), (150, 1.75)), "Soft pads of pure cotton that hold toner and lift make-up without coming apart."),
    _pads("CTPOSM", "Oval Smooth Cotton Pads", SORREL, "Oval", "Smooth",
          counts((50, 1.25), (100, 2.0)), "Wide pads with sealed edges that sweep across the eyes in one pass.", ROSE),
    _pads("CTPSQU", "Square Quilted Cotton Pads", VEILMOOR, "Square", "Quilted",
          counts((60, 1.5), (120, 2.5)), "Thick pads with stitched layers that stay whole when soaked."),
    _pads("CTPREX", "Round Exfoliating Cotton Pads", FENMERE, "Round", "Exfoliating",
          counts((80, 1.5), (150, 2.5)), "Two-sided pads, one face raised to buff the skin and one soft to finish.", LILAC),
    _pads("CTPSSM", "Square Smooth Cotton Pads", ALDERMIST, "Square", "Smooth",
          counts((50, 1.1), (100, 1.9), (150, 2.6)), "Flat, lint-free pads for nail polish remover and toner alike."),
    _pads("CTPOQU", "Oval Quilted Cotton Pads", VEILMOOR, "Oval", "Quilted",
          counts((70, 1.6), (140, 2.8)), "Long pads that cover the lid and the lashes, in a resealable bag.", ROSE),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: shape or texture, so only a policy that reads ``pad_shape`` or ``pad_texture`` puts the real
#: bags first.
DECOYS = (
    Decoy(6, "square cotton pads", "generic", decoy(
        ROWS[0], "CTPDY1", "Square Mile Round Quilted Cotton Pads",
        "From the Square Mile range: soft pads that hold toner and lift make-up.")),
    Decoy(6, "smooth cotton pads", "generic", decoy(
        ROWS[3], "CTPDY2", "Smooth Day Round Exfoliating Cotton Pads",
        "From the Smooth Day range: two-sided pads, one face raised to buff the skin.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="cotton_pads",
    department="Beauty",
    product_type="Cotton Pads",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
