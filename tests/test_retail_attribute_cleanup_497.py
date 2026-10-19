"""The retail attribute clean-up of #497, first slice: no published attribute restates the
product type.

``attribute_cleanup.clean`` runs inside ``export._product_attributes`` and ``export._variant``,
so the guards read the documents the scaler builds (every template), not the helper alone.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"))

import attribute_cleanup  # noqa: E402
import scale  # noqa: E402

CEILING = 81322


def _e(key: str, value: Any) -> dict[str, Any]:
    return {"key": key, "name": key.title(), "value": value}


@cache
def _docs() -> tuple[dict[str, Any], ...]:
    return tuple(scale.documents(scale.build(CEILING)))


def _entries(doc: dict[str, Any]):
    yield from doc["attributes"]
    for variant in doc["variants"]:
        yield from variant["attributes"]


def test_a_key_that_restates_the_type_is_dropped_and_a_real_sub_kind_stays() -> None:
    got = attribute_cleanup.clean(
        [
            _e("storage_type", "Storage Box"),
            _e("type", "Set Screw"),
            _e("storage_type", "Underbed"),
            _e("type", "Deep Groove"),
            _e("color", "Storage Box"),
        ],
        "Storage Box",
    )
    assert [(e["key"], e["value"]) for e in got] == [
        ("type", "Set Screw"),
        ("storage_type", "Underbed"),
        ("type", "Deep Groove"),
        ("color", "Storage Box"),
    ]
    band = attribute_cleanup.clean([_e("tracker_type", "Fitness band")], "Fitness Band")
    assert band == []


def test_a_type_equal_to_the_product_type_is_dropped_whatever_its_case() -> None:
    kept = attribute_cleanup.clean([_e("type", "set screw"), _e("type", "Socket")], "Set Screw")
    assert [e["value"] for e in kept] == ["Socket"]


def test_no_published_attribute_restates_its_product_type() -> None:
    restating = {
        (doc["product_type"], e["key"], e["value"])
        for doc in _docs()
        for e in _entries(doc)
        if e["key"] in {"storage_type", "tracker_type", "type"}
        and str(e["value"]).casefold() == doc["product_type"].casefold()
    }
    assert restating == set()


def test_the_real_sub_kinds_of_a_removed_key_stay_published() -> None:
    """A storage box's Underbed and a nursery storage's Basket say something the type does
    not, so their ``storage_type`` stays; the Fitness Band loses its ``tracker_type`` whole."""
    seen: dict[tuple[str, str], set[str]] = {}
    for doc in _docs():
        for e in _entries(doc):
            if e["key"] in {"storage_type", "tracker_type"}:
                seen.setdefault((doc["product_type"], e["key"]), set()).add(e["value"])
    assert seen == {
        ("Storage Box", "storage_type"): {"Underbed"},
        ("Nursery Storage", "storage_type"): {"Basket", "Cube", "Hanging Organizer"},
    }
