"""Jewellery and watches, cut 2 (gen#1113): pendants, anklets, watch straps, and the derived range.

The jewellery and watch types are derivable, so the scaled build grows them. A derived style is its
template's build under another brand, range and price: its stone, style and strap are drawn, so a
style that changed one would say a thing its picture does not show.
"""

from __future__ import annotations

from typing import Any

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import kit_jewellery, scale, scale_text, type_registry

TYPES = scale_text.JEWELLERY_TYPES
METAL_TYPES = (
    "Hoop Earrings", "Drop Earrings", "Stud Earrings", "Bangle", "Bracelet", "Necklace", "Pendant",
    "Anklet", "Ring", "Cufflinks", "Charm", "Brooch",
)  # fmt: skip
NEW = {"pendant": "Pendant", "anklet": "Anklet", "watch_strap": "Watch Strap"}
#: The color a metal may have: a gold plated SKU is gold, and nothing else.
METAL_COLOR = {
    "Gold Plated": "Gold", "Gold Plated Stainless Steel": "Gold", "Sterling Silver": "Silver",
    "Stainless Steel": "Silver", "Rose Gold Plated": "Rose Gold",
    "Rose Gold Plated Stainless Steel": "Rose Gold",
}  # fmt: skip
#: Hand-written bracelets (authored samples) that state no metal, as before this cut.
NO_METAL = {"PLT-DY70", "PLT-DY74", "PLT-DY549"}
#: The SKUs of the range on the ceiling build, all 19 Womens and Mens types (456 before cut 2,
#: 2,028 after it; cut 3's charms, brooches and jewellery boxes take it to 2,309).
RANGE_FLOOR = 2_300


@pytest.fixture(scope="module")
def build() -> scale.Scaled:
    return ceiling_build()


@pytest.fixture(scope="module")
def by_id(build: scale.Scaled) -> dict[str, dict]:
    return {r["product_id"]: r for r in build.records}


@pytest.fixture(scope="module")
def index(build: scale.Scaled) -> br.Index:
    return br.Index(build.records)


def _of(build: scale.Scaled, ptype: str) -> list[dict]:
    return [r for r in build.records if r["product_type"] == ptype]


def _attrs(rec: dict, keys: frozenset[str]) -> set[tuple[str, str]]:
    return {(a["key"], str(a["value"])) for a in rec["attributes"] if a["key"] in keys}


def _pairs(build: scale.Scaled, by_id: dict[str, dict], ptype: str) -> list[tuple[dict, dict]]:
    """Each derived style of a type, with the template it came from."""
    return [
        (r, by_id[build.template_of[r["product_id"]]])
        for r in _of(build, ptype) if r["product_id"] in build.template_of
    ]  # fmt: skip


@pytest.mark.parametrize("ptype", TYPES)
def test_every_type_has_derived_styles(build: scale.Scaled, by_id: dict, ptype: str) -> None:
    assert len(_pairs(build, by_id, ptype)) >= 8, ptype


@pytest.mark.parametrize("ptype", TYPES)
def test_a_derived_style_keeps_the_build_its_drawing_shows(
    build: scale.Scaled, by_id: dict, ptype: str
) -> None:
    fixed = scale_text.JEWELLERY_KEYS - {"metal"}  # the metals are the SKUs' own, held below
    for rec, tpl in _pairs(build, by_id, ptype):
        assert _attrs(rec, fixed) == _attrs(tpl, fixed), (rec["title"], tpl["title"])
        assert rec["drawing"]["shape"] == tpl["drawing"]["shape"], rec["title"]
        assert rec["drawing"]["params"] == tpl["drawing"]["params"], rec["title"]


@pytest.mark.parametrize("ptype", METAL_TYPES)
def test_a_jewellery_sku_is_colored_by_its_metal(build: scale.Scaled, ptype: str) -> None:
    for r in _of(build, ptype):
        if r["product_id"] in NO_METAL:
            continue
        for s in r["skus"]:
            assert s["color"] == METAL_COLOR[s["metal"]], (r["title"], s)


@pytest.mark.parametrize("ptype", sorted(NEW.values()))
def test_a_new_type_is_a_spec_with_two_decoys_and_four_brands(ptype: str) -> None:
    key = next(k for k, v in NEW.items() if v == ptype)
    spec = type_registry.specs()[key]
    assert spec.product_type == ptype and spec.derivable
    assert len(spec.decoys) >= 2 and len({r.brand for r in spec.rows}) >= 4


