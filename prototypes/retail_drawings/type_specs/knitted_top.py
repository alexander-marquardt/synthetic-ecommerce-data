"""Knitted tops (gen#309, a spec by gen#351): tank tops and slipovers in the knitwear grid.

:mod:`knitwear_rows` generates the whole knitwear depth (jumpers, cardigans and these tops) from
one grid of style by material, so this spec takes its rows from there: the floor products and the
text-match decoys whose type is Knitted Top. The styles are templates only (``derivable`` False),
so the seeded derivation is what it was.
"""

from __future__ import annotations

import knitwear_rows
from type_registry import ApparelPlan, Decoy, TypeSpec

_DECOY_CODES = {d.code: d for d in knitwear_rows.TABLE}
_DECOYS = tuple(
    Decoy(_DECOY_CODES[r.code].klass, _DECOY_CODES[r.code].query, _DECOY_CODES[r.code].policy, r)
    for r in knitwear_rows.TOP_ROWS if r.code in _DECOY_CODES
)  # fmt: skip

SPEC = TypeSpec(
    key="knitted_top",
    department="Clothing",
    product_type="Knitted Top",
    derivable=False,
    apparel=ApparelPlan(
        compounds=(
            ("vest", "Knitted Vest Top"),
            ("cami", "Knitted Cami Top"),
            ("polo", "Knitted Polo Top"),
            ("tunic", "Knitted Tunic Top"),
        )
    ),
    rows=tuple(r for r in knitwear_rows.TOP_ROWS if r.code not in _DECOY_CODES),
    decoys=_DECOYS,
)
