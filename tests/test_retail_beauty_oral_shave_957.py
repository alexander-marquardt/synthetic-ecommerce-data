"""Beauty, slice 2 (gen#957): oral care and shaving, with toothbrushes, toothpaste and razors.

After slice 1 (#1000, hair care) main's ceiling build held 7,792 Beauty SKUs against the 500K
mix's 14,000, with no toothbrush, toothpaste or razor, so a search for ``toothbrush``,
``whitening toothpaste`` or ``5 blade razor`` found nothing, and Aftershave held three styles.
This slice adds three types, each a spec of its own (``type_specs/toothbrush.py``,
``toothpaste.py``, ``razor.py``) drawn by :mod:`kit_grooming`, and widens Aftershave by three
authored styles. These checks hold the slice's Done-when: the ceiling build has at least 9,150
Beauty SKUs; each new type's styles have unique ids, titles, twin keys and SKU ids; the rows and
their drawings are the same on every call; each title-shown value draws its own figure; and a
golden slice pins each new type's first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, kit_grooming, scale, type_registry

KEYS = {"Toothbrush": "toothbrush", "Toothpaste": "toothpaste", "Razor": "razor"}
TYPES = tuple(KEYS)
#: Each new type's leaf (the gate comment of gen#957).
PATHS = {
    "Toothbrush": ("Beauty", "Dental", "Toothbrushes"),
    "Toothpaste": ("Beauty", "Dental", "Toothpaste"),
    "Razor": ("Beauty", "Shaving", "Razors"),
}
#: The department the slice deepens.
DEPARTMENT = "Beauty"
#: The slice's floor at the ceiling build (the gate comment of gen#957).
FLOOR = 9_150


@pytest.fixture(scope="module")
def beauty() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == DEPARTMENT]


def test_the_ceiling_build_holds_the_slice_floor_of_beauty_skus(beauty) -> None:
    skus = sum(r["sku_count"] for r in beauty)
    assert skus >= FLOOR, skus


@pytest.mark.parametrize("ptype", TYPES)
def test_every_new_type_is_derived_under_its_own_leaf(beauty, ptype) -> None:
    derived = set(ceiling_build().template_of)
    mine = [r for r in beauty if r["product_type"] == ptype]
    assert any(r["product_id"] in derived for r in mine)
    assert {tuple(r["category_path"]) for r in mine} == {PATHS[ptype]}


def test_aftershave_is_widened_by_authored_styles_only() -> None:
    spec = type_registry.specs()["aftershave"]
    assert not spec.derivable
    assert len(spec.rows) >= 6
    families = {v for r in spec.rows for k, _, v in r.attrs if k == "fragrance_family"}
    assert len(families) >= 6, families


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


@pytest.mark.parametrize(
    ("shape", "key", "values"),
    [
        ("toothbrush", "power", ("manual", "electric", "sonic", "battery")),
        ("toothbrush", "bristle", tuple(kit_grooming.TUFT)),
        ("toothpaste", "benefit", ("whitening", "sensitive", "cavity protection", "gum care",
                                   "enamel repair", "fresh breath")),  # fmt: skip
        ("toothpaste", "flavour", tuple(kit_grooming.STRIPE)),
        ("razor", "blades", ("2-blade", "3-blade", "4-blade", "5-blade")),
        ("razor", "handle", ("rubber grip", "weighted", "slim", "ergonomic")),
    ],
)
def test_each_param_value_draws_its_own_figure(shape, key, values) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    drawn = {kit.render(shape, fill, label="Toothpaste", params={key: v}) for v in values}
    assert len(drawn) == len(values)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_style_draws_the_values_its_title_shows(beauty, ptype) -> None:
    """A derived style's drawing params are its own attribute values, so a style that states
    ``Sonic`` or ``5-Blade`` draws it (gen#512)."""
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
    "Toothbrush": [
        ("BRD-007BFC80AF6B", "Holley Firm Manual Toothbrush", 18, 2.75),
        ("BRD-00FBE1A18EE9", "Linholme Soft Battery Toothbrush", 9, 10.0),
        ("BRD-0404370786BF", "Halgate Soft Electric Toothbrush", 18, 8.0),
    ],
    "Toothpaste": [
        ("BRD-0036A75ADD44", "Yaringham Sensitive Herbal Toothpaste", 3, 4.4),
        ("BRD-010BCB2EF73F", "Townworth Cavity Protection Herbal Toothpaste", 3, 4.1),
        ("BRD-01CBEFB85181", "Hulhurst Cavity Protection Eucalyptus Toothpaste", 3, 4.75),
    ],
    "Razor": [
        ("BRD-01F28475B2DB", "Tidstead Ergonomic 3-Blade Razor", 18, 9.0),
        ("BRD-04CB51D2C187", "Belwick Weighted 2-Blade Razor", 15, 14.5),
        ("BRD-0A0D84A23618", "Skelhill Rubber Grip 4-Blade Razor", 18, 4.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(beauty, ptype) -> None:
    assert _golden(beauty, ptype) == GOLDEN[ptype]
