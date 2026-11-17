"""Electronics smart home, slice 2a (gen#956): smart plugs, smart bulbs and doorbell cameras.

The Electronics department held 1,166 SKUs at the ceiling build, against the 14,000 the 500K mix
plans (``docs/catalogue-mix-837.md``), and a shopper searching for a smart plug, a smart bulb or a
video doorbell found nothing. Slice 2a adds three derivable types under
``Electronics > Smart Home``, each a spec of its own (``type_specs/smart_plug.py``,
``smart_bulb.py``, ``doorbell_camera.py``) drawn by :mod:`kit_smart_home`.

These checks hold the slice's Done-when (the gate comment of gen#956). The three types add at
least 1,200 SKUs to the ceiling build on their own, so the slice holds whether or not slice 1
(audio) is merged first. Each type is sized between 350 and 900 SKUs: slices 2a, 2b and 3 share
the department's last 4,500 SKUs, so a type that grows past the band takes another type's share.
Each type's styles have unique ids, titles, SKUs and twin keys. The rows and their drawings are
the same on every call. A golden slice pins each type's first derived styles, so a change that
moves them shows here.

A smart bulb product is its brand, range, shape and fitting (the 2026-11-15 ruling on gen#1005:
every different product has a different picture). Each shape has its own outline, a shape is
derived only on a fitting it is sold on, and no two bulb products of one brand share a picture,
on the ceiling build and on a bulb-only build of seeds 0 to 5. The brand's own mark is drawn
from the brand, so the picture key is the leaf, the brand and the drawing spec.
"""

from __future__ import annotations

import collections
import copy
import json

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    export,
    kit,
    scale,
    smart_home_rows,
    type_registry,
)

TYPES = ("Smart Plug", "Smart Bulb", "Doorbell Camera")
KEYS = {
    "Smart Plug": "smart_plug",
    "Smart Bulb": "smart_bulb",
    "Doorbell Camera": "doorbell_camera",
}
#: What the slice adds at the ceiling build on its own (the gate comment of gen#956).
FLOOR = 1_200
#: Each type's share of the department's remaining SKUs: low, high.
BAND = (350, 900)


@pytest.fixture(scope="module")
def electronics() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == smart_home_rows.ROOT]


def _skus(electronics: list[dict], ptype: str) -> int:
    return sum(r["sku_count"] for r in electronics if r["product_type"] == ptype)


def test_the_slice_adds_its_floor_of_electronics_skus(electronics) -> None:
    added = sum(_skus(electronics, t) for t in TYPES)
    assert added >= FLOOR, added


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_holds_its_share_of_the_department(electronics, ptype) -> None:
    low, high = BAND
    assert low <= _skus(electronics, ptype) <= high, _skus(electronics, ptype)


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(electronics) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in electronics if r["product_id"] in derived}
    assert kinds >= set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_sits_under_smart_home(electronics, ptype) -> None:
    mine = [r for r in electronics if r["product_type"] == ptype]
    assert mine
    assert {tuple(r["category_path"][:2]) for r in mine} == {(smart_home_rows.ROOT, "Smart Home")}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(electronics, ptype) -> None:
    mine = [r for r in electronics if r["product_type"] == ptype]
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


#: Every bulb shape but the A60 the drawing defaults to.
OTHER_SHAPES = ("candle", "golf ball", "large globe", "reflector", "spot", "edison filament")


@pytest.mark.parametrize(
    ("shape", "param", "one", "other"),
    [
        ("smart_plug", "plug_form", "mini", "dual outlet"),
        ("smart_plug", "plug_form", "mini", "outdoor"),
        ("smart_bulb", "bulb_fitting", "e27", "gu10"),
        ("smart_bulb", "bulb_fitting", "e27", "b22"),
        *(("smart_bulb", "bulb_shape", "a60 standard", other) for other in OTHER_SHAPES),
        ("doorbell_camera", "doorbell_power", "battery", "wired"),
    ],
)
def test_a_param_changes_the_drawing(shape, param, one, other) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    assert kit.render(shape, fill, params={param: one}) != kit.render(
        shape, fill, params={param: other}
    )


def test_every_bulb_shape_has_its_own_outline() -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    shapes = [s.lower() for s in smart_home_rows.BULB_FITTINGS]
    drawn = {kit.render("smart_bulb", fill, params={"bulb_shape": s, "bulb_fitting": "e27"})
             for s in shapes if s != "spot"}  # fmt: skip
    assert len(drawn) == len(shapes) - 1


