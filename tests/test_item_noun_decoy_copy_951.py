"""An item-noun decoy says its noun in its own copy, not only in its title (#951).

A plain O-ring holds ``o-ring`` in its title, its category leaf and its text. A decoy whose title is
its only mention ranked 56th and lower on ``o-rings`` with policies off, so the demo's first page
showed no decoy for the category policy to remove. Each decoy type that
``seed_decoys.SEED_DECOYS`` lists under an item noun (``o-rings``, ``screws``, ``bolts``,
``washers``, ``nuts``) therefore has use lines: what the product does, written the way a catalogue
writes it, naming the noun the way the product uses it. The copy reaches the searchable ``text``
(``emit._searchable_text``). The record's ``description`` keeps the reference grammar (#937).
"""

from __future__ import annotations

import re
from functools import cache

import pytest

from synthetic_ecommerce_data.core import emit, voice
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import seed_decoys
from synthetic_ecommerce_data.domains.industrial.generate import generate

ITEM_NOUNS = ("o-rings", "screws", "bolts", "washers", "nuts")
#: Fewer than this many mentions outside the title leaves the decoy under the plain items.
MENTIONS = 2

CASES = [
    pytest.param(query, key, id=f"{query}-{key}")
    for query in ITEM_NOUNS
    for key in seed_decoys.SEED_DECOYS[query]
]


def _noun(query: str) -> str:
    (term,), _forbidden = seed_decoys.SEED_TERMS[query]
    return term


def _mentions(noun: str, text: str) -> int:
    """Whole-word mentions with an optional plural, as the #462 table matches a title."""
    return len(re.findall(rf"(?<!\w){re.escape(noun)}(?:e?s)?(?!\w)", text, re.IGNORECASE))


@cache
def _skus_by_type() -> dict[str, tuple[dict, ...]]:
    rows: dict[str, list[dict]] = {}
    for row in emit.iter_flat(generate(GeneratorConfig(lines=1, new_type_share={}))):
        rows.setdefault(row["product_type"], []).append(row)
    return {key: tuple(value) for key, value in rows.items()}


def test_every_item_noun_lists_its_decoys():
    for query in ITEM_NOUNS:
        assert seed_decoys.SEED_DECOYS[query], query
        assert _noun(query), query


@pytest.mark.parametrize(("query", "key"), CASES)
def test_each_use_line_names_the_noun_twice(query, key):
    lines = voice.USE_LINES.get(key)
    assert lines, f"{key} falls back to the generic use lines"
    noun = _noun(query)
    for line in lines:
        assert _mentions(noun, line) >= MENTIONS, (key, line)


@pytest.mark.parametrize(("query", "key"), CASES)
def test_each_sku_text_names_the_noun_twice_outside_its_title(query, key):
    noun = _noun(query)
    skus = _skus_by_type()[key]
    assert skus, key
    for sku in skus:
        rest = sku["text"].replace(sku["title"], "", 1)
        assert _mentions(noun, rest) >= MENTIONS, (key, sku["sku"], rest)
