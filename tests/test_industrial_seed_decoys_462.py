"""Every industrial seed query has text-match decoys the category policy can remove (#462).

A decoy for a seed is a real product whose title holds all the seed's words and whose category
path does not name the seed's own category. The table is ``domains/industrial/seed_decoys.py``;
each decoy is one type module under ``domains/industrial/product_types/decoys/``.
"""

from __future__ import annotations

import re
from functools import cache
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import seed_decoys
from synthetic_ecommerce_data.domains.industrial.generate import generate

DECOY_DIR = (
    Path(__file__).resolve().parents[1]
    / "src/synthetic_ecommerce_data/domains/industrial/product_types/decoys"
)

#: The queries the issue's four tables name; dropping one from the seed table must not pass.
ISSUE_SEEDS = (
    "hex nuts", "lock nuts", "m10 washers", "stainless steel hex bolts", "7/16-14 hex head bolts",
    "m12x1.75 socket cap screws", "m6x1 set screws", "1/4-20 screws", "dowel pins",
    "retaining rings", "ball bearings", "6203 bearing", "roller chain", "sprockets", "shackles",
    "1/2 endmill", "3/8 square endmill", "2.5mm end mill", "25mm end mill", "3/8 inch drill bit",
    "carbide drill bit", "spiral flute tap", "flap discs", "cut-off wheels", "hammers",
    "screwdrivers", "hex keys", "bar stock", "o-rings", "screws", "bolts", "washers", "nuts",
)
ITEM_NOUNS = ("o-rings", "screws", "bolts", "washers", "nuts")


def _seed_id(query: str) -> str:
    return re.sub(r"[^a-z0-9.]+", "-", query)


SEEDS = [pytest.param(query, id=_seed_id(query)) for query in seed_decoys.SEED_TERMS]


@cache
def _skus_by_type() -> dict[str, tuple[dict, ...]]:
    """Every emitted SKU row, by the type key that made it (a decoy type is one product line)."""
    rows: dict[str, list[dict]] = {}
    for row in emit.iter_flat(generate(GeneratorConfig(lines=1, new_type_share={}))):
        rows.setdefault(row["product_type"], []).append(row)
    return {key: tuple(value) for key, value in rows.items()}


def _holds(term: str, title: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(term)}(?:e?s)?(?!\w)", title, re.IGNORECASE) is not None


def _serves(query: str, key: str) -> bool:
    """One SKU's title holds every term and no SKU's category path holds a forbidden phrase."""
    terms, forbidden = seed_decoys.SEED_TERMS[query]
    skus = _skus_by_type()[key]
    paths = [" / ".join(sku["category_path"]).lower() for sku in skus]
    if any(phrase in path for phrase in forbidden for path in paths):
        return False
    return any(all(_holds(term, sku["title"]) for term in terms) for sku in skus)


@pytest.mark.parametrize(
    ("term", "title", "held"),
    [
        pytest.param("screw", "Thread Repair Insert Kit for 1/4-20 Screws", True, id="plural"),
        pytest.param("screw", "Magnetic Screwdriver Bit Holder, 2 in", False, id="longer-word"),
        pytest.param("nut", "Hex Nut Driver, 1/4 in", True, id="singular"),
        pytest.param("25 mm", "End Mill Storage Rack, 2.5 mm to 25 mm", True, id="size"),
        pytest.param("25 mm", "Tool Storage Rack, 125 mm", False, id="inside-a-number"),
        pytest.param("o-ring", "Coupling with Viton O-Ring Seal, 1/4 in", True, id="hyphen"),
    ],
)
def test_a_term_is_a_whole_word_with_an_optional_plural(term, title, held):
    assert _holds(term, title) is held


def test_the_seed_table_names_every_query_of_the_issue():
    assert set(ISSUE_SEEDS) <= set(seed_decoys.SEED_TERMS)
    assert set(ITEM_NOUNS) <= set(seed_decoys.SEED_TERMS)
    assert set(seed_decoys.SEED_DECOYS) == set(seed_decoys.SEED_TERMS)


def test_the_sections_partition_the_seeds():
    listed = [query for queries in seed_decoys.SECTIONS.values() for query in queries]
    assert sorted(listed) == sorted(seed_decoys.SEED_TERMS)


@pytest.mark.parametrize("query", SEEDS)
def test_each_seed_has_two_decoy_lines(query):
    keys = seed_decoys.SEED_DECOYS[query]
    assert len(set(keys)) == len(keys), query
    serving = [key for key in keys if _serves(query, key)]
    assert len(serving) >= 2, (query, serving)
    # a listed type that does not serve the seed is a table error, not an extra
    assert serving == list(keys), (query, set(keys) - set(serving))


@pytest.mark.parametrize("noun", ITEM_NOUNS)
def test_each_item_noun_has_two_decoy_lines(noun):
    assert len(seed_decoys.SEED_DECOYS[noun]) >= 2, noun


def test_every_decoy_type_serves_a_seed():
    on_disk = {path.stem for path in DECOY_DIR.glob("*.py") if path.stem != "__init__"}
    claimed = {key for keys in seed_decoys.SEED_DECOYS.values() for key in keys}
    assert on_disk, "no decoy module found"
    assert on_disk == claimed, (sorted(on_disk - claimed), sorted(claimed - on_disk))