def _picture(r: dict) -> tuple:
    """A product's hero picture: its leaf, its brand (its mark) and its drawing spec."""
    spec = json.dumps(export.drawing_spec(r, r["skus"][0]), sort_keys=True)
    return (r["category_leaf"], r["brand"], spec)


def _shared_pictures(records: list[dict]) -> list[str]:
    bulbs = [r for r in records if r["product_type"] == "Smart Bulb"]
    seen = collections.Counter(_picture(r) for r in bulbs)
    return sorted(r["product_id"] for r in bulbs if seen[_picture(r)] > 1)


def _shapes_off_their_fittings(records: list[dict]) -> list[str]:
    out = []
    for r in records:
        if r["product_type"] != "Smart Bulb":
            continue
        values = {x["key"]: x["value"] for x in r["attributes"]}
        if values["bulb_fitting"] not in smart_home_rows.BULB_FITTINGS[values["bulb_shape"]]:
            out.append(r["product_id"])
    return out


def test_no_two_bulb_products_share_a_picture_at_the_ceiling(electronics) -> None:
    assert _shared_pictures(electronics) == []
    assert _shapes_off_their_fittings(electronics) == []


@pytest.mark.parametrize("seed", range(6))
def test_no_two_bulb_products_share_a_picture_on_any_seed(monkeypatch, seed) -> None:
    """A bulb-only build with every bulb template exhausted (as ``test_retail_stable_ids_626``)."""
    tpls = [t for t in scale.templates() if t["product_type"] == "Smart Bulb"]
    monkeypatch.setattr(scale, "templates", lambda baseline=True: copy.deepcopy(tpls))
    total = 10**6
    built = scale.build(total, seed=seed)
    derived = [r for r in built.records if r["product_id"] in built.template_of]
    assert len(derived) > 100, len(derived)
    assert _shared_pictures(built.records) == []
    assert _shapes_off_their_fittings(built.records) == []


def test_a_bulbs_skus_carry_its_light_connection_and_brightness(electronics) -> None:
    """Light, connection and brightness are SKU options; the brightness is one the shape has."""
    for r in (r for r in electronics if r["product_type"] == "Smart Bulb"):
        shape = next(x["value"] for x in r["attributes"] if x["key"] == "bulb_shape")
        for sku in r["skus"]:
            assert sku["bulb_light"] in smart_home_rows.LIGHT_WEIGHT, r["product_id"]
            assert sku["connectivity"] in smart_home_rows.LINK_WEIGHT, r["product_id"]
            assert int(sku["brightness_lm"]) in smart_home_rows.BULB_LUMENS[shape], r["product_id"]


def _golden(electronics: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in electronics
                   if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
#: Main's brand pool moved the range words in the window gen#962, gen#1007, gen#1010 and
#: gen#967 merged in; ids, SKU counts, prices are unchanged.
GOLDEN: dict[str, list[tuple]] = {  # fmt: skip
    "Smart Plug": [
        ("BRD-01793710EC8B", "Tidton Mini Zigbee Smart Plug", 2, 31.0),
        ("BRD-02062D564652", "Ravridge Mini Zigbee Smart Plug", 6, 16.5),
        ("BRD-065868823F3B", "Beling Mini Zigbee Smart Plug", 6, 37.0),
    ],
    "Smart Bulb": [
        ("BRD-0069548F2733", "Ryton Golf Ball Smart Bulb, E14 Fitting", 6, 8.0),
        ("BRD-05A7A8562577", "Eskshaw Spot Smart Bulb, GU10 Fitting", 6, 12.5),
        ("BRD-05DDC409DDB8", "Arking Large Globe Smart Bulb, B22 Fitting", 6, 15.0),
    ],
    "Doorbell Camera": [
        ("BRD-0284498502E6", "Ravmouth Video Doorbell Camera with Package Detection", 2, 140.0),
        ("BRD-066BF8907A5A", "Falfield Video Doorbell Camera with Night Vision", 6, 130.0),
        ("BRD-072A1FF1DEDA", "Norstead Wired Doorbell Camera with App Alerts", 6, 61.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(electronics, ptype) -> None:
    assert _golden(electronics, ptype) == GOLDEN[ptype]
