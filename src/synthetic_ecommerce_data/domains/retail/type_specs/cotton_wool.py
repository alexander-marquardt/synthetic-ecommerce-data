"""Cotton wool (gen#1112, slice 2): Beauty > Cotton > Cotton Wool.

A breadth type (``derivable``): the title shows the form (balls, a pleat or a roll) and the grade
(pure or organic cotton), and the scaled build draws more bags by swapping them. A SKU is a bag of
50 g to 400 g (``net_weight_g``). The drawing is a soft bag with the balls, the folded pleat or
the rolled sheet in its window, and a leaf for organic (:func:`kit_beauty_cotton.cotton_wool_bag`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.cotton_rows import (
    ALDERMIST,
    FENMERE,
    OWNERS,
    ROSE,
    SAGE,
    SORREL,
    VEILMOOR,
    counts,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _wool(code, title, brand, form, grade, sizes, desc, color=None) -> object:  # noqa: ANN001
    attrs = (a("wool_form", "Form", form), a("cotton_grade", "Cotton", grade))
    extra = {"color": color} if color else {}
    return row(
        code,
        title,
        brand,
        "Cotton Wool",
        "cotton_wool_bag",
        desc,
        attrs,
        sizes,
        "net_weight_g",
        **extra,
    )


ROWS = (
    _wool("CTWPBA", "Pure Cotton Wool Balls", ALDERMIST, "Balls", "Pure",
          counts((50, 1.0), (100, 1.75), (200, 3.0)), "Big, fluffy balls that do not shed, for removing make-up and nail polish."),
    _wool("CTWOBA", "Organic Cotton Wool Balls", SORREL, "Balls", "Organic",
          counts((50, 1.75), (100, 3.0)), "Soft balls of unbleached cotton in a paper bag.", SAGE),
    _wool("CTWPPL", "Pure Cotton Wool Pleat", VEILMOOR, "Pleat", "Pure",
          counts((80, 1.5), (150, 2.5)), "A long folded strip to tear off by the length, for first aid and baby care.", ROSE),
    _wool("CTWORO", "Organic Cotton Wool Roll", FENMERE, "Roll", "Organic",
          counts((100, 2.25), (200, 3.75)), "A rolled sheet of unbleached cotton to cut to size, in a paper wrap.", SAGE),
    _wool("CTWPRO", "Pure Cotton Wool Roll", ALDERMIST, "Roll", "Pure",
          counts((100, 1.6), (250, 3.25), (400, 4.75)), "A thick rolled sheet for the bathroom cabinet, in a resealable bag."),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: form or grade, so only a policy that reads ``wool_form`` or ``cotton_grade`` puts the real
#: bags first.
DECOYS = (
    Decoy(6, "organic cotton wool", "generic", decoy(
        ROWS[0], "CTWDY1", "Organic Meadow Pure Cotton Wool Balls",
        "From the Organic Meadow range: big, fluffy balls that do not shed.")),
    Decoy(6, "cotton wool roll", "generic", decoy(
        ROWS[2], "CTWDY2", "Roll Call Pure Cotton Wool Pleat",
        "From the Roll Call range: a long folded strip to tear off by the length.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="cotton_wool",
    department="Beauty",
    product_type="Cotton Wool",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
