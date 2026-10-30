"""TVs, volt meters and five invented brands that cross departments (#721).

The issue's table is the row test: each brand holds each of its types. ``real_brands.check`` and
the ``tv`` ranking run over the ceiling build, the whole catalogue, not the templates alone.
"""

from __future__ import annotations

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    baseline_rank,
    house_styles,
    kit,
    main_colors,
    real_brands,
    scale,
)

TV_NODE = ("Electronics", "TVs")
VOLT_METER_NODE = ("Home", "DIY & Tools", "Volt Meters")
TV = "TV"
VOLT_METER = "Volt Meter"
FRIDGE = "Fridge & Freezer"
WASHING_MACHINE = "Washing Machine"
PHONE = "Smartphone"
LAPTOP = "Laptop"
DESKTOP = "Desktop Computer"
MONITOR = "Monitor"

TABLE = {
    "Grape Computer": {LAPTOP, DESKTOP},
    "GoodLook": {TV, WASHING_MACHINE, FRIDGE},
    "SingingSam": {TV, WASHING_MACHINE, FRIDGE, PHONE, LAPTOP},
    "PackingHarder": {MONITOR, DESKTOP, LAPTOP, VOLT_METER},
    "Xell": {DESKTOP, LAPTOP},
}
#: The metric's four families.
FAMILY = {
    PHONE: "phones", "Basic Phone": "phones",
    LAPTOP: "computers", DESKTOP: "computers",
    TV: "tvs",
    FRIDGE: "appliances", WASHING_MACHINE: "appliances",
}  # fmt: skip
SLUG = {b: b.lower().replace(" ", "_") for b in TABLE}


def _kind(doc: dict) -> str:
    """The table's word for a document: a laundry appliance is its kind, not its product type."""
    if doc["product_type"] == "Laundry Appliance":
        return next(a["value"] for a in doc["attributes"] if a["key"] == "appliance_type")
    return doc["product_type"]


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return ceiling_build().records


@pytest.mark.parametrize("brand", TABLE, ids=SLUG.get)
def test_each_brand_holds_each_type_of_the_table(templates, brand):
    held = {_kind(d) for d in templates if d["brand"] == brand}
    assert held >= TABLE[brand], f"{brand} lacks {sorted(TABLE[brand] - held)}"


@pytest.mark.parametrize("brand", TABLE, ids=SLUG.get)
def test_each_brand_has_a_house_style_with_its_own_mark(brand):
    style = house_styles.HOUSE_STYLES.get(brand)
    assert style is not None, brand
    assert style.mark != house_styles.NO_MARK, "an invented brand draws its mark"


def test_tvs_and_volt_meters_are_nodes_of_the_tree(templates):
    paths = {tuple(d["category_path"]) for d in templates}
    assert {TV_NODE, VOLT_METER_NODE} <= paths


def test_every_tv_and_volt_meter_sits_in_its_node(templates):
    for doc in templates:
        if doc["product_type"] == TV:
            assert tuple(doc["category_path"]) == TV_NODE, doc["title"]
        if doc["product_type"] == VOLT_METER:
            assert tuple(doc["category_path"]) == VOLT_METER_NODE, doc["title"]


def test_a_tv_comes_only_in_its_four_frame_colors(templates):
    tvs = [doc for doc in templates if doc["product_type"] == TV]
    assert main_colors.offered(tvs) == {"Black", "Grey", "Silver", "White"}


def test_at_least_three_of_the_five_brands_span_two_families(templates):
    """The issue's metric, over the five brands: Halvern and its peers already span phones and
    computers, so counting every brand would pass before this change."""
    spans: dict[str, set[str]] = {b: set() for b in TABLE}
    for doc in templates:
        family = FAMILY.get(_kind(doc))
        if family and doc["brand"] in spans:
            spans[doc["brand"]].add(family)
    assert sum(len(f) >= 2 for f in spans.values()) >= 3, spans


def test_the_tv_drawing_changes_with_its_form():
    fill = kit.Fill("solid", "#2d2d33")
    assert kit.render("tv", fill, params={"form": "flat"}) != kit.render(
        "tv", fill, params={"form": "curved"}
    )


def test_the_volt_meter_drawing_changes_with_its_form():
    fill = kit.Fill("solid", "#f2c230")
    assert kit.render("volt_meter", fill, params={"form": "handheld"}) != kit.render(
        "volt_meter", fill, params={"form": "clamp"}
    )


def test_a_volt_meter_is_found_by_its_one_word_spelling(ceiling):
    index = baseline_rank.Index(ceiling)
    top = baseline_rank.rank(index, "voltmeter", 12, popular=False)
    assert top, "no document holds the word voltmeter"
    assert {d["product_type"] for d in top} == {VOLT_METER}


def test_real_brands_check_passes_on_the_whole_build(ceiling):
    assert real_brands.check(ceiling) == []
    assert {d["brand"] for d in ceiling} >= set(TABLE)


def test_tv_ranks_the_tv_node_in_the_top_12_of_the_build(ceiling):
    index = baseline_rank.Index(ceiling)
    top = baseline_rank.rank(index, "tv", 12)
    assert len(top) == 12
    assert [tuple(d["category_path"]) for d in top] == [TV_NODE] * 12
