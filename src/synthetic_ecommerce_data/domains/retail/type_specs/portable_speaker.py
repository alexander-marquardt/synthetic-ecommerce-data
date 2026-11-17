"""Portable speakers (gen#956): Electronics > Audio > Portable Speakers.

A breadth type: ``derivable`` True, so the scaled build draws more speakers from these rows by
the values their titles show (size, weatherproofing and extra). The body is the SKU's color;
``speaker_size`` draws a mini, compact or large cylinder (:func:`kit_audio.portable_speaker`).
Each SKU is a color, sold single or as a 2 pack for stereo, which ``pack_copies`` draws as two.
Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.audio_rows import BLACK, BLUE, SPEAKERS, decoy, row
from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ARDMOOR,
    BOLTWICK,
    CINDREL,
    DASKEL,
    ELECTRONICS_OWNERS,
    MARRICK,
    QUORRIN,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _sp(code: str, title: str, brand: str, price: float, description: str, size: str,
        water: str, extra: str) -> object:  # fmt: skip
    attrs = (a("speaker_size", "Speaker size", size), a("weatherproofing", "Weatherproofing", water),
             a("speaker_extra", "Extra", extra))  # fmt: skip
    packs = (("Single", price), ("2 pack", round(price * 1.8, 2)))
    return row(code, title, brand, SPEAKERS, "Portable Speaker", "portable_speaker", price,
               description, attrs, (("speaker_size", size.lower()),), packs, "pack_size")  # fmt: skip


ROWS = (
    _sp("AUS001", "Mini Waterproof Bluetooth Speaker", CINDREL, 25.0,
        "A pocket speaker that clips to a bag and keeps playing in the rain.", "Mini", "Waterproof", "Carry Strap"),
    _sp("AUS002", "Large Splash-Proof Bluetooth Speaker", MARRICK, 119.0,
        "Room-filling sound for a garden party, with twenty hours per charge.", "Large", "Splash-Proof", "Light Show"),
    _sp("AUS003", "Waterproof Bluetooth Speaker with Light Show", BOLTWICK, 69.0,
        "Lights that pulse with the beat and a body that floats in the pool.", "Compact", "Waterproof", "Light Show"),
    _sp("AUS004", "Splash-Proof Bluetooth Speaker with Carry Strap", WEXMOOR, 49.0,
        "A strap to hang it from a tent or a branch, and twelve hours of play.", "Compact", "Splash-Proof", "Carry Strap"),
    _sp("AUS005", "Compact Bluetooth Speaker with Built-In Mic", ARDMOOR, 35.0,
        "Take calls hands-free and pair two for stereo sound.", "Compact", "Waterproof", "Built-In Mic"),
    _sp("AUS006", "Mini Bluetooth Speaker with Light Show", TORVANE, 29.0,
        "A small speaker with a ring of light and a punchy little driver.", "Mini", "Splash-Proof", "Light Show"),
    _sp("AUS007", "Large Waterproof Bluetooth Speaker with Built-In Mic", DASKEL, 149.0,
        "Deep bass for the beach, a power bank port and a mic for calls.", "Large", "Waterproof", "Built-In Mic"),
    _sp("AUS008", "Compact Splash-Proof Bluetooth Speaker with Carry Strap", QUORRIN, 55.0,
        "A rugged shell and a strap for the handlebars or the shower rail.", "Compact", "Splash-Proof", "Carry Strap"),
)  # fmt: skip

SPEC = TypeSpec(
    key="portable_speaker",
    department=DEPARTMENT,
    product_type="Portable Speaker",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "yellow speaker", "vocabulary", decoy(ROWS[0], "AUSYST", "Yellow Strap Mini Waterproof Bluetooth Speaker",
              "A black mini speaker with a yellow carry strap that clips to a bag.", BLACK)),
        Decoy(6, "green speaker", "generic", decoy(ROWS[3], "AUSGVL", "Green Valley Splash-Proof Bluetooth Speaker",
              "From the Green Valley range: a splash-proof speaker in blue.", BLUE)),
    ),
)  # fmt: skip
