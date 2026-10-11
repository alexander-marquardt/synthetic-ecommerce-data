"""Every SKU carries ``variant_axes``, checked against the data (gen#47).

The five invariants of the issue, each a function over a catalog's products and each shown to
fail on a planted defect, then run on the Industrial and the Retail build:

1. within a product the axis tuple names exactly one SKU;
2. an attribute that is not an axis holds one value across the product, or is *derived*: it
   follows a single axis (a nut's width across flats follows its thread size, a color family
   follows the color). A derived attribute is not a second dropdown, so it is not an axis;
   one that is neither constant nor derived would be a hidden axis;
3. every axis takes at least two values;
4. brand is never an axis, and a product has one brand;
5. a single-SKU product has ``[]``.

A "SKU" is read the way the flat document states it: the product's attributes, less the keys the
SKU restates, then the SKU's own.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.variant_axes import derived_from_one, profile, variant_axes
from synthetic_ecommerce_data.domains.industrial.generate import generate

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import scale  # noqa: E402


def sku_profiles(doc: dict) -> list[dict[str, tuple[str, ...]]]:
    """Each SKU's attributes as its flat document states them, by key."""
    out = []
    for variant in doc["variants"]:
        own = {e["key"] for e in variant["attributes"]}
        kept = [e for e in doc["attributes"] if e["key"] not in own]
        out.append(profile(kept + variant["attributes"]))
    return out


def check_unique(doc: dict) -> list[str]:
    axes = doc["variant_axes"]
    tuples = [tuple(p.get(k) for k in axes) for p in sku_profiles(doc)]
    return (
        [] if len(set(tuples)) == len(tuples) else [f"{doc['product_id']}: two SKUs share {axes}"]
    )


def check_no_hidden_axis(doc: dict) -> list[str]:
    """A non-axis attribute is constant or follows a single axis."""
    axes = doc["variant_axes"]
    profiles = sku_profiles(doc)
    return [
        f"{doc['product_id']}: {key} varies and follows no single axis"
        for key in dict.fromkeys(k for p in profiles for k in p)
        if key not in axes
        and len({p.get(key) for p in profiles}) > 1
        and not derived_from_one(key, axes, profiles)
    ]


def check_no_hidden_axis_strict(doc: dict) -> list[str]:
    """The issue's wording: a non-axis attribute holds one value across the product."""
    profiles = sku_profiles(doc)
    return [
        f"{doc['product_id']}: {key}"
        for key in dict.fromkeys(k for p in profiles for k in p)
        if key not in doc["variant_axes"] and len({p.get(key) for p in profiles}) > 1
    ]


def check_axes_vary(doc: dict) -> list[str]:
    profiles = sku_profiles(doc)
    return [
        f"{doc['product_id']}: {k} is a dead dropdown"
        for k in doc["variant_axes"]
        if len({p.get(k) for p in profiles}) < 2
    ]


def check_brand(doc: dict) -> list[str]:
    bad = [f"{doc['product_id']}: {k} is an axis" for k in doc["variant_axes"] if k == "brand"]
    brands = {v.get("brand", doc["brand"]) for v in doc["variants"]}
    return bad + ([f"{doc['product_id']}: many brands"] if brands != {doc["brand"]} else [])


def check_single(doc: dict) -> list[str]:
    ok = doc["variant_axes"] == [] if len(doc["variants"]) == 1 else bool(doc["variant_axes"])
    return (
        [] if ok else [f"{doc['product_id']}: {len(doc['variants'])} SKUs, {doc['variant_axes']}"]
    )


CHECKS = {
    "unique": check_unique,
    "no_hidden_axis": check_no_hidden_axis,
    "axes_vary": check_axes_vary,
    "brand": check_brand,
    "single": check_single,
}


def failures(name: str, docs: list[dict]) -> list[str]:
    return [m for doc in docs for m in CHECKS[name](doc)]


# ------------------------------------------------------------ the planted failures


@pytest.fixture(scope="module")
def planted_base() -> dict:
    """A two-axis product: three thread sizes x two lengths, one derived width."""
    variants = []
    for i, (size, length) in enumerate([(s, n) for s in ("M4", "M5", "M6") for n in ("10", "20")]):
        width = {"M4": "7", "M5": "8", "M6": "10"}[size]
        attrs = [("thread_size", size), ("length", length), ("width_across_flats", width)]
        variants.append({"sku": f"S{i}", "attributes": [{"key": k, "value": v} for k, v in attrs]})
    return {
        "product_id": "P1",
        "brand": "Acme",
        "attributes": [{"key": "material", "value": "Steel"}],
        "variants": variants,
        "variant_axes": ["thread_size", "length"],
    }


