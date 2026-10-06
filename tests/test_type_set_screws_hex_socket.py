"""Per-type gates for hex socket set screws, the first breadth category deepened (#53).

Each gate is one of #53's per-type gates: uniqueness at zero, census
conformance, byte-determinism over two builds, and a golden slice. The fifth,
every other type unchanged, is the seam suite's removal test
(``tests/test_type_seam.py``), which is parametrized over every type key.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import all_type_keys, generate

KEY = "set_screws_hex_socket"
ROOT = Path(__file__).resolve().parent.parent


def _documents(config: GeneratorConfig) -> list[dict]:
    catalog = generate(config, types=[KEY])
    return [doc for line in catalog.lines for doc in emit.flat_documents(catalog, line)]


@pytest.fixture(scope="module")
def docs() -> list[dict]:
    return _documents(GeneratorConfig())


def test_the_type_is_modelled_not_breadth() -> None:
    assert KEY in all_type_keys("modelled")


def test_the_type_is_deep(docs: list[dict]) -> None:
    assert all(doc["spec_quality"] != "fast_and_cheap" for doc in docs)
    assert len(docs) > 100


def test_no_brand_sells_one_spec_twice(docs: list[dict]) -> None:
    """Uniqueness at zero: no two SKUs of one brand publish the same attributes."""
    seen: dict[tuple, str] = {}
    duplicates = []
    for doc in docs:
        spec = (doc["brand"], tuple(sorted((a["name"], a["value"]) for a in doc["attributes"])))
        if spec in seen:
            duplicates.append((seen[spec], doc["sku"]))
        seen[spec] = doc["sku"]
    assert duplicates == []


def test_every_published_name_is_a_census_name(docs: list[dict]) -> None:
    census = json.loads((ROOT / "reference-statistics/00_attribute_name_census.json").read_text())
    names = {entry["name_verbatim"] for entry in census["names_by_frequency"]}
    published = {a["name"] for doc in docs for a in doc["attributes"]}
    # ``Standards`` and the measurement-system spellings are catalog-wide names.
    assert published - names - {"Standards"} == set()


def test_two_builds_are_byte_identical() -> None:
    small = GeneratorConfig(lines=400)
    first = json.dumps(_documents(small), sort_keys=True)
    assert first == json.dumps(_documents(small), sort_keys=True)


def test_the_golden_slice_is_the_type_built_alone(docs: list[dict]) -> None:
    """The type's records in the committed catalog are exactly its own build."""
    golden = [
        json.loads(row)
        for row in (ROOT / "golden-catalog/flat.jsonl").read_text().splitlines()
        if f'"product_type": "{KEY}"' in row
    ]
    assert golden == json.loads(json.dumps(docs))


def test_every_point_style_and_both_systems_are_built(docs: list[dict]) -> None:
    values = {(a["name"], a["value"]) for doc in docs for a in doc["attributes"]}
    for point in ("Cup Point", "Flat Point", "Cone Point", "Dog Point"):
        assert ("Point Type", point) in values
    threads = {v for n, v in values if n == "Dia./Thread Size"}
    assert any(t.startswith("M") for t in threads) and any("-" in t for t in threads)
