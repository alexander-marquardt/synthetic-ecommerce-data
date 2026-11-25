"""Sewing Needles (gen#1118, cut 3): Office & School > Sewing & Knitting > Sewing Needles.

A breadth type: ``derivable`` True, so the scaled build draws more needles from these four by the
value their titles show (the needle kind). Hand sewing needles are sold in a needle book, and the
SKU is the book's color, sold singly or as a 3 pack. Each style comes in three of the six main
colors, and the four styles between them carry all six (gen#275). The count of needles in a book
is an attribute and the description's, never the title's, so a pack's drawing never reads it as
a count of books. The drawing shows the book open on its felt page, its needles drawn by kind
(:func:`kit_sewing_notions.sewing_needles`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_sewing_notions,  # noqa: F401 -- registers sewing_needles
)
from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    decoy,
    packs,
)
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    BOBBINMERE,
    DEPARTMENT,
    OWNERS,
    SEWING_NEEDLES,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _row(code: str, kind: str, needles: int, brand: str, colors: tuple, description: str,
         price: float):  # fmt: skip
    attrs = (
        a("needle_kind", "Needle kind", kind),
        a("needle_count", "Needles in the book", str(needles)),
    )
    return row(code, f"{kind} Hand Sewing Needles", brand, SEWING_NEEDLES, "Sewing Needles", "sewing_needles",
               description, attrs, packs((1, price), (3, round(price * 2.6, 2))),
               (("needle_kind", kind.lower()),), colors=colors)  # fmt: skip


ROWS = (
    _row(
        "SNDSHP",
        "Sharps",
        20,
        BOBBINMERE,
        (RED, GREEN, WHITE),
        "A book of 20 medium-length needles with a round eye and a sharp point, for everyday hand sewing, hems and mending.",
        2.75,
    ),
    _row(
        "SNDEMB",
        "Embroidery",
        16,
        CALDERBY,
        (BLUE, YELLOW, BLACK),
        "A book of 16 needles with a long eye that takes several strands of floss, for crewel work and surface embroidery.",
        3.25,
    ),
    _row(
        "SNDTAP",
        "Tapestry",
        12,
        CALDERBY,
        (RED, YELLOW, BLACK),
        "A book of 12 thick needles with a large eye and a blunt point that slips between the threads, for cross stitch and needlepoint.",
        3.5,
    ),
    _row(
        "SNDQLT",
        "Quilting",
        24,
        BOBBINMERE,
        (BLUE, GREEN, WHITE),
        "A book of 24 short, fine needles with a small round eye, for even hand quilting stitches through several layers.",
        3.0,
    ),
)

SPEC = TypeSpec(
    key="sewing_needles",
    department=DEPARTMENT,
    product_type="Sewing Needles",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "red sewing needles", "vocabulary", decoy(ROWS[0], "SNDRTH", "Sharps Hand Sewing Needles with a Red Threader",
              "A blue needle book of sharps that comes with a wire threader on a bright tab.", BLUE)),
        Decoy(6, "green sewing needles", "generic", decoy(ROWS[1], "SNDGFN", "Green Finch Embroidery Hand Sewing Needles",
              "From the Green Finch range: a book of long-eyed needles in a yellow cover.", YELLOW)),
    ),
)  # fmt: skip
