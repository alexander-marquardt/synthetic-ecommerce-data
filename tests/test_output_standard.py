"""Every domain's nested output meets the one output standard (gen#125).

:func:`synthetic_ecommerce_data.core.standard.check_catalog` is the validator. It
runs here over a fresh industrial build, the committed industrial golden and the
retail export (``prototypes/retail_drawings/export.py``), and against planted
defects so that a validator that passes everything is red too.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core import emit, standard
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.domains.industrial.generate import generate

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
GOLDEN_NESTED = ROOT / "golden-catalog" / "nested.jsonl"

#: The retail build's size: one document per style (``build_preview4.SAMPLES``).
RETAIL_DOCS = 328
RETAIL_SKUS = 6861


def _retail() -> list[dict[str, Any]]:
    if str(RETAIL) not in sys.path:
        sys.path.insert(0, str(RETAIL))
    import export  # noqa: PLC0415 -- the prototype's own directory is its import root

    return export.documents()


def _industrial() -> list[dict[str, Any]]:
    return list(emit.iter_nested(generate(SMALL)))


def _golden() -> list[dict[str, Any]]:
    with GOLDEN_NESTED.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


SOURCES = {
    "industrial fresh SMALL build": _industrial,
    "industrial committed golden nested.jsonl": _golden,
    "retail export": _retail,
}


@pytest.fixture(scope="module")
def retail() -> list[dict[str, Any]]:
    return _retail()


@pytest.mark.parametrize("source", sorted(SOURCES))
def test_every_domain_meets_the_standard(source):
    retail = source.startswith("retail")
    problems = standard.check_catalog(SOURCES[source](), text_agrees=retail)
    assert problems == [], f"{len(problems)} problems, e.g. {problems[:8]}"


def test_the_retail_export_keeps_every_style_and_sku(retail):
    assert len(retail) == RETAIL_DOCS
    assert sum(d["variant_count"] for d in retail) == RETAIL_SKUS


def test_retail_keeps_its_gbp_amount_and_states_the_currency(retail):
    variants = [v for d in retail for v in d["variants"]]
    assert {v["currency"] for v in variants} == {"GBP"}
    assert all("price_usd" not in v for v in variants)
    jeans = next(d for d in retail if d["product_id"] == "JEA-HARROW")
    assert jeans["variants"][0]["price"] == 32.0


def test_industrial_states_usd_beside_its_price_usd():
    for doc in _industrial()[:50]:
        for v in doc["variants"]:
            assert (v["price"], v["currency"], v["in_stock"]) == (
                v["price_usd"],
                "USD",
                v["stock"] > 0,
            )


def test_sku_options_are_variant_attributes(retail):
    jeans = next(d for d in retail if d["product_id"] == "JEA-HARROW")
    first = {e["key"]: e for e in jeans["variants"][0]["attributes"]}
    assert first["color"]["value"] == "Rinse"
    assert first["size_uk"]["value"] == "4"
    assert first["inside_leg_length"] == {
        "key": "inside_leg_length",
        "name": "Inside leg length",
        "value": "28",
        "unit_code": "INH",
        "value_canonical": 711.2,
    }


def test_department_options_offers_and_ratings_are_product_attributes(retail):
    keys = {e["key"] for d in retail for e in d["attributes"]}
    assert {"department", "color", "size_uk", "offer", "rating", "review_count"} <= keys
    dress = next(d for d in retail if d["product_id"] == "PLT-LEMDRS")
    entries = {(e["key"], e["value"]) for e in dress["attributes"]}
    assert {("department", "Clothing"), ("offer", "no"), ("rating", "4.1")} <= entries


def test_an_image_id_is_the_drawing_specs_and_stable(retail):
    again = _retail()
    assert [d["image_id"] for d in again] == [d["image_id"] for d in retail]
    jeans = next(d for d in retail if d["product_id"] == "JEA-HARROW")
    ids = {v["image_id"] for v in jeans["variants"]}
    # one drawing per wash: a size changes no picture
    assert len(ids) == len({e["value"] for e in jeans["attributes"] if e["key"] == "color"})
    assert jeans["image_id"].startswith("jeans/JEA-HARROW/")
    assert jeans["image_url"] == f"/images/retail/{jeans['image_id']}.svg"


def test_the_mapping_declares_exactly_the_standards_fields():
    props = emit.NESTED_MAPPING["mappings"]["properties"]
    assert set(props) == set(standard.PRODUCT_FIELDS)
    assert set(props["variants"]["properties"]) == set(standard.VARIANT_FIELDS)


PLANTS = {
    "an unmapped field": lambda d: d.update(offer=True),
    "no product_type": lambda d: d.pop("product_type"),
    "a leaf that is not the path's": lambda d: d.update(category_leaf="Elsewhere"),
    "a variant without currency": lambda d: d["variants"][0].pop("currency"),
    "a numeric in_stock": lambda d: d["variants"][0].update(in_stock=1),
    "a variant without image_url": lambda d: d["variants"][0].pop("image_url"),
    "a product image not its first variant's": lambda d: d.update(image_id="x/y/z"),
    "an entry with no key": lambda d: d["attributes"].append({"name": "N", "value": "v"}),
    "a unit with a wrong canonical": lambda d: d["attributes"].append(
        {"key": "k", "name": "K", "value": "2", "unit_code": "MMT", "value_canonical": 3.0}
    ),
    "a wrong variant_count": lambda d: d.update(variant_count=d["variant_count"] + 1),
}


@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_the_validator_refuses_each_planted_defect(plant, retail):
    doc = deepcopy(retail[0])
    assert standard.check_document(doc) == []
    PLANTS[plant](doc)
    assert standard.check_document(doc) != []


def _set(doc: dict[str, Any], key: str, value: str) -> None:
    for entry in doc["attributes"]:
        if entry["key"] == key:
            entry["value"] = value


#: A doc, an attribute changed under its text, the problem's words (gen#125 review).
CONTRADICTIONS = {
    # the old wording stays: "two hook and loop straps" on a lace-up trainer
    "a description naming another closure": ("FTW-KTRHLT", "closure", "Lace-Up", "'Hook & Loop'"),
    # the title and the description both name the old closure: one problem per attribute
    "a title naming another closure": ("FTW-KSNDHL", "closure", "Buckle", "'Hook & Loop'"),
}


@pytest.mark.parametrize("plant", sorted(CONTRADICTIONS))
def test_a_title_or_description_contradicting_an_attribute_is_refused(plant, retail):
    """The plant is a derived copy beside its template, as the scaled build makes one: the
    template keeps the old value in the leaf's pool."""
    pid, key, value, named = CONTRADICTIONS[plant]
    doc = _copy(next(d for d in retail if d["product_id"] == pid), "PLANT-1")
    _set(doc, key, value)
    problems = standard.check_catalog([*retail, doc])
    assert len(problems) == 1, problems
    assert problems[0].startswith("PLANT-1: ") and named in problems[0] and key in problems[0]


