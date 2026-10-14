"""Every worn SKU has one audience; shirts exist; facets have one spelling.

The category tree keeps its Women / Men / Kids roots. Who a garment is for is also the
``audience`` facet (``Womens``, ``Mens``, ``Girls``, ``Boys``, ``Baby``, ``Unisex``), which a
search filters beside ``product_type`` ("mens jeans"). Kids' SKUs carried none, and a Women
or Men SKU carried one only when its template wrote it. The same build spelled ``pattern`` and
``rise`` two ways ("plain", "Plain"), which split one facet's bucket in two, and called a tee
both "Tee" and "T-Shirt". A search for "shirt" found only T-shirt bras and shirt dresses.

Every test reads the seed-0 build run to its ceiling, once.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import audience  # noqa: E402
import departments  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402
import shirt_rows  # noqa: E402

from synthetic_ecommerce_data.core import standard  # noqa: E402

SHIRT_LEAVES = {"Oxford Shirts", "Flannel Shirts", "Linen Shirts", "Denim Shirts"}
#: Mens shirts also have the formal, check and short sleeve leaves (gen#310).
MENS_SHIRT_LEAVES = SHIRT_LEAVES | {"Formal Shirts", "Check Shirts", "Short Sleeve Shirts"}
#: Product types folded into another (:data:`export.PRODUCT_TYPE_FOLDS`).
FOLDED = {"Tee": "T-Shirt"}


@pytest.fixture(scope="module")
def built():
    return scale.build(10_000_000)


@pytest.fixture(scope="module")
def docs(built):
    return scale.documents(built)


@pytest.fixture(scope="module")
def rows(docs):
    return scale.flat(docs)


def _worn(row: dict, department_of: dict[str, str]) -> bool:
    """Sold to a person: under a people root, or in a worn build department (the build record's
    own ``department``, which no document states: gen#281)."""
    return (
        row["category_path"][0] in audience.PEOPLE_ROOTS
        or department_of[row["product_id"]] in audience.WORN_DEPARTMENTS
    )


def test_every_worn_sku_has_exactly_one_audience(rows, built):
    department_of = {r["product_id"]: r["department"][0] for r in built.records}
    worn = [r for r in rows if _worn(r, department_of)]
    assert worn
    bad = collections.Counter(
        tuple(r["facets"].get("audience", ())) for r in worn
        if len(r["facets"].get("audience", ())) != 1
        or r["facets"]["audience"][0] not in audience.AUDIENCES
    )  # fmt: skip
    assert not bad, f"worn SKUs without exactly one audience: {dict(bad)}"


def test_the_audience_follows_the_category_root(rows):
    got = collections.defaultdict(set)
    for r in rows:
        path = r["category_path"]
        if path[0] in audience.PEOPLE_ROOTS:
            got[(path[0], path[1] if path[0] == "Kids" else "")].add(r["facets"]["audience"][0])
    assert got[("Women", "")] == {"Womens"}
    assert got[("Men", "")] == {"Mens"}
    assert got[("Kids", "Girls")] == {"Girls"}
    assert got[("Kids", "Boys")] == {"Boys"}
    assert got[("Kids", "Shoes")] == {"Unisex"}
    assert got[("Kids", "Baby")] == {"Baby"}


def test_an_audience_is_never_added_to_a_style_that_has_one(built):
    explicit = [r for r in built.records if any(a["key"] == "audience" for a in r["attributes"])]
    assert explicit
    for r in explicit:
        assert audience.audience_of(r) is None


def test_no_facet_has_two_values_that_differ_only_in_case(rows):
    seen = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        for key, values in r["facets"].items():
            for v in values:
                seen[key][str(v).lower()].add(v)
        seen["product_type"][r["product_type"].lower()].add(r["product_type"])
    split = {
        key: sorted(map(sorted, (vs for vs in by.values() if len(vs) > 1)))
        for key, by in seen.items()
    }
    assert not {k: v for k, v in split.items() if v}


def test_a_product_type_synonym_is_folded_into_its_category_node(rows, built):
    types = {r["product_type"] for r in rows}
    assert not types & set(FOLDED)
    assert set(FOLDED.values()) <= types
    tees = [r for r in built.records if r["product_type"] in FOLDED]
    assert tees
    for r in tees:  # the image ids are the authored ones: nothing to re-render
        assert export.image_id(r, r["skus"][0]).startswith(f"{r['product_type'].lower()}/")


def test_a_t_shirt_has_the_t_shirt_node_for_its_category(rows):
    for r in rows:
        if r["product_type"] == "T-Shirt":
            assert "T-Shirts" in r["category_path"] or "Sports Tees" in r["category_path"]


def test_shirts_sit_under_tops_for_mens_and_womens(rows):
    shirts = [r for r in rows if r["product_type"] == "Shirt"]
    assert shirts
    placed = collections.defaultdict(set)
    for r in shirts:
        *head, leaf = r["category_path"]
        assert head[1:] == ["Tops", "Shirts"]
        placed[head[0]].add(leaf)
        assert "Shirt" in r["title"] and "Tee" not in r["title"]
        assert r["facets"]["audience"] == {"Men": ["Mens"], "Women": ["Womens"]}[head[0]]
    assert placed == {"Men": MENS_SHIRT_LEAVES, "Women": SHIRT_LEAVES}


def test_there_are_twenty_to_thirty_shirt_styles():
    assert 20 <= len(shirt_rows.STYLES) <= 30


def test_a_shirt_is_a_template_no_derived_style_copies(built):
    ids = {s.doc()["product_id"] for s in shirt_rows.STYLES}
    assert ids == scale.SHIRT_IDS
    assert not ids & {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not ids & set(built.template_of.values())


def test_the_cleaning_root_is_one_and_every_build_department_is_on_the_list(docs, built):
    roots = {d["category_path"][0] for d in docs}
    assert "Cleaning & Janitorial" not in roots
    assert "Cleaning" in roots
    for r in built.records:
        departments.check(r["department"], r["product_id"])
    assert not standard.check_catalog(docs)


def test_the_document_json_round_trips_with_one_audience_entry_per_style(docs):
    for d in docs:
        assert sum(a["key"] == "audience" for a in d["attributes"]) <= 1
    json.dumps(docs[0])
