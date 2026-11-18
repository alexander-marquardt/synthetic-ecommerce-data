"""A word kept out of the scale range-name deal moves only its owner (#1052, slice 2).

Guard: the scale deal's base brands were dealt ``pool[i::85]`` over the scale half *after* the
reserved words (authored ranges, brand words) and the excluded ones (``range_ownership.EXCLUDED``)
were dropped, so one more such word shifted every later name to the next brand (measured on main
e9651a66: reserving or excluding ``Caldden`` moved all 85 brands' 60 slots). The base brands are
now dealt over the whole half less the roster's frozen gaps, and a word skipped later only leaves
its owner's names. Metric: the brands other than the owner whose 60 slots change (0).
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import range_ownership, scale


def _slots(deal: range_ownership.Deal, brand: str) -> list[str]:
    return [deal.owned(brand, slot) for slot in range(scale.RANGE_SLOTS)]


@pytest.fixture(scope="module")
def built() -> tuple[list[dict], dict[tuple[str, str], list[str]]]:
    tpls = scale.templates()
    return tpls, scale.brand_pools(scale.derivable(tpls))


def _a_used_word(deal: range_ownership.Deal) -> tuple[str, str]:
    """A name a base brand holds at a slot a style takes, mid-roster, so many names follow it."""
    owner = deal.brands[len(deal.brands) // 3]
    return _slots(deal, owner)[7], owner


def _moved(before: range_ownership.Deal, after: range_ownership.Deal) -> list[str]:
    return [b for b in before.brands if _slots(before, b) != _slots(after, b)]


def test_an_authored_range_reserved_moves_only_its_owner(built):
    """A new authored row whose range is a scale-half word (the real ``scale._range_deal`` path)
    takes that word from its owner alone."""
    tpls, brands = built
    before = scale._range_deal(tpls, brands)
    word, owner = _a_used_word(before)
    authored = {"product_line": word, "brand": "", "attributes": []}
    after = scale._range_deal([*tpls, authored], brands)
    assert _moved(before, after) == [owner]
    assert after.of(owner) == tuple(n for n in before.of(owner) if n != word)
    assert after.owner(word) is None


def test_a_brand_word_reserved_moves_only_its_owner(built):
    """A brand whose own word is in the scale half (as ``Fenmere`` is) takes it from its owner."""
    tpls, brands = built
    before = scale._range_deal(tpls, brands)
    word, owner = _a_used_word(before)
    branded = {"brand": f"{word} Supply", "attributes": []}
    after = scale._range_deal([*tpls, branded], brands)
    assert _moved(before, after) == [owner]
    assert after.owner(word) is None


def test_an_excluded_word_moves_only_its_owner(built, monkeypatch):
    """A new ``PRODUCT_WORDS``, ``AUTHORED`` or series word that is in the scale half."""
    tpls, brands = built
    before = scale._range_deal(tpls, brands)
    word, owner = _a_used_word(before)
    monkeypatch.setattr(range_ownership, "EXCLUDED", range_ownership.EXCLUDED | {word})
    after = scale._range_deal(tpls, brands)
    assert _moved(before, after) == [owner]
    assert after.of(owner) == tuple(n for n in before.of(owner) if n != word)
