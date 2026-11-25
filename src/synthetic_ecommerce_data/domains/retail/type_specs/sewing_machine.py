"""Sewing Machine (gen#1118, cut 2): Office & School > Sewing & Knitting > Sewing Machines.

A breadth type: ``derivable`` True, so the scaled build draws more machines from these four by
the value their titles show (the machine type). A machine states its built-in stitches, an
attribute and the description's, never the title's, so a derived machine type never reads a
count its template made up. The SKU is a body color, a machine sold singly. The drawing shows the
arm, pillar and bed in the body color, with the type on the pillar: dials, a screen, a steel face
plate, or a small body for a mini (:func:`kit_sewing_tools.sewing_machine`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_sewing_tools,  # noqa: F401 -- registers sewing_machine
)
from synthetic_ecommerce_data.domains.retail.office_rows import (
    CALDERBY,
    GREEN,
    WHITE,
    decoy,
    packs,
)
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    BOBBINMERE,
    DEPARTMENT,
    MACHINE,
    OWNERS,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _row(code: str, machine_type: str, stitches: int, brand: str, description: str, price: float):
    attrs = (a("machine_type", "Machine type", machine_type),
             a("built_in_stitches", "Built-in stitches", str(stitches)))  # fmt: skip
    return row(code, f"{machine_type} Sewing Machine", brand, MACHINE, "Sewing Machine", "sewing_machine",
               description, attrs, packs((1, price)), (("machine_type", machine_type.lower()),))  # fmt: skip


ROWS = (
    _row(
        "SWMMEC",
        "Mechanical",
        23,
        BOBBINMERE,
        "A sturdy machine with 23 built-in stitches chosen by dial, a four-step buttonhole and a free arm, for hems, repairs and dressmaking.",
        179.0,
    ),
    _row(
        "SWMCMP",
        "Computerized",
        200,
        CALDERBY,
        "A machine with 200 built-in stitches on a backlit screen, an automatic needle threader and a speed slider, for quilting and dressmaking.",
        349.0,
    ),
    _row(
        "SWMHDY",
        "Heavy Duty",
        32,
        CALDERBY,
        "A machine on a steel frame with a strong motor and 32 built-in stitches, for denim, canvas, leather and several layers at once.",
        279.0,
    ),
    _row(
        "SWMMIN",
        "Mini",
        12,
        BOBBINMERE,
        "A light, compact machine with 12 built-in stitches and a foot pedal, for first projects, mending and small spaces.",
        69.0,
    ),
)

SPEC = TypeSpec(
    key="sewing_machine",
    department=DEPARTMENT,
    product_type="Sewing Machine",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "yellow sewing machine", "vocabulary", decoy(ROWS[0], "SWMYDL", "Mechanical Sewing Machine with a Yellow Stitch Dial",
              "A white machine whose stitch dial is printed in a bright color, so each stitch is easy to find.", WHITE)),
        Decoy(6, "blue sewing machine", "generic", decoy(ROWS[1], "SWMBRB", "Blue Ribbon Computerized Sewing Machine",
              "From the Blue Ribbon range: a computerized machine in a leaf green body.", GREEN)),
    ),
)  # fmt: skip
