"""One ``pack_size`` vocabulary for a count of items (gen#246).

A count pack was written three ways: ``Single`` / ``3 pack`` (underwear, school, grocery),
``Set of 4`` (the furniture and tableware rows) and a bare digit (the planted distractors and
decoys), so the one ``pack_size`` facet listed all three side by side. The ruling is one term
per concept: a count is ``Single`` or ``N pack``. A title may keep natural wording ("Set of 4
Espresso Cups"); the attribute VALUE does not. A net weight or volume (``400g``, ``4 x 35g``,
``2 pint``, ``12 inch``, ``240 bags``) is a measure, not a count, and stays as it is.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402

#: A count of items: ``Single`` or ``N pack`` (N is 2 or more; one is ``Single``).
COUNT = re.compile(r"^(?:Single|(?:[2-9]|[1-9]\d+) pack)$")
#: A measure of what is in the pack, optionally times a count: ``400g``, ``4 x 35g``, ``12 inch``.
UNIT = r"(?:g|kg|ml|L|pint|inch|bags)"
MEASURE = re.compile(rf"^(?:\d+ x )?\d+(?:\.\d+)? ?{UNIT}$")


@pytest.fixture(scope="module")
def values() -> dict[str, set[str]]:
    """Every ``pack_size`` value of the authored build (style and SKU), by the style that has it."""
    found: dict[str, set[str]] = {}
    for rec in scale.templates():
        got = [str(a["value"]) for a in rec["attributes"] if a["key"] == "pack_size"]
        got += [str(s["pack_size"]) for s in rec.get("skus", []) if "pack_size" in s]
        for text in got:
            for value in text.split(", "):  # a style lists its SKUs' values, joined
                found.setdefault(value, set()).add(rec["product_id"])
    return found


def test_a_pack_size_is_a_count_in_one_vocabulary_or_a_measure(values: dict[str, set[str]]) -> None:
    assert values, "no pack_size value found: the census reads nothing"
    stray = {
        v: sorted(ids)[:2] for v, ids in values.items() if not (COUNT.match(v) or MEASURE.match(v))
    }
    assert stray == {}


def test_the_count_vocabulary_is_what_underwear_school_and_home_all_use(
    values: dict[str, set[str]],
) -> None:
    counts = {v: ids for v, ids in values.items() if COUNT.match(v)}
    prefixes = {"BRD-BXJRCT": "2 pack", "BRD-BWLCER": "4 pack", "BRD-CUTSRV": "2 pack",
                "BRD-DCCNT": "2 pack", "PLT-LEMONS": "4 pack", "PLT-ORANGS": "5 pack",
                "PLT-JNSHNG": "5 pack", "PLT-DXH04": "10 pack"}  # fmt: skip
    missing = {pid: want for pid, want in prefixes.items() if pid not in counts.get(want, set())}
    assert missing == {}


def test_a_count_label_is_single_or_the_skus_units_per_pack() -> None:
    bad = {}
    for rec in scale.templates():
        for sku in rec.get("skus", []):
            label, n = str(sku.get("pack_size", "")), sku.get("units_per_pack")
            if n is not None and COUNT.match(label):
                want = "Single" if n == 1 else f"{n} pack"
                if label != want:
                    bad[(rec["product_id"], label)] = want
    assert bad == {}
