"""Who a garment, shoe, lingerie or accessory is for: ``facets.audience`` on every such SKU.

The category tree keeps its Womens / Mens / Kids roots (Baby is a node under Kids), and the
audience is an attribute beside it: ``Womens``, ``Mens``, ``Girls``, ``Boys``, ``Baby`` or
``Unisex``. A search for "mens jeans" then filters ``audience`` and ``product_type`` rather than
leaning on the path, and a kids' style is no longer the one kind of garment with no audience value.

Most styles name their audience in a template attribute (the jeans, the bras). The rest are
filled in here, from the category path, by :func:`export.standard_document`:

- ``Womens/...`` is Womens and ``Mens/...`` is Mens;
- ``Kids/Girls/...`` is Girls and ``Kids/Boys/...`` is Boys; every other ``Kids/...`` node
  (shoes, tops, nightwear, school uniform) is sold to both, so it is Unisex, unless the
  style's own age group is baby, which is Baby;
- ``Kids/Baby/...`` is Baby.

A template's own value always wins, and exactly one value is written (a SKU is never both).
"""

from __future__ import annotations

from typing import Any

WOMENS, MENS, GIRLS, BOYS, BABY, UNISEX = "Womens", "Mens", "Girls", "Boys", "Baby", "Unisex"
#: Every value of ``facets.audience``.
AUDIENCES = (WOMENS, MENS, GIRLS, BOYS, BABY, UNISEX)
#: The roots of the category tree that sell to a person: each SKU under one has an audience.
PEOPLE_ROOTS = ("Womens", "Mens", "Kids")
#: The departments whose SKUs are worn: each has an audience, wherever its path sits.
WORN_DEPARTMENTS = ("Clothing", "Footwear", "Lingerie & Nightwear")


def audience_of_path(path: list[str] | tuple[str, ...], age_group: str = "adult") -> str | None:
    """The audience a category path implies, or None when its root is not a people root."""
    root = path[0]
    if root == "Womens":
        return WOMENS
    if root == "Mens":
        return MENS
    if root == "Kids":
        if age_group == "baby":
            return BABY
        return {"Girls": GIRLS, "Boys": BOYS, "Baby": BABY}.get(
            path[1] if len(path) > 1 else "", UNISEX
        )
    return None


def audience_of(rec: dict[str, Any]) -> str | None:
    """The audience to add to build record ``rec``, or None when it needs none or has one."""
    if any(a["key"] == "audience" for a in rec["attributes"]):
        return None
    return audience_of_path(rec["category_path"], rec.get("audience", "adult"))
