"""No two attribute keys on one document share a display name (gen#256).

A skirt exported ``garment_length`` and a SKU axis ``length``, both named "Length": a facet
panel showed two facets with one label. The axis is ``fit_length`` ("Fit length") since #280;
``name_guard.shared_name_findings`` keeps every type clean. The first block feeds the guard a
document broken on purpose (the mutant: the old skirt), the second runs it over the shipped
ceiling build, nested and flat.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path
from typing import Any

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import name_guard  # noqa: E402
import scale  # noqa: E402

CEILING = 10_000_000  # more SKUs than the templates reach, so ``scale.build`` runs to its ceiling


def _entry(key: str, name: str, value: str) -> dict[str, str]:
    return {"key": key, "name": name, "value": value}


def _skirt(axis_key: str, axis_name: str) -> dict[str, Any]:
    return {
        "product_id": "PLT-SKT",
        "attributes": [_entry("garment_length", "Length", "Maxi"),
                       _entry("fabric", "Fabric", "Cotton")],
        "variants": [{"attributes": [_entry(axis_key, axis_name, "Short/Petite")]}],
    }


def test_two_keys_with_one_name_on_a_nested_document_are_a_finding() -> None:
    found = name_guard.shared_name_findings([_skirt("length", "Length")])
    assert len(found) == 1
    assert "PLT-SKT" in found[0]
    assert "garment_length" in found[0]
    assert "length" in found[0]


def test_two_keys_with_one_name_on_a_flat_row_are_a_finding() -> None:
    row = {"product_id": "PLT-SKT", "attributes": [_entry("garment_length", "Length", "Maxi"),
                                                   _entry("length", "Length", "Long")]}
    assert len(name_guard.shared_name_findings([row])) == 1


def test_distinct_names_and_a_key_listed_twice_are_not_findings() -> None:
    assert name_guard.shared_name_findings([_skirt("fit_length", "Fit length")]) == []
    twice = _skirt("garment_length", "Length")
    assert name_guard.shared_name_findings([twice]) == []


@cache
def _docs() -> tuple[dict[str, Any], ...]:
    return tuple(scale.documents(scale.build(CEILING)))


def test_no_shipped_document_gives_two_keys_one_name() -> None:
    assert name_guard.shared_name_findings(_docs()) == []


def test_no_shipped_flat_row_gives_two_keys_one_name() -> None:
    assert name_guard.shared_name_findings(scale.flat(list(_docs()))) == []
