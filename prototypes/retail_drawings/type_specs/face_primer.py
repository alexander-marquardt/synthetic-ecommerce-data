"""Face Primer (gen#214): finish and skin type are attributes, the size in ml is the SKU.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK_ROSE, PACK_SAGE, PACK_SAND, PACK_SKY, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Make-Up", "Face", "Primers"), ptype="Face Primer")

ROWS = (
    _row("PRMMAT", "Matte Pore Blur Face Primer", "Pearlbrook", 14.0, "primer",
        "A silky primer that blurs pores and keeps an oily T-zone shine free all day.",
        (a("finish", "Finish", "Matte"), a("skin_type", "Skin type", "Oily")), (("15", 14.0), ("30", 22.0)), "net_volume_ml", (("form", "tube"),), (PACK_SAND,)),
    _row("PRMDEW", "Dewy Glow Face Primer", "Fenmere", 16.0, "primer",
        "A plumping primer for a fresh, lit-from-within base on thirsty skin.",
        (a("finish", "Finish", "Dewy"), a("skin_type", "Skin type", "Dry")), (("30", 16.0), ("50", 24.0)), "net_volume_ml", (("form", "pump"),), (PACK_ROSE,)),
    _row("PRMRAD", "Radiant Skin Primer", "Aldermist", 15.0, "primer",
        "A light primer with a soft glow that suits every day and every skin.",
        (a("finish", "Finish", "Radiant"), a("skin_type", "Skin type", "Normal")), (("15", 15.0), ("30", 23.0)), "net_volume_ml", (("form", "pump"),), (PACK_SKY,)),
    _row("PRMGRP", "Grip and Hold Face Primer", "Veilmoor", 13.0, "primer",
        "A gripping base that holds make-up in place from desk to dinner.",
        (a("finish", "Finish", "Satin"), a("skin_type", "Skin type", "Combination")), (("15", 13.0), ("30", 20.0)), "net_volume_ml", (("form", "tube"),), (PACK_SAGE,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="face_primer",
    department="Beauty",
    product_type="Face Primer",
    rows=ROWS,
    decoys=(
        Decoy(4, "dewy primer", "vocabulary", decoy("PRD1", "Dewy Gold Cap Face Primer", "A matte primer with a gold cap.", ROWS[0])),
        Decoy(6, "dewy primer", "generic", decoy("PRD2", "Dewy Meadow Pore Primer", "From the Dewy Meadow range: a matte primer.", ROWS[0])),
        Decoy(7, "dewy primer", "generic", decoy("PRD3", "Pore Blur Face Primer", "A matte primer for oily skin.", ROWS[0], brand="Dewy Finch")),
    ),
    owners=(("Aldermist", "third_party"), ("Dewy Finch", "third_party"), ("Fenmere", "third_party"), ("Pearlbrook", "third_party"), ("Veilmoor", "third_party"),),
)  # fmt: skip