def _axes(rec: dict, *keys: str) -> set[tuple[Any, ...]]:
    return {tuple(s[k] for k in keys) for s in rec["skus"]}


@pytest.mark.parametrize(
    ("ptype", "lengths"), [("Pendant", {"40", "45", "50"}), ("Anklet", {"23", "25"})]
)
def test_each_metal_is_sold_in_each_chain_length(
    build: scale.Scaled, ptype: str, lengths: set[str]
) -> None:
    for r in _of(build, ptype):
        assert r["category_path"][:2] == ["Womens", "Jewellery"], r["category_path"]
        metals = {s["metal"] for s in r["skus"]}
        want = {(m, cm) for m in metals for cm in lengths}
        assert _axes(r, "metal", "length_cm") == want and len(r["skus"]) == len(want), r["title"]


def test_a_stone_pendant_states_the_stone_it_draws(build: scale.Scaled) -> None:
    gems = [r for r in _of(build, "Pendant") if r["drawing"]["params"]["charm"] == "stone"]
    assert len({r["drawing"]["params"]["stone"] for r in gems}) >= 10
    for r in gems:
        ((_, stone),) = _attrs(r, frozenset({"stone"}))
        assert stone.lower() == r["drawing"]["params"]["stone"], r["title"]
        assert stone.lower() in r["title"].lower(), r["title"]


def test_a_watch_strap_is_a_lug_width_of_its_audience(build: scale.Scaled) -> None:
    widths = {"Womens": {"14", "16", "18"}, "Mens": {"18", "20", "22"}}
    seen = set()
    for r in _of(build, "Watch Strap"):
        who = r["category_path"][0]
        seen.add(who)
        assert r["category_path"][1:] == ["Watches", "Watch Straps"], r["category_path"]
        assert {s["lug_mm"] for s in r["skus"]} == widths[who], r["title"]
        assert len(_axes(r, "color", "lug_mm")) == len(r["skus"]), r["title"]
        assert len(_attrs(r, frozenset({"strap"}))) == 1, r["title"]
    assert seen == set(widths)


@pytest.mark.parametrize(
    ("shape", "param", "values"),
    [
        ("pendant", "charm", ("heart", "star", "moon", "cross", "disc", "pearl")),
        ("anklet", "style", ("chain", "beaded", "charm", "double")),
        ("watch_strap", "material", ("leather", "silicone", "fabric", "mesh")),
    ],
)
def test_a_param_changes_the_drawing(shape: str, param: str, values: tuple[str, ...]) -> None:
    draw = getattr(kit_jewellery, shape)
    drawn = {"".join(draw("#d4af37", None, None, **{param: v})) for v in values}
    assert len(drawn) == len(values)
    with pytest.raises(ValueError):
        draw("#d4af37", None, None, **{param: "nonsense"})


def test_a_pendant_draws_its_stone_and_refuses_one_it_cannot_draw() -> None:
    draw = kit_jewellery.pendant
    stones = [draw("#d4af37", None, None, charm="stone", stone=s) for s in ("emerald", "garnet")]
    assert stones[0] != stones[1]
    with pytest.raises(ValueError):
        draw("#d4af37", None, None, charm="stone", stone="nonsense")


#: A text query and the product types that must rank first on the baseline (text only).
TEXT = {
    "pendant necklace": {"Pendant", "Necklace"},
    "birthstone pendant": {"Pendant"},
    "anklet": {"Anklet"},
    "watch strap": {"Watch Strap"},
    "watch": {"Analog Watch", "Digital Watch", "Watch"},
    "gold hoop earrings": {"Hoop Earrings", "Earrings"},
}


@pytest.mark.parametrize("query", sorted(TEXT))
def test_a_query_ranks_its_family_first(index: br.Index, query: str) -> None:
    top = br.rank(index, query, 1, popular=False)[0]
    assert top["product_type"] in TEXT[query], (query, top["product_type"], top["title"])


def test_the_range_reaches_its_floor(build: scale.Scaled) -> None:
    types = {*TYPES, "Fitness Band", "Watch", "Earrings"}
    skus = sum(
        r["sku_count"] for r in build.records
        if r["product_type"] in types and r["category_path"][0] in {"Womens", "Mens"}
    )  # fmt: skip
    assert skus >= RANGE_FLOOR, skus
