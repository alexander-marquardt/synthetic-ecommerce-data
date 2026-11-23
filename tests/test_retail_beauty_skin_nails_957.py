"""Beauty (gen#957): facial cleansers, deodorants and nail polish.

After #1092 (oral care and shaving) main's ceiling build held 11,191 Beauty SKUs against the
issue's 13,300, with no facial cleanser, deodorant or nail polish, so a search for ``foaming face
wash``, ``roll-on deodorant`` or ``red nail polish`` found nothing. This slice adds three types,
each a spec of its own (``type_specs/facial_cleanser.py``, ``deodorant.py``, ``nail_polish.py``)
drawn by :mod:`kit_skin`. These checks hold the slice's Done-when: the ceiling build has at least
13,300 Beauty SKUs; each new type's styles have unique ids, titles, twin keys and SKU ids; the
rows and their drawings are the same on every call; each title-shown value draws its own figure;
and a golden slice pins each new type's first derived styles, so a change that moves them shows
here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

KEYS = {
    "Facial Cleanser": "facial_cleanser",
    "Deodorant": "deodorant",
    "Nail Polish": "nail_polish",
}
TYPES = tuple(KEYS)
#: Each new type's leaf (the gate comment of gen#957).
PATHS = {
    "Facial Cleanser": ("Beauty", "Skincare", "Cleansers"),
    "Deodorant": ("Beauty", "Body Care", "Deodorants"),
    "Nail Polish": ("Beauty", "Nails", "Nail Polish"),
}
#: The department the slice deepens.
DEPARTMENT = "Beauty"
#: The issue's floor at the ceiling build (95% of the 14,000 target, gen#957's Done when).
FLOOR = 13_300


@pytest.fixture(scope="module")
def beauty() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == DEPARTMENT]


def test_the_ceiling_build_holds_the_issue_floor_of_beauty_skus(beauty) -> None:
    skus = sum(r["sku_count"] for r in beauty)
    assert skus >= FLOOR, skus


@pytest.mark.parametrize("ptype", TYPES)
def test_every_new_type_is_derived_under_its_own_leaf(beauty, ptype) -> None:
    derived = set(ceiling_build().template_of)
    mine = [r for r in beauty if r["product_type"] == ptype]
    assert any(r["product_id"] in derived for r in mine)
    assert {tuple(r["category_path"]) for r in mine} == {PATHS[ptype]}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(beauty, ptype) -> None:
    mine = [r for r in beauty if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


def test_nail_polish_is_sold_in_the_six_main_colors() -> None:
    spec = type_registry.specs()["nail_polish"]
    for row in spec.rows:
        assert {c[0] for c in row.colors} == {"Red", "Blue", "Green", "Yellow", "Black", "White"}


@pytest.mark.parametrize(
    ("shape", "key", "values"),
    [
        ("facial_cleanser", "texture", ("foaming", "gel", "oil", "micellar", "balm", "clay")),
        (
            "facial_cleanser",
            "skin_type",
            ("oily", "dry", "sensitive", "combination", "normal", "blemish-prone"),
        ),  # fmt: skip
        ("deodorant", "applicator", ("roll-on", "stick", "spray", "gel")),
        (
            "deodorant",
            "scent",
            ("unscented", "citrus", "sandalwood", "aloe vera", "sea breeze", "cedarwood"),
        ),  # fmt: skip
        (
            "nail_polish",
            "finish",
            ("gloss", "matte", "shimmer", "glitter", "metallic", "gel effect"),
        ),  # fmt: skip
        ("nail_polish", "wear", ("quick dry", "long wear", "chip resistant", "strengthening")),
    ],
)
def test_each_param_value_draws_its_own_figure(shape, key, values) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    drawn = {kit.render(shape, fill, label="Deodorant", params={key: v}) for v in values}
    assert len(drawn) == len(values)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_style_draws_the_values_its_title_shows(beauty, ptype) -> None:
    """A derived style's drawing params are its own attribute values, so a style that states
    ``Micellar`` or ``Glitter`` draws it (gen#512)."""
    mine = [r for r in beauty if r["product_type"] == ptype]
    assert mine
    for r in mine:
        attrs = {a["key"]: str(a["value"]).lower() for a in r["attributes"]}
        params = r["drawing"]["params"]
        assert r["drawing"]["shape"] == KEYS[ptype], r["product_id"]
        assert {k: attrs[k] for k in params if k in attrs} == {
            k: v for k, v in params.items() if k in attrs}, r["product_id"]  # fmt: skip


def _golden(beauty: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in beauty if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each new type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Facial Cleanser": [
        ("BRD-01091CA80AD2", "Belworth Balm Facial Cleanser for Sensitive Skin", 3, 7.5),
        ("BRD-01A0556C1684", "Ramford Gel Facial Cleanser for Normal Skin", 3, 13.0),
        ("BRD-025B74640728", "Cudwood Micellar Facial Cleanser for Oily Skin", 3, 14.5),
    ],
    "Deodorant": [
        ("BRD-002CDCB0B79D", "Elmshaw Citrus Antiperspirant Stick Deodorant", 3, 3.5),
        ("BRD-005232EC9A8D", "Dalridge Cedarwood Gel Deodorant", 3, 6.5),
        ("BRD-009991C4F3B3", "Dewgarth Aloe Vera Antiperspirant Gel Deodorant", 3, 3.55),
    ],
    "Nail Polish": [
        ("BRD-0228319F8005", "Brammouth Quick Dry Glitter Nail Polish", 12, 4.55),
        ("BRD-03E143F006E7", "Wathwood Long Wear Glitter Nail Polish", 6, 6.5),
        ("BRD-03F50BB6BF13", "Stavwick Quick Dry Gel Effect Nail Polish", 9, 6.5),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(beauty, ptype) -> None:
    assert _golden(beauty, ptype) == GOLDEN[ptype]
