"""The retail ``pattern`` facet spells each pattern one way (gen#324).

After gen#188 the facet held ``Stripe`` (from the colorways) and ``Striped`` (authored on a tote
bag, an umbrella, a melamine plate and a wallpaper): one pattern under two spellings, so a shopper
who ticked one missed the other. ``Checked`` beside ``Check`` and ``Spotted`` beside ``Spot`` were
the same defect. The guard reads two places: the attributes of every authored template (all of
them, so a spelling on a style the sampled build does not reach is still seen) and the facet of a
built catalog (where the colorway split adds its own values).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402 -- the prototype's own directory is its import root

#: The spellings the authored rows used before this change, written out so the test does not read
#: the module that fixes them.
RETIRED = ("striped", "checked", "spotted")


def stem(value: str) -> str:
    """A pattern value with its ending taken off: ``Striped`` and ``Stripe`` both give ``strip``.

    The ending is a plural ``s``/``es`` or a past ``ed``; a doubled last letter (``spotted``) and a
    final ``e`` (``stripe``) go with it."""
    word = value.strip().lower()
    for end in ("ed", "es", "s"):
        if word.endswith(end) and len(word) > len(end) + 2:
            word = word[: -len(end)]
            break
    if len(word) > 3 and word[-1] == word[-2]:
        word = word[:-1]
    return word[:-1] if word.endswith("e") else word


def endings_clash(values: set[str]) -> list[tuple[str, ...]]:
    """The groups of two or more values that share a stem."""
    groups: dict[str, set[str]] = {}
    for v in values:
        groups.setdefault(stem(v), set()).add(v.strip().lower())
    return sorted(tuple(sorted(g)) for g in groups.values() if len(g) > 1)


def _values(entries: list[dict[str, Any]]) -> set[str]:
    return {e["value"].lower() for e in entries if e["key"] == "pattern"}


def test_the_guard_sees_an_ending_and_leaves_distinct_words_alone() -> None:
    assert endings_clash({"stripe", "striped"}) == [("stripe", "striped")]
    assert endings_clash({"check", "checked"}) == [("check", "checked")]
    assert endings_clash({"spot", "spotted"}) == [("spot", "spotted")]
    assert endings_clash({"polka dot", "polka dots"}) == [("polka dot", "polka dots")]
    distinct = {"stripe", "breton stripe", "check", "gingham", "plain", "print", "marl", "lace"}
    assert endings_clash(distinct) == []


def test_no_authored_template_spells_a_pattern_a_second_way() -> None:
    values: set[str] = set()
    for tpl in scale.templates():
        values |= _values(tpl["attributes"])
    assert endings_clash(values) == []
    assert sorted(set(RETIRED) & values) == []


@pytest.fixture(scope="module")
def nested() -> list[dict[str, Any]]:
    built = scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)
    return scale.documents(built)


def test_the_built_pattern_facet_has_no_two_values_that_differ_only_by_an_ending(
    nested: list[dict[str, Any]],
) -> None:
    values: set[str] = set()
    for doc in nested:
        values |= _values(doc["attributes"])
        for variant in doc["variants"]:
            values |= _values(variant["attributes"])
    assert "stripe" in values
    assert endings_clash(values) == []
    assert sorted(set(RETIRED) & values) == []
