"""Bunting (gen#966): Gifts > Party Supplies > Party Decorations.

A breadth type: ``derivable`` True, so the scaled build draws more bunting from these four by the
values their titles show (the material and the flag's shape). The flags are the color, every
second one a tint; the flag draws a pennant, a square or a scalloped flag, and the material
stitching or a felt edge (:func:`kit_party.bunting`). Each SKU is a color in a length in metres.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.party_rows import (
    BUNTING,
    DEPARTMENT,
    FERNBY,
    GREEN,
    HEARTH,
    LANTERNBY,
    RED,
    THISTLE,
    decoy,
    lengths,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a


def _bunting(material: str, flag: str) -> tuple[tuple, ...]:
    return (a("material", "Material", material), a("flag", "Flag shape", flag))


ROWS = (
    row("BUNPAP", "Paper Pennant Bunting", LANTERNBY, BUNTING, "Bunting", "bunting",
        "Paper pennant bunting on a cotton cord, to hang across a wall or a garden fence.",
        _bunting("Paper", "Pennant"), lengths((3, 3.0), (5, 4.5), (10, 8.0)),
        (("flag", "pennant"), ("material", "paper")), "length_m"),
    row("BUNFAB", "Fabric Square Bunting", THISTLE, BUNTING, "Bunting", "bunting",
        "Cotton fabric bunting with stitched square flags, washable and made to use again.",
        _bunting("Fabric", "Square"), lengths((3, 7.0), (5, 10.0), (10, 18.0)),
        (("flag", "square"), ("material", "fabric")), "length_m"),
    row("BUNFLT", "Felt Scalloped Bunting", FERNBY, BUNTING, "Bunting", "bunting",
        "Soft felt bunting with round-bottomed scalloped flags, for a nursery or a baby shower.",
        _bunting("Felt", "Scalloped"), lengths((3, 6.0), (5, 9.0), (10, 16.0)),
        (("flag", "scalloped"), ("material", "felt")), "length_m"),
    row("BUNFBP", "Fabric Pennant Bunting", HEARTH, BUNTING, "Bunting", "bunting",
        "Cotton fabric pennant bunting on a woven tape, for a wedding marquee or a street party.",
        _bunting("Fabric", "Pennant"), lengths((3, 8.0), (5, 12.0), (10, 20.0)),
        (("flag", "pennant"), ("material", "fabric")), "length_m"),
)

SPEC = TypeSpec(
    key="party_bunting",
    department=DEPARTMENT,
    product_type="Bunting",
    derivable=True,
    rows=ROWS,
    options=(Option("length_m", "item_length", "Item length", "MTR"),),
    decoys=(
        Decoy(4, "white bunting", "vocabulary", decoy(ROWS[0], "BUNWCD", "White Cord Pennant Bunting",
              "Paper pennant bunting in red, its flags strung on a white cotton cord.", RED)),
        Decoy(6, "black bunting", "generic", decoy(ROWS[1], "BUNBCT", "Black Cat Fabric Bunting",
              "From the Black Cat party range: fabric square bunting in green.", GREEN)),
    ),
)  # fmt: skip
