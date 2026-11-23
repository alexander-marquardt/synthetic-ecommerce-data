"""Razor cartridges (gen#1112, slice 3): Beauty > Shaving > Razor Cartridges.

A breadth type (``derivable``): the title shows the blade count (3, 4 or 5) and the lubricating
strip (aloe, shea, charcoal, cooling), and the scaled build draws more packs by swapping them. A
SKU is a pack of 4 to 12 cartridges (``piece_count``). The drawing is a blister card of four
heads, each with its blades and strip (:func:`kit_bath_shave.razor_cartridge_pack`). The razors
the cartridges fit are gen#957's ``Razor`` type, in the leaf beside this one.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bath_shave_rows import (
    ALDERMIST,
    NAVY,
    OWNERS,
    PEARLBROOK,
    SHAVING,
    SLATE,
    SORREL,
    TEAL,
    THORNLEA,
    decoy,
    row,
    sizes,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_PT = "Razor Cartridges"


def _pack(code, title, brand, blades, strip, skus, desc, color=NAVY) -> object:  # noqa: ANN001
    attrs = (a("blades", "Blades", blades), a("cartridge_strip", "Cartridge strip", strip))
    return row(code, title, brand, (*SHAVING, _PT), _PT, "razor_cartridge_pack", desc, attrs,
               skus, "piece_count", color, "Cartridges")  # fmt: skip


ROWS = (
    _pack("RZCAL3", "3-Blade Razor Cartridges with Aloe Strip", THORNLEA, "3-Blade", "Aloe",
          sizes((4, 6.0), (8, 11.0), (12, 15.0)), "Spare heads that click onto the handle and rinse clean under a running tap."),
    _pack("RZCSH5", "5-Blade Razor Cartridges with Shea Strip", ALDERMIST, "5-Blade", "Shea",
          sizes((4, 12.0), (8, 22.0), (12, 30.0)), "Refill heads with a pivot that follows the jaw, sold in a recyclable tray.", SLATE),
    _pack("RZCCH4", "4-Blade Razor Cartridges with Charcoal Strip", PEARLBROOK, "4-Blade", "Charcoal",
          sizes((4, 9.0), (8, 16.5), (12, 23.0)), "Replacement heads with a precision edge on the back for the sideburns."),
    _pack("RZCCO5", "5-Blade Razor Cartridges with Cooling Strip", SORREL, "5-Blade", "Cooling",
          sizes((4, 11.0), (8, 20.0), (12, 28.0)), "Spare heads in a tray that keeps the edges covered until they are used.", TEAL),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: strip or blade count, so only a policy that reads ``cartridge_strip`` or ``blades`` puts the
#: real packs first.
DECOYS = (
    Decoy(6, "aloe razor cartridges", "generic", decoy(
        ROWS[2], "RZCDY1", "Aloe Bay 4-Blade Razor Cartridges with Charcoal Strip",
        "From the Aloe Bay range: replacement heads with a precision edge on the back.")),
    Decoy(6, "cooling razor cartridges", "generic", decoy(
        ROWS[0], "RZCDY2", "Cooling Tower 3-Blade Razor Cartridges with Aloe Strip",
        "From the Cooling Tower range: spare heads that click onto the handle.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="razor_cartridges",
    department="Beauty",
    product_type=_PT,
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
