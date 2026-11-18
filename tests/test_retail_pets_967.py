"""Pets, slices 1 and 2 (gen#967): the department, its food, litter, treats, toys and beds.

The retail catalogue had no pets department, so a search for ``dry dog food`` or ``cat litter``
found nothing. Slice 1 adds the department (``core/departments.RETAIL``) and its first three
types, each a spec of its own (``type_specs/dog_food.py``, ``cat_food.py``, ``cat_litter.py``)
drawn by :mod:`kit_pets`. These checks hold the slice's Done-when: the ceiling build has at least
2,000 SKUs under the department; each type's styles have unique ids, titles and twin keys; the
rows and their drawings are the same on every call; and a golden slice pins each type's first
derived styles, so a change that moves them shows here. The pack draws what it says (its life
stage, flavor, breed size, special need and scent), so few Pets styles share a results grid tile.

Slice 2 adds Dog Treats, Pet Toy and Pet Bed (``type_specs/dog_treats.py``, ``pet_toy.py``,
``pet_bed.py``, drawn by :mod:`kit_pet_gear`) and raises the floor to 4,300 SKUs; the toys and
beds are sold in each of the six main colors (ruling 2026-10-13, gen#275).
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import departments
from synthetic_ecommerce_data.domains.retail import kit, pets_rows, scale, type_registry
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS

#: The department, the top level of every pets path.
ROOT = "Pets"
TYPES = ("Dog Food", "Cat Food", "Cat Litter", "Dog Treats", "Pet Toy", "Pet Bed")
KEYS = {"Dog Food": "dog_food", "Cat Food": "cat_food", "Cat Litter": "cat_litter",
        "Dog Treats": "dog_treats", "Pet Toy": "pet_toy", "Pet Bed": "pet_bed"}  # fmt: skip
#: The types sold in colors: each offers the six main colors (ruling 2026-10-13, gen#275).
COLORED = ("Pet Toy", "Pet Bed")
#: Slice 2's floor at the ceiling build (the gate comment of gen#967; slice 1's was 2,000).
FLOOR = 4_300
#: The Pets styles at the ceiling that may share a grid tile. The shapes drew only the animal,
#: the pack color and the format, and 389 of 619 did, which put the catalog over its cap.
PETS_GRID_CLONES = 0.02


@pytest.fixture(scope="module")
def pets() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


def test_the_department_is_on_the_closed_list() -> None:
    assert ROOT in departments.RETAIL


def test_the_ceiling_build_holds_the_slice_floor_of_pets_skus(pets) -> None:
    skus = sum(r["sku_count"] for r in pets)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(pets) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in pets if r["product_id"] in derived}
    assert kinds == set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(pets, ptype) -> None:
    mine = [r for r in pets if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", COLORED)
def test_each_colored_type_offers_the_six_main_colors(pets, ptype) -> None:
    offered = {s.get("color") for r in pets if r["product_type"] == ptype for s in r["skus"]}
    assert set(MAIN_COLORS) <= offered, sorted(set(MAIN_COLORS) - offered)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


def _golden(pets: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in pets if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Dog Food": [
        ("BRD-0139F80E655E", "Sowwick Puppy Small Breed Dry Dog Food with Beef & Vegetable", 3, 8.5),  # noqa: E501
        ("BRD-015EB9FD793C", "Quarthwaite Senior Medium Breed Dry Dog Food with Turkey & Sweet Potato", 3, 8.5),  # noqa: E501
        ("BRD-01F0AFDFC4B3", "Sedmouth Senior Small Breed Dry Dog Food with Duck & Pea", 3, 8.0),
    ],
    "Cat Food": [
        ("BRD-006AF6BEB0E4", "Foxgate Senior Wet Cat Food with Tuna Pate, Tins", 4, 2.55),
        ("BRD-01B4E9895FF8", "Caldness Adult Hairball Control Dry Cat Food with Chicken", 3, 4.9),
        ("BRD-02FDA95F49AE", "Chaphaugh Senior Wet Cat Food with Chicken in Jelly, Pouches", 3, 4.45),  # noqa: E501
    ],
    "Cat Litter": [
        ("BRD-00112B468C03", "Lingate Baby Powder Wood Pellet Cat Litter", 3, 6.5),
        ("BRD-03E57A1B6D5A", "Kilden Lavender Clumping Clay Cat Litter", 3, 3.2),
        ("BRD-06F75E8C843B", "Sowside Citrus Clumping Clay Cat Litter", 3, 5.5),
    ],
    "Dog Treats": [],
    "Pet Toy": [],
    "Pet Bed": [],
}  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(pets, ptype) -> None:
    assert _golden(pets, ptype) == GOLDEN[ptype]


def test_few_pets_styles_share_a_results_grid_tile(pets) -> None:
    """Guard: a pack that drops a :data:`pets_rows.DRAWN` attribute from its drawing clones
    tiles again. Metric: the Pets grid-clone share, in the failure message."""
    main = scale.derivable(pets)
    report = scale.grid_clones(main)
    rate = report["grid_clones"] / len(main)
    assert rate <= PETS_GRID_CLONES, f"{report['grid_clones']} of {len(main)} styles ({rate:.1%})"


#: Two values of each attribute the pack draws (:data:`pets_rows.DRAWN`).
DRAWN_VALUES = {"life_stage": ("puppy", "senior"), "flavor": ("chicken & rice", "salmon & potato"),
                "breed_size": ("small breed", "large breed"),
                "special_need": ("indoor", "sensitive"), "scent": ("lavender", "pine"),
                "treat_form": ("dental stick", "training bite"), "toy_kind": ("ball", "rope"),
                "play_feature": ("squeaky", "floating"), "bed_style": ("donut", "cave"),
                "cover": ("faux fur", "corduroy")}  # fmt: skip
#: The shape that draws each attribute; the rest are drawn on the dry food bag.
DRAWN_ON = {"scent": "cat_litter", "treat_form": "dog_treats", "toy_kind": "pet_toy",
            "play_feature": "pet_toy", "bed_style": "pet_bed", "cover": "pet_bed"}  # fmt: skip


@pytest.mark.parametrize("key", tuple(DRAWN_VALUES))
def test_each_drawn_attribute_changes_the_picture(key) -> None:
    """Two values of one drawn attribute give two pictures (on its shape in :data:`DRAWN_ON`, else
    on the dry food bag), and the rows draw each of them."""
    assert key in getattr(pets_rows, "DRAWN", ())
    shape = DRAWN_ON.get(key, "dry_pet_food")
    values = DRAWN_VALUES[key]
    fill = kit.Fill("solid", "#123456", "#654321")
    one, two = (kit.render(shape, fill, params={key: v}) for v in values)
    assert one != two
