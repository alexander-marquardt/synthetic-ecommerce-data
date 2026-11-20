"""A Tools decoy says its tool noun in its own copy, not only in its title (#1062).

A real end mill holds ``end mill`` in its title, its category leaf (``End mills``) and its text. A
decoy whose title is its only mention ranked past 500 on ``1/2 endmill``, ``2.5mm end mill``,
``25mm end mill``, ``3/8 inch drill bit``, ``flap discs`` and ``hex keys`` with policies off, so the
demo's first page showed no decoy for the category policy to remove. Each decoy type that
``seed_decoys.SEED_DECOYS`` lists under a seed whose terms hold ``end mill``, ``drill bit``,
``flap disc`` or ``hex key`` therefore has use lines, as the item-noun decoys of #951 do: what the
product does, written the way a catalogue writes it, naming the noun the way the product uses it.
The copy reaches the searchable ``text`` (``emit._searchable_text``).
"""

from __future__ import annotations

import re
from functools import cache

import pytest

from synthetic_ecommerce_data.core import emit, voice
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import seed_decoys
from synthetic_ecommerce_data.domains.industrial.generate import generate

TOOL_NOUNS = ("end mill", "drill bit", "flap disc", "hex key")
#: The seeds of the issue's Deliverable 1; dropping one from the seed table must not pass.
ISSUE_SEEDS = (
    "1/2 endmill",
    "3/8 square endmill",
    "2.5mm end mill",
    "25mm end mill",
    "3/8 inch drill bit",
    "carbide drill bit",
    "flap discs",
    "hex keys",
)
#: Fewer than this many mentions outside the title leaves the decoy under the real tools.
MENTIONS = 2


def _noun(query: str) -> str | None:
    """The tool noun one of the seed's terms holds, or None for a seed of another noun."""
    terms, _forbidden = seed_decoys.SEED_TERMS[query]
    return next((noun for noun in TOOL_NOUNS for term in terms if noun in term), None)


def _cases() -> dict[str, str]:
    """Each decoy type of a tool-noun seed, with the noun its copy names."""
    cases: dict[str, str] = {}
    for query, keys in seed_decoys.SEED_DECOYS.items():
        noun = _noun(query)
        if noun is None:
            continue
        for key in keys:
            assert cases.setdefault(key, noun) == noun, (key, query)
    return cases


CASES = [pytest.param(key, noun, id=key) for key, noun in sorted(_cases().items())]


def _mentions(noun: str, text: str) -> int:
    """Whole-word mentions with an optional plural, as the #462 table matches a title."""
    return len(re.findall(rf"(?<!\w){re.escape(noun)}(?:e?s)?(?!\w)", text, re.IGNORECASE))


@cache
def _skus_by_type() -> dict[str, tuple[dict, ...]]:
    rows: dict[str, list[dict]] = {}
    for row in emit.iter_flat(generate(GeneratorConfig(lines=1, new_type_share={}))):
        rows.setdefault(row["product_type"], []).append(row)
    return {key: tuple(value) for key, value in rows.items()}


def test_every_tool_noun_seed_lists_its_decoys():
    for query in ISSUE_SEEDS:
        assert _noun(query), query
        assert seed_decoys.SEED_DECOYS[query], query
    assert set(_cases().values()) == set(TOOL_NOUNS)


@pytest.mark.parametrize(
    ("noun", "text", "count"),
    [
        pytest.param("end mill", "Clamps an end mill's flat; holds end mills", 2, id="possessive"),
        pytest.param("drill bit", "Regrinds drill bits and a drill bit", 2, id="plural"),
        pytest.param("hex key", "Holds hex keyboards", 0, id="longer-word"),
    ],
)
def test_a_mention_is_a_whole_word_with_an_optional_plural(noun, text, count):
    assert _mentions(noun, text) == count


@pytest.mark.parametrize(("key", "noun"), CASES)
def test_each_use_line_names_the_noun_twice(key, noun):
    lines = voice.USE_LINES.get(key)
    assert lines, f"{key} falls back to the generic use lines"
    for line in lines:
        assert _mentions(noun, line) >= MENTIONS, (key, line)


@pytest.mark.parametrize(("key", "noun"), CASES)
def test_each_sku_text_names_the_noun_twice_outside_its_title(key, noun):
    skus = _skus_by_type()[key]
    assert skus, key
    for sku in skus:
        rest = sku["text"].replace(sku["title"], "", 1)
        assert _mentions(noun, rest) >= MENTIONS, (key, sku["sku"], rest)
