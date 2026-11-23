"""The phone range (gen#1117): invented handsets, and accessories that name the model they fit.

Pinned from the issue: new smartphones in storage, color, screen size and an unlocked or carrier
SKU axis; a case and a screen protector per model whose ``compatible_with`` is that model's
``model_line``; more chargers, cables and car mounts; about +1,200 SKUs over the issue's count;
and the demo query "case for <model>", which only that model's cases answer while the cases of
the next model in its family are the near misses.
"""

from __future__ import annotations

import collections
import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import phone_range_rows, scale

DOC = (Path(__file__).resolve().parents[1] / "docs" / "retail-electronics.md").read_text(
    encoding="utf-8"
)
#: The issue's count on the served index (2026-11-21), by product type.
BEFORE = {
    "Smartphone": 265,
    "Phone Case": 89,
    "Screen Protector": 21,
    "Charger": 35,
    "Cable": 88,
    "Phone Mount": 52,
}
#: The issue's target is about +1,200; the range may land within this band.
ADDED_BAND = (1000, 1500)
CASE_STYLES = {"Clear", "Rugged", "Wallet"}
FINISHES = {"Clear", "Matte", "Privacy"}
#: The demo model: its family holds "Halvern Arc 6 Pro" (the near-miss cases) and "Halvern Arc 5".
DEMO_MODEL = "Halvern Arc 6"


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _attrs(d: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in d["attributes"]}


def _of(templates: list[dict], ptype: str) -> list[dict]:
    return [d for d in templates if d["product_type"] == ptype]


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def test_the_range_adds_about_1200_skus_over_the_issue_count(templates):
    skus = collections.Counter()
    for d in templates:
        skus[d["product_type"]] += d["sku_count"]
    added = sum(skus[t] - n for t, n in BEFORE.items())
    assert ADDED_BAND[0] <= added <= ADDED_BAND[1], added
    assert all(skus[t] > n for t, n in BEFORE.items()), skus


def test_every_new_phone_is_sold_by_storage_color_and_network_lock(templates):
    new = {f"BRD-{r.code}" for r in phone_range_rows.SMARTPHONES}
    phones = [d for d in _of(templates, "Smartphone") if d["product_id"] in new]
    assert len(phones) == len(new) >= 20
    for p in phones:
        assert {s["network_lock"] for s in p["skus"]} == {"Unlocked", "Carrier-locked"}, p["title"]
        assert len({s["storage_gb"] for s in p["skus"]}) >= 2
        assert len({s["color"] for s in p["skus"]}) >= 3
        assert {"model_line", "screen_size", "connectivity"} <= _attrs(p).keys()
        locked = min(s["price"] for s in p["skus"] if s["network_lock"] == "Carrier-locked")
        assert locked < min(s["price"] for s in p["skus"] if s["network_lock"] == "Unlocked")


def test_every_smartphone_model_line_is_unique_and_the_range_lists_them_all(templates):
    lines = [_attrs(d)["model_line"] for d in _of(templates, "Smartphone")]
    assert len(lines) == len(set(lines))
    assert set(phone_range_rows.MODEL_LINES) == set(lines)


def test_every_phone_has_each_case_style_and_each_protector_finish(templates):
    lines = {_attrs(d)["model_line"] for d in _of(templates, "Smartphone")}
    cases = collections.defaultdict(set)
    for c in _of(templates, "Phone Case"):
        cases[_attrs(c)["compatible_with"]].add(_attrs(c)["case_style"])
    shields = collections.defaultdict(set)
    for s in _of(templates, "Screen Protector"):
        shields[_attrs(s)["compatible_with"]].add(_attrs(s)["finish"])
    assert {line for line in lines if cases[line] < CASE_STYLES} == set()
    assert {line for line in lines if shields[line] < FINISHES} == set()


@pytest.mark.parametrize("ptype", ["Phone Case", "Screen Protector", "Charger"])
def test_compatible_with_names_a_model_line_of_the_build(templates, ptype):
    devices = _of(templates, "Smartphone") + _of(templates, "Tablet")
    lines = {_attrs(d)["model_line"] for d in devices}
    for d in _of(templates, ptype):
        fits = _attrs(d)["compatible_with"]
        assert fits in lines, (d["product_id"], fits)
        if d["product_id"].startswith(("BRD-ECR", "BRD-ESR", "BRD-ECG")):
            assert d["title"].endswith(f" for {fits}"), d["title"]


def test_the_demo_query_finds_the_models_cases_and_its_family_as_near_misses(templates):
    query = set(_words(f"case for {DEMO_MODEL}"))
    hits = [c for c in _of(templates, "Phone Case") if query <= set(_words(c["title"]))]
    right = [c for c in hits if _attrs(c)["compatible_with"] == DEMO_MODEL]
    near = {_attrs(c)["compatible_with"] for c in hits} - {DEMO_MODEL}
    assert {_attrs(c)["case_style"] for c in right} == CASE_STYLES
    assert "Halvern Arc 6 Pro" in near, "the next model's cases hold every word of the query"
    assert f'"case for {DEMO_MODEL}"' in DOC


def test_the_car_mounts_grow_and_the_cables_name_no_model(templates):
    mounts = {d["title"] for d in _of(templates, "Phone Mount")}
    assert any("Magnetic Wireless Charging Phone Mount" in t for t in mounts)
    new = {f"BRD-{r.code}" for r in phone_range_rows.CABLES_NEW}
    cables = [d for d in _of(templates, "Cable") if d["product_id"] in new]
    assert len(cables) == len(new) >= 6
    assert not [d for d in cables if "compatible_with" in _attrs(d)]
