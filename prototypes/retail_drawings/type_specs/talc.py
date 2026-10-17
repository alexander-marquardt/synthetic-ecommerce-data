"""Talc (gen#214): the fragrance is an attribute, the size in g is the SKU.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK, PACK_ROSE, PACK_SKY, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Bath & Body", "Talc"), ptype="Talc")

ROWS = (
    _row("TLCLAV", "Lavender Body Talc", "Sorrel & Salt", 4.0, "talc",
        "A silky talc that leaves skin soft and dry, with a calming lavender scent.",
        (a("fragrance", "Fragrance", "Lavender"),),
        (("100", 4.0), ("200", 6.5)), "net_weight_g", (("lid", "shaker"),), (PACK_SKY,)),
    _row("TLCPWD", "Rose Dusting Powder with Puff", "Fenmere", 9.0, "talc",
        "A luxurious dusting powder in a tin with a soft puff, scented with garden rose.",
        (a("fragrance", "Fragrance", "Rose"),),
        (("100", 9.0), ("150", 12.0)), "net_weight_g", (("lid", "puff"),), (PACK_ROSE,)),
    _row("TLCUNS", "Fragrance Free Body Talc", "Aldermist", 4.5, "talc",
        "A gentle, plain talc for sensitive skin.",
        (a("fragrance", "Fragrance", "Unscented"),),
        (("100", 4.5), ("200", 7.0)), "net_weight_g", (("lid", "shaker"),), (PACK,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="talc",
    department="Beauty",
    product_type="Talc",
    rows=ROWS,
    decoys=(
        Decoy(4, "rose talc", "vocabulary", decoy("TLD1", "Rose Puff Lavender Talc", "A lavender talc with a rose-pink puff.", ROWS[0])),
        Decoy(6, "rose talc", "generic", decoy("TLD2", "Rose Bay Lavender Talc", "From the Rose Bay range: a lavender talc.", ROWS[0])),
        Decoy(7, "rose talc", "generic", decoy("TLD3", "Lavender Body Talc", "A lavender body talc.", ROWS[0], brand="Rose Kestrel")),
    ),
    owners=(("Aldermist", "third_party"), ("Fenmere", "third_party"), ("Rose Kestrel", "third_party"), ("Sorrel & Salt", "third_party"),),
)  # fmt: skip
