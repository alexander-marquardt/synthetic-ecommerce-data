"""Jewellery and watches, cut 4 (gen#1113): jewellery sets, kids' watches, sports and dress watches.

A jewellery set and a kids' watch are specs with drawings of their own, derivable so the scaled
build grows them. Sports and dress watches are styles of the analog and digital watches, so each of
those rows states its ``watch_style``. What a row says it is (its pieces, its stone, its dial, its
face) is what its drawing shows.
"""

from __future__ import annotations

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import kit_jewellery, scale, type_registry
from synthetic_ecommerce_data.domains.retail.kit import Fill
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS

NEW = {"jewellery_set": "Jewellery Set", "kids_watch": "Kids Watch"}
STYLES = {"Dress", "Sports", "Field", "Everyday"}
#: The pieces a set's ``set_contents`` names, as its drawing's ``pieces`` reads them.
PIECES = {"Necklace and Earrings": "2", "Necklace, Earrings and Bracelet": "3"}


@pytest.fixture(scope="module")
def build() -> scale.Scaled:
    return ceiling_build()


def _of(build: scale.Scaled, ptype: str) -> list[dict]:
    return [r for r in build.records if r["product_type"] == ptype]


def _attr(rec: dict, key: str) -> str | None:
    return next((str(a["value"]) for a in rec["attributes"] if a["key"] == key), None)


@pytest.mark.parametrize("key", sorted(NEW))
def test_a_new_type_is_a_derivable_spec_with_two_decoys_and_four_brands(key: str) -> None:
    specs = type_registry.specs()
    assert key in specs, sorted(k for k in specs if "watch" in k or "jewel" in k)
    spec = specs[key]
    assert spec.product_type == NEW[key] and spec.derivable
    assert len(spec.decoys) >= 2 and len({r.brand for r in spec.rows}) >= 4


def test_a_jewellery_set_sits_in_its_leaf_and_sells_one_sku_a_metal(build: scale.Scaled) -> None:
    recs = _of(build, "Jewellery Set")
    assert sum(r["product_id"] in build.template_of for r in recs) >= 8
    for r in recs:
        assert r["category_path"] == ["Womens", "Jewellery", "Jewellery Sets"], r["category_path"]
        metals = [s["metal"] for s in r["skus"]]
        assert metals and len(set(metals)) == len(metals), r["title"]


def test_a_jewellery_set_draws_the_pieces_and_the_stone_it_states(build: scale.Scaled) -> None:
    recs = _of(build, "Jewellery Set")
    assert {_attr(r, "set_contents") for r in recs} == set(PIECES)
    for r in recs:
        params = r["drawing"]["params"]
        assert params["pieces"] == PIECES[_attr(r, "set_contents")], r["title"]
        assert _attr(r, "piece_count") == params["pieces"], r["title"]
        if params["motif"] == "stone":
            assert _attr(r, "stone").lower() == params["stone"], r["title"]
            assert params["stone"] in r["title"].lower(), r["title"]
    assert len({r["drawing"]["params"].get("stone") for r in recs} - {None}) >= 3


def test_a_kids_watch_sits_under_kids_in_the_six_main_colors(build: scale.Scaled) -> None:
    recs = _of(build, "Kids Watch")
    assert sum(r["product_id"] in build.template_of for r in recs) >= 8
    for r in recs:
        assert r["category_path"] == ["Kids", "Watches"], r["category_path"]
        assert _attr(r, "audience") == "Unisex", r["title"]
        face = r["drawing"]["params"]["face"]
        assert _attr(r, "watch_type") == ("Digital" if face == "digital" else "Analog"), r["title"]
        assert int(_attr(r, "water_resistance")) >= 30, r["title"]
    colors = {s["color"] for r in recs for s in r["skus"]}
    assert set(MAIN_COLORS) <= colors, set(MAIN_COLORS) - colors


@pytest.mark.parametrize("ptype", ["Analog Watch", "Digital Watch"])
def test_every_analog_and_digital_watch_states_its_style(build: scale.Scaled, ptype: str) -> None:
    recs = _of(build, ptype)
    for r in recs:
        assert _attr(r, "watch_style") in STYLES, r["title"]
    assert {"Dress", "Sports"} <= {_attr(r, "watch_style") for r in _of(build, "Analog Watch")}


def test_a_sports_watch_is_water_resistant_and_draws_its_dial(build: scale.Scaled) -> None:
    watches = [*_of(build, "Analog Watch"), *_of(build, "Digital Watch")]
    sports = [r for r in watches if _attr(r, "watch_style") == "Sports"]
    assert len(sports) >= 8
    for r in sports:
        assert int(_attr(r, "water_resistance")) >= 100, r["title"]
    for r in _of(build, "Analog Watch"):
        dial = r["drawing"]["params"].get("dial", "plain")
        title = r["title"].lower()
        assert ("chronograph" in title) == (dial == "chrono"), r["title"]
        assert ("dive" in title or "diver" in title) == (dial == "dive"), r["title"]


@pytest.mark.parametrize(
    ("shape", "param", "values"),
    [
        ("jewellery_set", "motif", ("plain", "heart", "pearl", "stone")),
        ("jewellery_set", "pieces", ("2", "3")),
        ("kids_watch", "face", ("teacher", "digital")),
        ("analog_watch", "dial", ("plain", "chrono", "dive")),
        ("analog_watch", "strap", ("leather", "mesh", "fabric", "silicone")),
    ],
)
def test_a_param_changes_the_drawing(shape: str, param: str, values: tuple[str, ...]) -> None:
    draw = getattr(kit_jewellery, shape)
    stone = {"stone": "emerald"} if shape == "jewellery_set" else {}
    fill = Fill("solid", "#d4af37")
    drawn = {"".join(draw("#d4af37", fill, None, **stone, **{param: v})) for v in values}
    assert len(drawn) == len(values)
    with pytest.raises(ValueError):
        draw("#d4af37", fill, None, **{param: "nonsense"})


def test_a_set_stone_is_drawn_and_one_the_kit_cannot_draw_is_refused() -> None:
    draw = kit_jewellery.jewellery_set
    stones = [draw("#d4af37", None, None, motif="stone", stone=s) for s in ("emerald", "ruby")]
    assert stones[0] != stones[1]
    with pytest.raises(ValueError):
        draw("#d4af37", None, None, motif="stone", stone="nonsense")


#: A text query and the product types that must rank first on the baseline (text only).
TEXT = {
    "jewellery set": {"Jewellery Set"},
    "necklace and earrings set": {"Jewellery Set"},
    "kids watch": {"Kids Watch"},
    "time teacher watch": {"Kids Watch"},
}
#: A text query and the watch style that must rank first.
STYLE_TEXT = {"dress watch": "Dress", "sports watch": "Sports", "chronograph watch": "Sports"}


@pytest.fixture(scope="module")
def index(build: scale.Scaled) -> br.Index:
    return br.Index(build.records)


@pytest.mark.parametrize("query", sorted(TEXT))
def test_a_query_ranks_its_family_first(index: br.Index, query: str) -> None:
    top = br.rank(index, query, 1, popular=False)[0]
    assert top["product_type"] in TEXT[query], (query, top["product_type"], top["title"])


@pytest.mark.parametrize("query", sorted(STYLE_TEXT))
def test_a_watch_style_query_ranks_a_watch_of_that_style_first(index: br.Index, query: str) -> None:
    top = br.rank(index, query, 1, popular=False)[0]
    style = _attr(top, "watch_style")
    assert style == STYLE_TEXT[query], (query, top["product_type"], top["title"])
