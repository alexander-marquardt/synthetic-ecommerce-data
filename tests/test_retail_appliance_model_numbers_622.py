"""Large appliances (gen#622): a series belongs to one brand, a model number is one product.

Every large appliance leads its title with its brand, then the series, then the brand's model
number, then the spec and the kind: "Frostholm Arden FW712DW 7kg 1200 Spin Washing Machine". The
model number is a letter-and-digit code the brand's scheme builds from the kind, the capacity,
the spin speed, the generation and the color; a color variant changes only the last letter. A few
washing machines carry the second title form, "Washing Machine from Frostholm, Model FW712DW".
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import appliance_model_numbers as amn  # noqa: E402
import large_appliance_rows as lar  # noqa: E402
import scale  # noqa: E402

ROOT = ["Home", "Large Appliances"]
#: the attribute holding each kind's capacity: a load, litres, or place settings
CAPACITY_KEYS = ("load", "capacity", "place_settings")
FROM_FORM = re.compile(r"^(?P<kind>.+) from (?P<brand>.+), Model (?P<code>[A-Z0-9-]+)$")


@pytest.fixture(scope="module")
def appliances() -> list[dict]:
    return [r for r in scale.templates() if r["category_path"][:2] == ROOT]


def _attrs(record: dict) -> dict[str, str]:
    return {a["key"]: a["value"] for a in record["attributes"]}


def test_the_worked_example_decodes_to_a_frostholm_seven_kilo_white_washing_machine():
    assert amn.decode("FW712DW") == {
        "brand": "Frostholm", "kind": "Washing Machine", "capacity": 7, "spin": 1200,
        "generation": "D", "color": "White",
    }  # fmt: skip
    assert amn.encode("Frostholm", "Washing Machine", 7, 1200, "D", "White") == "FW712DW"


@pytest.mark.parametrize("brand", lar.BRANDS)
def test_each_brand_builds_its_own_codes_and_reads_them_back(brand):
    code = amn.encode(brand, "Washing Machine", 10, 1400, "C", "Black")
    assert code.startswith(amn.SCHEMES[brand].lead)
    assert amn.decode(code) == {
        "brand": brand, "kind": "Washing Machine", "capacity": 10, "spin": 1400,
        "generation": "C", "color": "Black",
    }  # fmt: skip


def test_the_brands_do_not_share_a_prefix_scheme():
    codes = {b: amn.encode(b, "Larder Fridge", 290, 0, "B", "White") for b in lar.BRANDS}
    assert len(set(codes.values())) == len(lar.BRANDS), codes
    assert len({amn.SCHEMES[b].lead for b in lar.BRANDS}) == len(lar.BRANDS)


def test_every_large_appliance_names_a_series(appliances):
    assert all(r.get("product_line") for r in appliances), [
        r["title"] for r in appliances if not r.get("product_line")
    ]


def test_a_series_belongs_to_exactly_one_brand_across_every_kind(appliances):
    brands = defaultdict(set)
    for r in appliances:
        brands[r.get("product_line")].add(r["brand"])
    assert None not in brands
    shared = {s: b for s, b in brands.items() if len(b) > 1}
    assert not shared, shared


def test_a_series_spans_more_than_one_kind(appliances):
    kinds = defaultdict(set)
    for r in appliances:
        kinds[r.get("product_line")].add(_attrs(r)["appliance_type"])
    assert None not in kinds
    assert max(len(k) for k in kinds.values()) > 1


def test_every_title_starts_with_its_brand_or_reads_kind_from_brand_model_code(appliances):
    for r in appliances:
        m = FROM_FORM.match(r["title"])
        if m:
            assert m["brand"] == r["brand"], r["title"]
        else:
            assert r["title"].startswith(f"{r['brand']} "), r["title"]


def test_a_title_reads_brand_series_model_number_spec_then_kind(appliances):
    plain = [r for r in appliances if not FROM_FORM.match(r["title"])]
    assert len(plain) >= len(appliances) - 6
    for r in plain:
        head = f"{r['brand']} {r.get('product_line')} {_attrs(r).get('model_number')} "
        assert r["title"].startswith(head), r["title"]
        assert len(r["title"]) > len(head)


def test_the_washing_machine_title_carries_capacity_and_spin_speed():
    washer = next(r for r in scale.templates() if r["product_id"] == "BRD-LWM001")
    a = _attrs(washer)
    assert f"{a['load']}kg {a['spin_rpm']} Spin Washing Machine" in washer["title"], washer["title"]


def test_a_few_washing_machines_use_the_from_brand_title_form(appliances):
    forms = [r for r in appliances if FROM_FORM.match(r["title"])]
    assert 1 <= len(forms) <= 4, [r["title"] for r in forms]
    for r in forms:
        m = FROM_FORM.match(r["title"])
        assert m["kind"] == "Washing Machine"
        assert m["code"] == _attrs(r)["model_number"]
        assert r["product_type"] == "Laundry Appliance"


def test_every_large_appliance_has_a_model_number_that_decodes_to_its_own_attributes(appliances):
    for r in appliances:
        a = _attrs(r)
        got = amn.decode(a.get("model_number", ""))
        assert got is not None, (r["title"], a.get("model_number"))
        cap = next(a[k] for k in CAPACITY_KEYS if k in a)
        assert got["brand"] == r["brand"], r["title"]
        assert got["kind"] == a["appliance_type"], r["title"]
        assert got["capacity"] == int(cap), r["title"]
        assert got["spin"] == int(a.get("spin_rpm", 0)), r["title"]
        assert got["generation"] == a["generation"], r["title"]
        assert got["color"] == r["color_options"][0]["color"], r["title"]


def test_the_base_model_is_the_model_number_without_its_color_letter(appliances):
    for r in appliances:
        a = _attrs(r)
        assert a["model_number"].startswith(a["base_model"]), r["title"]
        assert len(a["model_number"]) == len(a["base_model"]) + 1, r["title"]


def test_one_model_number_is_one_product_and_no_number_repeats_across_brands(appliances):
    owners = defaultdict(set)
    bases = defaultdict(set)
    for r in appliances:
        a = _attrs(r)
        owners[a["model_number"]].add(r["brand"])
        bases[a["base_model"]].add(r["product_id"])
    assert all(len(b) == 1 for b in owners.values()), owners
    assert all(len(p) == 1 for p in bases.values()), {k: p for k, p in bases.items() if len(p) > 1}
    assert len({r["product_id"] for r in appliances}) == len(bases)


def test_each_series_and_generation_is_its_own_attribute(appliances):
    for r in appliances:
        a = _attrs(r)
        assert re.fullmatch(r"[B-HJ-Z]", a.get("generation", "")), r["title"]
        assert "series" not in a, "the series is the top-level field; a key would shadow it"


def test_each_exported_sku_states_the_model_number_of_its_own_color(appliances):
    flat = scale.flat([scale.standard_document(r) for r in appliances])
    seen: dict[str, str] = {}
    for d in flat:
        a = {e["key"]: e["value"] for e in d["attributes"]}
        got = amn.decode(a.get("model_number", ""))
        assert got is not None, (d["sku"], a.get("model_number"))
        assert got["color"] == a["color"], (d["sku"], a["model_number"], a["color"])
        assert a["model_number"].startswith(a["base_model"]), d["sku"]
        assert seen.setdefault(a["model_number"], d["sku"]) == d["sku"], a["model_number"]
    assert len(flat) > len(appliances), "color variants are SKUs of their own"