def _copy(doc: dict[str, Any], pid: str) -> dict[str, Any]:
    out = deepcopy(doc)
    out["product_id"] = pid
    for n, v in enumerate(out["variants"]):
        v["sku"] = f"{pid}-{n}"
    return out


def test_a_value_named_inside_another_attribute_or_beside_its_own_is_no_contradiction(retail):
    """ "Leather Penny Loafers" on a rubber sole names the upper's value; a text naming the
    doc's own value too ("cotton and linen") is a blend, not a contradiction."""
    shoe = _copy(next(d for d in retail if d["product_id"] == "FTW-KTRHLT"), "PLANT-1")
    _set(shoe, "closure", "Lace-Up")
    shoe["title"] = "Kids' Lace-Up Trainers"
    for v in shoe["variants"]:
        v["title"] = shoe["title"]
        v["description"] += " Laces sit under the straps: a lace-up look."
    loafer = next(d for d in retail if d["product_id"] == "FTW-WLOAFP")
    assert {"Leather Penny Loafers", "Rubber"} <= {loafer["title"], *_values(loafer, "sole")}
    assert standard.check_catalog([*retail, shoe]) == []


def _values(doc: dict[str, Any], key: str) -> list[str]:
    return [e["value"] for e in doc["attributes"] if e["key"] == key]


def test_industrial_text_is_exempt_from_the_contradiction_check():
    """Its descriptions name a second standard or grade by design (a Grade 8 nut for a
    Grade 5 bolt); the check guards the retail build's derived text."""
    docs = _industrial()
    assert standard.check_catalog(docs, text_agrees=False) == []
    assert standard.check_catalog(docs) != []


def test_a_repeated_sku_and_a_key_with_two_names_are_refused(retail):
    one, two = deepcopy(retail[0]), deepcopy(retail[1])
    two["variants"][0]["sku"] = one["variants"][0]["sku"]
    two["attributes"].append({"key": "color", "name": "Shade", "value": "Red"})
    problems = standard.check_catalog([one, two])
    assert any("is not unique" in p for p in problems)
    assert any("key 'color' names" in p for p in problems)
