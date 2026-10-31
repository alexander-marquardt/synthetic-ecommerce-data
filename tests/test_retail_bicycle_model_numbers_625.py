"""Bicycle model numbers and short-titled accessory decoys (gen#625, in the scheme of gen#622).

Every bicycle leads its title with its brand, then the series, then the brand's model number,
then the spec and the bike: "Wrenfield Aero Elite RD28-18-26 28in 18 Speed Aluminum Road Bike". The
model number is built from the kind, the wheel inches, the gears and the model year, and decodes
back to the bike's own attributes. Next to the bikes sit accessories with short titles holding
``bicycle`` or ``bike``, each in its own Cycling leaf: on a plain BM25 match over the titles they
outrank the bikes, whose titles are longer.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import bicycle_model_numbers as bmn
from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail import (
    kit,
    scale,
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import OWNERS

CYCLING = ["Sports & Outdoors", "Cycling"]
BIKES = [*CYCLING, "Bikes"]
#: The accessory decoys of gen#625: product type -> its own Cycling leaf.
ACCESSORIES = {
    "Chain Lube": "Chain Lube",
    "Bike Bottle": "Bike Bottles",
    "Bike Saddle": "Bike Saddles",
    "Bike Pedals": "Bike Pedals",
    "Bike Helmet": "Bike Helmets",
}


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def bikes(templates) -> list[dict]:
    found = [r for r in templates if r["product_type"] == "Bicycle"]
    assert len(found) >= 4
    return found


@pytest.fixture(scope="module")
def accessories(templates) -> list[dict]:
    return [r for r in templates if r["product_type"] in ACCESSORIES]


def _attrs(record: dict) -> dict[str, str]:
    return {a["key"]: a["value"] for a in record["attributes"]}


# -- the scheme ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("args", "code"),
    [
        (("Wrenfield", "Road", 28, 18), "RD28-18-26"),
        (("Harbour & Pine", "Mountain", 29, 21), "HP26MT2921"),
        (("Larkmoor", "Electric", 28, 7), "LMEB-262807"),
        (("Wrenfield", "Kids", None, 1), "KD-01-26"),
        (("Gorsecliff", "Mountain", 29, 24), "GC26MT-29-24"),
        (("Rindlemoor", "Road", 28, 22), "RM-RD22-2826"),
        (("Tolvaney", "Road", 28, 18), "TV28RD18.26"),
        (("Ostlebury", "Electric", 26, 8), "OB08-EB26-26"),
        (("Wattlebrook", "Electric", 28, 7), "WBEB28.07.26"),
        (("Pipkinford", "Kids", None, 1), "PK-KD2601"),
        (("Hessenby", "Kids", None, 1), "HB26-01KD"),
    ],
)
def test_each_brand_builds_its_code_from_kind_wheel_gears_and_year(args, code):
    assert bmn.encode(*args) == code
    brand, kind, wheel, gears = args
    want = {"brand": brand, "kind": kind, "wheel": wheel, "gears": gears, "year": 2026}
    assert bmn.decode(code) == want


def test_only_a_kids_bike_leaves_the_wheel_out_of_its_code():
    with pytest.raises(ValueError):
        bmn.encode("Wrenfield", "Road", None, 18)
    with pytest.raises(ValueError):
        bmn.encode("Wrenfield", "Kids", 16, 1)


def test_a_code_no_scheme_builds_decodes_to_nothing():
    assert bmn.decode("RD28-18") is None
    assert bmn.decode("XX28-18-26") is None
    assert bmn.decode("KD28-01-26") is None  # a kids' code never carries a wheel


def _sold() -> list[tuple[str, str]]:
    """Every ``(brand, kind)`` the range sells."""
    return [(brand, kind) for brand, series in bmn.SERIES.items() for kind in series]


def test_the_same_bike_from_each_brand_gets_a_code_only_that_brand_builds():
    for kind in bmn.KINDS:
        wheel = None if kind == "Kids" else 28
        codes = {b: bmn.encode(b, kind, wheel, 18) for b, k in _sold() if k == kind}
        assert len(set(codes.values())) == len(codes)
        for brand, code in codes.items():
            assert bmn.decode(code)["brand"] == brand


def test_every_brand_round_trips_every_kind_it_sells_in_either_year():
    assert len(bmn.SCHEMES) == 10
    for brand, kind in _sold():
        for gears in (1, 8, 24):
            for year in (bmn.MODEL_YEAR, bmn.MODEL_YEAR - 1):
                wheel = None if kind == "Kids" else 29
                code = bmn.encode(brand, kind, wheel, gears, year)
                want = {"brand": brand, "kind": kind, "wheel": wheel, "gears": gears, "year": year}
                assert bmn.decode(code) == want


def test_a_brand_refuses_a_kind_it_does_not_sell():
    with pytest.raises(ValueError):
        bmn.encode("Wattlebrook", "Road", 28, 18)
    assert bmn.decode("WBRD28.18.26") is None


def test_each_scheme_has_lead_letters_of_its_own():
    leads = [s.split("{")[0].rstrip("-") for s in bmn.SCHEMES.values()]
    named = [lead for lead in leads if lead]
    assert len(named) == len(set(named)) == len(bmn.SCHEMES) - 1  # Wrenfield leads with the kind
    assert not set(named) & set(bmn.KINDS.values())


def test_a_series_name_belongs_to_one_brand():
    names = [s for series in bmn.SERIES.values() for s in series.values()]
    assert len(names) == len(set(names))
    assert all(set(series) <= set(bmn.KINDS) for series in bmn.SERIES.values())


def test_each_new_brand_has_a_house_style_and_a_mark_of_its_own():
    new = set(bmn.SERIES) - {"Wrenfield", "Harbour & Pine", "Larkmoor"}
    assert len(new) == 7
    marks = [hs.HOUSE_STYLES[brand].mark for brand in new]
    assert hs.NO_MARK not in marks
    assert len(set(marks)) == len(new)


def test_each_new_brand_is_another_houses_make():
    new = set(bmn.SERIES) - {"Wrenfield", "Harbour & Pine", "Larkmoor"}
    assert {OWNERS[brand] for brand in new} == {"third_party"}


def test_the_spec_names_wheel_and_speed():
    assert bmn.spec(18, 28) == "28in 18 Speed"
    assert bmn.spec(1, None) == "Single Speed"


# -- the bicycle rows ---------------------------------------------------------------------------


def test_every_bicycle_title_holds_its_model_number_after_brand_and_series(bikes):
    for r in bikes:
        a = _attrs(r)
        code = a["model_number"]
        assert r["title"].startswith(f"{r['brand']} {r['product_line']} {code} "), r["title"]


def test_every_model_number_decodes_to_the_bikes_own_attributes(bikes):
    for r in bikes:
        a = _attrs(r)
        got = bmn.decode(a["model_number"])
        assert got is not None, a["model_number"]
        assert got["brand"] == r["brand"]
        assert got["kind"] == a["bike_type"]
        assert got["gears"] == int(a["gears"])
        assert got["year"] == int(a["model_year"])
        assert got["wheel"] == (int(a["wheel_size"]) if "wheel_size" in a else None)
        assert r["product_line"] == bmn.series_for(r["brand"], a["bike_type"])


def test_no_model_number_repeats_and_every_sku_carries_its_bikes_code(bikes):
    codes = [_attrs(r)["model_number"] for r in bikes]
    assert len(codes) == len(set(codes))
    for r in bikes:
        assert {s["model_number"] for s in r["skus"]} == {_attrs(r)["model_number"]}


# -- the accessory decoys -----------------------------------------------------------------------


def test_each_accessory_decoy_says_bicycle_or_bike_and_sits_outside_bikes(accessories):
    types = {r["product_type"] for r in accessories}
    assert types == set(ACCESSORIES)
    for r in accessories:
        words = r["title"].lower().split()
        assert "bicycle" in words or "bike" in words, r["title"]
        assert r["category_path"] == [*CYCLING, ACCESSORIES[r["product_type"]]], r["category_path"]
        assert r["category_path"][: len(BIKES)] != BIKES
        assert "model_number" not in _attrs(r)


def test_each_accessory_is_drawn_as_its_own_shape(accessories):
    for r in accessories:
        assert r["drawing"]["shape"] in kit.SHAPES
        assert r["drawing"]["shape"] != "bicycle"


@pytest.mark.parametrize("shape", ["chain_lube", "bike_bottle", "bike_saddle", "bike_pedals"])
def test_each_accessory_shape_draws_every_style(shape):
    from synthetic_ecommerce_data.domains.retail import kit_cycling

    styles = {
        "chain_lube": ("drip", "spray"),
        "bike_bottle": ("squeeze", "insulated"),
        "bike_saddle": ("road", "comfort"),
        "bike_pedals": ("flat", "clipless"),
    }[shape]
    draw = kit_cycling.SHAPES[shape]
    drawn = {s: draw("#c8312e", kit.Fill(base="#c8312e"), None, style=s) for s in styles}
    assert all(drawn.values())
    assert drawn[styles[0]] != drawn[styles[1]]


# -- the decoy effect ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def cycling_index(templates) -> tuple[br.Index, list[dict]]:
    """The cycling templates plus every other title that holds the words, so raw BM25 over the
    titles runs on the same competition the full catalogue gives them."""
    return br.Index(templates), templates


def _title_ranking(index: br.Index, records: list[dict], query: str) -> list[dict]:
    words = br.tokens(query)
    scored = sorted(
        ((index._field_score("title", i, words), records[i]) for i in index.candidates(words)),
        key=lambda s: (-s[0], s[1]["product_id"]),
    )
    return [r for s, r in scored if s > 0] + [r for s, r in scored if s <= 0]


@pytest.mark.parametrize("query", ["bicycle", "bike"])
def test_three_accessory_decoys_outrank_the_first_bicycle_on_title_bm25(cycling_index, query):
    index, records = cycling_index
    ranking = _title_ranking(index, records, query)
    first_bike = next(i for i, r in enumerate(ranking) if r["product_type"] == "Bicycle")
    above = [r for r in ranking[:first_bike] if r["product_type"] in ACCESSORIES]
    assert len(above) >= 3, [r["title"] for r in ranking[: first_bike + 1]]


def test_a_full_model_number_finds_its_bike_first(cycling_index, bikes):
    index, _ = cycling_index
    for r in bikes:
        code = _attrs(r)["model_number"]
        assert br.rank(index, code, 1, popular=False)[0]["product_id"] == r["product_id"], code
