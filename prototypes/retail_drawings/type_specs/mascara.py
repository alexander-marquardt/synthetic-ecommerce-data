"""Mascara (gen#214): effect and waterproof are attributes, the shade is the SKU; a declared color exception.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import BLACK, BLUE, BROWN, GREEN, PURPLE, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Make-Up", "Eyes", "Mascara"), ptype="Mascara")

ROWS = (
    _row("MSCVOL", "Volume Boost Mascara", "Veilmoor", 11.0, "mascara",
        "A thick, buildable formula and a full brush for big lashes.",
        (a("effect", "Effect", "Volume"), a("waterproof", "Waterproof", "No")), (), "size", (("effect", "volume"),), (BLACK, BROWN, BLUE)),
    _row("MSCLNG", "Lash Lengthening Mascara", "Pearlbrook", 10.0, "mascara",
        "A long, slim brush that separates and stretches each lash.",
        (a("effect", "Effect", "Length"), a("waterproof", "Waterproof", "No")), (), "size", (("effect", "length"),), (BLACK, BROWN, GREEN)),
    _row("MSCCRL", "Curl Lift Waterproof Mascara", "Aldermist", 12.0, "mascara",
        "A curved brush that lifts lashes into a curl that lasts all day and survives rain.",
        (a("effect", "Effect", "Curl"), a("waterproof", "Waterproof", "Yes")), (), "size", (("effect", "curl"),), (BLACK, PURPLE, BLUE)),
    _row("MSCWPV", "Waterproof Volume Mascara", "Veilmoor", 13.0, "mascara",
        "A smudge-proof, swim-proof formula with a full brush for dramatic lashes.",
        (a("effect", "Effect", "Volume"), a("waterproof", "Waterproof", "Yes")), (), "size", (("effect", "volume"),), (BLACK, BROWN)),
    _row("MSCWPL", "Waterproof Length Mascara", "Pearlbrook", 12.5, "mascara",
        "A long-wearing, waterproof formula on a slim brush.",
        (a("effect", "Effect", "Length"), a("waterproof", "Waterproof", "Yes")), (), "size", (("effect", "length"),), (BLACK, BLUE, GREEN)),
)  # fmt: skip

SPEC = TypeSpec(
    key="mascara",
    department="Beauty",
    product_type="Mascara",
    rows=ROWS,
    decoys=(
        Decoy(1, "pink mascara", "color", decoy("MSD1", "Pink Cap Volume Mascara", "A black mascara in a tube with a pink cap.", ROWS[0])),
        Decoy(6, "green mascara", "generic", decoy("MSD2", "Green Valley Volume Mascara", "From the Green Valley range: a black volume mascara.", ROWS[0])),
        Decoy(7, "red mascara", "generic", decoy("MSD3", "Volume Mascara", "A black volume mascara.", ROWS[0], brand="Red Kestrel")),
    ),
    owners=(("Aldermist", "third_party"), ("Pearlbrook", "third_party"), ("Red Kestrel", "third_party"), ("Veilmoor", "third_party"),),
)  # fmt: skip
