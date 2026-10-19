"""The attribute census and the sparsity table report one quantity, so they agree (#367).

``00_attribute_name_census.json`` names a field ``n_records`` and says it holds "the
number of records containing" a name. ``06_attribute_sparsity.json`` holds the per-record
presence of the same 585 names. A name repeated on several rows of one specification
table was once counted per row in the census, so seven names read higher there than in
the sparsity table, and a reader reconciling the two could not tell which was wrong.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "reference-statistics"


def _load(name: str) -> dict:
    return json.loads((ROOT / name).read_text("utf-8"))


def _census_names() -> dict[str, dict]:
    census = _load("00_attribute_name_census.json")
    return {entry["name_verbatim"]: entry for entry in census["names_by_frequency"]}


def _sparsity_names() -> dict[str, dict]:
    sparsity = _load("06_attribute_sparsity.json")
    return {entry["name_verbatim"]: entry for entry in sparsity["overall"]["presence"]}


def test_the_census_and_the_sparsity_table_cover_the_same_names():
    """A name in one and not the other would make the agreement check below vacuous."""
    assert set(_census_names()) == set(_sparsity_names())


def test_census_n_records_equals_sparsity_n_for_every_name():
    census, sparsity = _census_names(), _sparsity_names()
    disagree = {
        name: (census[name]["n_records"], sparsity[name]["n"])
        for name in census
        if census[name]["n_records"] != sparsity[name]["n"]
    }
    assert disagree == {}


def test_census_presence_rate_equals_sparsity_rate_for_every_name():
    census, sparsity = _census_names(), _sparsity_names()
    disagree = {
        name: (census[name]["presence_rate"], sparsity[name]["rate"])
        for name in census
        if census[name]["presence_rate"] != sparsity[name]["rate"]
    }
    assert disagree == {}


def test_census_presence_rate_is_n_records_over_the_corpus():
    """The rate is derived from the count, so a corrected count cannot leave a stale rate."""
    census = _load("00_attribute_name_census.json")
    total = census["n_records"]
    stale = {
        entry["name_verbatim"]: (entry["presence_rate"], round(entry["n_records"] / total, 4))
        for entry in census["names_by_frequency"]
        if entry["presence_rate"] != round(entry["n_records"] / total, 4)
    }
    assert stale == {}


def test_census_names_stay_in_descending_frequency_order():
    """The list is named ``names_by_frequency``; a corrected count must not leave it unsorted."""
    names = _load("00_attribute_name_census.json")["names_by_frequency"]
    counts = [entry["n_records"] for entry in names]
    assert counts == sorted(counts, reverse=True)


def test_concept_group_counts_equal_the_per_name_counts():
    """The grouped spellings restate census counts; they must not drift from the names above."""
    census = _load("00_attribute_name_census.json")
    by_name = _census_names()
    drift = {
        f"{group}/{spelling}": (count, by_name[spelling]["n_records"])
        for group, body in census["concept_groups_used_downstream"].items()
        for spelling, count in body["counts"].items()
        if count != by_name[spelling]["n_records"]
    }
    assert drift == {}


def test_the_method_says_a_repeated_name_counts_once_per_record():
    census = _load("00_attribute_name_census.json")
    assert "once per record" in census["method"]
