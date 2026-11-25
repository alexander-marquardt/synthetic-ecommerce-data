"""Brand line-ups of the large appliances (#1116, round 4): the department at 1,700+ SKUs.

Each own brand sold one model of most kinds, so a brand could not be compared with itself. Every
own brand now sells every kind in at least four models that differ in what they state, and the
department holds the issue's target. The authored rows before them are untouched:
``AUTHORED_SAMPLES`` pins one model a product type, with its model number.
"""

from __future__ import annotations

from collections import defaultdict

import pytest

from synthetic_ecommerce_data.domains.retail import appliance_model_numbers as amn
from synthetic_ecommerce_data.domains.retail import large_appliance_rows as lar
from synthetic_ecommerce_data.domains.retail import scale

ROOT = ["Home", "Large Appliances"]
#: The parts of a model number; two models of one brand and kind differ in more than these.
CODES = {"model_number", "base_model", "generation", "line"}
AUTHORED_SAMPLES = {
    "BRD-LWM001": "Frostholm Arden FW712BW 7kg 1200 Spin Washing Machine",
    "BRD-FFA001": "Brimwell Fenner BRDB260W 260L 70/30 Fridge Freezer",
    "BRD-DWF001": "Hollinmere Selby HMOB12W 12 Place Full-Size Dishwasher",
    "BRD-RCD001": "Brimwell Heywood BRJD090B 90cm Dual Fuel Range Cooker",
    "BRD-OVS001": "Tavorne Ormond TVV-065EW 65L Built-in Single Oven",
    "BRD-HBI001": "Brimwell Garrow BRAC060B 60cm Induction Hob",
    "BRD-CHC001": "Tavorne Ormond TVM-060CS 60cm Chimney Cooker Hood",
}


@pytest.fixture(scope="module")
def appliances() -> list[dict]:
    return [r for r in scale.templates() if r["category_path"][:2] == ROOT]


def _attrs(record: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in record["attributes"]}


@pytest.fixture(scope="module")
def ranges(appliances) -> dict[tuple[str, str], list[dict]]:
    """(brand, kind) -> its models."""
    out: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in appliances:
        out[r["brand"], _attrs(r)["appliance_type"]].append(r)
    return out


def test_the_department_holds_the_target(appliances):
    assert sum(r["sku_count"] for r in appliances) >= 1700


def test_an_own_brand_sells_at_least_four_models_of_every_kind(ranges):
    held = {(b, k): len(ranges.get((b, k), ())) for b in lar.BRANDS for k in amn.KINDS}
    thin = {key: n for key, n in held.items() if n < 4}
    assert not thin, thin


def test_two_models_of_one_brand_and_kind_state_different_attributes(ranges):
    for (brand, kind), models in ranges.items():
        seen: dict[tuple, str] = {}
        for r in models:
            key = tuple(sorted((k, v) for k, v in _attrs(r).items() if k not in CODES))
            other = seen.setdefault(key, r["product_id"])
            assert other == r["product_id"], (brand, kind, other, r["product_id"])


def test_an_added_model_is_sold_on_a_feature_its_description_states(appliances):
    featured = [r for r in appliances if "feature" in _attrs(r)]
    assert len(featured) >= 500
    from synthetic_ecommerce_data.domains.retail import appliance_lineups as lineups

    for r in featured:
        words = dict(lineups.FEATURES[r["product_type"]])
        assert r["description"].endswith(f" It has {words[_attrs(r)['feature']]}."), r["title"]


def test_a_brand_keeps_its_place_in_the_market(ranges):
    """Brimwell's added models cost less than Lunden & Voss's, kind by kind."""
    for kind in amn.KINDS:
        mean = {}
        for brand in ("Brimwell", "Lunden & Voss"):
            models = ranges.get((brand, kind), ())
            added = [r["price"] for r in models if "feature" in _attrs(r)]
            assert added, (brand, kind)
            mean[brand] = sum(added) / len(added)
        assert mean["Brimwell"] < mean["Lunden & Voss"], (kind, mean)


def test_the_authored_rows_are_unchanged(appliances):
    titles = {r["product_id"]: r["title"] for r in appliances}
    assert {p: titles[p] for p in AUTHORED_SAMPLES} == AUTHORED_SAMPLES
