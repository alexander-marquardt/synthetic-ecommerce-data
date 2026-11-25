"""Crochet Hook (gen#1118, cut 2): Office & School > Sewing & Knitting > Crochet Hooks.

A breadth type: ``derivable`` True, so the scaled build draws more hooks from these four by the
values their titles show (the handle and the material). A hook is sold by its size in
millimeters, the measured ``hook_mm`` SKU axis (``Option("hook_mm", "hook_size", ...)``, ``MMT``):
3.5, 4 and 5 mm, the hooks a 4 ply to an aran yarn takes. :mod:`size_ladder` draws a larger hook
larger. Each style comes in three of the six main colors, and the four styles between them carry
all six (gen#275). The drawing shows the hook's notch, its thumb rest, and a ribbed soft grip
handle when the title says so (:func:`kit_sewing_tools.crochet_hook`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_sewing_tools,  # noqa: F401 -- registers crochet_hook
)
from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    BLUE,
    GREEN,
    LANTERNBY,
    RED,
    WHITE,
    YELLOW,
    decoy,
)
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    DEPARTMENT,
    HOOKS,
    OWNERS,
    PURLWICK,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a

#: A hook's sizes in millimeters and what each adds to the style's price.
SIZES = (("3.5", 0.0), ("4", 0.25), ("5", 0.5))


def _row(code: str, handle: str, material: str, brand: str, colors: tuple, description: str,
         price: float):  # fmt: skip
    attrs = (a("handle", "Handle", handle), a("material", "Material", material))
    params = (("handle", handle.lower()), ("material", material.lower()))
    sizes = tuple((mm, round(price + extra, 2)) for mm, extra in SIZES)
    return row(code, f"{handle} {material} Crochet Hook", brand, HOOKS, "Crochet Hook", "crochet_hook",
               description, attrs, sizes, params, size_key="hook_mm", colors=colors)  # fmt: skip


ROWS = (
    _row(
        "CRHINA",
        "Inline",
        "Aluminum",
        PURLWICK,
        (RED, GREEN, WHITE),
        "A 15 cm hook with a deep inline throat and a flat thumb rest, so each loop sits where it should.",
        3.5,
    ),
    _row(
        "CRHSGA",
        "Soft Grip",
        "Aluminum",
        PURLWICK,
        (BLUE, YELLOW, BLACK),
        "A hook set in a thick, cushioned handle that eases the hand on long projects, for blankets and amigurumi.",
        6.0,
    ),
    _row(
        "CRHSGP",
        "Soft Grip",
        "Plastic",
        LANTERNBY,
        (RED, YELLOW, GREEN),
        "A light hook in a ribbed, cushioned handle that grips the fingers, for beginners and children's first projects.",
        4.5,
    ),
    _row(
        "CRHINP",
        "Inline",
        "Plastic",
        LANTERNBY,
        (BLUE, WHITE, BLACK),
        "A light, warm 14 cm hook with a smooth shaft and a flat thumb rest, for cotton and acrylic yarns.",
        2.5,
    ),
)

SPEC = TypeSpec(
    key="crochet_hook",
    department=DEPARTMENT,
    product_type="Crochet Hook",
    derivable=True,
    owners=OWNERS,
    options=(Option("hook_mm", "hook_size", "Hook size", "MMT"),),
    rows=ROWS,
    decoys=(
        Decoy(4, "yellow crochet hook", "vocabulary", decoy(ROWS[0], "CRHYTR", "Inline Aluminum Crochet Hook with a Yellow Thumb Rest",
              "A green aluminum hook whose thumb rest is printed with its size.", GREEN)),
        Decoy(6, "black crochet hook", "generic", decoy(ROWS[1], "CRHBCT", "Black Cat Soft Grip Aluminum Crochet Hook",
              "From the Black Cat range: a soft grip hook in a bright blue.", BLUE)),
    ),
)  # fmt: skip
