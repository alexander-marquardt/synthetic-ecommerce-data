"""Every displayed Helix Angle on an end mill has its numeric facet (#120).

The modelled angle defect publishes ``Helix Angle = 42"`` (the inch mark keyed
for the degree mark). The nested entry reads that as 42 degrees (``DD``, canonical
42.0), but the flat document's ``facets_num`` once carried no ``helix_angle`` for
it: the two numeric shapes disagreed on every such row. Walks the generated
end-mill set, fresh and committed, and asserts each displayed angle has its
number, and that it is the number the nested entry carries.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.config import SMALL, GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate

GOLDEN_FLAT = Path(__file__).resolve().parents[1] / "golden-catalog" / "flat.jsonl"


def _fresh_small() -> list[dict[str, Any]]:
    return list(emit.iter_flat(generate(SMALL)))


def _fresh_default() -> list[dict[str, Any]]:
    return list(emit.iter_flat(generate(GeneratorConfig())))


def _golden() -> list[dict[str, Any]]:
    with GOLDEN_FLAT.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


SOURCES = {
    "fresh SMALL build": _fresh_small,
    "fresh default build": _fresh_default,
    "committed golden flat.jsonl": _golden,
}


@pytest.fixture(scope="module", params=sorted(SOURCES))
def end_mills(request: pytest.FixtureRequest) -> list[dict[str, Any]]:
    docs = SOURCES[request.param]()
    return [d for d in docs if d["product_type"].startswith("end_mill")]


def test_every_displayed_helix_angle_has_its_numeric_facet(end_mills):
    shown = 0
    missing = []
    for doc in end_mills:
        for attribute in doc["attributes"]:
            if attribute["name"] != "Helix Angle":
                continue
            shown += 1
            if "helix_angle" not in doc["facets_num"]:
                missing.append((doc["sku"], attribute["value"]))
    assert shown > 0
    assert missing == []


def test_the_numeric_facet_is_the_degrees_the_entry_carries(end_mills):
    compared = 0
    for doc in end_mills:
        for attribute in doc["attributes"]:
            if attribute["name"] == "Helix Angle" and "value_canonical" in attribute:
                compared += 1
                assert doc["facets_num"].get("helix_angle") == attribute["value_canonical"]
    assert compared > 0
