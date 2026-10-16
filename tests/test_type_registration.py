"""A type registers in its own files only, so type pull requests merge in either order (#48).

Two pull requests that each deepen one breadth type used to conflict in six
files that are not generated: each added a branch to ``conformance.applicable``,
a row to ``MAY_CLAIM`` and ``KEY`` in the facts tests, an entry to the
noise tables and to ``price.KEY_ATTRIBUTES``, restated ``DEPTH_LINES`` and
``DEPTH_SKUS``, and deleted its row from the one breadth YAML table, where two
neighbouring rows conflict. Measured with two throwaway deepened types on two
branches from one base: all six conflicted, in both merge orders.

Each of those is now declared on the type's own ``TypeSpec`` (its size too:
``test_type_facts`` holds those per type), and each breadth row is a file of
its own. These tests hold that: no shared table names a type that has a
module, a planted type reaches every table from its spec alone, and a key
declared in both places is refused.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
import yaml

from synthetic_ecommerce_data.core import noise, price, typespec, voice
from synthetic_ecommerce_data.domains.industrial import breadth, conformance, taxonomy, vocab
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_shapes import cylinder
from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES
from synthetic_ecommerce_data.domains.industrial.type_labels import PRODUCT_TYPE_LABELS
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "synthetic_ecommerce_data"
INDUSTRIAL = SRC / "domains" / "industrial"

#: The files a type pull request used to edit to add itself to a shared,
#: type-keyed table. A type with a module declares all of it on its spec.
SHARED = (
    INDUSTRIAL / "conformance.py",
    SRC / "core" / "noise.py",
    REPO / "tests" / "test_catalog_facts.py",
    REPO / "tests" / "type_facts.py",
    REPO / "tests" / "catalog_size.py",
    # Not test_compatibility_text.py: it names the socket screw in tests of
    # that type's own sentences; its thread table is checked in place.
)

#: The type-keyed tables a modelled spec's per-type fields register into.
#: Each must register the type modules before it answers a read.
TABLES = {
    "conformance.CLAIMS": lambda: getattr(conformance, "CLAIMS", None),
    "price.KEY_ATTRIBUTES": lambda: price.KEY_ATTRIBUTES,
    "price.KEYS": lambda: price.KEYS,
    "noise.THREADED": lambda: noise.THREADED,
    "noise.FASTENERS": lambda: noise.FASTENERS,
    "noise.UNIT_PRIMARY": lambda: noise.UNIT_PRIMARY,
}

TOY = "toy_registration_widget"


def _toy_claims(facts, *, metric, provenance, standard):
    steel = "Steel" in facts["Material"]
    return ("ISO 0001" if metric else "ASME TOY", "ISO 0002" if steel else "")


def _toy_spec(**overrides) -> typespec.TypeSpec:
    fields = {
        "category": ("Raw Materials", "Bar & Rod Stock", "Toy Widgets"),
        "standards_family": "fastener",
        "vocab": (AttrSpec("Item", "line"), AttrSpec("Size", "sku", kind="length")),
        "figure": cylinder,
        "extent": (2.4, 0.6),
        "make": lambda gen, type_key, category: None,
        "share": 0.1,
        "price": price.PriceModel(10.0, 0.5, 0.8, 0.3, 0.2, measured=False),
        "claims": _toy_claims,
        "may_claim": frozenset({"ISO 0001", "ISO 0002", "ASME TOY"}),
        "key_attributes": ("Size",),
        "threaded": "Thread Size",
        "fastener": True,
        "unit_primary": "Size",
        "module": "tests.toy",
    }
    return typespec.TypeSpec(TOY, **{**fields, **overrides})


def _unregister(key: str) -> None:
    """Take ``key`` out of every table registration writes, without a read hook."""
    tables = [
        taxonomy.LEAVES,
        taxonomy.DRAWING,
        vocab.VOCAB,
        vocab.STANDARDS_FAMILY,
        voice.USE_LINES,
        FIGURES,
        price.MODELS,
        typespec.DECLARED_BLOCKS,
        PRODUCT_TYPE_LABELS,
        *(table() for table in TABLES.values()),
    ]
    for table in tables:
        if isinstance(table, dict):
            dict.pop(table, key, None)


@pytest.fixture
def planted(monkeypatch):
    typespec.ensure_registered()
    spec = _toy_spec()
    try:
        typespec.register(spec)
        # Discovery lists it too, as it would a module found on disk: the
        # facts tests read the specs from there.
        monkeypatch.setitem(typespec.registered(), TOY, spec)
        yield spec
    finally:
        _unregister(TOY)


def _quoted_keys(path: Path, keys) -> list[str]:
    text = path.read_text("utf-8")
    return [key for key in sorted(keys) if f'"{key}"' in text or f"'{key}'" in text]


def test_no_shared_table_names_a_type_that_has_a_module() -> None:
    """A type with a module edits no shared file to join a per-type table.

    Every modelled module is checked, so a type that adds itself to one of
    these files, rather than declaring the entry on its ``TypeSpec``, is red.
    """
    keys = typespec.modelled()
    named = {path.name: _quoted_keys(path, keys) for path in SHARED}
    assert {name: found for name, found in named.items() if found} == {}


def test_every_per_type_table_registers_before_it_answers() -> None:
    plain = sorted(
        name for name, table in TABLES.items() if not isinstance(table(), typespec.RegistryTable)
    )
    assert plain == []


def test_a_planted_type_reaches_every_per_type_table_from_its_spec(planted) -> None:
    facts_tests = importlib.import_module("test_catalog_facts")
    facts = {"Material": "Alloy Steel"}
    claimed = conformance.applicable(TOY, facts, metric=True, provenance="", standard="")
    reached = {
        "claims": claimed,
        "may_claim": facts_tests.may_claim(TOY),
        "title key": facts_tests.title_key(TOY),
        "price key": tuple(price.KEY_ATTRIBUTES.get(TOY, ())),
        "price reader": TOY in price.KEYS,
        "threaded": noise.THREADED.get(TOY),
        "fastener": TOY in noise.FASTENERS,
        "unit primary": noise.UNIT_PRIMARY.get(TOY),
    }
    assert reached == {
        "claims": ("ISO 0001", "ISO 0002"),
        "may_claim": planted.may_claim,
        "title key": ("Size",),
        "price key": ("Size",),
        "price reader": True,
        "threaded": "Thread Size",
        "fastener": True,
        "unit primary": "Size",
    }


def test_an_inch_line_of_the_planted_type_claims_what_its_spec_says(planted) -> None:
    claimed = conformance.applicable(
        TOY, {"Material": "Brass"}, metric=False, provenance="", standard=""
    )
    assert claimed == ("ASME TOY",)


#: Every shared table ``typespec.register`` writes a spec field into.
_OWN_TABLES = [
    (conformance, "CLAIMS", "claims", _toy_claims),
    (price, "KEY_ATTRIBUTES", "key_attributes", ("Size",)),
    (noise, "THREADED", "threaded", "Thread Size"),
    (noise, "FASTENERS", "fastener", True),
    (noise, "UNIT_PRIMARY", "unit_primary", "Size"),
]


@pytest.mark.parametrize(
    ("owner", "table", "field", "value"), _OWN_TABLES, ids=[row[1] for row in _OWN_TABLES]
)
def test_a_key_in_a_shared_table_and_in_its_spec_is_refused(
    monkeypatch, owner, table: str, field: str, value
) -> None:
    """Two declarations of one entry: which wins would depend on registration order."""
    typespec.ensure_registered()
    monkeypatch.setitem(getattr(owner, table), TOY, value)
    refused = None
    try:
        typespec.register(_toy_spec(**{field: value}))
    except typespec.TypeCollisionError as error:
        refused = str(error)
    finally:
        _unregister(TOY)
    assert refused is not None and table in refused and TOY in refused


def test_a_label_on_the_spec_joins_the_label_table() -> None:
    """The label is on the type's own module, so a new type edits no shared table (#103)."""
    typespec.ensure_registered()
    try:
        typespec.register(_toy_spec(label="Toy Widget"))
        assert PRODUCT_TYPE_LABELS[TOY] == "Toy Widget"
    finally:
        _unregister(TOY)


