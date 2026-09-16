"""The published-string layer must produce strings the parser can read back.

A generated value that the repository's own dimension parser cannot read is
worse than useless: it looks like data, renders nothing, and the failure shows
up far from its cause. So the property under test is a round trip, not a
spelling.
"""

from __future__ import annotations

import math

import pytest

from synthetic_industrial_products.catalog.formats import (
    IMPERIAL_STYLES,
    METRIC_STYLES,
    LengthStyle,
    UnpublishableMagnitude,
    format_angle,
    format_length,
    format_length_best,
)
from synthetic_industrial_products.dimensions import DimensionParseError, parse_length

#: Magnitudes in inches that the conventional series actually produces.
SERIES_INCHES = [
    0.0625,
    0.09375,
    0.125,
    0.1875,
    0.25,
    0.3125,
    0.375,
    0.5,
    0.625,
    0.75,
    1.0,
    1.25,
    1.5,
    2.5,
    3.0,
    4.125,
]


def _tolerance_inches(text: str, style: LengthStyle) -> float:
    """The most this spelling can be off by, in inches.

    Read off the text that was actually produced, not off the style that was
    requested: ``format_length_best`` falls through to a shape that can state
    the magnitude, so a request for an integer may come back as a decimal. A
    fraction, a mixed number and an integer are exact; a decimal is exact only
    to its last printed place. Asserting a tighter bound than the spelling
    carries would be asserting something false.
    """
    if "." not in text:
        return 1e-9
    _, _, tail = text.partition(".")
    places = sum(1 for ch in tail if ch.isdigit())
    # Half a place is the exact bound, and a magnitude that lands on a tie
    # (15.875 mm printed to two places) sits precisely on it; the float slack
    # keeps the comparison from turning that tie into a spurious failure.
    half_place = 0.5 * 10.0 ** (-places) * (1 + 1e-9)
    return half_place if style.system == "in" else half_place / 25.4


@pytest.mark.parametrize("inches", SERIES_INCHES)
@pytest.mark.parametrize("style,_weight", IMPERIAL_STYLES)
def test_every_imperial_style_round_trips(inches: float, style: LengthStyle, _weight: float):
    text = format_length_best(inches, style)
    if style.unitless:
        # A unitless value is ambiguous by construction and the parser is
        # right to refuse it; that is the point of the unitless case.
        with pytest.raises(DimensionParseError):
            parse_length(text)
        return
    tolerance = _tolerance_inches(text, style)
    assert math.isclose(parse_length(text).inches, inches, rel_tol=0, abs_tol=tolerance), text


@pytest.mark.parametrize("inches", SERIES_INCHES)
@pytest.mark.parametrize("style,_weight", METRIC_STYLES)
def test_every_metric_style_round_trips(inches: float, style: LengthStyle, _weight: float):
    text = format_length_best(inches, style)
    tolerance = _tolerance_inches(text, style)
    assert math.isclose(parse_length(text).inches, inches, rel_tol=0, abs_tol=tolerance), text


def test_a_lossy_spelling_is_detectable_rather_than_silent():
    """3/8" has no exact 2-decimal millimetre spelling, and that must show.

    9.525 mm prints as "9.52mm", which is 0.37480" -- not 0.375". The generator
    therefore treats the PUBLISHED STRING as the source of truth and parses
    value_num back out of it, so the numeric and the textual representation of
    one attribute can never disagree. This test pins the drift that makes that
    rule necessary.
    """
    text = format_length(0.375, LengthStyle("mm", "mm", "decimal", places=2))
    assert text == "9.52mm"
    assert parse_length(text).inches != 0.375
    assert parse_length(text).inches == pytest.approx(0.375, abs=2.5e-4)


def test_published_spellings_match_the_corpus():
    assert format_length(0.375, LengthStyle("in", '"', "fraction")) == '3/8"'
    assert format_length(0.375, LengthStyle("in", " in", "fraction")) == "3/8 in"
    assert format_length(1.5, LengthStyle("in", '"', "mixed")) == '1-1/2"'
    assert format_length(0.021, LengthStyle("in", '"', "decimal", places=4)) == '0.0210"'
    assert format_length(3.0 / 25.4, LengthStyle("mm", "mm", "decimal", places=2)) == "3.00mm"
    assert format_length(6.0 / 25.4, LengthStyle("mm", "mm", "integer")) == "6mm"


def test_a_magnitude_with_no_fractional_spelling_raises_rather_than_rounding():
    # 0.0210" is not a multiple of 1/64 and has no honest fractional form.
    with pytest.raises(UnpublishableMagnitude):
        format_length(0.021, LengthStyle("in", '"', "fraction"))


def test_the_fallback_never_rounds():
    # Asked for a vulgar fraction, 1.5" is a mixed number and must come back
    # as one -- never as "3/2" and never rounded to 1".
    assert format_length_best(1.5, LengthStyle("in", '"', "fraction")) == '1-1/2"'
    # Asked for a fraction, 0.021" has no fractional form and falls through to
    # a decimal that states it exactly.
    text = format_length_best(0.021, LengthStyle("in", '"', "fraction"))
    assert parse_length(text).inches == pytest.approx(0.021, abs=1e-9)


def test_a_whole_number_is_not_published_as_a_vulgar_fraction():
    with pytest.raises(UnpublishableMagnitude):
        format_length(1.0, LengthStyle("in", '"', "fraction"))


def test_a_value_with_no_whole_part_is_not_a_mixed_number():
    with pytest.raises(UnpublishableMagnitude):
        format_length(0.5, LengthStyle("in", '"', "mixed"))


def test_metric_is_never_written_as_a_fraction():
    with pytest.raises(UnpublishableMagnitude):
        format_length(0.5, LengthStyle("mm", "mm", "fraction"))


def test_angles_carry_their_unit_word():
    assert format_angle(30) == "30 Degrees"
    assert format_angle(38.0) == "38 Degrees"


def test_style_weights_are_a_distribution():
    for styles in (IMPERIAL_STYLES, METRIC_STYLES):
        total = sum(weight for _, weight in styles)
        assert math.isclose(total, 1.0, abs_tol=1e-9), total
