"""Printers (gen#956, slice 3b): Electronics > Printers > Printers.

A breadth type: ``derivable`` True, so the scaled build draws more printers from these rows by
the values their titles show (a type, a function, a feature, or a type and a function). The case
is the SKU's color. ``printer_type`` draws a low wide inkjet or a deep laser box with a toner
door, and ``printer_function`` draws a scanner lid or a photo on the sheet
(:func:`kit_printers.printer`). Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ARDMOOR,
    BOLTWICK,
    CINDREL,
    DASKEL,
    ELECTRONICS_OWNERS,
    HALVERN,
    MARRICK,
    PELLIMAR,
    QUORRIN,
)
from synthetic_ecommerce_data.domains.retail.printers_rows import (
    BLACK,
    PRINTERS,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _pr(code: str, title: str, brand: str, price: float, description: str, kind: str,
        function: str, feature: str) -> object:  # fmt: skip
    attrs = (a("printer_type", "Printer type", kind),
             a("printer_function", "Printer function", function),
             a("printer_feature", "Printer feature", feature))  # fmt: skip
    return row(code, title, brand, PRINTERS, "Printer", "printer", price, description, attrs,
               (("printer_type", kind.lower()), ("printer_function", function.lower())))  # fmt: skip


ROWS = (
    _pr("PRN001", "Inkjet Printer", HALVERN, 69.0,
        "Prints school projects, tickets and letters in color, with a 100-sheet paper tray.", "Inkjet", "Multifunction", "Wi-Fi"),
    _pr("PRN002", "Laser Printer", MARRICK, 159.0,
        "Sharp black text at 30 pages a minute, for a home office that prints a lot.", "Laser", "Multifunction", "Auto Duplex"),
    _pr("PRN003", "Photo Printer", CINDREL, 129.0,
        "Borderless photos with rich colors, straight from a phone or a memory card.", "Inkjet", "Photo", "Wi-Fi"),
    _pr("PRN004", "Multifunction Printer", QUORRIN, 99.0,
        "Prints, scans and copies, with a flatbed lid for books and receipts.", "Inkjet", "Multifunction", "Auto Duplex"),
    _pr("PRN005", "Printer with Wi-Fi", DASKEL, 79.0,
        "Print from any phone or laptop in the house, with no cable to the desk.", "Laser", "Multifunction", "Wi-Fi"),
    _pr("PRN006", "Printer with Auto Duplex", PELLIMAR, 119.0,
        "Prints on both sides of the page by itself and saves half the paper.", "Laser", "Multifunction", "Auto Duplex"),
    _pr("PRN007", "Inkjet Photo Printer", ARDMOOR, 149.0,
        "Six inks for skin tones and skies, and a second tray for photo paper.", "Inkjet", "Photo", "Wi-Fi"),
    _pr("PRN008", "Laser Multifunction Printer", BOLTWICK, 229.0,
        "Prints, scans and copies at office speed, with a 50-page document feeder.", "Laser", "Multifunction", "Auto Duplex"),
)  # fmt: skip

SPEC = TypeSpec(
    key="printer",
    department=DEPARTMENT,
    product_type="Printer",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "green printer", "vocabulary", decoy(ROWS[1], "PRNGSL", "Laser Printer with Green Status Light",
              "A black laser printer with a small green light that shows when it is ready.", BLACK)),
        Decoy(6, "red printer", "generic", decoy(ROWS[3], "PRNRFN", "Red Fern Multifunction Printer",
              "From the Red Fern range: a multifunction printer in white.", WHITE)),
    ),
)  # fmt: skip
