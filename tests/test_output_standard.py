"""Every domain's nested output meets the one output standard (gen#125).

:func:`synthetic_ecommerce_data.core.standard.check_catalog` is the validator. It
runs here over a fresh industrial build, the committed industrial golden and the
retail export (``prototypes/retail_drawings/export.py``), and against planted
defects so that a validator that passes everything is red too.
"""

from __future__ import annotations

import json
import subprocess
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
    problems = standard.check_catalog(SOURCES[source]())
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


def _add(row: dict[str, Any], **entry: Any) -> None:
    row["attributes"].append(entry)


def _other_image(doc: dict[str, Any]) -> str:
    """A drawing of this product that is not its first variant's."""
    first = doc["variants"][0]["image_id"]
    return next(v["image_id"] for v in doc["variants"] if v["image_id"] != first)


def _set_product_image(doc: dict[str, Any], image: str) -> None:
    url = f"{doc['image_url'].rsplit('/', 3)[0]}/{image}.svg"
    doc.update(image_id=image, image_url=url, image_detail_url=url)


#: One defect per plant: plant(doc) -> the one problem check_document reports, ``P``
#: the document's id and ``V`` its first variant's ``<id>/<sku>``. Each row is the
#: check it pins; removing that check turns the row red (the PR body's mutant run).
PLANTS: dict[str, tuple[Any, str]] = {
    "an unmapped field": (
        lambda d: d.update(offer=True),
        "P: 'offer' is not a field of the standard",
    ),
    "no product_type": (lambda d: d.pop("product_type"), "P: lacks 'product_type'"),
    "an empty brand": (lambda d: d.update(brand=""), "P: 'brand' is not a str: ''"),
    "a leaf that is not the path's": (
        lambda d: d.update(category_leaf="Elsewhere"),
        "P: category_leaf/category_depth do not match PATH",
    ),
    "a depth that is not the path's length": (
        lambda d: d.update(category_depth=d["category_depth"] + 1),
        "P: category_leaf/category_depth do not match PATH",
    ),
    "a variant without currency": (
        lambda d: d["variants"][0].pop("currency"),
        "V: lacks 'currency'",
    ),
    "a lowercase currency": (
        lambda d: d["variants"][0].update(currency="gbp"),
        "V: currency 'gbp' is not an ISO 4217 code",
    ),
    "a currency name, not its code": (
        lambda d: d["variants"][0].update(currency="Pounds"),
        "V: currency 'Pounds' is not an ISO 4217 code",
    ),
    "a zero price": (
        lambda d: d["variants"][0].update(price=0.0),
        "V: price 0.0 is not positive",
    ),
    "a numeric in_stock": (
        lambda d: d["variants"][0].update(in_stock=1),
        "V: 'in_stock' is not a bool: 1",
    ),
    "a variant without image_url": (
        lambda d: d["variants"][0].pop("image_url"),
        "V: lacks 'image_url'",
    ),
    "an image_url naming another product's image": (
        lambda d: d["variants"][0].update(image_url="/images/retail/jeans/JEA-OTHER/abc.svg"),
        "V: image_url '/images/retail/jeans/JEA-OTHER/abc.svg' is not IMAGE.svg",
    ),
    "a product image not its first variant's": (
        lambda d: _set_product_image(d, _other_image(d)),
        "P: image_id is not its first variant's",
    ),
    "an entry with no key": (
        lambda d: _add(d, name="N", value="v"),
        "P: entry key None is not ^[a-z0-9][a-z0-9_]*$",
    ),
    "an entry key with upper case and a space": (
        lambda d: _add(d, key="Fit Note", name="Fit note", value="v"),
        "P: entry key 'Fit Note' is not ^[a-z0-9][a-z0-9_]*$",
    ),
    "an entry with an empty value": (
        lambda d: _add(d, key="fit_note", name="Fit note", value=""),
        "P: entry 'fit_note' has no value string",
    ),
    "an extra entry field": (
        lambda d: _add(d, key="k", name="K", value="v", unit_class="length"),
        "P: entry field 'unit_class' is not standard",
    ),
    "a unit with no canonical value": (
        lambda d: _add(d, key="k", name="K", value="2", unit_code="MMT"),
        "P: entry 'k' has unit_code or value_canonical alone",
    ),
    "an unknown unit code": (
        lambda d: _add(d, key="k", name="K", value="2", unit_code="XYZ", value_canonical=2.0),
        "P: entry 'k' unit 'XYZ' is not a known code",
    ),
    "a percent unit, which prism does not spell": (
        lambda d: _add(d, key="k", name="K", value="2", unit_code="P1", value_canonical=2.0),
        "P: entry 'k' unit 'P1' is not a known code",
    ),
    "a unit on a value that is not a bare number": (
        lambda d: _add(
            d, key="k", name="K", value="approx 3", unit_code="MMT", value_canonical=3.0
        ),
        "P: entry 'k' value 'approx 3' is not a bare number",
    ),
    "a unit with a wrong canonical": (
        lambda d: _add(d, key="k", name="K", value="2", unit_code="MMT", value_canonical=3.0),
        "P: entry 'k' canonical 3.0 is not 2 MMT",
    ),
    "a wrong variant_count": (
        lambda d: d.update(variant_count=d["variant_count"] + 1),
        "P: variant_count 445 is not 444",
    ),
}


