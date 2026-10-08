from __future__ import annotations

import pytest

from synthetic_ecommerce_data.dimensions import (
    MM_PER_INCH,
    DimensionParseError,
    parse_angle_degrees,
    parse_count,
    parse_length,
    parse_thread,
)


@pytest.mark.parametrize(
    ("published", "inches", "unit"),
    [
        ('1/4"', 0.25, "in"),
        ('3/8"', 0.375, "in"),
        ('3/16"', 0.1875, "in"),
        ('1/2"', 0.5, "in"),
        ('1"', 1.0, "in"),
        ('3"', 3.0, "in"),
        ('1-3/8"', 1.375, "in"),
        ('3-3/8"', 3.375, "in"),
        ('2-5/16"', 2.3125, "in"),
        ("1/2 in", 0.5, "in"),
        ("1/8 in", 0.125, "in"),
        ("0.411 in", 0.411, "in"),
        ("0.127 in", 0.127, "in"),
        ("6 mm", 6 / MM_PER_INCH, "mm"),
        ("3.5 mm", 3.5 / MM_PER_INCH, "mm"),
        ("57 mm", 57 / MM_PER_INCH, "mm"),
    ],
)
def test_published_lengths_are_read_exactly(published, inches, unit):
    length = parse_length(published)
    assert length.inches == pytest.approx(inches, abs=1e-12)
    assert length.unit == unit


def test_a_length_remembers_how_it_was_published():
    # The drawing prints the catalog's own string. A renderer that reformatted
    # 1-3/8" as 1.375" would be showing a value the record does not contain.
    assert parse_length('1-3/8"').display() == '1-3/8"'
    assert parse_length("6 mm").display() == "6 mm"


def test_metric_and_inch_lengths_are_comparable():
    assert parse_length("25.4 mm").inches == pytest.approx(parse_length('1"').inches)


@pytest.mark.parametrize(
    "malformed",
    [
        "",
        "   ",
        "banana",
        'abc"',
        '1/0"',
        '3-"',
        '-1/2"',
        '1/2/3"',
        "1/2",  # no unit: which one?
        "#10-32",  # a thread designation, not a length
        "1/2 furlong",
        '0"',
        "0 mm",
    ],
)
def test_a_value_that_cannot_be_read_raises(malformed):
    # The alternative -- a default -- puts a number in the drawing that the
    # record does not contain, and nothing downstream can tell.
    with pytest.raises(DimensionParseError):
        parse_length(malformed)


def test_a_non_string_raises_rather_than_coercing():
    with pytest.raises(DimensionParseError):
        parse_length(0.375)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("designation", "major_in", "pitch_in"),
    [
        ("#10-32", 0.190, 1 / 32),
        ("#8-32", 0.164, 1 / 32),
        ('1/4"-20', 0.25, 1 / 20),
        ("M6x1", 6 / MM_PER_INCH, 1 / MM_PER_INCH),
        ("M6 x 1", 6 / MM_PER_INCH, 1 / MM_PER_INCH),
    ],
)
def test_thread_designations_yield_their_major_diameter_and_pitch(designation, major_in, pitch_in):
    thread = parse_thread(designation)
    assert thread.major.inches == pytest.approx(major_in, abs=1e-9)
    assert thread.pitch_in == pytest.approx(pitch_in, abs=1e-12)


def test_the_minor_diameter_matches_the_published_thread_table():
    # 10-32 UNF has a basic minor diameter of 0.1517" on the external thread.
    # Arriving there from major diameter and pitch alone is the check that the
    # 60-degree form, not a guess, is what the drawing uses.
    assert parse_thread("#10-32").minor_in == pytest.approx(0.1517, abs=0.0005)
    assert parse_thread("#10-32").tpi == pytest.approx(32.0)


@pytest.mark.parametrize("malformed", ["", "M6", "flange", "#10-0", "10-32-4", "Torx"])
def test_an_unreadable_thread_designation_raises(malformed):
    with pytest.raises(DimensionParseError):
        parse_thread(malformed)


@pytest.mark.parametrize(
    ("published", "degrees"), [("30 Degrees", 30.0), ("45", 45.0), ("38 deg", 38.0)]
)
def test_helix_angles_are_read(published, degrees):
    assert parse_angle_degrees(published) == pytest.approx(degrees)


@pytest.mark.parametrize("malformed", ["", "steep", "90 Degrees", "-5 Degrees"])
def test_an_unusable_helix_angle_raises(malformed):
    with pytest.raises(DimensionParseError):
        parse_angle_degrees(malformed)


@pytest.mark.parametrize(("published", "count"), [("4", 4), ("2", 2), (" 6 ", 6)])
def test_counts_are_read(published, count):
    assert parse_count(published) == count


@pytest.mark.parametrize("malformed", ["", "four", "0", "2.5", "-3"])
def test_an_unusable_count_raises(malformed):
    with pytest.raises(DimensionParseError):
        parse_count(malformed)
