"""No industrial product holds the misspelling `pliars`: it is a card game's name (gen#1130).

The R&I demo serves a misspelled search's literal hits. It offers the common spelling only when
there are 3 Best results or fewer and the common spelling is at least 5 times more common. #944
put `pliars` in the titles of 3 industrial pliers ("Conduit Pliars"), which read as a typo in the
data. gen#1130 moved the word to Pliars, a retail bluffing card game of 3 products
(``feature_decoys/misspelled_words_944.py``), so no pliers line may hold it, and the industrial
pliers are the common spelling the suggestion offers. See
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
GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog" / "flat.jsonl"


def _text(line) -> str:
    skus = " ".join(f"{sku.title} {sku.description}" for sku in line.children)
    return f"{line.title} {line.brand} {skus}"


@pytest.fixture(scope="module", params=(None, 20_000), ids=("default", "lines-20000"))
def built(request):
    """The two pliers types #944 planted the word on, at the default size and at a larger one."""
    config = GeneratorConfig()
    if request.param is not None:
        config = replace(config, lines=request.param)
    return generate(config, types=TYPES).lines


def test_no_pliers_line_holds_the_misspelling_at_any_size(built):
    assert built
    held = [line.title for line in built if WORD.search(_text(line))]
    assert held == []


def test_each_pliers_type_builds_its_own_line_only(built):
    """The one-SKU misspelled lines are gone: each type builds its breadth line and no more."""
    assert sorted(line.type_key for line in built) == sorted(TYPES)


def _golden() -> list[dict]:
    return [json.loads(raw) for raw in GOLDEN.read_text().splitlines()]


def _row_text(row: dict) -> str:
    """A flat (SKU) row's searched text: its title, brand, description and ``text``."""
    fields = ("title", "parent_title", "brand", "description", "text")
    return " ".join(str(row.get(f, "")) for f in fields)


def test_the_golden_catalogue_holds_no_pliars():
    held = [row["title"] for row in _golden() if WORD.search(_row_text(row))]
    assert held == []


def test_the_golden_catalogue_sells_pliers_five_times_the_card_games_three():
    """The suggestion needs the common spelling 5 times more common than the 3 Pliars games."""
    pliers = re.compile(r"\bpliers\b", re.IGNORECASE)
    assert sum(1 for row in _golden() if pliers.search(_row_text(row))) >= 5 * 3
