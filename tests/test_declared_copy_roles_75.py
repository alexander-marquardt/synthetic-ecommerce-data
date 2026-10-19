"""A type declares its compatibility text, near-miss axis and noise roles (#75).

The cross-reference sentence, the near-miss period and the noise eligibility
used to be if-chains and tuples keyed by type, so a type added later got none
and nothing failed. They are declared on the ``TypeSpec`` now, and a modelled
type that says nothing about compatibility is refused at registration.
"""

from __future__ import annotations

import importlib

import pytest

from compat_text import compatibility_sentences, noise_sentences
from published import authored_attributes
from synthetic_ecommerce_data.core import emit, noise, typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import compat
from synthetic_ecommerce_data.domains.industrial.generate import generate

SET_SCREW = "set_screws_hex_socket"
LOCK_NUT = "lock_nuts_nylon_insert"

registration = importlib.import_module("test_type_registration")


@pytest.fixture(scope="module")
def fresh() -> list[dict]:
    """The default build, emitted in memory, as ``test_compatibility_text`` reads it."""
    return list(emit.iter_flat(generate(GeneratorConfig())))


def _published(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in authored_attributes(doc)}


def _of(docs: list[dict], key: str) -> list[dict]:
    return [d for d in docs if d["product_type"] == key]


# --- the two types the issue names ---------------------------------------------


def test_a_set_screw_names_the_hex_key_it_takes(fresh):
    """``Takes a 2mm hex key.`` on every set screw whose drive is a nominal key."""
    carried = 0
    for doc in _of(fresh, SET_SCREW):
        drive = _published(doc)["Drive Size"]
        found = [m for m in compatibility_sentences(doc["description"]) if m["key"]]
        if compat.drive_sentence(drive) is None:
            assert not found, doc["sku"]  # an off-series drive is no key
            continue
        assert [m["key"] for m in found] == [_key_spelling(drive)], doc["sku"]
        carried += 1
    assert carried > 400, carried


def _key_spelling(drive: str) -> str:
    return compat.drive_sentence(drive).removeprefix("Takes a ").removesuffix(" hex key.")


def test_a_lock_nut_names_the_thread_it_fits(fresh):
    """``Fits M12x1.75 bolts and screws.`` on every lock nut, from its own thread."""
    docs = _of(fresh, LOCK_NUT)
    assert len(docs) > 300, len(docs)
    for doc in docs:
        found = [m["nut"] for m in compatibility_sentences(doc["description"]) if m["nut"]]
        assert found == [_published(doc)["Thread Size"]], doc["sku"]


def test_the_two_types_join_the_noise_tables_from_their_specs():
    specs = typespec.modelled()
    assert specs[SET_SCREW].fastener and specs[SET_SCREW].threaded == "Dia./Thread Size"
    assert SET_SCREW in noise.FASTENERS and SET_SCREW in noise.THREADED
    assert LOCK_NUT in noise.FASTENERS and LOCK_NUT in noise.THREADED


def test_a_set_screw_carries_the_near_miss_thread_sentence(fresh):
    """``Not for M10 or M16 threads.`` -- only a threaded type writes it."""
    negatives = [
        m
        for doc in _of(fresh, SET_SCREW)
        for m in noise_sentences(doc["description"])
        if m["not_threads"]
    ]
    assert len(negatives) > 40, len(negatives)


def test_a_set_screw_reads_its_declared_period_for_the_fine_pitch_near_miss(fresh):
    """An inch size with a fine series is built to UNF on every Nth line, N being the
    period the spec declares. At period 3 the default build holds 26 UNF lines; a
    period of 5 (the bolt's) leaves 10, so a set screw reading another type's period
    falls under the floor."""
    assert compat.NEAR_MISS_PERIOD[SET_SCREW] == 3
    fine, coarse = 0, 0
    for doc in _of(fresh, SET_SCREW):
        values = _published(doc)
        size = values["Dia./Thread Size"]
        if values.get("Thread Type") not in ("UNC", "UNF") or size[:2] == "#0":
            continue
        if values["Thread Type"] == "UNF":
            fine += 1
        else:
            coarse += 1
    assert fine >= 20, (fine, coarse)


# --- the declarations, from the spec -------------------------------------------


def test_a_modelled_type_that_declares_no_compat_is_refused():
    """A type that says nothing about compatibility gets none and nothing fails
    (#75): the build names the type's module and the field instead."""
    typespec.ensure_registered()
    refused = None
    try:
        typespec.register(registration._toy_spec(compat=None))
    except typespec.TypeModuleError as error:
        refused = str(error)
    finally:
        registration._unregister(registration.TOY)
    assert refused is not None
    assert "tests.toy" in refused and "compat" in refused


@pytest.mark.parametrize(
    ("fields", "named"),
    [
        ({"compat": ("sprocket", "Size")}, "compat=('sprocket', 'Size')"),
        ({"compat": ("nut",)}, "compat=('nut',)"),
        ({"compat": False, "near_miss_period": 1}, "near_miss_period=1"),
    ],
)
def test_a_malformed_declaration_is_refused_naming_it(fields, named):
    """An unknown kind, a relation without an attribute, and a period of one (every
    line a near miss, none the product itself) are refused where they are declared."""
    typespec.ensure_registered()
    refused = None
    try:
        typespec.register(registration._toy_spec(**fields))
    except typespec.TypeModuleError as error:
        refused = str(error)
    finally:
        registration._unregister(registration.TOY)
    assert refused is not None and named in refused


def test_compat_false_states_there_is_none_and_registers(planted_none):
    assert registration.TOY not in compat.RELATIONS
    assert compat.sentence_for(registration.TOY, {"Size": "5mm"}) is None


def test_a_declared_relation_writes_its_sentence_for_a_planted_type(planted_nut):
    assert compat.sentence_for(registration.TOY, {"Thread Size": "M8x1.25"}) == (
        "Fits M8x1.25 bolts and screws."
    )


def test_a_declared_near_miss_period_and_cutting_reach_their_tables(planted_nut):
    assert compat.NEAR_MISS_PERIOD.get(registration.TOY) == 4
    assert registration.TOY in noise.CUTTING


@pytest.fixture
def planted_none(monkeypatch):
    yield from _plant(monkeypatch, compat=False)


@pytest.fixture
def planted_nut(monkeypatch):
    yield from _plant(monkeypatch, compat=("nut", "Thread Size"), near_miss_period=4, cutting=True)


def _plant(monkeypatch, **fields):
    typespec.ensure_registered()
    spec = registration._toy_spec(**fields)
    try:
        typespec.register(spec)
        monkeypatch.setitem(typespec.registered(), registration.TOY, spec)
        yield spec
    finally:
        registration._unregister(registration.TOY)
