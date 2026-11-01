"""Picture hooks (gen#34): a breadth leaf of two plain packs.

Breadth is not depth: **Home > DIY & Tools > Picture Hooks** holds two packs, and the plain word
``hook`` gains a category. Each hook is colorless, because its metal is what it is, and each pack
is drawn as its count by :mod:`pack_copies`.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_plain_goods,  # noqa: F401 -- registers picture_hook
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, a, cw

_PATH = ("Home", "DIY & Tools", "Picture Hooks")
_BRAND = "Calderby & Lune"
BRASS = cw("Brass", "#c9a24b")
NICKEL = cw("Nickel", "#b9bcc2")

SPEC = TypeSpec(
    key="picture_hook",
    department="Home",
    product_type="Picture Hook",
    rows=(
        Row("PHKBRS", "Brass Picture Hooks, 10 Pack", _BRAND, "Home", _PATH, "Picture Hook", 3.0,
            "picture_hook", "Single pin picture hooks in brass that tap into a plaster wall "
            "with a small hammer, for a light frame or a mirror.",
            (BRASS,), (a("material", "Material", "Brass"), a("fixing", "Fixing", "Single pin"),
                       a("pack_size", "Pack size", "10 pack")),
            colorless=True, params=(("pins", "1"),)),
        Row("PHKNCK", "Double Pin Picture Hooks, 6 Pack", _BRAND, "Home", _PATH, "Picture Hook",
            4.0, "picture_hook", "Nickel plated picture hooks with two hardened pins that share "
            "the weight of a heavy frame on a plaster wall.",
            (NICKEL,), (a("material", "Material", "Nickel Plated Steel"),
                        a("fixing", "Fixing", "Double pin"), a("pack_size", "Pack size", "6 pack")),
            colorless=True, params=(("pins", "2"),)),
    ),
)  # fmt: skip
