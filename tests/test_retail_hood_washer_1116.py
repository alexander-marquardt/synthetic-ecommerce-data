"""Cooker hoods, deeper laundry and freezers, and ``washer`` in laundry titles (#1116, round 3).

The department held no cooker hood, six chest and six upright freezers, and no laundry title with
the US word ``washer``, so ``washer`` met windshield washer fluid only. Cooker Hood (chimney or
integrated) now has a leaf, a shape of :mod:`kit_cooking` and gen#622 model numbers by width. The
ranking checks run the no-policy baseline ranker without popularity.

``washer`` has three families: machines, windshield washer fluid and the industrial flat washers.
Over the retail templates a machine is in the top ten. Over the retail templates and the flat
washers, both families are found, but the top ten is flat washers: their titles are three words
("Flat Washer: Nylon"). A policy, not the data, picks the laundry intent.
"""

from __future__ import annotations

from collections import Counter

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.domains.industrial import generate
from synthetic_ecommerce_data.domains.retail import appliance_model_numbers as amn
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import kit, scale

ROOT = ["Home", "Large Appliances"]
HOOD_KINDS = {"Chimney Cooker Hood", "Integrated Cooker Hood"}
#: The grown kinds and the fewest models each now holds.
GROWN = {"Washing Machine": 18, "Washer Dryer": 12, "Tumble Dryer (Heat Pump)": 12,
         "Chest Freezer": 12, "Upright Freezer": 12}  # fmt: skip


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def index(templates) -> br.Index:
    return br.Index(templates)


@pytest.fixture(scope="module")
def merged(templates) -> br.Index:
    """The retail templates and the industrial flat washers, as the combined catalog holds them."""
    catalog = generate.generate(generate.GeneratorConfig(), types=["washer_flat"])
    flat = [
        {"title": d["title"], "description": d.get("description", ""),
         "product_id": str(d["sku"]), "product_type": "Flat Washer"}
        for line in catalog.lines
        for d in emit.flat_documents(catalog, line)
    ]  # fmt: skip
    return br.Index([*templates, *flat])


def _attrs(record: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in record["attributes"]}


def test_cooker_hoods_have_their_own_leaf_shape_and_six_models_of_each_kind(templates):
    rows = [r for r in templates if r["product_type"] == "Cooker Hood"]
    assert {tuple(r["category_path"]) for r in rows} == {(*ROOT, "Cooker Hoods")}
    assert {r["drawing"]["shape"] for r in rows} == {"cooker_hood"}
    count = Counter(_attrs(r)["appliance_type"] for r in rows)
    assert set(count) == HOOD_KINDS, count
    assert min(count.values()) >= 6, count
    assert len({r["brand"] for r in rows}) >= 2


def test_a_hood_states_its_width_in_the_title_the_number_and_the_drawing(templates):
    rows = [r for r in templates if r["product_type"] == "Cooker Hood"]
    assert rows
    for r in rows:
        width = _attrs(r)["item_width"]
        assert f" {width}cm " in r["title"], r["title"]
        assert amn.decode(_attrs(r)["model_number"])["capacity"] == int(width), r["title"]
        assert r["drawing"]["params"]["width"] == width, r["title"]


@pytest.mark.parametrize(
    ("param", "one", "other"), [("kind", "chimney", "integrated"), ("width", "60", "90")]
)
def test_a_param_changes_the_hood_drawing(param, one, other):
    assert "cooker_hood" in kit.shapes()  # kit.shapes() imports every kit module first
    fill = kit.Fill("solid", "#c8312e")
    a = kit.render("cooker_hood", fill, params={param: one})
    b = kit.render("cooker_hood", fill, params={param: other})
    assert "<svg" in a and a != b


@pytest.mark.parametrize("kind", sorted(GROWN))
def test_the_laundry_and_freezer_kinds_are_grown(templates, kind):
    got = sum(_attrs(r).get("appliance_type") == kind for r in templates)
    assert got >= GROWN[kind], (kind, got)


def test_cooker_hood_finds_only_cooker_hoods(index):
    top = br.rank(index, "cooker hood", 5, popular=False)
    assert [r["product_type"] for r in top] == ["Cooker Hood"] * 5, [r["title"] for r in top]


def test_washer_meets_a_washing_machine_and_washer_fluid_in_the_retail_top_ten(index):
    top = br.rank(index, "washer", 10, popular=False)
    kinds = {_attrs(r).get("appliance_type") for r in top}
    assert "Washing Machine" in kinds, [r["title"] for r in top]
    assert "Windshield Washer Fluid" in {r["product_type"] for r in top}


def test_washer_finds_both_families_and_without_a_policy_the_flat_washers_fill_the_top_ten(merged):
    hits = br.rank(merged, "washer", len(merged.catalog), popular=False)
    found = {r["product_type"] for r in hits}
    assert {"Laundry Appliance", "Flat Washer"} <= found, found
    assert {r["product_type"] for r in hits[:10]} == {"Flat Washer"}


def test_washer_8kg_is_laundry_and_m8_washer_is_fasteners(merged):
    kg = br.rank(merged, "washer 8kg", 5, popular=False)
    m8 = br.rank(merged, "m8 washer", 5, popular=False)
    assert {r["product_type"] for r in kg} == {"Laundry Appliance"}, [r["title"] for r in kg]
    assert {r["product_type"] for r in m8} == {"Flat Washer"}, [r["title"] for r in m8]


def test_heat_pump_dryer_finds_only_tumble_dryers(index):
    top = br.rank(index, "heat pump dryer", 10, popular=False)
    assert {r["product_type"] for r in top} == {"Laundry Appliance"}, [r["title"] for r in top]