def test_a_label_in_the_table_and_on_the_spec_is_refused(monkeypatch) -> None:
    """Two declarations of one label: which wins would depend on registration order."""
    typespec.ensure_registered()
    monkeypatch.setitem(PRODUCT_TYPE_LABELS, TOY, "Toy Widget")
    refused = None
    try:
        typespec.register(_toy_spec(label="Toy Widget"))
    except typespec.TypeCollisionError as error:
        refused = str(error)
    finally:
        _unregister(TOY)
    assert refused is not None and "PRODUCT_TYPE_LABELS" in refused and TOY in refused


def test_a_modelled_type_without_a_key_dimension_is_refused() -> None:
    """Every modelled SKU is priced off its key dimension (``price.KEYS``)."""
    typespec.ensure_registered()
    refused = None
    try:
        typespec.register(_toy_spec(key_attributes=()))
    except typespec.TypeModuleError as error:
        refused = str(error)
    finally:
        _unregister(TOY)
    assert refused is not None and "key_attributes" in refused


def test_each_breadth_row_is_a_file_of_its_own() -> None:
    """Deleting one row's file cannot touch a neighbouring row's lines."""
    table = INDUSTRIAL / "data" / "breadth_categories"
    assert table.is_dir(), f"{table} is not a directory of one-row files"
    files = sorted(table.glob("*.yaml"))
    keys = [yaml.safe_load(path.read_text("utf-8"))["key"] for path in files]
    assert keys == [path.stem for path in files]
    yaml_rows = [row.key for row in breadth.rows() if row.key in set(keys)]
    assert sorted(yaml_rows) == keys


def test_a_row_file_named_for_another_key_is_refused(monkeypatch, tmp_path) -> None:
    """Every refusal names a row by its file, so the name has to be its key."""
    table = tmp_path / "breadth_categories"
    table.mkdir()
    source = INDUSTRIAL / "data" / "breadth_categories" / "shaft_collars.yaml"
    (table / "shaft_collar.yaml").write_text(source.read_text("utf-8"), "utf-8")
    monkeypatch.setattr(breadth.resources, "files", lambda package: tmp_path)
    with pytest.raises(ValueError, match=r"shaft_collar\.yaml holds the row for 'shaft_collars'"):
        breadth.load_rows()
