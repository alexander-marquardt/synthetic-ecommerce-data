"""Every nested attribute entry meets the data contract elastic/prism#9935 rules.

The maintainer's rulings (2026-10-01, restated on #34; tracked here as #42), whose
engine side is elastic/prism#9938:

* every entry carries a REQUIRED machine ``key`` (``^[a-z0-9][a-z0-9_]*$``) beside its
  display ``name``. The Engine discovers attributes from that key, so a missing one is
  an attribute no facet, click or policy can reach;
* a MEASURED value is fully split: ``value`` is the bare magnitude (``1/2``, ``0.5``)
  with no unit marker, ``unit_code`` is the only place the unit lives, and
  ``value_canonical`` is derived from the pair. A count is measured too (``C62``);
* one shape across the whole catalog: no ``1/2"`` / ``1/2 in`` / ``1/2 in.`` inside a
  nested value. Composite designators (``1/4-20``, ``M10x1.5``) stay unitless text.

Checked on a fresh SMALL build (both serialisations) AND on the committed
``golden-catalog/nested.jsonl``, so a regeneration from a broken generator is red too.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.config import SMALL
from synthetic_industrial_products.catalog.entry import published, split
from synthetic_industrial_products.catalog.generate import generate

GOLDEN_NESTED = Path(__file__).resolve().parents[1] / "golden-catalog" / "nested.jsonl"

KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]*$")

#: A bare magnitude: an integer, a decimal, a fraction or a mixed number (``1-1/4``).
#: No thousands separator -- the Engine's exact parser expects one already removed.
MAGNITUDE = re.compile(r"^(?:[0-9]+-[0-9]+/[0-9]+|[0-9]+/[0-9]+|[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$")

#: A magnitude with a unit written into it: the shape the ruling forbids in a value.
MAGNITUDE_WITH_UNIT = re.compile(
    r"^\s*(?:[0-9]+(?:[ -][0-9]+)?/[0-9]+|[0-9][0-9,]*(?:\.[0-9]+)?|\.[0-9]+)\s*"
    r"(?:mm|in|in\.|\"|Degrees|oz|lbf|lb)\s*$"
)

#: The size of one unit in its kind's canonical unit -- millimetres, grams, degrees,
#: one, rpm, pound-force -- the canonical units the industrial deployment declares.
CANONICAL_PER_UNIT: dict[str, Fraction] = {
    "INH": Fraction(127, 5),
    "MMT": Fraction(1),
    "DD": Fraction(1),
    "ONZ": Fraction(45359237, 1600000),
    "LBR": Fraction(45359237, 100000),
    "C62": Fraction(1),
    "RPM": Fraction(1),
    "C78": Fraction(1),
}

#: Attributes that are counts, so they carry ``C62`` with a bare value.
COUNTS = ("Number of Flutes", "Grit", "Package Quantity", "Number of Pieces")

#: Names a document already uses as a top-level column: a nested key equal to one
#: collides with a declared field, which the Engine's boot census reports as a data
#: error. ``Series`` is namespaced, as the field map already names it.
TOP_LEVEL_NAMES = frozenset({"series", "brand", "title", "description", "sku", "product_id"})


def _exact(magnitude: str) -> Fraction:
    if "-" in magnitude:
        whole, frac = magnitude.split("-")
        return int(whole) + Fraction(frac)
    return Fraction(magnitude)


def _entries(doc: dict[str, Any]) -> Iterator[dict[str, Any]]:
    yield from doc["attributes"]
    for variant in doc.get("variants", ()):
        yield from variant["attributes"]


def _fresh() -> list[dict[str, Any]]:
    catalog = generate(SMALL)
    return list(emit.iter_nested(catalog)) + list(emit.iter_flat(catalog))


def _golden() -> list[dict[str, Any]]:
    with GOLDEN_NESTED.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


SOURCES = {"fresh SMALL build": _fresh, "committed golden nested.jsonl": _golden}


@pytest.fixture(scope="module", params=sorted(SOURCES))
def entries(request: pytest.FixtureRequest) -> list[dict[str, Any]]:
    return [entry for doc in SOURCES[request.param]() for entry in _entries(doc)]


def test_every_entry_carries_a_well_formed_key_and_a_display_name(entries):
    missing = [e for e in entries if not KEY_PATTERN.fullmatch(str(e.get("key") or ""))]
    assert not missing, f"{len(missing)} entries without a well-formed key, e.g. {missing[:3]}"
    unnamed = [e for e in entries if not isinstance(e.get("name"), str) or not e["name"]]
    assert not unnamed, f"{len(unnamed)} entries without a display name, e.g. {unnamed[:3]}"
    assert all(isinstance(e.get("value"), str) and e["value"] for e in entries)


def test_one_key_names_one_attribute_and_none_collides_with_a_top_level_column(entries):
    names_by_key: dict[str, set[str]] = {}
    for entry in entries:
        names_by_key.setdefault(entry["key"], set()).add(entry["name"])
    merged = {k: v for k, v in names_by_key.items() if len(v) > 1}
    assert not merged, f"one key carries several attributes: {merged}"
    assert not set(names_by_key) & TOP_LEVEL_NAMES, set(names_by_key) & TOP_LEVEL_NAMES
    assert names_by_key.get("attr_series", {"Series"}) == {"Series"}


def test_no_value_carries_its_unit_inside(entries):
    unsplit = [e for e in entries if MAGNITUDE_WITH_UNIT.match(e["value"])]
    assert not unsplit, f"{len(unsplit)} measured values are not split, e.g. {unsplit[:3]}"


def test_a_measured_value_carries_magnitude_unit_code_and_value_canonical(entries):
    measured = [e for e in entries if "unit_code" in e or "value_canonical" in e]
    assert measured, "no entry carries a unit code: the measurements were not split"
    for entry in measured:
        assert MAGNITUDE.fullmatch(entry["value"]), entry
        assert entry["unit_code"] in CANONICAL_PER_UNIT, entry
        expected = float(_exact(entry["value"]) * CANONICAL_PER_UNIT[entry["unit_code"]])
        assert entry["value_canonical"] == pytest.approx(expected, rel=1e-12, abs=0), entry


def test_counts_carry_c62_and_the_old_inch_number_is_gone(entries):
    for entry in entries:
        assert "value_num" not in entry, entry
        if entry["name"] in COUNTS and MAGNITUDE.fullmatch(entry["value"]):
            assert entry.get("unit_code") == "C62", entry


def _golden_pair() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    flat = GOLDEN_NESTED.with_name("flat.jsonl")
    with flat.open(encoding="utf-8") as handle:
        return _golden(), [json.loads(line) for line in handle]


def _fresh_pair() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    catalog = generate(SMALL)
    return list(emit.iter_nested(catalog)), list(emit.iter_flat(catalog))


#: The value parts of a nested entry, which the published spelling must split into.
PARTS = ("value", "unit_code", "value_canonical")


@pytest.mark.parametrize("source", [_golden_pair, _fresh_pair], ids=["golden", "fresh SMALL"])
def test_every_nested_entrys_published_spelling_is_its_skus_flat_facet(source):
    """The join a drawing and the spelling tests rely on is complete and agrees.

    A nested entry carries no spelling (Option C on #42): a consumer that prints
    one reads it from the SKU's flat ``facets``, walking the line's entries then
    the SKU's. That join must account for every flat value -- none left over,
    none missing -- and each spelling must split back into the very magnitude
    and unit the nested entry carries, or the two documents disagree on a value.
    """
    nested, flat = source()
    facets = {doc["sku"]: doc["facets"] for doc in flat}
    joined = 0
    for parent in nested:
        for variant in parent["variants"]:
            entries = [*parent["attributes"], *variant["attributes"]]
            pairs = published(entries, facets[variant["sku"]])
            assert len(pairs) == sum(map(len, facets[variant["sku"]].values())), variant["sku"]
            for entry, (_, spelling) in zip(entries, pairs, strict=True):
                parts = {
                    k: entry[k] for k in ("value", "unit_code", "value_canonical") if k in entry
                }
                assert split(entry["name"], spelling, entry.get("unit_code")) == parts, (
                    variant["sku"],
                    spelling,
                    entry,
                )
                joined += 1
    assert joined > 1000