@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_the_validator_refuses_each_planted_defect_with_its_own_problem(plant, retail):
    doc = deepcopy(retail[0])
    first = doc["variants"][0]
    assert (doc["product_id"], doc["variant_count"]) == ("JEA-HARROW", 444)
    assert standard.check_document(doc) == []
    apply, problem = PLANTS[plant]
    apply(doc)
    expected = (
        problem.replace("V:", f"{doc['product_id']}/{first['sku']}:")
        .replace("P:", f"{doc['product_id']}:")
        .replace("PATH", repr(doc["category_path"]))
        .replace("IMAGE", first["image_id"])
    )
    assert _problems(doc) == [expected]


def _problems(doc: dict[str, Any]) -> list[str]:
    """check_document's report; a validator that raises on a defect fails to report it."""
    try:
        return standard.check_document(doc)
    except Exception as exc:  # noqa: BLE001 -- the raise IS the finding, reported as one
        return [f"check_document raised {exc!r}"]


def test_a_repeated_sku_and_a_key_with_two_names_are_refused(retail):
    one, two = deepcopy(retail[0]), deepcopy(retail[1])
    two["variants"][0]["sku"] = one["variants"][0]["sku"]
    two["attributes"].append({"key": "color", "name": "Shade", "value": "Red"})
    problems = standard.check_catalog([one, two])
    assert any("is not unique" in p for p in problems)
    assert any("key 'color' names" in p for p in problems)


def _entry(key: str, name: str) -> dict[str, str]:
    return {"key": key, "name": name, "value": "x"}


#: Defects only the catalog-level pass sees, or that it must pass on from
#: check_document: plant(one, two) -> the one problem check_catalog reports.
CATALOG_PLANTS = {
    "a document's own defect": (
        lambda one, two: one.pop("product_type"),
        lambda one, two: f"{one['product_id']}: lacks 'product_type'",
    ),
    "a repeated product_id": (
        lambda one, two: two.update(product_id=one["product_id"]),
        lambda one, two: f"product_id {one['product_id']} is not unique (2 times)",
    ),
    "a variant-level key with a second name": (
        lambda one, two: (
            one["attributes"].append(_entry("fit_note", "Fit note")),
            two["variants"][0]["attributes"].append(_entry("fit_note", "Fit remark")),
        ),
        lambda one, two: "key 'fit_note' names ['Fit note', 'Fit remark']",
    ),
    "a key that shadows a product field": (
        lambda one, two: one["attributes"].append(_entry("brand", "Brand")),
        lambda one, two: "key 'brand' shadows a top-level field",
    ),
    "a key that shadows a variant field": (
        lambda one, two: two["variants"][0]["attributes"].append(_entry("in_stock", "In stock")),
        lambda one, two: "key 'in_stock' shadows a top-level field",
    ),
}


@pytest.mark.parametrize("plant", sorted(CATALOG_PLANTS))
def test_check_catalog_reports_each_catalog_level_defect(plant, retail):
    one, two = deepcopy(retail[0]), deepcopy(retail[1])
    assert standard.check_catalog([one, two]) == []
    apply, expected = CATALOG_PLANTS[plant]
    apply(one, two)
    assert standard.check_catalog([one, two]) == [expected(one, two)]


def test_a_percent_is_a_plain_number_named_in_percent(retail):
    """No ``P1`` unit: prism spells none for percent, so the name carries it."""
    entries = [e for d in retail for row in (d, *d["variants"]) for e in row["attributes"]]
    assert [e for e in entries if e.get("unit_code") == "P1"] == []
    beer = next(d for d in retail if d["product_id"] == "PLT-BRTROP")
    dress = next(d for d in retail if d["product_id"] == "PLT-PETDRS")
    assert {"key": "abv", "name": "ABV (%)", "value": "4.8"} in beer["attributes"]
    assert {"key": "discount", "name": "Discount (%)", "value": "30"} in dress["attributes"]


GOLDEN_FLAT = ROOT / "golden-catalog" / "flat.jsonl"

