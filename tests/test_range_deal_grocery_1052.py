"""The grocery range-name deal is append-stable (#1052, slice 3).

Guard: ``grocery.range_names`` dealt the grocery half of the range-name pool round-robin over the
sorted grocery brands, so one grocery brand more changed the deal's brand count and moved every
grocery brand's names (measured on main 5d730297: 45 of 45 brands moved when one was added). The
deal now holds the append-only ``range_ownership.GROCERY`` roster: the 45 brands dealt before it
keep that deal, and a grocery brand appended to it takes a block of names from grocery stems of
its own, apart from the scale roster's. Metric: the existing grocery brands whose names change
when two brands are appended (0).
"""

from __future__ import annotations

import re
from dataclasses import replace

import pytest

from synthetic_ecommerce_data.domains.retail import grocery, grocery_rows, range_ownership

NEW = ("Pennywhistle Angling", "Larchmere Golf")


@pytest.fixture
def fresh():
    """``grocery.range_names`` is cached: clear it around a test that changes its inputs."""
    grocery.range_names.cache_clear()
    yield
    grocery.range_names.cache_clear()


def _grown(added: tuple[str, ...], monkeypatch: pytest.MonkeyPatch) -> range_ownership.Deal:
    """The real grocery deal with ``added`` new to the build (as a tier's extra brands) and
    appended to its roster, as a contributor adds a grocery brand."""
    roster = range_ownership.GROCERY
    monkeypatch.setattr(range_ownership, "GROCERY", replace(roster, added=roster.added + added))
    monkeypatch.setitem(grocery_rows.TIER_BRANDS, ("zz-probe",), added)
    grocery.range_names.cache_clear()
    return grocery.range_names()


def test_appending_grocery_brands_moves_no_existing_grocery_brands_names(fresh, monkeypatch):
    before = grocery.range_names()
    after = _grown(NEW, monkeypatch)
    moved = [b for b in before.brands if before.of(b) != after.of(b)]
    assert moved == []
    assert set(before.brands) | set(NEW) == set(after.brands)


def test_the_base_brands_keep_the_deal_they_had_before_1052(fresh, monkeypatch):
    """The roster's base is the brand set dealt round-robin before #1052 and its gaps the words
    skipped then, so today's grocery titles and goldens stay put: the rostered deal is the plain
    round-robin over the same brands less the same words."""
    rostered = grocery.range_names()
    roster = range_ownership.GROCERY
    assert rostered.brands == list(roster.base)
    reserved = {w for b in rostered.brands for w in re.findall(r"[A-Za-z]+", b)}
    plain = range_ownership.Deal("grocery", rostered.brands, reserved)
    assert {b: rostered.of(b) for b in rostered.brands} == {b: plain.of(b) for b in plain.brands}
    whole = range_ownership.whole_halves()["grocery"]
    skipped = {w for w in whole if w in reserved or w in range_ownership.EXCLUDED}
    assert roster.gaps == skipped


def test_appended_grocery_brands_own_names_no_other_brand_half_or_scale_block_holds(
    fresh, monkeypatch
):
    deal = _grown(NEW, monkeypatch)
    a, b = (set(deal.of(x)) for x in NEW)
    assert len(a) == len(b) == range_ownership.GROCERY.share
    assert a.isdisjoint(b)
    halves = range_ownership.halves()
    assert (a | b).isdisjoint(set(halves["scale"]) | set(halves["grocery"]))
    assert (a | b).isdisjoint(range_ownership.added_words())
    assert (a | b) <= set(range_ownership.candidates())
    assert all(deal.owner(n) == x for x in NEW for n in deal.of(x))


def test_the_grocery_and_scale_added_stems_never_share_a_word():
    """A stem appended to either list only appends words, so a clash here would hand one word to
    a scale-appended and a grocery-appended brand at once."""
    scale = set(range_ownership.added_words())
    grocery_words = range_ownership.added_words(range_ownership.GROCERY_STEMS)
    assert scale.isdisjoint(grocery_words)
    assert len(grocery_words) == len(set(grocery_words))


def test_a_grocery_brand_off_the_roster_is_refused_by_name(fresh, monkeypatch):
    monkeypatch.setitem(grocery_rows.TIER_BRANDS, ("zz-probe",), ("Unlisted Brand",))
    with pytest.raises(ValueError, match="Unlisted Brand"):
        grocery.range_names()
