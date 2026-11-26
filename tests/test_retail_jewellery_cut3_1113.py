"""Jewellery and watches, cut 3 (gen#1113): charms, brooches and jewellery boxes.

Each is a spec with a drawing of its own, derivable so the scaled build grows it. A charm's and a
brooch's SKUs are its metals; a jewellery box's are the colors of its covering. What a row says
it is (its motif, its stone, its mirror) is what its drawing shows.
"""

from __future__ import annotations

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import kit_jewellery, scale, type_registry
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS

NEW = {"charm": "Charm", "brooch": "Brooch", "jewellery_box": "Jewellery Box"}
LEAF = {"Charm": "Charms", "Brooch": "Brooches", "Jewellery Box": "Jewellery Boxes"}


@pytest.fixture(scope="module")
def build() -> scale.Scaled:
    return ceiling_build()


def _of(build: scale.Scaled, ptype: str) -> list[dict]:
    return [r for r in build.records if r["product_type"] == ptype]


def _attr(rec: dict, key: str) -> str | None:
    return next((str(a["value"]) for a in rec["attributes"] if a["key"] == key), None)


@pytest.mark.parametrize("key", sorted(NEW))
def test_a_new_type_is_a_derivable_spec_with_two_decoys_and_four_brands(key: str) -> None:
    spec = type_registry.specs()[key]
    assert spec.product_type == NEW[key] and spec.derivable
    assert len(spec.decoys) >= 2 and len({r.brand for r in spec.rows}) >= 4


@pytest.mark.parametrize("ptype", sorted(LEAF))
def test_a_new_type_sits_in_its_jewellery_leaf_and_grows(build: scale.Scaled, ptype: str) -> None:
    recs = _of(build, ptype)
    assert sum(r["product_id"] in build.template_of for r in recs) >= 8, ptype
    for r in recs:
        assert r["category_path"] == ["Womens", "Jewellery", LEAF[ptype]], r["category_path"]


@pytest.mark.parametrize("ptype", ["Charm", "Brooch"])
def test_a_charm_and_a_brooch_sell_one_sku_a_metal(build: scale.Scaled, ptype: str) -> None:
    for r in _of(build, ptype):
        metals = [s["metal"] for s in r["skus"]]
        assert metals and len(set(metals)) == len(metals), r["title"]


@pytest.mark.parametrize("ptype", ["Charm", "Brooch"])
def test_a_stone_style_states_the_stone_it_draws(build: scale.Scaled, ptype: str) -> None:
    gems = [r for r in _of(build, ptype) if r["drawing"]["params"]["motif"] == "stone"]
    assert len({r["drawing"]["params"]["stone"] for r in gems}) >= 5, ptype
    for r in gems:
        assert _attr(r, "stone").lower() == r["drawing"]["params"]["stone"], r["title"]
        assert r["drawing"]["params"]["stone"] in r["title"].lower(), r["title"]


def test_a_charm_fastens_as_it_is_drawn(build: scale.Scaled) -> None:
    for r in _of(build, "Charm"):
        bead = r["drawing"]["params"]["motif"] == "bead"
        assert _attr(r, "fastening") == ("Threaded" if bead else "Lobster Clasp"), r["title"]


def test_a_jewellery_box_says_it_has_a_mirror_only_when_it_draws_one(build: scale.Scaled) -> None:
    boxes = _of(build, "Jewellery Box")
    for r in boxes:
        drawn = r["drawing"]["params"]["style"] == "mirror"
        assert _attr(r, "mirror") == ("Yes" if drawn else "No"), r["title"]
        assert int(_attr(r, "compartments")) >= 1, r["title"]
    colors = {s["color"] for r in boxes for s in r["skus"]}
    assert set(MAIN_COLORS) <= colors, set(MAIN_COLORS) - colors


@pytest.mark.parametrize(
    ("shape", "param", "values"),
    [
        ("charm", "motif", ("heart", "star", "moon", "cross", "clover", "paw", "bead")),
        ("brooch", "motif", ("flower", "bee", "bow", "leaf", "pearl")),
        ("jewellery_box", "style", ("case", "mirror", "drawers", "travel")),
    ],
)
def test_a_param_changes_the_drawing(shape: str, param: str, values: tuple[str, ...]) -> None:
    draw = getattr(kit_jewellery, shape)
    drawn = {"".join(draw("#d4af37", None, None, **{param: v})) for v in values}
    assert len(drawn) == len(values)
    with pytest.raises(ValueError):
        draw("#d4af37", None, None, **{param: "nonsense"})


@pytest.mark.parametrize("shape", ["charm", "brooch"])
def test_a_stone_is_drawn_and_one_the_kit_cannot_draw_is_refused(shape: str) -> None:
    draw = getattr(kit_jewellery, shape)
    stones = [draw("#d4af37", None, None, motif="stone", stone=s) for s in ("emerald", "ruby")]
    assert stones[0] != stones[1]
    with pytest.raises(ValueError):
        draw("#d4af37", None, None, motif="stone", stone="nonsense")


#: A text query and the product types that must rank first on the baseline (text only).
TEXT = {
    "charm": {"Charm"},
    "birthstone charm": {"Charm"},
    "brooch": {"Brooch"},
    "pearl brooch": {"Brooch"},
    "jewellery box": {"Jewellery Box"},
    "travel jewelry case": {"Jewellery Box"},
}


@pytest.fixture(scope="module")
def index(build: scale.Scaled) -> br.Index:
    return br.Index(build.records)


@pytest.mark.parametrize("query", sorted(TEXT))
def test_a_query_ranks_its_family_first(index: br.Index, query: str) -> None:
    top = br.rank(index, query, 1, popular=False)[0]
    assert top["product_type"] in TEXT[query], (query, top["product_type"], top["title"])
