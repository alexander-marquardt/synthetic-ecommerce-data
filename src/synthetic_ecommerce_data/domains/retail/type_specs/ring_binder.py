"""Ring binders (gen#969, slice 2): Office & school > Binders & folders > Ring binders.

A breadth type: ``derivable`` True, so the scaled build draws more binders from these four by the
values their titles show (the page size and the ring type). The color is the cover's; the ring
type draws the mechanism's rings round, D-shaped or slanted
(:func:`kit_office.ring_binder`). Each SKU is a color sold singly or in a pack of 4 or 10.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BINDERS,
    BLUE,
    CALDERBY,
    DEPARTMENT,
    GREEN,
    LANTERNBY,
    THISTLE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _binder(size: str, ring: str, cover: str) -> tuple[tuple, ...]:
    return (a("page_size", "Page size", size), a("ring_type", "Ring type", ring),
            a("cover", "Cover", cover))  # fmt: skip


ROWS = (
    row("RBNA4D", "A4 D-Ring Binder", CALDERBY, BINDERS, "Ring Binder", "ring_binder",
        "A sturdy binder whose mechanism holds up to 300 punched sheets flat, with a label window on the spine.",
        _binder("A4", "D-Ring", "Polypropylene"), packs((1, 4.0), (4, 13.0), (10, 30.0)),
        (("ring_type", "d-ring"),)),
    row("RBNA5R", "A5 Round Ring Binder", LANTERNBY, BINDERS, "Ring Binder", "ring_binder",
        "A compact binder for punched pages that snaps shut, sized for a school bag or a kitchen drawer.",
        _binder("A5", "Round Ring", "Board"), packs((1, 3.0), (4, 10.0), (10, 23.0)),
        (("ring_type", "round ring"),)),
    row("RBNLTS", "Letter Slanted Ring Binder", THISTLE, BINDERS, "Ring Binder", "ring_binder",
        "A binder whose rings lean back so the pages turn easily and lie flat, for reports and course notes.",
        _binder("Letter", "Slanted Ring", "Linen"), packs((1, 5.0), (4, 17.0), (10, 39.0)),
        (("ring_type", "slanted ring"),)),
    row("RBNFSD", "Foolscap D-Ring Binder", LANTERNBY, BINDERS, "Ring Binder", "ring_binder",
        "A tall binder with a label window on the spine and a finger hole to pull it from a shelf.",
        _binder("Foolscap", "D-Ring", "Polypropylene"), packs((1, 4.5), (4, 15.0), (10, 35.0)),
        (("ring_type", "d-ring"),)),
)

SPEC = TypeSpec(
    key="ring_binder",
    department=DEPARTMENT,
    product_type="Ring Binder",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "yellow binder", "vocabulary", decoy(ROWS[0], "RBNYLB", "A4 D-Ring Binder with Yellow Spine Label",
              "A blue binder that holds up to 300 punched sheets, with a yellow label on its spine.", BLUE)),
        Decoy(6, "white binder", "generic", decoy(ROWS[1], "RBNWCL", "White Cliffs A5 Round Ring Binder",
              "From the White Cliffs range: a green binder for punched pages that snaps shut.", GREEN)),
    ),
)  # fmt: skip
