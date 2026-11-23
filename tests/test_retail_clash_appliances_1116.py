"""Steam irons, vacuum cleaners and microwaves (#1116, round 2, slice 1).

The catalog sold no clothes iron, vacuum or microwave. So ``steam iron`` and ``iron`` met
minerals, frying pans and kettlebells ("iron" as the metal), ``vacuum cleaner`` met floor cleaner
and ``microwave`` met ready meals ("microwave" on a pack). Three types now sit in leaves of their
own under Home > Small Appliances, each drawn by a shape of :mod:`kit_household_appliances` that
shows its kind. The ranking checks run the no-policy baseline ranker over the templates: the bare
``iron`` meets both families, and a category policy, not the data, picks the intent.
"""

from __future__ import annotations

from collections import Counter

import pytest

from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import kit, scale

ROOT = ["Home", "Small Appliances"]
#: product type -> (its leaf, its drawing shape, its type key, its kinds)
TYPES = {
    "Steam Iron": ("Irons", "steam_iron", "iron_type",
                   {"Standard", "Cordless", "Steam Generator", "Travel"}),
    "Vacuum Cleaner": ("Vacuum Cleaners", "vacuum_cleaner", "vacuum_type",
                       {"Upright", "Cylinder", "Cordless Stick", "Handheld", "Robot"}),
    "Microwave": ("Microwaves", "microwave", "microwave_type", {"Solo", "Grill", "Combination"}),
}  # fmt: skip


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def index(templates) -> br.Index:
    return br.Index(templates)


def _attrs(record: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in record["attributes"]}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_clash_type_has_its_own_leaf_its_own_shape_and_six_models(templates, ptype):
    leaf, shape, key, kinds = TYPES[ptype]
    rows = [r for r in templates if r["product_type"] == ptype]
    assert {tuple(r["category_path"]) for r in rows} == {(*ROOT, leaf)}, ptype
    assert {r["drawing"]["shape"] for r in rows} == {shape}
    assert {_attrs(r)[key] for r in rows} == kinds
    assert len(rows) >= 6, len(rows)
    assert len({r["brand"] for r in rows}) >= 2
    for r in rows:
        assert r["drawing"]["params"]["kind"] == _attrs(r)[key].lower(), r["title"]


@pytest.mark.parametrize(
    ("shape", "one", "other"),
    [("steam_iron", "standard", "steam generator"), ("steam_iron", "cordless", "travel"),
     ("vacuum_cleaner", "upright", "cylinder"), ("vacuum_cleaner", "cordless stick", "robot"),
     ("vacuum_cleaner", "handheld", "upright"),
     ("microwave", "solo", "grill"), ("microwave", "grill", "combination")],
)  # fmt: skip
def test_a_kind_changes_the_drawing(shape, one, other):
    assert shape in kit.shapes(), shape  # kit.shapes() imports every kit module first
    fill = kit.Fill("solid", "#3f6fb5")
    a = kit.render(shape, fill, params={"kind": one})
    b = kit.render(shape, fill, params={"kind": other})
    assert "<svg" in a and a != b


def test_steam_iron_finds_only_steam_irons_without_a_policy(index):
    top = br.rank(index, "steam iron", 5, popular=False)
    assert [r["product_type"] for r in top] == ["Steam Iron"] * 5, [r["title"] for r in top]


def test_iron_meets_steam_irons_and_the_metal_iron_products_without_a_policy(index):
    """Both families in the top 10, as the issue's table asks: a policy, not the data, picks the
    intent."""
    types = Counter(r["product_type"] for r in br.rank(index, "iron", 10, popular=False))
    assert types["Steam Iron"] >= 1, types
    assert set(types) - {"Steam Iron"}, types


@pytest.mark.parametrize(
    ("query", "ptype"),
    [("vacuum cleaner", "Vacuum Cleaner"), ("cordless vacuum", "Vacuum Cleaner"),
     ("microwave", "Microwave")],
)  # fmt: skip
def test_a_clash_query_finds_its_own_type_first(index, query, ptype):
    top = br.rank(index, query, 5, popular=False)
    assert [r["product_type"] for r in top] == [ptype] * 5, [r["title"] for r in top]


def test_combination_microwave_finds_the_combination_microwaves_first(index, templates):
    """Its kind is in its title and its structured type, so the combination ones lead, before the
    combination locks."""
    want = sum(1 for r in templates if r["product_type"] == "Microwave"
               and _attrs(r)["microwave_type"] == "Combination")  # fmt: skip
    top = br.rank(index, "combination microwave", want, popular=False)
    got = [(r["product_type"], _attrs(r).get("microwave_type")) for r in top]
    assert want >= 2 and got == [("Microwave", "Combination")] * want, [r["title"] for r in top]
