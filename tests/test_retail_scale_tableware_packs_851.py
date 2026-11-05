"""A plate, bowl or glass set is sold in a 2, 4 and 8 pack, as the cup set is (#851).

After slice 2 each brand's cup set sold every color in a 2, 4 and 8 pack, but the plate, bowl and
glass rows of the same kitchen and dining aisle each named their own packs: Single, 4 and 6 for a
dinner plate, 4 and Single for a cereal bowl, 2, 4 and 6 for a wine glass, and none of them 8. The
maintainer asked for each brand's set in those aisles to be one product whose SKUs are pack size
(2, 4, 8) x color, each pack drawn with that many items. A large single piece (a platter, a salad
or serving bowl) is not sold in packs and keeps no pack axis.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import pack_copies, scale_measures, tableware_rows

PACKS = {"2 pack": 2, "4 pack": 4, "8 pack": 8}
#: The plate, bowl and glass templates sold in packs: template id -> product type.
SETS = {r.product_id: r.product_type
        for r in (*tableware_rows.PLATES, *tableware_rows.BOWLS, *tableware_rows.GLASSES)
        if r.size_key == "pack_size" and r.sizes}  # fmt: skip


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def _sets(ceiling) -> list[dict]:
    return [r for r in ceiling.records
            if ceiling.template_of.get(r["product_id"], r["product_id"]) in SETS]  # fmt: skip


def test_every_plate_bowl_and_glass_row_sold_in_packs_is_found():
    """The rows this file guards: a change that drops the pack axis from a row drops it here."""
    assert collections.Counter(SETS.values()) == {"Plate": 5, "Bowl": 3, "Glassware": 6}


def test_a_plate_bowl_or_glass_set_sells_each_color_in_a_2_4_and_8_pack(ceiling):
    """Guard (#851): each row named its own packs (Single, 4, 6; 4, Single; 2, 4). Metric: products
    of such a template, or derived from it, with a color not sold in exactly the three packs."""
    recs = _sets(ceiling)
    assert len(recs) > len(SETS)
    wrong = []
    for r in recs:
        per_color: dict[str, list] = collections.defaultdict(list)
        for s in r["skus"]:
            per_color[s["color"]].append(s.get("pack_size"))
        wrong += [(r["title"], c, p) for c, p in per_color.items()
                  if sorted(p, key=str) != sorted(PACKS)]  # fmt: skip
    assert wrong == [], wrong[:5]


def test_a_plate_bowl_or_glass_pack_draws_as_many_items_as_it_holds(ceiling):
    """Guard (#851, #728): a pack of 8 drawn as six reads as a pack of six. Metric: SKUs whose
    drawing is laid out from another count than their pack size."""
    wrong = [
        (r["title"], s.get("pack_size"), pack_copies.copies(r, s))
        for r in _sets(ceiling)
        for s in r["skus"]
        if pack_copies.copies(r, s) != PACKS.get(s.get("pack_size"))
    ]
    assert wrong == [], wrong[:5]


def test_a_plate_bowl_or_glass_set_has_no_one_sku_product(ceiling):
    """Guard (#851): a set sold in one pack of one color is a one-SKU product beside its brand's
    others. A brand may sell two plates of one template that differ by material or finish
    (stoneware, bone china), which the issue allows. Metric: one-SKU products of such a template,
    and the kinds left in ``single_sku_kinds``."""
    assert [r["title"] for r in _sets(ceiling) if len(r["skus"]) < len(PACKS)] == []
    kinds = scale_measures.single_sku_kinds(ceiling.records)
    assert {"Plate", "Bowl", "Glassware"} & set(kinds) == set()
