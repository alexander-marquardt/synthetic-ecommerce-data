"""The inch set screw lengths FastenersWB lacks (5/16", 5/8", 7/8") are filled from
ASME B18.3 itself, and the data file no longer records them as a gap (#67).

FastenersWB's ``inch_fs_length.csv`` runs 1/4, 3/8, 7/16, 1/2, 3/4, 1 and has no 5/16,
5/8 or 7/8. The standard's own length increments (Table 5A, note 3) put all three on
the grid: 0.06 in. (1/16) from 0.13 through 0.50, then 0.13 (1/8) from 0.50 through 1.00.
"""

from __future__ import annotations

import json
from fractions import Fraction
from importlib import resources

import pytest

from test_type_set_screws_hex_socket import LARGE_LINES, _clean_docs, _inches, _values

INCH_TABLE = "ASME B18.3 set screws"
MISSING = ("5/16", "5/8", "7/8")

#: ASME B18.3-1998 Table 5A note 3, "Standard Length Increments for Set Screws":
#: (from, through, increment), inches, the decimals as the table prints them
#: (0.06 is 1/16 and 0.13 is 1/8).
B18_3_LENGTH_INCREMENTS = (
    (Fraction(1, 8), Fraction(3, 16), Fraction(1, 32)),  # 0.03 in., sizes 0 to 3 only
    (Fraction(1, 8), Fraction(1, 2), Fraction(1, 16)),
    (Fraction(1, 2), Fraction(1), Fraction(1, 8)),
    (Fraction(1), Fraction(2), Fraction(1, 4)),
    (Fraction(2), Fraction(6), Fraction(1, 2)),
)


def _meta() -> dict:
    path = resources.files("synthetic_ecommerce_data.domains.industrial.data")
    text = path.joinpath("set_screw_standards.json").read_text("utf-8")
    return json.loads(text)[INCH_TABLE]["_meta"]


def _on_the_b18_3_grid(length: Fraction) -> bool:
    return any(
        low <= length <= high and (length - low) % step == 0
        for low, high, step in B18_3_LENGTH_INCREMENTS
    )


@pytest.mark.parametrize("length", MISSING)
def test_each_missing_length_is_a_b18_3_standard_length(length):
    assert _on_the_b18_3_grid(Fraction(length)), length


def test_the_data_file_lists_the_three_lengths_in_order_and_no_longer_records_a_gap():
    meta = _meta()
    nominal = [Fraction(v) for v in meta["nominal_lengths_in"]]
    for length in MISSING:
        assert Fraction(length) in nominal, f"{length} is not a nominal inch length"
    assert nominal == sorted(set(nominal)), "the nominal inch lengths are not ascending"
    assert "nominal_lengths_gap" not in meta


def test_the_data_file_cites_a_second_source_for_the_filled_lengths():
    meta = _meta()
    cite = meta.get("nominal_lengths_fill_source", "")
    assert "ASME B18.3" in cite and "Table 5A" in cite, cite
    for length in MISSING:
        assert length in cite, f"{length} is not named in the citation"


@pytest.fixture(scope="module")
def inch_lengths_by_size() -> dict[str, set[Fraction]]:
    """Each inch size's lengths in the ``LARGE_LINES`` build, which reaches every range's end."""
    found: dict[str, set[Fraction]] = {}
    for doc in _clean_docs(LARGE_LINES):
        values = _values(doc)
        thread = values["Dia./Thread Size"]["value"]
        if thread.startswith("M"):
            continue
        size = thread.rsplit("-", 1)[0]
        inches = Fraction(_inches(values["Length"])).limit_denominator(64)
        found.setdefault(size, set()).add(inches)
    return found


@pytest.mark.parametrize("length", MISSING)
def test_the_build_makes_every_size_that_admits_the_length(inch_lengths_by_size, length):
    """A size admits a nominal length inside its range (``length_min_in`` to
    ``length_max_in``); each such size is built at it."""
    rows = _meta_rows()
    admitting = {
        r["size"]
        for r in rows
        if Fraction(r["length_min_in"]) <= Fraction(length) <= Fraction(r["length_max_in"])
    }
    assert len(admitting) >= 5, admitting
    missing = sorted(s for s in admitting if Fraction(length) not in inch_lengths_by_size[s])
    assert missing == [], f"no {length}\" SKU for {missing}"


def _meta_rows() -> list[dict]:
    path = resources.files("synthetic_ecommerce_data.domains.industrial.data")
    return json.loads(path.joinpath("set_screw_standards.json").read_text("utf-8"))[INCH_TABLE][
        "rows"
    ]


def test_the_citation_carries_the_fifth_increment_of_the_note():
    """#557 quotes the note's 0.03 in. step (0.13 through 0.19, sizes 0 to 3 only)."""
    cite = _meta().get("nominal_lengths_fill_source", "")
    assert "0.03 in. from 0.13 through 0.19" in cite, cite
    assert "sizes 0 to 3 only" in cite, cite
