"""One attribute key has one class: no key carries a unit on some rows and none on others.

The Engine refuses to start on a key whose rows are unit-classed on some documents and
not on others (``AmbiguousClassKeyError``). The retail build's Christmas trees were sized
under ``size`` as ``5 ft``, which the core's ``split`` reads as a length (``unit_code``
``FOT``), while a garment's ``size`` is text: 35 classed rows among 2,214 unclassed ones in
the loaded catalog. A tree's height is not a size system, so it is named ``height``.
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
    assert mixed == {}, f"keys with both classed and unclassed entries (classed, unclassed): {mixed}"


def test_a_christmas_trees_height_is_a_height_not_a_size():
    docs = [d for d in _template_documents() if d["category_leaf"] == "Real Christmas Trees"]
    assert docs
    for doc in docs:
        keys = {e["key"] for v in doc["variants"] for e in v["attributes"]}
        assert "height" in keys and "size" not in keys, (doc["product_id"], sorted(keys))
