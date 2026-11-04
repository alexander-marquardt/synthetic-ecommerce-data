"""A cup set is sold in sets of 2, 4 and 8, and a travel cup or tumbler in three capacities (#851).

After slice 1 each brand sold one cup set, but every SKU of it was "Set of 4" and differed by
color alone, and each brand's travel cup and steel tumbler had no size at all. The maintainer asked
for each brand's set to be one product whose SKUs are pack size (2, 4, 8) x color, each pack
drawn with that many cups, and for a single item where a pack is not natural (a travel cup, a
tumbler) to be one product whose SKUs are capacity x color.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import export, pack_copies, size_axes, size_ladder

PACKS = {"Set of 2": 2, "Set of 4": 4, "Set of 8": 8}
#: The templates sold by capacity, and the capacities (ml) each color comes in.
SIZED = {"PLT-DRKTRV": "Travel Cup", "PLT-DRKTMB": "Tumbler"}
CAPACITIES = [350, 470, 590]


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def _of(ceiling, template: str) -> list[dict]:
    return [r for r in ceiling.records
            if ceiling.template_of.get(r["product_id"], r["product_id"]) == template]  # fmt: skip


def _per_color(rec: dict, key: str) -> dict[str, list]:
    out: dict[str, list] = collections.defaultdict(list)
    for s in rec["skus"]:
        out[s["color"]].append(s.get(key))
    return out


def test_a_cup_set_sells_each_color_in_sets_of_2_4_and_8(ceiling):
    """Guard (#851): every cup set SKU was "Set of 4". Metric: cup sets with a color not sold in
    exactly the three set sizes, or a title that names one count for all of them."""
    sets = [r for r in ceiling.records if r["product_type"] == "Cup Set"]
    assert len(sets) > 1
    wrong = [
        (r["title"], color, packs)
        for r in sets
        for color, packs in _per_color(r, "pack_size").items()
        if sorted(packs, key=str) != sorted(PACKS)
    ]
    assert wrong == [], wrong[:5]
    assert [r["title"] for r in sets if "Set of" in r["title"]] == []


def test_a_cup_set_sku_draws_as_many_cups_as_its_set_holds(ceiling):
    """Guard (#851, #728): a set of 8 drawn as one cup reads as a single. Metric: SKUs whose
    drawing is laid out from another count than their set size."""
    wrong = [
        (r["title"], s.get("pack_size"), pack_copies.copies(r, s))
        for r in ceiling.records
        if r["product_type"] == "Cup Set"
        for s in r["skus"]
        if pack_copies.copies(r, s) != PACKS.get(s.get("pack_size"))
    ]
    assert wrong == [], wrong[:5]


@pytest.mark.parametrize("template", sorted(SIZED))
def test_a_travel_cup_or_tumbler_sells_each_color_in_three_capacities(ceiling, template):
    """Guard (#851): a travel cup and a tumbler had color SKUs only. Metric: products of the
    template with a color not sold in the three capacities, or two products of one brand."""
    recs = _of(ceiling, template)
    assert len(recs) > 1
    assert {r["product_type"] for r in recs} == {SIZED[template]}
    wrong = [
        (r["title"], color, sizes)
        for r in recs
        for color, sizes in _per_color(r, "capacity_ml").items()
        if sorted(sizes, key=str) != CAPACITIES
    ]
    assert wrong == [], wrong[:5]
    per_brand = collections.Counter(r["brand"] for r in recs)
    assert max(per_brand.values()) == 1, per_brand


@pytest.mark.parametrize("template", sorted(SIZED))
def test_a_larger_capacity_draws_larger(ceiling, template):
    """Guard (#851): a capacity is a size, so each one is its own rung of the size ladder.
    Metric: the scales of one color's SKUs, smallest capacity first."""
    assert SIZED[template] in size_axes.AXES
    for r in _of(ceiling, template):
        color = r["skus"][0]["color"]
        skus = sorted((s for s in r["skus"] if s["color"] == color),
                      key=lambda s: s["capacity_ml"])  # fmt: skip
        scales = [size_ladder.size_scale(r, s) for s in skus]
        assert None not in scales and scales == sorted(set(scales)), (r["title"], scales)


def test_a_capacity_is_exported_in_millilitres():
    """Guard (#851): the shopper reads the capacity with its unit. Metric: the export entry."""
    assert export.OPTIONS["capacity_ml"] == ("capacity", "Capacity", "MLT")
