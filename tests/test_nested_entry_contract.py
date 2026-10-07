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

from industrial_units import Unit, pinned
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

#: Each unit code's kind and exact size, as the industrial deployment declares
#: them (the pinned ``canonical_units`` block; see :mod:`industrial_units`). Read,
#: never written here: ``TPI`` is a reciprocal LENGTH by ruling (elastic/prism#9877),
#: and a test that wrote its own size could overrule that unseen.
#:
#: ``LBR`` and ``FOT`` are the codes this catalog writes that the deployment does
#: not declare, so their sizes are stated here: ``LBR`` on one row
#: (elastic/prism-industrial-products#164), ``FOT`` on a roller chain's
#: ``Length`` (elastic/prism-industrial-products#170).
UNITS: dict[str, Unit] = {
    **pinned(),
    "LBR": Unit("mass", Fraction(45359237, 100000)),
    "FOT": Unit("length", Fraction(1524, 5)),
}

#: The one modelled defect that puts a second quantity under a key on purpose: an
#: angle published in INCHES (``Helix Angle = 42"``, measured at 4.7% of the
#: reference records carrying an angle). Its exact values and unit are the
#: generator's own (``Generator._corrupt_angle``), so a length that reaches an
#: angle key any other way -- another value, or the same value in ``mm`` -- is red.
ANGLE_DEFECT = {
    "keys": frozenset({"helix_angle", "point_angle"}),
    "entries": frozenset(("INH", v) for v in ("42", "1", "1-1/4", "2", "1-5/8")),
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
        assert entry["unit_code"] in UNITS, entry
        expected = float(UNITS[entry["unit_code"]].canonical(_exact(entry["value"])))
        assert entry["value_canonical"] == expected, entry


def test_the_lbr_size_stated_here_redeclares_no_pinned_unit():
    assert "LBR" not in pinned()


def test_the_fot_size_stated_here_redeclares_no_pinned_unit():
    assert "FOT" not in pinned()


def _quantity(entry: dict[str, Any]) -> str | None:
    """What an entry measures: its unit's dimension, ``bare number`` for a magnitude
    with no unit, ``None`` for text such as a designator (``M10``, ``1/4-20``)."""
    if "unit_code" in entry:
        return UNITS[entry["unit_code"]].kind
    return "bare number" if MAGNITUDE.fullmatch(entry["value"]) else None


def test_every_keys_measured_entries_share_one_unit_dimension(entries):
    """No key mixes quantity kinds, so a facet over it never shows ``2 lb`` beside ``440 lbf``.

    Kinds are the deployment's: ``TPI``, ``INH`` and ``MMT`` are all ``length``.
    A bare number with no unit counts as a quantity of its own: under a key whose
    other entries are millimetres it is a figure no shopper can read. The angle
    defect is the single exception, and it must actually occur.
    """
    by_key: dict[str, dict[str, set[tuple[str, str]]]] = {}
    for entry in entries:
        quantity = _quantity(entry)
        if quantity is not None:
            by_key.setdefault(entry["key"], {}).setdefault(quantity, set()).add(
                (entry.get("unit_code", ""), entry["value"])
            )
    mixed = {}
    defect_seen = False
    for key, quantities in by_key.items():
        if len(quantities) < 2:
            continue
        if (
            key in ANGLE_DEFECT["keys"]
            and set(quantities) == {"plane_angle", "length"}
            and quantities["length"] <= ANGLE_DEFECT["entries"]
        ):
            defect_seen = True
            continue
        mixed[key] = {q: sorted(v)[:5] for q, v in quantities.items()}
    assert not mixed, f"keys whose entries measure different quantities: {mixed}"
    assert defect_seen, "the angle defect no longer occurs: drop its exception"


def test_counts_carry_c62_and_the_old_inch_number_is_gone(entries):
    for entry in entries:
        assert "value_num" not in entry, entry
        if entry["name"] in COUNTS and MAGNITUDE.fullmatch(entry["value"]):
            assert entry.get("unit_code") == "C62", entry


#: A published spelling, worked out by hand: ``(name, spelling, bare_unit)`` and the
#: exact parts it must split into. Independent of :func:`split` -- every magnitude,
#: code and canonical below was written down, not computed by the code under test --
#: so a ``split()`` that rewrote ``1/2`` as ``0.5`` is red here even when the golden
#: catalog was regenerated from it.
SPLIT_ORACLE: tuple[tuple[str, str, str | None, dict[str, Any]], ...] = (
    ("Drive Size", '1/2"', None, {"value": "1/2", "unit_code": "INH", "value_canonical": 12.7}),
    (
        "Milling Dia.",
        '3/16"',
        None,
        {"value": "3/16", "unit_code": "INH", "value_canonical": 4.7625},
    ),
    (
        "Overall Length",
        '1-1/2"',
        None,
        {"value": "1-1/2", "unit_code": "INH", "value_canonical": 38.1},
    ),
    (
        "Overall Length",
        "1 1/4 in",
        None,
        {"value": "1-1/4", "unit_code": "INH", "value_canonical": 31.75},
    ),
    (
        "Width Across Flats",
        "1-1/8 in",
        None,
        {"value": "1-1/8", "unit_code": "INH", "value_canonical": 28.575},
    ),
    (
        "Width Across Flats",
        "11/32 in.",
        None,
        {"value": "11/32", "unit_code": "INH", "value_canonical": 8.73125},
    ),
    (
        "Neck Length",
        '0.2469"',
        None,
        {"value": "0.2469", "unit_code": "INH", "value_canonical": 6.27126},
    ),
    ("Height", '.25"', None, {"value": ".25", "unit_code": "INH", "value_canonical": 6.35}),
    (
        "Decimal Equivalent",
        "0.4844",
        None,
        {"value": "0.4844", "unit_code": "INH", "value_canonical": 12.30376},
    ),
    ("Milling Dia.", "2mm", None, {"value": "2", "unit_code": "MMT", "value_canonical": 2.0}),
    (
        "Width Across Flats",
        "5.5 mm",
        None,
        {"value": "5.5", "unit_code": "MMT", "value_canonical": 5.5},
    ),
    ("Pitch", "0.5", "MMT", {"value": "0.5", "unit_code": "MMT", "value_canonical": 0.5}),
    # A thread count's canonical is its pitch LENGTH (elastic/prism#9877): 127/5 / n
    # mm. 13 does not terminate, and is the nearest float to 127/65, like any value.
    (
        "Threads per Inch",
        "32",
        "TPI",
        {"value": "32", "unit_code": "TPI", "value_canonical": 0.79375},
    ),
    (
        "Threads per Inch",
        "20",
        "TPI",
        {"value": "20", "unit_code": "TPI", "value_canonical": 1.27},
    ),
    (
        "Threads per Inch",
        "13",
        "TPI",
        {"value": "13", "unit_code": "TPI", "value_canonical": 1.9538461538461538},
    ),
    (
        "Helix Angle",
        "38 Degrees",
        None,
        {"value": "38", "unit_code": "DD", "value_canonical": 38.0},
    ),
    ("Helix Angle", '42"', None, {"value": "42", "unit_code": "INH", "value_canonical": 1066.8}),
    (
        "Dynamic Load Capacity",
        "1,070 lbf",
        None,
        {"value": "1070", "unit_code": "C78", "value_canonical": 1070.0},
    ),
    (
        "Static Load Capacity",
        "440 lbf",
        None,
        {"value": "440", "unit_code": "C78", "value_canonical": 440.0},
    ),
    (
        "Capacity",
        "100 lb",
        None,
        {"value": "100", "unit_code": "LBR", "value_canonical": 45359.237},
    ),
    (
        "Head Weight",
        "6 oz",
        None,
        {"value": "6", "unit_code": "ONZ", "value_canonical": 170.09713875},
    ),
    ("Max. RPM", "6,900", None, {"value": "6900", "unit_code": "RPM", "value_canonical": 6900.0}),
    ("Number of Flutes", "2", None, {"value": "2", "unit_code": "C62", "value_canonical": 2.0}),
    ("Thread Size", "1/4-20", None, {"value": "1/4-20"}),
    ("Thread Size", "M10x1.5", None, {"value": "M10x1.5"}),
    ("Size", "M6", None, {"value": "M6"}),
    # A bare number whose unit nothing states stays text: no unit is guessed.
    ("Pitch", "32", None, {"value": "32"}),
)


@pytest.mark.parametrize(("name", "spelling", "bare_unit", "parts"), SPLIT_ORACLE)
def test_split_gives_the_hand_worked_parts_of_each_published_spelling(
    name, spelling, bare_unit, parts
):
    assert split(name, spelling, bare_unit) == parts


#: The test's OWN reading of a published spelling, written apart from
#: :mod:`~synthetic_industrial_products.catalog.entry` so the round trip below is
#: not judged by the function that produced the entries.
_ORACLE_NUMBER = (
    r"(?:[0-9]+[ -][0-9]+/[0-9]+|[0-9]+/[0-9]+"
    r"|[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?|\.[0-9]+)"
)
_ORACLE_SPELLING = re.compile(
    rf"^(?P<number>{_ORACLE_NUMBER})(?:\s*(?P<suffix>lbf|lb|in\.|in|mm|ft|oz|Degrees|\"))?$"
)
ORACLE_UNIT_FOR_SUFFIX = {
    '"': "INH",
    "in": "INH",
    "in.": "INH",
    "mm": "MMT",
    "ft": "FOT",
    "Degrees": "DD",
    "oz": "ONZ",
    "lbf": "C78",
    "lb": "LBR",
}

#: The unit each key's BARE number is in. Only these keys publish a bare number
#: that is a measurement; any other bare number stays text. Keyed by the entry's
#: key, never by the unit the entry itself claims, so an entry cannot certify its
#: own unit.
ORACLE_BARE_UNIT_FOR_KEY = {
    "number_of_flutes": "C62",
    "grit": "C62",
    "package_quantity": "C62",
    "number_of_pieces": "C62",
    "max_rpm": "RPM",
    "decimal_equivalent": "INH",
    "pitch": "MMT",
    "threads_per_inch": "TPI",
}


#: The value parts of a nested entry, which the published spelling must split into.
PARTS = ("value", "unit_code", "value_canonical")


def _oracle_parts(key: str, spelling: str) -> dict[str, Any]:
    """The parts a published spelling must split into, worked out without ``split()``."""
    match = _ORACLE_SPELLING.fullmatch(spelling)
    if match is None:
        return {"value": spelling}
    suffix = match["suffix"]
    unit = ORACLE_UNIT_FOR_SUFFIX[suffix] if suffix else ORACLE_BARE_UNIT_FOR_KEY.get(key)
    if unit is None:
        return {"value": spelling}
    magnitude = match["number"].replace(",", "")
    if " " in magnitude:
        magnitude = magnitude.replace(" ", "-")
    exact = UNITS[unit].canonical(_exact(magnitude))
    return {"value": magnitude, "unit_code": unit, "value_canonical": float(exact)}


def _golden_pair() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    flat = GOLDEN_NESTED.with_name("flat.jsonl")
    with flat.open(encoding="utf-8") as handle:
        return _golden(), [json.loads(line) for line in handle]


def _fresh_pair() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    catalog = generate(SMALL)
    return list(emit.iter_nested(catalog)), list(emit.iter_flat(catalog))


@pytest.mark.parametrize("source", [_golden_pair, _fresh_pair], ids=["golden", "fresh SMALL"])
def test_every_nested_entrys_published_spelling_is_its_skus_flat_facet(source):
    """The join a drawing and the spelling tests rely on is complete and agrees.

    A nested entry carries no spelling (Option C on #42): a consumer that prints
    one reads it from the SKU's flat ``facets``, walking the line's entries then
    the SKU's. That join must account for every flat value -- none left over,
    none missing -- and each spelling, read by this test's own oracle, must give
    the very magnitude, unit and canonical the nested entry carries. The unit a
    bare number takes comes from its key, not from the entry.
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
                parts = {k: entry[k] for k in PARTS if k in entry}
                assert parts == _oracle_parts(entry["key"], spelling), (
                    variant["sku"],
                    spelling,
                    entry,
                )
                joined += 1
    assert joined > 1000
