"""A tap's drive square is a published attribute, sized by the standard (#3).

``vocab._TAP`` declared ``Square Size`` at a presence of 0.46 and no record ever
carried it, so the declared rate was a number nothing could reach and the tap
drawing's square (``render/tap.py``) was dead code. These tests hold the data
side: the attribute is emitted at its declared presence, its value is the
``ASME B94.9`` / ``ISO 529`` square for the tap's own thread size, and it pairs
with the shank diameter of the SAME row of that standard.
"""

from __future__ import annotations

from collections import defaultdict

import pytest

from synthetic_ecommerce_data.core import standards_library as lib
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.dimensions import parse_length
from synthetic_ecommerce_data.domains.industrial import names, series
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.vocab import VOCAB

MM_PER_INCH = 25.4

#: Published to four places in inches and two in millimetres, so a figure read back
#: from a record is within this of the table's.
TOLERANCE_IN = 2e-4


@pytest.fixture(scope="module")
def tap_skus() -> list[dict[str, str]]:
    """Every spiral point tap SKU of the DEFAULT build, as ``{name: value}``."""
    catalog = generate(GeneratorConfig())
    return [
        {a.name: a.value for a in catalog.merged_attributes(line, child)}
        for line in catalog.lines
        if line.type_key == "tap_spiral_point"
        for child in line.children
    ]


@pytest.fixture(scope="module")
def carried_by_type() -> dict[str, set[str]]:
    catalog = generate(GeneratorConfig())
    seen: dict[str, set[str]] = defaultdict(set)
    for line in catalog.lines:
        for child in line.children:
            seen[line.type_key] |= {a.name for a in catalog.merged_attributes(line, child)}
    return seen


def _row_for(designation: str) -> tuple[dict, float]:
    """The standard's row for a ``Thread Size`` value, and mm-per-unit of its columns."""
    rows = {row["size"]: row for row in lib.table("tap_shank_squares").rows}
    if designation.startswith("M"):
        return rows[designation.split("x")[0]], 1 / MM_PER_INCH
    return rows[designation.split("-")[0]], 1.0


def _inches(text: str) -> float:
    return parse_length(text).inches


def test_the_default_build_carries_square_size_at_its_declared_presence(tap_skus):
    declared = next(s.presence for s in VOCAB["tap_spiral_point"] if s.name == "Square Size")
    carried = sum("Square Size" in sku for sku in tap_skus)
    assert len(tap_skus) > 200
    achieved = carried / len(tap_skus)
    assert abs(achieved - declared) < 0.1, (carried, len(tap_skus), declared)


def test_every_declared_name_is_carried_by_some_record_of_its_type(carried_by_type):
    """The vocabulary is the contract: a name declared and never emitted is fiction."""
    never = {
        type_key: sorted(
            spec.name
            for spec in specs
            if spec.presence > 0 and spec.name not in carried_by_type[type_key]
        )
        for type_key, specs in VOCAB.items()
    }
    assert {k: v for k, v in never.items() if v} == {}


def test_a_tap_square_is_the_standards_square_for_its_thread_size(tap_skus):
    wrong = []
    checked = 0
    for sku in tap_skus:
        if "Square Size" not in sku:
            continue
        row, scale = _row_for(sku["Thread Size"])
        want = row.get("square_in", 0) or row["square_mm"] * scale
        checked += 1
        if abs(_inches(sku["Square Size"]) - want) > TOLERANCE_IN:
            wrong.append((sku["Thread Size"], sku["Square Size"], round(want, 4)))
    assert checked > 50
    assert wrong == []


def test_a_tap_shank_is_the_same_row_of_the_standard_as_its_square(tap_skus):
    """Shank and square are one pair in ASME B94.9 and ISO 529, so one row serves both."""
    wrong = []
    checked = 0
    for sku in tap_skus:
        if "Shank Dia." not in sku:
            continue
        row, scale = _row_for(sku["Thread Size"])
        want = row.get("shank_in", 0) or row["shank_mm"] * scale
        checked += 1
        if abs(_inches(sku["Shank Dia."]) - want) > TOLERANCE_IN:
            wrong.append((sku["Thread Size"], sku["Shank Dia."], round(want, 4)))
    assert checked > 100
    assert wrong == []


def test_a_square_always_fits_on_its_shank(tap_skus):
    both = [sku for sku in tap_skus if "Square Size" in sku and "Shank Dia." in sku]
    assert len(both) > 30
    too_big = [
        (sku["Thread Size"], sku["Square Size"], sku["Shank Dia."])
        for sku in both
        if _inches(sku["Square Size"]) >= _inches(sku["Shank Dia."])
    ]
    assert too_big == []


def test_the_table_has_a_row_for_every_thread_size_the_catalog_taps_offer():
    sizes = {row["size"] for row in lib.table("tap_shank_squares").rows}
    offered = {
        designation.split("x")[0] if designation.startswith("M") else designation.split("-")[0]
        for table in (
            series.TAP_SIZES_UNC,
            series.TAP_SIZES_UNF,
            series.TAP_SIZES_METRIC,
            series.TAP_SIZES_METRIC_FINE,
        )
        for designation, _ in table
    }
    assert offered <= sizes, sorted(offered - sizes)


def test_the_tables_squares_are_smaller_than_their_shanks():
    for row in lib.table("tap_shank_squares").rows:
        unit = "in" if "shank_in" in row else "mm"
        assert 0 < row[f"square_{unit}"] < row[f"shank_{unit}"], row["size"]


def test_no_name_exception_still_says_the_name_is_never_emitted():
    stale = {n: why for n, why in names.NAME_EXCEPTIONS.items() if "never emitted" in why}
    assert stale == {}
