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
    IMPERIAL_CANONICAL,
    METRIC_CANONICAL,
    LengthStyle,
    UnpublishableMagnitude,
    canonical_style,
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
@pytest.mark.parametrize("style", [IMPERIAL_CANONICAL, METRIC_CANONICAL])
def test_the_canonical_spelling_round_trips(inches: float, style: LengthStyle):
    text = format_length_best(inches, style)
    tolerance = _tolerance_inches(text, style)
    assert math.isclose(parse_length(text).inches, inches, rel_tol=0, abs_tol=tolerance), text


@pytest.mark.parametrize("style", [IMPERIAL_CANONICAL, METRIC_CANONICAL])
def test_the_canonical_spelling_is_never_unitless(style: LengthStyle):
    """A unitless value is ambiguous by construction, and the parser refuses it.

    The old weighted table carried two unitless imperial styles at a combined
    0.04, so roughly one dimension in twenty-five was published as a bare
    ``4-1/2`` -- 4-1/2 of what? Whatever else the canonical spelling is, it
    cannot be that, and this is the assertion that says so rather than leaving
    it to be read off the constant.
    """
    assert not style.unitless
    with pytest.raises(DimensionParseError):
        parse_length(format_length_best(0.375, LengthStyle(style.system, "", style.shape)))


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


def test_the_fallback_keeps_the_precision_it_was_asked_for():
    """A value asked for at two decimals must not silently gain two more.

    ``format_length_best`` tries a sequence of shapes, and an early version
    reset the precision on every attempt -- including the one the caller
    actually asked for. The visible symptom was a defect value published as
    "6.2121 in" where the generator had asked for "6.21 in", which reads as a
    suspiciously precise measurement rather than as a formatting bug.
    """
    assert format_length_best(6.21, LengthStyle("in", " in", "decimal", places=2)) == "6.21 in"
    assert format_length_best(0.375, LengthStyle("mm", "mm", "decimal", places=1)) == "9.5mm"
    assert format_length_best(0.021, LengthStyle("in", '"', "decimal", places=4)) == '0.0210"'


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


def test_one_magnitude_yields_exactly_one_string_per_system():
    """The whole point of the canonical spelling, asserted on the output.

    Not "the table has one row" -- that is the WIRING. This asks what the
    formatter actually PRODUCES: feed every series magnitude through the
    canonical style many times and count the distinct strings. A magnitude
    that can be spelled two ways is a facet bucket that splits in two.

    The counts are the assertion. One string per magnitude per system, so the
    distinct-string total equals the distinct-magnitude total exactly; a
    formatter that varied its spelling would exceed it and a formatter that
    collapsed two magnitudes onto one string would fall short.
    """
    for style in (IMPERIAL_CANONICAL, METRIC_CANONICAL):
        produced = {inches: set() for inches in SERIES_INCHES}
        for _ in range(25):
            for inches in SERIES_INCHES:
                produced[inches].add(format_length_best(inches, style))
        per_magnitude = {inches: len(texts) for inches, texts in produced.items()}
        assert set(per_magnitude.values()) == {1}, per_magnitude
        all_strings = {next(iter(texts)) for texts in produced.values()}
        assert len(all_strings) == len(SERIES_INCHES), sorted(all_strings)


def test_the_canonical_spellings_are_the_ones_the_corpus_writes():
    """Pin the actual strings, because "one spelling" does not say WHICH.

    These are the shapes measured in ``07_value_format_variation.json``: the
    inch double-prime on the tidiest exact fraction, and the millimetre
    written as the corpus writes it -- ``6mm`` whole, ``12.70mm`` otherwise.
    A magnitude off the 1/64 ladder has no fraction and falls to a decimal
    rather than being rounded onto a size the product does not have.
    """
    assert format_length_best(0.75, IMPERIAL_CANONICAL) == '3/4"'
    assert format_length_best(1.5, IMPERIAL_CANONICAL) == '1-1/2"'
    assert format_length_best(3.0, IMPERIAL_CANONICAL) == '3"'
    assert format_length_best(0.021, IMPERIAL_CANONICAL) == '0.0210"'
    assert format_length_best(6.0 / 25.4, METRIC_CANONICAL) == "6mm"
    assert format_length_best(12.7 / 25.4, METRIC_CANONICAL) == "12.70mm"


def test_an_undeclared_unit_system_is_refused_not_guessed():
    """``canonical_style`` has no default, and that is deliberate.

    Returning the imperial spelling for an unknown system would publish a
    catalog of inches labelled as something else, silently.
    """
    with pytest.raises(ValueError, match="no canonical spelling"):
        canonical_style("cubits")
