"""Jewellery and watches, cut 1 (gen#1113): stud earrings, bangles and cufflinks.

Three new spec types, each with a shape of its own: a stud earring is a metal (and a stone, when it
has one), a bangle is a metal times a size, and cufflinks are the first Mens jewellery. The four
search-demo queries of the issue are held here too, each on the family it should find: two by the
baseline text rank of the ceiling build, and two on the structured fields a policy reads, because
the words alone find another product first ("18 inch" names a pedestal fan, and a ring size is a
letter).
"""

from __future__ import annotations

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import kit_jewellery, type_registry

NEW = {"stud_earrings": "Stud Earrings", "bangle": "Bangle", "cufflinks": "Cufflinks"}
METALS = {
    "Gold Plated", "Sterling Silver", "Rose Gold Plated",
    "Gold Plated Stainless Steel", "Stainless Steel", "Rose Gold Plated Stainless Steel",
}  # fmt: skip


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return ceiling_build().records


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _of(records: list[dict], ptype: str) -> list[dict]:
    return [r for r in records if r["product_type"] == ptype]


def _attrs(rec: dict, key: str) -> list[str]:
    return [a["value"] for a in rec["attributes"] if a["key"] == key]


def test_the_three_types_are_specs_with_two_decoys_each() -> None:
    specs = type_registry.specs()
    for key, ptype in NEW.items():
        assert specs[key].product_type == ptype
        assert len(specs[key].rows) >= 6 and len(specs[key].decoys) >= 2, key
        assert len({r.brand for r in specs[key].rows}) >= 4, key


@pytest.mark.parametrize("ptype", sorted(NEW.values()))
def test_every_sku_is_a_metal_and_the_color_is_that_metal(ceiling: list[dict], ptype: str) -> None:
    rows = _of(ceiling, ptype)
    assert rows, ptype
    for r in rows:
        for s in r["skus"]:
            assert s["metal"] in METALS, (r["title"], s)
            assert s["color"] in {"Gold", "Silver", "Rose Gold"}, (r["title"], s)
        assert set(_attrs(r, "metal")) == {s["metal"] for s in r["skus"]}, r["title"]


def test_a_stone_stud_states_its_stone_and_draws_it(ceiling: list[dict]) -> None:
    gems = [r for r in _of(ceiling, "Stud Earrings") if r["drawing"]["params"].get("stud") == "gem"]
    assert len(gems) >= 4
    for r in gems:
        (stone,) = _attrs(r, "stone")
        assert stone.lower() in r["title"].lower()
        assert r["drawing"]["params"]["stone"] == stone.lower()


def test_a_bangle_sells_each_metal_in_three_sizes(ceiling: list[dict]) -> None:
    for r in _of(ceiling, "Bangle"):
        assert r["category_path"][-2:] == ["Bracelets", "Bangles"], r["category_path"]
        pairs = {(s["metal"], s["size"]) for s in r["skus"]}
        assert len(pairs) == len(r["skus"]) == 3 * len(_attrs(r, "metal")), r["title"]
        assert {s["size"] for s in r["skus"]} == {"Small", "Medium", "Large"}


def test_cufflinks_are_mens_jewellery(ceiling: list[dict]) -> None:
    rows = _of(ceiling, "Cufflinks")
    assert rows
    for r in rows:
        assert r["category_path"][:2] == ["Mens", "Jewellery"], r["category_path"]
        assert _attrs(r, "audience") == ["Mens"]


@pytest.mark.parametrize(
    ("shape", "param", "a", "b"),
    [
        ("stud_earrings", "stud", "ball", "pearl"),
        ("bangle", "style", "plain", "hammered"),
        ("cufflinks", "face", "round", "square"),
    ],
)
def test_a_param_changes_the_drawing(shape: str, param: str, a: str, b: str) -> None:
    draw = getattr(kit_jewellery, shape)
    assert draw("#d4af37", None, None, **{param: a}) != draw("#d4af37", None, None, **{param: b})
    with pytest.raises(ValueError):
        draw("#d4af37", None, None, **{param: "nonsense"})


#: A text query and the product types that must rank first on the baseline (text only).
TEXT = {
    "gold hoop earrings": {"Hoop Earrings", "Earrings"},
    "watch": {"Analog Watch", "Digital Watch", "Watch"},
    "stud earrings": {"Stud Earrings", "Earrings"},
    "bangle": {"Bangle"},
    "cufflinks": {"Cufflinks"},
    "sapphire stud earrings": {"Stud Earrings"},
}


@pytest.mark.parametrize("query", sorted(TEXT))
def test_a_query_ranks_its_family_first(index: br.Index, query: str) -> None:
    top = br.rank(index, query, 1, popular=False)[0]
    assert top["product_type"] in TEXT[query], (query, top["product_type"], top["title"])


def test_gold_hoop_earrings_have_a_gold_metal_sku(ceiling: list[dict]) -> None:
    hoops = _of(ceiling, "Hoop Earrings")
    assert any(s["metal"].startswith("Gold") for r in hoops for s in r["skus"])


def test_silver_necklace_18_inch_is_a_45_cm_silver_necklace_sku(ceiling: list[dict]) -> None:
    """18 inches is 45.7 cm: the necklace length axis is in centimetres (``length_cm``)."""
    assert any(
        s.get("length_cm") == "45" and s["metal"] in {"Sterling Silver", "Stainless Steel"}
        for r in _of(ceiling, "Necklace") for s in r["skus"]
    )  # fmt: skip


def test_ring_size_n_is_a_ring_sku_in_uk_and_us_sizes(ceiling: list[dict]) -> None:
    sized = [s for r in _of(ceiling, "Ring") for s in r["skus"] if s.get("ring_size_uk") == "N"]
    assert sized and all(s["ring_size_us"] == "7" for s in sized)
