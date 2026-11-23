"""Cotton buds (gen#1112, slice 2): Beauty > Cotton > Cotton Buds.

A breadth type (``derivable``): the title shows the stem (paper or bamboo) and the tip (standard,
precision, or a safety tip for babies), and the scaled build draws more tubs by swapping them. A
SKU is a tub of 56 to 500 buds (``piece_count``). The drawing is a round tub with a fan of buds
standing out of it (:func:`kit_beauty_cotton.cotton_bud_tub`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.cotton_rows import (
    ALDERMIST,
    FENMERE,
    OWNERS,
    SAGE,
    SORREL,
    VEILMOOR,
    counts,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _buds(code, title, brand, stem, tip, sizes, desc, color=None) -> object:  # noqa: ANN001
    attrs = (a("bud_stem", "Stem", stem), a("bud_tip", "Tip", tip))
    extra = {"color": color} if color else {}
    return row(
        code,
        title,
        brand,
        "Cotton Buds",
        "cotton_bud_tub",
        desc,
        attrs,
        sizes,
        "piece_count",
        **extra,
    )


ROWS = (
    _buds("CTBPST", "Paper Standard Tip Cotton Buds", ALDERMIST, "Paper", "Standard",
          counts((200, 1.0), (300, 1.4), (500, 2.0)), "Firm buds with a generous cotton tip at each end, in a tub with a snap lid."),
    _buds("CTBBST", "Bamboo Standard Tip Cotton Buds", SORREL, "Bamboo", "Standard",
          counts((100, 1.5), (200, 2.5), (300, 3.25)), "Buds on a rigid stem that goes in the compost bin, in a card tub.", SAGE),
    _buds("CTBBPR", "Bamboo Precision Tip Cotton Buds", VEILMOOR, "Bamboo", "Precision",
          counts((100, 2.0), (200, 3.25)), "A tightly wound, tapered tip for tidying eyeliner and lipstick edges.", SAGE),
    _buds("CTBPSA", "Paper Safety Tip Cotton Buds", FENMERE, "Paper", "Safety",
          counts((56, 1.5), (112, 2.6)), "Short buds with a wide, soft bulb for cleaning round a baby's ears and nose."),
    _buds("CTBPPR", "Paper Precision Tip Cotton Buds", ALDERMIST, "Paper", "Precision",
          counts((100, 1.75), (200, 3.0), (300, 4.0)), "Slim buds with one pointed and one rounded tip for make-up touch-ups."),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: stem or tip, so only a policy that reads ``bud_stem`` or ``bud_tip`` puts the real tubs first.
DECOYS = (
    Decoy(6, "bamboo cotton buds", "generic", decoy(
        ROWS[0], "CTBDY1", "Bamboo Grove Paper Standard Tip Cotton Buds",
        "From the Bamboo Grove range: firm buds with a generous cotton tip at each end.")),
    Decoy(6, "precision tip cotton buds", "generic", decoy(
        ROWS[1], "CTBDY2", "Precision Line Bamboo Standard Tip Cotton Buds",
        "From the Precision Line range: buds on a rigid stem, in a card tub.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="cotton_buds",
    department="Beauty",
    product_type="Cotton Buds",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
