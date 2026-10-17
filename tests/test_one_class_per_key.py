"""One attribute key has one class: no key carries a unit on some rows and none on others.

The Engine refuses to start on a key whose rows are unit-classed on some documents and
not on others (``AmbiguousClassKeyError``). The retail build's Christmas trees were sized
under ``size`` as ``5 ft``, which the core's ``split`` reads as a length (``unit_code``
``FOT``), while a garment's ``size`` is text: 35 classed rows among 2,214 unclassed ones in
the loaded catalog. A tree's height is not a size system, so it is named ``item_height``, the
one key every measured height shares (gen#227).
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"


def _template_documents() -> list[dict[str, Any]]:
    """Every authored retail style (the templates the scaled build derives from) as the
    output standard's nested document."""
    if str(RETAIL) not in sys.path:
        sys.path.insert(0, str(RETAIL))
    import export  # noqa: PLC0415 -- the prototype's own directory is its import root
    import scale  # noqa: PLC0415

    return [export.standard_document(rec) for rec in scale.templates()]


def _mixed_keys(docs: list[dict[str, Any]]) -> dict[str, tuple[int, int]]:
    """key -> (classed, unclassed) entry counts, for each key that has both."""
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for doc in docs:
        for row in (doc, *doc["variants"]):
            for entry in row["attributes"]:
                counts[entry["key"]][entry.get("unit_code") is not None] += 1
    return {k: (c[1], c[0]) for k, c in counts.items() if all(c)}


def test_no_retail_key_mixes_unit_classed_and_unclassed_values():
    mixed = _mixed_keys(_template_documents())
    assert mixed == {}, f"keys with classed and unclassed entries, (classed, unclassed): {mixed}"


def test_the_validator_refuses_a_key_that_mixes_classed_and_unclassed_entries():
    from synthetic_ecommerce_data.core import standard  # noqa: PLC0415

    docs = _template_documents()[:2]
    assert standard.check_catalog(docs, one_class_per_key=True) == []
    classed = {"key": "probe", "name": "Probe", "value": "5", "unit_code": "FOT"}
    docs[0]["attributes"].append({**classed, "value_canonical": 1524.0})
    docs[1]["variants"][0]["attributes"].append({"key": "probe", "name": "Probe", "value": "M"})
    expected = "key 'probe' has a unit_code on 1 entries and none on 1"
    assert standard.check_catalog(docs, one_class_per_key=True) == [expected]
    assert standard.check_catalog(docs) == [], "the check is opt-in: industrial keys mix today"


def test_a_christmas_trees_height_is_an_item_height_not_a_size():
    docs = [d for d in _template_documents() if d["category_leaf"] == "Real Christmas Trees"]
    assert docs
    keys = {
        d["product_id"]: {e["key"] for v in d["variants"] for e in v["attributes"]} for d in docs
    }
    assert all("size" not in ks for ks in keys.values()), keys
    assert {"item_height"} in keys.values(), keys
