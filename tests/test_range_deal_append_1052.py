"""The scale range-name deal is append-stable (#1052).

Guard: a brand added to the scale build's range-name deal (``range_ownership.Deal`` built by
``scale._range_deal``) used to change the deal's brand count, so every brand's names moved and
styles in every department were retitled (measured on main dada7074: 85 of 85 brands moved when one
brand was added). The deal now holds an append-only roster: the brands dealt before #1052 keep that
deal, and a brand appended to the roster takes a block of names from stems outside the shuffled
pool. Metric: the existing brands whose 60 slots change when two brands are appended (0).
"""

from __future__ import annotations

import re
from dataclasses import replace

import pytest

from synthetic_ecommerce_data.domains.retail import range_ownership, scale

NEW = ("Probe Brand One", "Probe Brand Two")


def _slots(deal: range_ownership.Deal, brand: str) -> list[str]:
    return [deal.owned(brand, slot) for slot in range(scale.RANGE_SLOTS)]


@pytest.fixture(scope="module")
def built() -> tuple[list[dict], dict[tuple[str, str], list[str]]]:
    tpls = scale.templates()
    return tpls, scale.brand_pools(scale.derivable(tpls))


def _reserved(tpls: list[dict]) -> set[str]:
    """The words ``scale._range_deal`` keeps out of the deal: authored ranges and brand words."""
    reserved = {x for r in tpls if (x := scale._line(r))}
    return reserved | {w for r in tpls for w in re.findall(r"[A-Za-z]+", r["brand"])}


def _grown(
    tpls: list[dict], brands: dict, added: tuple[str, ...], monkeypatch: pytest.MonkeyPatch
) -> range_ownership.Deal:
    """The real scale deal (``scale._range_deal``) with ``added`` new to the build and appended
    to its roster, as a contributor adds a brand."""
    roster = range_ownership.SCALE
    monkeypatch.setattr(range_ownership, "SCALE", replace(roster, added=roster.added + added))
    return scale._range_deal(tpls, dict(brands) | {("zz-probe", "zz-probe"): list(added)})


def test_appending_brands_moves_no_existing_brands_range_names(built, monkeypatch):
    tpls, brands = built
    before = scale._range_deal(tpls, brands)
    after = _grown(tpls, brands, NEW, monkeypatch)
    moved = [b for b in before.brands if _slots(before, b) != _slots(after, b)]
    assert moved == []
    assert set(before.brands) <= set(after.brands)


def test_the_base_brands_keep_the_deal_they_had_before_1052(built, monkeypatch):
    """The roster's base is the brand set dealt round-robin before #1052, so today's titles and
    goldens stay put: the rostered deal is the plain round-robin over the same brands with the
    roster's gaps (the words skipped then) kept out, less the words skipped now (slice 2)."""
    tpls, brands = built
    rostered = scale._range_deal(tpls, brands)
    roster = range_ownership.SCALE
    assert rostered.brands == sorted({*roster.base, *roster.added})
    skip = _reserved(tpls) | range_ownership.EXCLUDED
    monkeypatch.setattr(range_ownership, "EXCLUDED", frozenset())
    plain = range_ownership.Deal("scale", roster.base, roster.gaps)
    expected = {b: tuple(n for n in plain.of(b) if n not in skip) for b in plain.brands}
    assert {b: rostered.of(b) for b in roster.base} == expected


def test_the_gaps_are_the_words_the_base_deal_skipped():
    """Every gap is a word of the scale half, so the frozen set names only what the base skipped."""
    assert range_ownership.SCALE.gaps <= set(range_ownership.whole_halves()["scale"])


def test_appended_brands_own_names_no_other_brand_or_half_holds(built, monkeypatch):
    tpls, brands = built
    deal = _grown(tpls, brands, NEW, monkeypatch)
    a, b = (set(deal.of(x)) for x in NEW)
    assert len(a) == len(b) == range_ownership.ADDED_SHARE
    assert a.isdisjoint(b)
    halves = range_ownership.halves()
    assert (a | b).isdisjoint(set(halves["scale"]) | set(halves["grocery"]))
    assert (a | b) <= set(range_ownership.candidates())
    assert all(deal.owner(n) == x for x in NEW for n in deal.of(x))


def test_a_brand_off_the_roster_is_refused_by_name(built):
    tpls, brands = built
    grown = dict(brands) | {("zz-probe", "zz-probe"): ["Unlisted Brand"]}
    with pytest.raises(ValueError, match="Unlisted Brand"):
        scale._range_deal(tpls, grown)


def test_appending_a_stem_only_appends_place_words(monkeypatch):
    """A block an added brand holds never moves when the added stems grow."""
    words = range_ownership.added_words()
    monkeypatch.setattr(range_ownership, "ADDED_STEMS", (*range_ownership.ADDED_STEMS, "Zyx"))
    grown = range_ownership.added_words()
    assert grown[: len(words)] == words
    assert len(grown) > len(words)
