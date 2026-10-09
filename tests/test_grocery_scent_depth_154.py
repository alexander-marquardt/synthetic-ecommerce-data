"""Scent depth for the demo words "lemon" and "honey" (gen#154).

"lemon" is a fruit, a flavor and a scent; "honey" a food, a flavor and a scent. The fruit
(``variety``) and the flavor (``flavor``) were stocked in dozens; the scent was a handful of
SKUs under two attribute keys. Each scent leaf now holds dozens of SKUs carrying the one
``scent`` attribute, beside the product type, so a policy can route "lemon" on the pair and
not on a title word. The new families are drawn from their own stream: the core grocery
styles are what they were.
"""

from __future__ import annotations

import sys
from collections import Counter
from functools import cache
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import grocery  # noqa: E402
import grocery_rows  # noqa: E402

#: Product types whose lemon scent a household shopper means (department, scented SKUs wanted).
LEMON_SCENTED = {
    "Dish Soap": "Cleaning & Janitorial",
    "Glass Cleaner": "Cleaning & Janitorial",
    "Floor Cleaner": "Cleaning & Janitorial",
    "Bathroom Cleaner": "Cleaning & Janitorial",
    "Laundry Detergent": "Cleaning & Janitorial",
    "Hand Wash": "Beauty",
    "Shower Gel": "Beauty",
}
HONEY_SCENTED = {"Hand Wash": "Beauty", "Shower Gel": "Beauty"}
#: "Dozens, not one": a product type shows a scent in at least this many SKUs.
VISIBLE = 12


@cache
def records() -> list[dict]:
    return grocery.build(grocery.TARGET)


def scented(scent: str) -> Counter[tuple[str, str]]:
    """``(product type, department)`` -> SKUs whose own ``scent`` attribute is ``scent``."""
    return Counter(
        (r["product_type"], r["department"][0])
        for r in records()
        for s in r["skus"]
        if s.get("scent") == scent
    )


@pytest.mark.parametrize(("product_type", "department"), sorted(LEMON_SCENTED.items()))
def test_lemon_is_a_scent_in_dozens_of_skus_of_each_household_and_body_type(
    product_type: str, department: str
) -> None:
    assert scented("Lemon")[(product_type, department)] >= VISIBLE


@pytest.mark.parametrize(("product_type", "department"), sorted(HONEY_SCENTED.items()))
def test_honey_is_a_scent_in_dozens_of_skus_of_each_body_care_type(
    product_type: str, department: str
) -> None:
    assert scented("Honey")[(product_type, department)] >= VISIBLE


def test_a_scented_sku_is_told_apart_by_attribute_not_by_title() -> None:
    """The scent is an attribute of the style and of every SKU, the style's department is not
    Food & Drink, and the SKU has no flavor: a food-flavor facet never matches a cleaner."""
    scent_families = [f for f in grocery_rows.FAMILIES if f.axis == "scent"]
    codes = {f.code for f in scent_families}
    assert len(codes) >= 9
    seen = 0
    for r in records():
        if r["product_id"].split("-")[1] not in codes:
            continue
        seen += 1
        assert r["department"] != ["Food & Drink"]
        assert {a["value"] for a in r["attributes"] if a["key"] == "scent"} == {
            s["scent"] for s in r["skus"]
        }
        assert all("flavor" not in s and "scent" in s for s in r["skus"])
    assert seen >= 200


def test_the_scent_leaves_are_the_breadth_rows_leaves() -> None:
    """A scent family sits on the leaf the hand-written rows already use, so a shopper
    finds one Dish Soap leaf and not two."""
    import scale

    paths = {
        tuple(r["category_path"])
        for r in scale.templates()
        if not r["product_id"].startswith(scale.GROCERY_PREFIX)
    }
    wanted = {
        tuple(f.path)
        for f in grocery_rows.FAMILIES
        if f.product_type in LEMON_SCENTED and f.axis == "scent"
    }
    assert wanted
    assert {p for p in wanted if p[0] == "Cleaning"} <= paths


def test_the_core_styles_do_not_move_when_scent_depth_is_dropped() -> None:
    """Depth families have their own budget base and stream: removing them leaves every core
    style, id and SKU as built."""
    full = records()
    core_codes = {f.code for f in grocery_rows.FAMILIES if not getattr(f, "depth", False)}
    core = [r for r in full if r["product_id"].split("-")[1] in core_codes]
    keep = tuple(f for f in grocery_rows.FAMILIES if f.code in core_codes)
    saved = grocery.FAMILIES
    grocery.FAMILIES = keep
    try:
        alone = grocery.build(grocery.TARGET)
    finally:
        grocery.FAMILIES = saved
    assert alone == core
    assert len(full) > len(core)
