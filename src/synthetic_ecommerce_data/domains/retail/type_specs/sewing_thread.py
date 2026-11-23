"""Sewing Thread (gen#1118, cut 1): Office & School > Sewing & Knitting > Sewing Thread.

A breadth type: ``derivable`` True, so the scaled build draws more threads from these four by the
values their titles show (the style and the fiber). A spool's length is measured, in meters with
its canonical millimeters, so the build never changes it: a 100 m spool, a 250 m and a 500 m one
are drawn short to tall, and a 1000 m thread on a cone (:func:`kit_sewing.sewing_thread`). The
SKU is a thread color, a spool sold singly or in a 3 pack. A ``thread`` query also reaches the
industrial catalogue's threaded rods and taps; this is the retail side of that clash.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    CALDERBY,
    RED,
    THISTLE,
    WHITE,
    decoy,
    packs,
)
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    BOBBINMERE,
    DEPARTMENT,
    OWNERS,
    THREAD,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _thread(meters: int, style: str, material: str) -> tuple[tuple, ...]:
    return (("spool_length", "Spool length", str(meters), "MTR", float(meters * 1000)),
            a("style", "Style", style), a("material", "Material", material))  # fmt: skip


def _params(meters: int, style: str, material: str) -> tuple[tuple[str, str], ...]:
    return (("spool_length", str(meters)), ("style", style.lower()), ("material", material.lower()))


def _row(
    code: str, meters: int, style: str, material: str, brand: str, description: str, price: float
):
    title = f"{meters} m {style} {material} Sewing Thread"
    return row(code, title, brand, THREAD, "Sewing Thread", "sewing_thread", description,
               _thread(meters, style, material), packs((1, price), (3, round(price * 2.6, 2))),
               _params(meters, style, material))  # fmt: skip


ROWS = (
    _row(
        "SWT500",
        500,
        "All Purpose",
        "Polyester",
        BOBBINMERE,
        "A strong, smooth 50 wt thread that runs cleanly through any home sewing machine, for seams, hems and repairs.",
        4.5,
    ),
    _row(
        "SWT250",
        250,
        "Quilting",
        "Cotton",
        CALDERBY,
        "A 40 wt long-staple thread with a low lint finish, for piecing and machine quilting.",
        3.5,
    ),
    _row(
        "SWT100",
        100,
        "Topstitch",
        "Polyester",
        THISTLE,
        "A heavy 30 wt thread that stands out on the surface, for topstitching jeans, bags and jackets.",
        2.5,
    ),
    _row(
        "SWTK10",
        1000,
        "Embroidery",
        "Rayon",
        BOBBINMERE,
        "A fine 40 wt thread with a high gloss on a cone, for machine embroidery and decorative stitching.",
        7.0,
    ),
)

SPEC = TypeSpec(
    key="sewing_thread",
    department=DEPARTMENT,
    product_type="Sewing Thread",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "red sewing thread", "vocabulary", decoy(ROWS[0], "SWTRSP", "500 m All Purpose Polyester Sewing Thread on a Red Spool",
              "White thread on a red plastic spool that snaps shut over the loose end.", WHITE)),
        Decoy(6, "yellow sewing thread", "generic", decoy(ROWS[1], "SWTYRS", "Yellow Rose 250 m Quilting Cotton Sewing Thread",
              "From the Yellow Rose quilting range: a long-staple thread in a deep red.", RED)),
    ),
)  # fmt: skip
