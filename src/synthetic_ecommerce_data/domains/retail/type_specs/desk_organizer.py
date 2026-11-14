"""Desk Organizers (gen#969, slice 3): Office & school > Desk accessories > Desk organizers.

A breadth type: ``derivable`` True, so the scaled build draws more organizers from these four by
the values their titles show (the number of compartments and the material). The color is the
organizer's; the drawing shows its compartments, stepped from front to back, and its material as
a mesh, a stitched felt edge, a metal sheen or plain plastic (:func:`kit_office.desk_organizer`).
Each SKU is a color sold singly or in a 2 or 4 pack (an office's order).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    CALDERBY,
    DEPARTMENT,
    GREEN,
    LANTERNBY,
    ORGANIZERS,
    THISTLE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a, count


def _org(compartments: str, material: str) -> tuple[tuple, ...]:
    return (count("compartments", "Compartments", int(compartments)),
            a("material", "Material", material))  # fmt: skip


def _params(compartments: str, material: str) -> tuple[tuple[str, str], ...]:
    return (("compartments", compartments), ("material", material.lower()))


ROWS = (
    row("DSKM05", "5 Compartment Mesh Desk Organizer", CALDERBY, ORGANIZERS, "Desk Organizer", "desk_organizer",
        "A desk organizer in a powder-coated steel mesh, with upright sections for pens, notes, scissors and a stapler.",
        _org("5", "Mesh"), packs((1, 12.0), (2, 21.0), (4, 40.0)), _params("5", "Mesh")),
    row("DSKP03", "3 Compartment Plastic Desk Organizer", LANTERNBY, ORGANIZERS, "Desk Organizer", "desk_organizer",
        "A molded plastic desk tidy with a tall pen cup, a tray for clips and a slot for sticky notes.",
        _org("3", "Plastic"), packs((1, 7.0), (2, 12.0), (4, 22.0)), _params("3", "Plastic")),
    row("DSKF04", "4 Compartment Felt Desk Organizer", THISTLE, ORGANIZERS, "Desk Organizer", "desk_organizer",
        "A soft felt desk caddy with stitched edges and open pockets for pens, a phone and a notebook.",
        _org("4", "Felt"), packs((1, 14.0), (2, 25.0), (4, 46.0)), _params("4", "Felt")),
    row("DSKT06", "6 Compartment Metal Desk Organizer", THISTLE, ORGANIZERS, "Desk Organizer", "desk_organizer",
        "A sheet metal desk organizer with stepped file slots at the back and pen cups at the front.",
        _org("6", "Metal"), packs((1, 18.0), (2, 32.0), (4, 60.0)), _params("6", "Metal")),
)

SPEC = TypeSpec(
    key="desk_organizer",
    department=DEPARTMENT,
    product_type="Desk Organizer",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "blue desk organizer", "vocabulary", decoy(ROWS[0], "DSKBLF", "5 Compartment Mesh Desk Organizer with Blue Feet",
              "A black steel mesh desk organizer standing on blue rubber feet.", BLACK)),
        Decoy(6, "yellow desk organizer", "generic", decoy(ROWS[2], "DSKYMD", "Yellow Meadow 4 Compartment Felt Desk Organizer",
              "From the Yellow Meadow range: a green felt desk caddy with stitched edges.", GREEN)),
    ),
)  # fmt: skip