#: The retail flat document is industrial's (``golden-catalog/flat.jsonl``, which
#: prism-industrial-products loads as ``catalog.ndjson``) but for these keys.
#: Industrial keeps its USD amount and stock count and its provenance notes;
#: retail states ``price`` in ``currency`` and only knows whether a SKU is in stock.
INDUSTRIAL_ONLY_FLAT = frozenset({"price_usd", "stock", "dimension_provenance", "spec_quality"})
RETAIL_ONLY_FLAT = {"price": float, "currency": str, "in_stock": bool}
#: Present only on a style with a product line (6 of 328).
RETAIL_OPTIONAL_FLAT = frozenset({"series"})


def _shape(value: Any) -> Any:
    """A value's type, and its members' types for a list or an object."""
    if isinstance(value, list):
        return ("list", sorted({repr(_shape(v)) for v in value}))
    if isinstance(value, dict):
        return ("dict", sorted({repr(_shape(v)) for v in value.values()}))
    return type(value).__name__


def _shapes(rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for row in rows:
        for key, value in row.items():
            shape = _shape(value)
            # an empty list or object has no member types to compare
            if shape not in (("list", []), ("dict", [])):
                out.setdefault(key, set()).add(repr(shape))
    return out


def _first(rows: list[dict[str, Any]], field: str, value: str) -> dict[str, Any]:
    found = [row for row in rows if row[field] == value]
    assert found, f"no flat document with {field} {value!r}"
    return found[0]


@pytest.fixture(scope="module")
def retail_flat() -> list[dict[str, Any]]:
    _retail()
    import export  # noqa: PLC0415 -- on sys.path once _retail() ran

    return export.flat_documents()


def test_the_retail_flat_file_is_one_document_per_sku(retail_flat):
    assert len(retail_flat) == RETAIL_SKUS
    assert len({d["sku"] for d in retail_flat}) == RETAIL_SKUS


def test_the_retail_flat_document_has_industrials_keys_and_types(retail_flat):
    with GOLDEN_FLAT.open(encoding="utf-8") as handle:
        industrial = [json.loads(line) for line in handle]
    shared = set(industrial[0]) - INDUSTRIAL_ONLY_FLAT
    for doc in retail_flat:
        assert set(doc) - RETAIL_OPTIONAL_FLAT == (shared - RETAIL_OPTIONAL_FLAT) | set(
            RETAIL_ONLY_FLAT
        ), doc["sku"]
        assert {k: type(doc[k]) for k in RETAIL_ONLY_FLAT} == RETAIL_ONLY_FLAT
    theirs, ours = _shapes(industrial), _shapes(retail_flat)
    assert {k: ours.get(k) for k in shared} == {k: theirs[k] for k in shared}


def test_rating_rank_and_was_price_are_numbers_in_the_flat_document(retail_flat):
    dress = _first(retail_flat, "product_id", "PLT-PETDRS")
    numbers = ("rating", "bestseller_rank", "was_price", "discount")
    assert {k: dress["facets_num"].get(k) for k in numbers} == {
        "rating": 3.9,
        "bestseller_rank": 119.0,
        "was_price": 40.0,
        "discount": 30.0,
    }
    assert (dress["currency"], dress["facets"]["rating"]) == ("GBP", ["3.9"])
    jeans = _first(retail_flat, "product_id", "JEA-HARROW")
    # a measured value in its own unit (inches), as industrial's facets_num holds it
    assert jeans["facets_num"].get("inside_leg_length") == 28.0
    assert "size_uk" not in jeans["facets_num"]


def test_a_flat_document_is_its_variant_under_its_product(retail, retail_flat):
    jeans = next(d for d in retail if d["product_id"] == "JEA-HARROW")
    variant = jeans["variants"][0]
    flat = _first(retail_flat, "sku", variant["sku"])
    own = {e["key"] for e in variant["attributes"]}
    # the SKU's own color and sizes replace the style's lists of them
    assert own == {"color", "length", "inside_leg_length", "size_uk", "size_eu", "size_us"}
    kept = [e for e in jeans["attributes"] if e["key"] not in own]
    assert flat["attributes"] == kept + variant["attributes"]
    assert (flat["title"], flat["parent_title"], flat["price"], flat["image_id"]) == (
        variant["title"],
        jeans["title"],
        variant["price"],
        variant["image_id"],
    )
    assert flat["attribute_names"] == sorted({e["name"] for e in flat["attributes"]})
    assert flat["facets"]["color"] == ["Rinse"]
    assert "Rinse" in flat["text"].split() and "Jeans" in flat["text"].split()


def test_the_export_writes_the_nested_and_the_flat_file(tmp_path, retail, retail_flat):
    subprocess.run([sys.executable, str(RETAIL / "export.py"), str(tmp_path)], check=True, cwd=ROOT)
    with (tmp_path / "nested.jsonl").open(encoding="utf-8") as handle:
        assert [json.loads(line) for line in handle] == retail
    with (tmp_path / "flat.jsonl").open(encoding="utf-8") as handle:
        assert [json.loads(line) for line in handle] == retail_flat
