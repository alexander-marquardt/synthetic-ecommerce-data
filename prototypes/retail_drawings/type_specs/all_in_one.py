"""All-in-ones and onesies (gen#213), for women, men and children: fleece, teddy and jersey,
hooded or not. :mod:`kit_baby` draws each as its own shape."""

from __future__ import annotations

from babywear_rows import (
    ADULT,
    BLACK,
    BLUE,
    GREEN,
    GREY,
    HARBOUR,
    KIDS,
    LITTLE_FERNBY,
    NAVY,
    PINK,
    QUILLON,
    RED,
    WHITE,
    WRENFIELD,
    YELLOW,
    a,
    garment,
    priced,
    yes,
)
from type_registry import ApparelPlan, TypeSpec


def _aio(code, title, brand, path, price, desc, colors, fabric, hood, who, sizes,
         age="adult"):  # fmt: skip
    return garment(
        code, title, brand, path, "All-in-One", "all_in_one", price, desc, colors,
        (a("fabric", "Fabric", fabric), a("hood", "Hood", yes(hood)),
         a("audience", "Audience", who), a("season", "Season", "Winter")),
        (("hood", "yes" if hood else "no"), ("fabric", fabric.lower())),
        sizes, dept="Lingerie & Nightwear", audience=age,
    )  # fmt: skip


_W, _M, _K = ("Womens", "Nightwear", "All-in-Ones"), ("Mens", "Nightwear", "All-in-Ones"), (
    "Kids", "Nightwear", "All-in-Ones")  # fmt: skip

SPEC = TypeSpec(
    key="all_in_one",
    department="Lingerie & Nightwear",
    product_type="All-in-One",
    rows=(
        _aio("AIOWFL", "Women's Hooded Fleece All-in-One", HARBOUR, _W, 28.0,
             "A fleece all-in-one with a grown-on hood, a front zip and a kangaroo pocket.",
             (GREY, RED, BLUE, GREEN), "Fleece", True, "Womens", priced(ADULT, 28.0)),
        _aio("AIOMTD", "Men's Teddy Fleece Onesie", WRENFIELD, _M, 32.0,
             "A warm teddy fleece onesie with a front zip and two hand pockets.",
             (BLACK, NAVY, YELLOW), "Teddy", False, "Mens", priced(ADULT, 32.0)),
        _aio("AIOKJS", "Kids Hooded Jersey All-in-One", LITTLE_FERNBY, _K, 14.0,
             "A cotton jersey all-in-one with a hood, for lounging and "
             "sleepovers.",
             (WHITE, PINK, GREEN), "Jersey", True, "Unisex", priced(KIDS, 14.0), "kids"),
        _aio("AIOKTD", "Kids Teddy Fleece Onesie", QUILLON, _K, 18.0,
             "A cuddly teddy fleece onesie with a zip front and elastic cuffs.",
             (YELLOW, BLUE, RED), "Teddy", False, "Unisex", priced(KIDS, 18.0), "kids"),
    ),
    apparel=ApparelPlan(
        compounds=(("jumpsuit", "Jumpsuit All-in-One"), ("onesie", "Onesie All-in-One"),
            ("pyjama", "Pyjama All-in-One"))
    ),
)  # fmt: skip
