"""The Electronics department (gen#332): phones, computers, tablets and their accessories.

Pinned from the issue and the maintainer's ruling of 2026-10-30 (gen#720): every brand is invented;
the accessories keep their own brands and name the phone they fit, which is true and is the
model-word decoy; the department ships cross-department word decoys
("mouse", "tablet", "monitor", "mobile", "charger") as class 8 rows.
"""

from __future__ import annotations

import collections
import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import (
    decoy_product_words,
    kit,
    real_brands,
    scale,
)

NOTE = (Path(__file__).resolve().parents[1] / "docs" / "retail-electronics.md").read_text(
    encoding="utf-8"
)
DEVICE_NODES = {
    ("Electronics", "Phones", "Smartphones"),
    ("Electronics", "Phones", "Basic Phones"),
    ("Electronics", "Computers", "Laptops"),
    ("Electronics", "Computers", "Desktops"),
    ("Electronics", "Tablets", "Tablets"),
    ("Electronics", "Tablets", "E-readers"),
}
ACCESSORY_LEAVES = {
    "Phone Cases", "Screen Protectors", "Chargers", "Cables", "Earbuds", "Laptop Sleeves",
    "Mice", "Keyboards", "Monitors",
}  # fmt: skip


@pytest.fixture(scope="module")
def electronics() -> list[dict]:
    return [d for d in scale.templates() if d["category_path"][0] == "Electronics"]


def _attrs(d: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in d["attributes"]}


def _devices(docs: list[dict]) -> list[dict]:
    return [d for d in docs if tuple(d["category_path"]) in DEVICE_NODES]


def _accessories(docs: list[dict]) -> list[dict]:
    return [d for d in docs if d["category_path"][1] == "Accessories"]


def test_the_department_is_on_the_closed_list_and_holds_every_node_of_the_issue(electronics):
    from synthetic_ecommerce_data.domains.retail import departments

    assert "Electronics" in departments.DEPARTMENTS
    assert {tuple(d["category_path"]) for d in electronics} >= DEVICE_NODES
    assert {d["category_leaf"] for d in _accessories(electronics)} >= ACCESSORY_LEAVES


def test_at_least_60_devices_and_80_accessories_in_distinct_products(electronics):
    assert len(_devices(electronics)) >= 60
    assert len(_accessories(electronics)) >= 80
    assert len({d["product_id"] for d in electronics}) == len(electronics)


def test_a_smartphone_states_its_structured_attributes_and_sells_by_storage_and_color(electronics):
    phones = [d for d in electronics if d["category_path"][-1] == "Smartphones"]
    assert len(phones) >= 20
    for p in phones:
        attrs = _attrs(p)
        assert {"model_line", "operating_system", "connectivity"} <= set(attrs), p["product_id"]
        storages = {s["storage_gb"] for s in p["skus"]}
        assert storages and {int(s) for s in storages} <= {64, 128, 256, 512}
        assert len({s["color"] for s in p["skus"]}) >= 2


def test_a_laptop_sells_by_ram_storage_and_screen_and_a_desktop_by_ram_and_storage(electronics):
    for leaf, fields in (("Laptops", {"ram_gb", "storage_gb", "screen_size_in"}),
                         ("Desktops", {"ram_gb", "storage_gb"})):  # fmt: skip
        docs = [d for d in electronics if d["category_path"][-1] == leaf]
        assert len(docs) >= 8, leaf
        for d in docs:
            assert fields <= set(d["skus"][0]), d["product_id"]


def test_the_other_device_makers_are_refused():
    docs = [{"product_id": "x", "brand": "Samsung", "title": "Galaxy S24 phone", "description": ""}]
    assert real_brands.check(docs), "Samsung stays refused"
    for name in ("Xiaomi", "Motorola", "OnePlus", "Oppo", "Asus", "Acer", "Huawei"):
        assert real_brands.check([{"product_id": "x", "brand": name}]), name


def test_the_department_names_no_real_brand(electronics):
    assert real_brands.check(electronics) == []
    brands = collections.Counter(d["brand"] for d in _devices(electronics))
    assert brands["Grape Computer"] >= 8
    assert sum(1 for b in brands if b != "Grape Computer") >= 8, "a device has many makers"


def test_grape_computer_devices_carry_the_line_names(electronics):
    titles = [d["title"] for d in electronics if d["brand"] == "Grape Computer"]
    assert sum("GrapePhone" in t for t in titles) >= 5
    assert sum("GrapePad" in t for t in titles) >= 3
    assert not [t for t in titles if re.search(r"MacBook|iMac|Mac mini", t)]


def test_an_accessory_names_the_phone_it_fits_and_has_an_invented_brand(electronics):
    cases = [d for d in electronics if d["category_leaf"] == "Phone Cases"]
    assert len(cases) >= 10
    phones = [d for d in electronics if d["category_path"][-1] == "Smartphones"]
    tablets = [d for d in electronics if d["category_path"][-1] == "Tablets"]
    lines = {_attrs(d)["model_line"] for d in phones + tablets}
    for c in cases:
        fits = _attrs(c)["compatible_with"]
        assert fits in lines, c["product_id"]
        assert fits in c["title"], "the title names the phone line: the model-word decoy"
    assert len({_attrs(c)["compatible_with"] for c in cases}) >= 8


def test_a_model_line_query_matches_more_accessories_than_phones(electronics):
    line = "GrapePhone 15"
    hits = [d for d in electronics if line.lower() in d["title"].lower()]
    phones = [d for d in hits if d["category_path"][-1] == "Smartphones"]
    assert phones, "the phone itself is found"
    assert len(hits) - len(phones) >= 3, "its cases, protectors and chargers hold the same words"


@pytest.mark.parametrize(
    ("word", "target"),
    [
        ("mouse", "Computer Mouse"),
        ("tablet", "Tablet"),
        ("monitor", "Monitor"),
        ("mobile", "Smartphone"),
        ("charger", "Charger"),
    ],
)
def test_each_cross_department_word_has_at_least_three_class_8_decoys(word, target):
    rows = [r for r in decoy_product_words.TABLE
            if r.device_type == target and word in r.query and r.cross]  # fmt: skip
    assert len(rows) >= 3, f"{word}: {len(rows)}"


def test_the_color_decoys_say_one_color_and_draw_another(electronics):
    glow = [d for d in electronics if "Blue Glow" in d["title"]]
    assert glow, "a Blue Glow keyboard that is white"
    assert {s["color"] for s in glow[0]["skus"]} == {"White"}


def test_the_devices_have_drawings():
    for shape in ("smartphone", "laptop", "tablet", "phone_case", "earbuds", "monitor"):
        assert shape in kit.SHAPES, shape


def test_the_doc_records_the_rulings():
    assert "## Every brand is invented (gen#720)" in NOTE
    assert "which is now GrapePhone" in NOTE
