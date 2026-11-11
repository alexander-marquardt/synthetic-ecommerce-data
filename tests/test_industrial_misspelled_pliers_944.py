"""The industrial build sells 3 pliers whose text holds the misspelling `pliars` (#944).

The R&I demo serves a misspelled search's literal hits. It offers the common spelling only when
there are 3 Best results or fewer and the common spelling is at least 5 times more common. With
3 products, `pliars` shows the hits and the suggestion "pliers". The misspelling is product text
only: no category, type label or attribute holds it, so no vocabulary learns it. See
docs/retail-prototype/misspelled-words-944.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial.generate import generate

WORD = re.compile(r"\bpliars\b", re.IGNORECASE)
TYPES = ("conduit_pliers", "snap_ring_pliers")
GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog" / "nested.jsonl"


def _text(line) -> str:
    skus = " ".join(f"{sku.title} {sku.description}" for sku in line.children)
    return f"{line.title} {line.brand} {skus}"


@pytest.fixture(scope="module", params=(None, 20_000), ids=("default", "lines-20000"))
def built(request):
    """The two pliers types, at the default size and at a larger one."""
    config = GeneratorConfig()
    if request.param is not None:
        config = replace(config, lines=request.param)
    return generate(config, types=TYPES).lines


def test_three_pliers_hold_the_misspelling_at_any_size(built):
    held = [line for line in built if WORD.search(_text(line))]
    assert len(held) == 3, [line.title for line in held]
    for line in held:
        assert line.type_key in TYPES
        assert "Pliers" in line.category, line.category
        same_type = [other for other in built if other.type_key == line.type_key]
        (own,) = [other for other in same_type if not WORD.search(_text(other))]
        assert line.category == own.category
        assert WORD.search(line.children[0].title), "the misspelling is in the title"


def test_the_misspelling_is_product_text_only(built):
    for line in built:
        assert not WORD.search(" ".join(line.category)), line.category
        assert not WORD.search(line.type_label), line.type_label
        attributes = [*line.attributes, *(a for sku in line.children for a in sku.attributes)]
        for attribute in attributes:
            assert not WORD.search(f"{attribute.name} {attribute.value}"), attribute


def test_no_misspelled_line_names_a_seed_noun(built):
    """A seed decoy (#462) holds `nut` or `retaining ring`; these lines must not add to them."""
    for line in built:
        if WORD.search(_text(line)):
            title = line.children[0].title.lower()
            assert "nut" not in title and "retaining ring" not in title, title


def test_the_golden_catalogue_sells_the_three():
    rows = [json.loads(raw) for raw in GOLDEN.read_text().splitlines()]
    held = [
        row
        for row in rows
        if WORD.search(json.dumps([row["title"], row["brand"], row.get("description", "")]))
        or any(WORD.search(f"{v['title']} {v['description']}") for v in row.get("variants", ()))
    ]
    assert len(held) == 3, [row["title"] for row in held]
    assert {row["product_type"] for row in held} == set(TYPES)
    for row in held:
        assert row["category_path"][:3] == ["Tools", "Hand tools", "Pliers"], row["category_path"]
