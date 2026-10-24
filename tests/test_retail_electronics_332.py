"""The Electronics department (gen#332): phones, computers, tablets and their accessories.

Pinned from the issue and the maintainer's two rulings (2026-10-15): the only real names are Apple,
iPhone and iPad (text only, no logo); every other brand is invented; the accessories keep invented
brands and name the phone they fit, which is true and is the model-word decoy; the department
ships cross-department word decoys
("mouse", "tablet", "monitor", "mobile", "charger", "apple") as class 8 rows.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_product_words  # noqa: E402
import kit  # noqa: E402
import real_brands  # noqa: E402
import scale  # noqa: E402

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
    import departments

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


def test_the_only_real_names_are_apple_iphone_and_ipad():
    assert {"Apple", "iPhone", "iPad"} <= set(real_brands.ALLOWED)
    docs = [{"product_id": "x", "brand": "Samsung", "title": "Galaxy S24 phone", "description": ""}]
    assert real_brands.check(docs), "Samsung stays refused"
    for name in ("Xiaomi", "Motorola", "OnePlus", "Oppo", "Asus", "Acer", "Huawei"):
        assert real_brands.check([{"product_id": "x", "brand": name}]), name


def test_the_department_names_no_real_brand_but_apple(electronics):
    assert real_brands.check(electronics) == []
    brands = collections.Counter(d["brand"] for d in _devices(electronics))
    assert brands["Apple"] >= 8
    assert sum(1 for b in brands if b != "Apple") >= 8, "the other brands are invented"


def test_apple_devices_carry_the_public_line_names(electronics):
    titles = [d["title"] for d in electronics if d["brand"] == "Apple"]
    assert sum("iPhone" in t for t in titles) >= 5
    assert sum("iPad" in t for t in titles) >= 3
    assert not [t for t in titles if re.search(r"MacBook|iMac|Mac mini", t)]


def test_an_accessory_names_the_phone_it_fits_and_has_an_invented_brand(electronics):
    cases = [d for d in electronics if d["category_leaf"] == "Phone Cases"]
    assert len(cases) >= 10
    phones = [d for d in electronics if d["category_path"][-1] == "Smartphones"]
    lines = {_attrs(d)["model_line"] for d in phones}
    for c in cases:
        fits = _attrs(c)["compatible_with"]
        assert fits in lines, c["product_id"]
        assert fits in c["title"], "the title names the phone line: the model-word decoy"
        assert c["brand"] != "Apple"
    assert len({_attrs(c)["compatible_with"] for c in cases}) >= 8


def test_a_model_line_query_matches_more_accessories_than_phones(electronics):
    line = "iPhone 15"
    hits = [d for d in electronics if line.lower() in d["title"].lower()]
    phones = [d for d in hits if d["category_path"][-1] == "Smartphones"]
    assert phones, "the phone itself is found"
    assert len(hits) - len(phones) >= 3, "its cases, protectors and chargers hold the same words"


def test_the_apple_devices_have_apple_clashes_across_departments():
    rows = {r.code: r for r in decoy_product_words.TABLE}
    queries = {r.query for r in rows.values()}
    assert "apple" in queries or any("apple" in q for q in queries)
    apple = [
        r for r in rows.values() if "apple" in r.query and r.device_type in {"Smartphone", "Tablet"}
    ]
    assert len(apple) >= 3, "juice, tree and candle clash with the devices"


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


def test_the_devices_have_drawings_and_the_brand_is_text_only(electronics):
    for shape in ("smartphone", "laptop", "tablet", "phone_case", "earbuds", "monitor"):
        assert shape in kit.SHAPES, shape
    apple = next(d for d in electronics if d["brand"] == "Apple")
    assert "Apple" not in str(apple["drawing"]), "no mark, no wordmark"


def test_the_doc_records_the_rulings():
    assert "## Real names (Apple, iPhone, iPad only)" in NOTE
    assert "maybe we should only allow apple and iphone as exceptions" in NOTE
