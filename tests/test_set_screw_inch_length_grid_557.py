"""Every nominal inch length of the set screw data file is on ASME B18.3's length grid,
or is kept with a cited reason (#557).

FastenersWB's ``inch_fs_length.csv`` runs on past the grid: ASME B18.3-1998 Table 5A
note 3 steps 1 to 2 in. by 0.25 and 2 to 6 in. by 0.50, and the list holds nine lengths
between those steps. The grid itself is restated once, in
``test_set_screw_inch_lengths_67.py``; this file holds the data to it.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from test_set_screw_inch_lengths_67 import _meta, _on_the_b18_3_grid
from test_type_set_screws_hex_socket import LARGE_LINES, _clean_docs, _inches, _values

#: The nine entries FastenersWB's list has between B18.3's steps.
OFF_GRID = ("1.375", "1.625", "2.25", "2.75", "3.25", "3.75", "4.25", "4.75", "5.25")

#: The grid starts at 0.13 in. (1/8); these two are below it, where note 3 says nothing.
BELOW_THE_GRID = ("1/16", "3/32")

#: The standard steps that the off-grid lengths sit between, so a reader sees the rule.
ON_GRID_NEIGHBOURS = ("1.25", "1.5", "1.75", "2", "2.5", "3", "3.5", "4", "4.5", "5", "5.5", "6")


def _nominal() -> list[str]:
    return _meta()["nominal_lengths_in"]


def test_the_grid_check_tells_the_listed_neighbours_from_the_off_grid_lengths():
    for length in ON_GRID_NEIGHBOURS:
        assert _on_the_b18_3_grid(Fraction(length)), length
    for length in OFF_GRID:
        assert not _on_the_b18_3_grid(Fraction(length)), length


@pytest.mark.parametrize("length", OFF_GRID)
def test_an_off_grid_length_is_not_a_nominal_length(length):
    assert length not in _nominal()


def test_every_nominal_length_is_on_the_grid_or_below_it_with_a_reason():
    below = [v for v in _nominal() if Fraction(v) < Fraction(1, 8)]
    assert below == list(BELOW_THE_GRID), below
    off = [
        v
        for v in _nominal()
        if Fraction(v) >= Fraction(1, 8) and not _on_the_b18_3_grid(Fraction(v))
    ]
    assert off == [], f"off ASME B18.3's length grid: {off}"


def test_the_two_lengths_below_the_grid_carry_a_cited_reason():
    note = _meta().get("nominal_lengths_below_grid_note", "")
    assert "ASME B18.3" in note and "Table 5A" in note and "0.13" in note, note
    for length in BELOW_THE_GRID:
        assert length in note, f"{length} is not named in the note"


@pytest.fixture(scope="module")
def built_inch_lengths() -> set[Fraction]:
    found: set[Fraction] = set()
    for doc in _clean_docs(LARGE_LINES):
        values = _values(doc)
        if values["Dia./Thread Size"]["value"].startswith("M"):
            continue
        found.add(Fraction(_inches(values["Length"])).limit_denominator(64))
    return found


def test_the_build_makes_no_inch_set_screw_at_an_off_grid_length(built_inch_lengths):
    off = sorted(
        v
        for v in built_inch_lengths
        if v >= Fraction(1, 8) and not _on_the_b18_3_grid(v)
    )
    assert off == [], [str(v) for v in off]