def test_the_planted_base_is_clean(planted_base):
    assert planted_base["variant_axes"] == variant_axes(sku_profiles(planted_base))
    for name in CHECKS:
        assert failures(name, [planted_base]) == [], name


def test_planted_duplicate_sku_fails_the_unique_axis_tuple(planted_base):
    doc = copy.deepcopy(planted_base)
    doc["variants"][1] = copy.deepcopy(doc["variants"][0]) | {"sku": "DUP"}
    assert failures("unique", [doc])


def test_planted_hidden_axis_fails(planted_base):
    doc = copy.deepcopy(planted_base)
    doc["variants"][0]["attributes"].append({"key": "coating", "value": "Zinc"})
    doc["variants"][1]["attributes"].append({"key": "coating", "value": "Black oxide"})
    assert failures("no_hidden_axis", [doc])
    assert failures("no_hidden_axis", [planted_base]) == []


def test_planted_dead_dropdown_fails(planted_base):
    doc = copy.deepcopy(planted_base) | {"variant_axes": ["thread_size", "length", "material"]}
    assert failures("axes_vary", [doc]) == ["P1: material is a dead dropdown"]


def test_planted_brand_axis_fails(planted_base):
    doc = copy.deepcopy(planted_base) | {"variant_axes": ["brand", "length"]}
    assert failures("brand", [doc])
    doc = copy.deepcopy(planted_base)
    doc["variants"][2]["brand"] = "Other"
    assert failures("brand", [doc])


def test_planted_axes_on_a_single_sku_or_none_on_a_multi_sku_fail(planted_base):
    one = copy.deepcopy(planted_base) | {"variants": planted_base["variants"][:1]}
    assert failures("single", [one])
    assert failures("single", [one | {"variant_axes": []}]) == []
    assert failures("single", [copy.deepcopy(planted_base) | {"variant_axes": []}])


def test_the_derivation_keeps_an_independent_axis_and_drops_a_derived_one():
    colors = [("red", "warm"), ("pink", "warm"), ("blue", "cool")]
    rows = [{"color": (c,), "family": (f,), "size": (s,)} for c, f in colors for s in ("S", "L")]
    assert variant_axes(rows) == ["color", "size"] or variant_axes(rows) == ["size", "color"]
    assert "family" not in variant_axes(rows)
    assert variant_axes(rows[:1]) == []


# ------------------------------------------------------------ the two builds


@pytest.fixture(scope="module")
def industrial() -> tuple[list[dict], list[dict]]:
    catalog = generate(SMALL)
    return list(emit.iter_nested(catalog)), list(emit.iter_flat(catalog))


@pytest.fixture(scope="module")
def retail() -> tuple[list[dict], list[dict]]:
    docs = [export.standard_document(r) for r in scale.build(30000).records]
    flat = [
        row for doc in docs for row in export.standard.flat_documents(doc, export.NUMERIC_FACTS)
    ]
    return docs, flat


@pytest.mark.parametrize("name", sorted(CHECKS))
@pytest.mark.parametrize("build", ["industrial", "retail"])
def test_the_invariant_holds_on_the_build(build, name, request):
    docs, _ = request.getfixturevalue(build)
    assert len(docs) > 100
    assert failures(name, docs) == []


@pytest.mark.parametrize("build", ["industrial", "retail"])
def test_the_build_has_single_and_multi_sku_products_with_axes(build, request):
    docs, _ = request.getfixturevalue(build)
    assert any(len(d["variants"]) == 1 and d["variant_axes"] == [] for d in docs)
    assert any(len(d["variants"]) > 1 and d["variant_axes"] for d in docs)


@pytest.mark.parametrize("build", ["industrial", "retail"])
def test_every_flat_document_states_its_products_axes_and_they_name_one_sku(build, request):
    docs, flat = request.getfixturevalue(build)
    axes = {d["product_id"]: d["variant_axes"] for d in docs}
    seen: dict[tuple, str] = {}
    for row in flat:
        assert row["variant_axes"] == axes[row["product_id"]]
        values = tuple(tuple(row["facets"].get(k, ())) for k in row["variant_axes"])
        key = (row["product_id"], values)
        assert seen.setdefault(key, row["sku"]) == row["sku"], f"{row['product_id']}: {values}"
        assert all(k in row["facets"] for k in row["variant_axes"])
