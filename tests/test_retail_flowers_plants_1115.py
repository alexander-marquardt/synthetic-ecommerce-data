"""Garden's live flowers and plants (gen#1115): cut flowers, letterbox flowers, house plants and
plant food.

The ceiling build held 5 bouquets and no house plant, so a shopper's search for roses or a pet
safe house plant found nothing live. gen#1115 grows the Bouquet type with its own derivable rows
(``type_specs/bouquet.py``: hand-tied bouquets and a new Letterbox Flowers leaf) and adds two
types, House Plant (``house_plant.py``) and Plant Food (``plant_food.py``), all drawn by
:mod:`kit_flowers`. These checks hold the issue's Deliverables: the three types add at least
1,140 SKUs at the ceiling build (95% of the +1,200 target); each bouquet carries its flower,
occasion, bloom color and stem count; every house plant carries its light needs and pot size,
and both pet safe values are built; plant food is built; and each drawing param draws apart.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, kit_flowers, scale_text, type_registry

TYPES = ("Bouquet", "House Plant", "Plant Food")
#: The SKUs the three types held at the ceiling build before gen#1115: 5 bouquets.
BEFORE = 5
#: The floor the issue's Deliverable 4 sets: 95% of the +1,200 target.
FLOOR = 1_140


@pytest.fixture(scope="module")
def live() -> list[dict]:
    return [r for r in ceiling_build().records if r["product_type"] in TYPES]


def test_the_three_types_add_the_floor_of_skus_at_the_ceiling_build(live) -> None:
    by_type = collections.Counter()
    for r in live:
        by_type[r["product_type"]] += r["sku_count"]
    assert sum(by_type.values()) - BEFORE >= FLOOR, by_type
    assert all(by_type[t] for t in TYPES), by_type


def test_every_new_type_is_derived_in_garden(live) -> None:
    derived = set(ceiling_build().template_of)
    assert {r["product_type"] for r in live if r["product_id"] in derived} == set(TYPES)
    assert {r["category_path"][0] for r in live if r["product_id"] in derived} == {"Garden"}


def test_letterbox_flowers_have_their_own_leaf(live) -> None:
    leaves = {tuple(r["category_path"]) for r in live if r["product_type"] == "Bouquet"}
    assert ("Garden", "Flowers", "Letterbox Flowers") in leaves
    assert ("Garden", "Flowers", "Bouquets") in leaves


def test_each_new_bouquet_carries_flower_occasion_color_and_stem_count(live) -> None:
    new = [r for r in live if r["product_type"] == "Bouquet" and r["category_path"][1] == "Flowers"]
    assert len(new) > len(type_registry.specs()["bouquet"].rows)
    for r in new:
        keys = {a["key"] for a in r["attributes"]}
        assert {"flower", "occasion"} <= keys, r["title"]
        assert all(s.get("color") and s.get("stem_count") for s in r["skus"]), r["title"]
    roses = [r for r in new if any(a["value"] == "Rose" for a in r["attributes"])]
    assert roses, "the 'roses' demo query needs cut roses"


def test_every_house_plant_carries_light_needs_and_pot_size_and_both_pet_safe_values(live) -> None:
    plants = [r for r in live if r["product_type"] == "House Plant"]
    safe = collections.Counter()
    for r in plants:
        attrs = {a["key"]: a["value"] for a in r["attributes"]}
        assert attrs.get("light_needs"), r["title"]
        safe[attrs["pet_safe"]] += 1
        assert all(s.get("pot_size_cm") for s in r["skus"]), r["title"]
    assert set(safe) == {"Yes", "No"}, safe


def test_a_derived_house_plant_keeps_its_pot_and_the_facts_of_its_kind() -> None:
    """A house plant's text names its pot ("in a ceramic pot") and its toxicity, so a derived
    style that swapped the pot or the kind would contradict its own description."""
    assert {"plant_kind", "pot_material", "light_needs", "pet_safe"} <= scale_text.FROZEN_KEYS


def test_each_plant_food_text_names_its_own_plant_and_no_other() -> None:
    """A derived plant food swaps the plant the title shows, word for word in its text too, so
    a template's text names its plant and states nothing true only of that plant: an orchid
    feed's "flower spikes" would follow the swap onto a tomato feed."""
    plants = kit_flowers.PLANTS
    for row in type_registry.specs()["plant_food"].rows:
        own = dict(row.params)["plant"]
        text = row.doc()["description"].lower()
        assert own in text, row.code
        assert [p for p in plants if p != own and p in text] == [], row.code
        words = set(text.replace(":", " ").split())
        assert not {"spike", "truss", "bloom", "fruit"} & words, row.code


def test_plant_food_is_built_colorless_at_the_ceiling_build(live) -> None:
    food = [r for r in live if r["product_type"] == "Plant Food"]
    assert food
    assert all(s.get("color") is None for r in food for s in r["skus"])


def _pairs(shape: str, param: str, values: tuple[str, ...]) -> list[tuple]:
    """Each value beside the next, as two params of ``shape`` that must draw apart."""
    return [(shape, {param: v}, {param: w}) for v, w in zip(values, values[1:], strict=False)]


VARIANTS = [
    *_pairs("cut_flowers", "flower", kit_flowers.FLOWERS),
    *_pairs("cut_flowers", "pack", kit_flowers.PACKS),
    *_pairs("house_plant", "kind", kit_flowers.KINDS),
    *_pairs("house_plant", "pot", kit_flowers.POTS),
    *_pairs("plant_food", "form", kit_flowers.FORMS),
    *_pairs("plant_food", "plant", kit_flowers.PLANTS),
]


@pytest.mark.parametrize(("shape", "one", "other"), VARIANTS, ids=str)
def test_a_param_changes_the_drawing(shape: str, one: dict, other: dict) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    assert kit.render(shape, fill, params=one) != kit.render(shape, fill, params=other)
