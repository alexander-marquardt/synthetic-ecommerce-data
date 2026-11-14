"""Document folders (gen#969, slice 2): Office & school > Binders & folders > Document folders.

A breadth type: ``derivable`` True, so the scaled build draws more folders from these four by the
values their titles show (the page size and the closure). The color is the folder's; the closure
draws two elastic bands, a press stud on the flap or a zip with its pull
(:func:`kit_office.document_folder`). Each SKU is a color in a pack of 5, 10 or 25.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLUE,
    CALDERBY,
    DEPARTMENT,
    FOLDERS,
    LANTERNBY,
    RED,
    THISTLE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _folder(size: str, closure: str) -> tuple[tuple, ...]:
    return (a("page_size", "Page size", size), a("closure", "Closure", closure),
            a("material", "Material", "Polypropylene"))  # fmt: skip


ROWS = (
    row("DFLA4E", "A4 Elastic Document Folders", CALDERBY, FOLDERS, "Document Folder", "document_folder",
        "Slim folders with a fold-over flap that keep loose papers flat and dry on the way to school or work.",
        _folder("A4", "Elastic"), packs((5, 4.0), (10, 7.0), (25, 15.0)),
        (("closure", "elastic"),)),
    row("DFLA5P", "A5 Press Stud Document Folders", LANTERNBY, FOLDERS, "Document Folder", "document_folder",
        "Translucent folders that close with one popper on the flap, sized for receipts, tickets and small notes.",
        _folder("A5", "Press Stud"), packs((5, 3.0), (10, 5.5), (25, 12.0)),
        (("closure", "press stud"),)),
    row("DFLFSZ", "Foolscap Zip Document Folders", THISTLE, FOLDERS, "Document Folder", "document_folder",
        "Folders that seal papers, pens and small items in one wipe-clean wallet with a sliding pull.",
        _folder("Foolscap", "Zip"), packs((5, 5.0), (10, 9.0), (25, 20.0)),
        (("closure", "zip"),)),
    row("DFLLTP", "Letter Press Stud Document Folders", CALDERBY, FOLDERS, "Document Folder", "document_folder",
        "Wipe-clean folders with a gusset that takes up to 100 sheets, for forms, bills and homework.",
        _folder("Letter", "Press Stud"), packs((5, 4.5), (10, 8.0), (25, 17.0)),
        (("closure", "press stud"),)),
)

SPEC = TypeSpec(
    key="document_folder",
    department=DEPARTMENT,
    product_type="Document Folder",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "black folder", "vocabulary", decoy(ROWS[0], "DFLBLE", "A4 Document Folders with Black Elastic",
              "Red folders with a fold-over flap, each held shut by a black elastic band.", RED)),
        Decoy(6, "red folder", "generic", decoy(ROWS[1], "DFLRFN", "Red Fern A5 Press Stud Document Folders",
              "From the Red Fern range: blue folders that close with one popper on the flap.", BLUE)),
    ),
)  # fmt: skip
