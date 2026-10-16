"""One casing per exported attribute value (gen#255, elastic/prism#11856).

A facet that carries two values differing only in case shows two counts while a click on
either returns their sum. ``pattern`` is lower case and ``rise`` is High/Mid/Low, the
casing the catalogue repo reads (``RETAIL_VALUE_SPELLINGS`` in its ``combined_catalog``).
Every test reads the seed-0 build run to its ceiling, once.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402


@pytest.fixture(scope="module")
def docs():
    return scale.documents(scale.build(10_000_000))


@pytest.fixture(scope="module")
def rows(docs):
    return scale.flat(docs)


def _values(rows, keys=None):
    """``{key: {value}}`` over every attribute entry and facet value the export writes."""
    seen = collections.defaultdict(set)
    for r in rows:
        for a in r["attributes"]:
            if keys is None or a["key"] in keys:
                seen[a["key"]].add(a["value"])
        for key, vals in r["facets"].items():
            if keys is None or key in keys:
                seen[key].update(vals)
    return seen


def test_pattern_is_lower_case_in_every_attribute_and_facet(rows):
    pattern = _values(rows, {"pattern"})["pattern"]
    assert pattern
    assert {v for v in pattern if v != v.lower()} == set()


def test_rise_is_high_mid_low_in_every_attribute_and_facet(rows):
    assert _values(rows, {"rise"})["rise"] == {"High", "Mid", "Low"}


def test_no_exported_attribute_has_two_values_equal_under_case_folding(rows):
    clashes = {}
    for key, vals in _values(rows).items():
        by_fold = collections.defaultdict(set)
        for v in vals:
            if isinstance(v, str):
                by_fold[v.casefold()].add(v)
        split = sorted(sorted(vs) for vs in by_fold.values() if len(vs) > 1)
        if split:
            clashes[key] = split
    assert not clashes
