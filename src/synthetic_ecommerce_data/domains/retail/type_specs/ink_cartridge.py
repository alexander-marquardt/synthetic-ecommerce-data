"""Ink cartridges (gen#956, slice 3b): Electronics > Printers > Ink Cartridges.

A breadth type: ``derivable`` True, so the scaled build draws more cartridges from these rows by
the values their titles show (a yield, a formula, a feature, or a yield and a formula). The SKU's
color is the ink's, offered in the six main colors (gen#275) as photo and pigment printers sell
red, blue, green and white inks beside black and yellow. ``ink_yield`` draws a standard or a
tall XL cartridge, and ``ink_formula`` draws a drop on the label for dye or a hatched band for
pigment (:func:`kit_printers.ink_cartridge`). Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    DUNVALE,
    ELECTRONICS_OWNERS,
    HALVERN,
    MERVANE,
    NIMBREL,
    PELLIMAR,
    QUORRIN,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.printers_rows import (
    BLACK,
    INK_CARTRIDGES,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _ink(code: str, title: str, brand: str, price: float, description: str, yield_: str,
         formula: str, feature: str) -> object:  # fmt: skip
    attrs = (a("ink_yield", "Ink yield", yield_),
             a("ink_formula", "Ink formula", formula),
             a("ink_feature", "Ink feature", feature))  # fmt: skip
    return row(code, title, brand, INK_CARTRIDGES, "Ink Cartridge", "ink_cartridge", price,
               description, attrs, (("ink_yield", yield_.lower()), ("ink_formula", formula.lower())))  # fmt: skip


ROWS = (
    _ink("INK001", "XL Ink Cartridge", HALVERN, 29.0,
         "Prints about twice as many pages as a regular cartridge before it runs dry.", "XL", "Dye", "Smart Chip"),
    _ink("INK002", "Standard Ink Cartridge", TORVANE, 15.0,
         "A single cartridge for everyday letters, forms and homework.", "Standard", "Dye", "Ink Level Window"),
    _ink("INK003", "Pigment Ink Cartridge", NIMBREL, 22.0,
         "Pigment ink that resists smudges and highlighters on plain paper.", "Standard", "Pigment", "Smart Chip"),
    _ink("INK004", "Dye Ink Cartridge", QUORRIN, 17.0,
         "Bright dye ink for vivid photos and color charts on glossy paper.", "Standard", "Dye", "Ink Level Window"),
    _ink("INK005", "Ink Cartridge with Smart Chip", WEXMOOR, 19.0,
         "A chip tells the printer how much ink is left, so it warns you in time.", "Standard", "Pigment", "Smart Chip"),
    _ink("INK006", "Ink Cartridge with Ink Level Window", DUNVALE, 14.0,
         "A clear strip on the side shows how much ink is left at a glance.", "XL", "Dye", "Ink Level Window"),
    _ink("INK007", "XL Pigment Ink Cartridge", MERVANE, 34.0,
         "High-yield pigment ink for a busy office printer, sealed in a foil bag.", "XL", "Pigment", "Smart Chip"),
    _ink("INK008", "Standard Dye Ink Cartridge", PELLIMAR, 16.0,
         "Everyday dye ink in a recyclable shell, with a pull tab that seals the nozzle.", "Standard", "Dye", "Ink Level Window"),
)  # fmt: skip

SPEC = TypeSpec(
    key="ink_cartridge",
    department=DEPARTMENT,
    product_type="Ink Cartridge",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "blue ink cartridge", "vocabulary", decoy(ROWS[1], "INKBPT", "Standard Ink Cartridge with Blue Pull Tab",
              "A black ink cartridge whose seal comes off with a blue pull tab.", BLACK)),
        Decoy(6, "yellow ink cartridge", "generic", decoy(ROWS[6], "INKYCV", "Yellow Cove XL Pigment Ink Cartridge",
              "From the Yellow Cove range: a high-yield pigment ink cartridge with black ink.", BLACK)),
    ),
)  # fmt: skip
