"""Christmas tree decorations sit at Home > Christmas > Tree Decorations (gen#772).

A bauble is Christmas season stock, not a gift: ``Gifts > Christmas Gifts`` read wrong, and a
shopper browsing Home found no Christmas area. Only the path moves. The rows keep the department
Gifts because a department picks a derived style's rate and brands (:mod:`scale`): moving it
redraws the brand on 38 of these SKUs and retitles 243 others. :data:`PINNED` holds the 73 SKUs
as main built them before the move.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import breadth_rows, export, scale

KIND = "Christmas Decoration"
PATH = ["Home", "Christmas", "Tree Decorations"]
PINNED = Path(__file__).resolve().parent / "data" / "tree_decorations_772.json"


@pytest.fixture(scope="module")
def ceiling() -> scale.Scaled:
    return ceiling_build()


def _decorations(ceiling: scale.Scaled) -> list[dict]:
    return [r for r in ceiling.records if r["product_type"] == KIND]


def test_every_authored_decoration_sits_under_home_christmas() -> None:
    rows = [d for d in breadth_rows.docs() if d["product_type"] == KIND]
    assert len(rows) == 6
    assert all(d["category_path"] == PATH for d in rows)


def test_a_shopper_reads_the_decorations_at_home_christmas(ceiling: scale.Scaled) -> None:
    docs = [scale.standard_document(r) for r in _decorations(ceiling)]
    assert {"/".join(d["category_path"]) for d in docs} == {"Home/Christmas/Tree decorations"}


def test_the_christmas_gifts_node_is_gone(ceiling: scale.Scaled) -> None:
    assert not [r["title"] for r in ceiling.records if "Christmas Gifts" in r["category_path"]]


def test_the_home_christmas_node_holds_the_decorations_alone(ceiling: scale.Scaled) -> None:
    held = {r["product_type"] for r in ceiling.records if r["category_path"][:2] == PATH[:2]}
    assert held == {KIND}


def test_the_decorations_keep_their_skus_images_brands_and_titles(ceiling: scale.Scaled) -> None:
    built = [
        {
            "sku": sku["sku"],
            "product_id": rec["product_id"],
            "image_id": export.image_id(rec, sku),
            "drawing_id": export.drawing_id(rec, sku),
            "brand": rec["brand"],
            "title": rec["title"],
        }
        for rec in _decorations(ceiling)
        for sku in rec["skus"]
    ]
    pinned = json.loads(PINNED.read_text("utf-8"))
    assert len(pinned) == 73 and len({r["product_id"] for r in pinned}) == 56
    assert sorted(built, key=lambda r: r["sku"]) == pinned


@pytest.mark.parametrize(
    "path",
    [
        ["Garden", "Trees", "Christmas Trees"],
        ["Food & Drink", "Bakery", "Festive Bakes"],
        ["Food & Drink", "Desserts", "Christmas Puddings"],
    ],
)
def test_the_other_christmas_leaves_stay_where_they_are(
    ceiling: scale.Scaled, path: list[str]
) -> None:
    assert any(r["category_path"] == path for r in ceiling.records)
