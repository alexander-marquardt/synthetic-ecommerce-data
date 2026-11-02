"""A domain registers its tables with core, and core reads them without importing it (#128).

Core used to answer "is this a product type?" (an image id's first segment), "which
brand family is this type in?" and "how is this type drawn?" from industrial tables it
imported, so a record of any other domain's type was refused. It also found types in the
industrial package alone and wrote each into industrial tables. These tests register a
second, test-only domain and check that core finds, registers, accepts and draws its type
through the registry alone.
"""

from __future__ import annotations

import dataclasses
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest

import synthetic_ecommerce_data.domains.industrial  # noqa: F401 - registers the domain
from synthetic_ecommerce_data.core import domain, drawing, emit
from synthetic_ecommerce_data.core.brands import BRAND_BOOK
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES, PACK_TYPES

#: A type no industrial table names.
MUG = "test_mug_128"


def _mug(record):
    figure = Figure(size_in=4.0)
    figure.rect(0.0, 0.0, 3.0, 4.0)
    return SimpleNamespace(figure=figure, source="record")


@pytest.fixture
def second_domain(monkeypatch):
    second = domain.Domain(
        name="test_second_128",
        product_types=lambda: frozenset({MUG}),
        brand_families=lambda: {MUG: "abrasive"},
        figures=lambda: {MUG: (_mug, (3.0, 4.0))},
        pack_types=lambda: frozenset({MUG}),
    )
    monkeypatch.setitem(domain._DOMAINS, second.name, second)
    return second


def test_the_industrial_domain_registers_itself():
    assert "industrial" in {d.name for d in domain.domains()}
    assert domain.is_product_type("end_mill_square")
    assert _family("end_mill_square") == "cutting_tool"


def test_a_second_domains_image_id_is_accepted(second_domain):
    assert emit.image_path(f"{MUG}/P-1/S-1") == f"{MUG}/P-1/S-1.svg"
    assert domain.product_type_for_image(f"{MUG}/P-1/S-1") == MUG


def test_a_type_no_domain_registers_is_refused():
    with pytest.raises(domain.ImageIdError, match=MUG):
        emit.image_path(f"{MUG}/P-1/S-1")


def _family(type_key: str) -> str | None:
    try:
        return domain.brand_family(type_key)
    except KeyError:
        return None


def _clashes(d: domain.Domain) -> bool:
    try:
        domain.register(d)
    except domain.DomainError:
        return True
    return False


def test_a_brand_reads_a_second_domains_family(second_domain):
    makers = [brand for brand in BRAND_BOOK if brand.makes(MUG)]
    assert makers == [brand for brand in BRAND_BOOK if "abrasive" in brand.families]
    assert makers


def test_a_type_with_no_family_is_a_key_error():
    assert _family(MUG) is None


def test_the_industrial_image_id_error_is_cores():
    from synthetic_ecommerce_data.domains.industrial import taxonomy

    assert taxonomy.ImageIdError is domain.ImageIdError


def test_a_second_registration_under_a_taken_name_is_refused(second_domain):
    other = domain.Domain(second_domain.name, lambda: frozenset(), lambda: {})
    assert _clashes(other)
    assert not _clashes(second_domain)  # the same object again is not a clash


def _figure(type_key: str):
    try:
        return domain.figure(type_key)
    except KeyError:
        return None


def test_a_domain_carries_its_figures_and_pack_types():
    names = {f.name for f in dataclasses.fields(domain.Domain)}
    assert {"figures", "pack_types"} <= names


def test_the_industrial_domain_registers_its_figures():
    assert _figure("end_mill_square") == FIGURES["end_mill_square"]
    assert all(domain.is_pack_type(t) for t in PACK_TYPES)
    plain = next(t for t in FIGURES if t not in PACK_TYPES)
    assert not domain.is_pack_type(plain)


def test_core_draws_a_second_domains_figure(second_domain):
    assert _figure(MUG) == second_domain.figures()[MUG]
    svg, source = drawing.draw_sku(MUG, BRAND_BOOK[0].name, {})
    assert source == "record"
    assert drawing.svg_problems(svg) == []


def test_core_reads_a_second_domains_pack_types(second_domain):
    one, _ = drawing.draw_sku(MUG, BRAND_BOOK[0].name, {"Units per Pack": "1"})
    three, _ = drawing.draw_sku(MUG, BRAND_BOOK[0].name, {"Units per Pack": "3"})
    assert one != three


def test_a_type_no_domain_draws_is_an_unknown_type():
    raised = None
    try:
        drawing.draw_sku(MUG, BRAND_BOOK[0].name, {})
    except KeyError as exc:
        raised = exc
    assert isinstance(raised, drawing.UnknownTypeError)
    assert MUG in str(raised)


#: A second domain's type module, as a domain package would hold it: core only.
_MUG_MODULE = f'''
from synthetic_ecommerce_data.core import price
from synthetic_ecommerce_data.core.typespec import TypeSpec

SPEC = TypeSpec(
    "{MUG}",
    category=("Kitchen", "Mugs"),
    standards_family="mug",
    vocab=("Capacity",),
    figure=lambda record: None,
    extent=(3.0, 4.0),
    make=lambda gen, type_key, category: None,
    share=0.1,
    price=price.PriceModel(10.0, 0.5, 0.8, 0.3, 0.2, measured=False),
    key_attributes=("Capacity",),
    compat=False,
)
'''

#: The second domain's package: it registers itself, its types package and its own table.
_SECOND_INIT = '''
from synthetic_ecommerce_data.core import domain

TABLE = {}

domain.register(
    domain.Domain(
        "test_second_128",
        lambda: frozenset(TABLE),
        lambda: {},
        types_package=__name__ + ".types",
        register_type=lambda spec: TABLE.__setitem__(spec.key, spec.category),
    )
)
'''


def _plant_second_domain(root):
    """``test_second_128/`` under ``root``: the package, and one type module in one family."""
    package = root / "test_second_128"
    family = package / "types" / "kitchen"
    family.mkdir(parents=True)
    (package / "__init__.py").write_text(_SECOND_INIT, encoding="utf-8")
    (package / "types" / "__init__.py").write_text("", encoding="utf-8")
    (family / "__init__.py").write_text("", encoding="utf-8")
    (family / f"{MUG}.py").write_text(_MUG_MODULE, encoding="utf-8")


def test_a_domain_carries_its_types():
    names = {f.name for f in dataclasses.fields(domain.Domain)}
    assert {"types_package", "load_types", "register_type"} <= names


def test_the_industrial_domain_hands_core_its_types_package():
    from synthetic_ecommerce_data.domains import industrial
    from synthetic_ecommerce_data.domains.industrial import product_types

    held = [d.types_package for d in domain.domains() if d.name == "industrial"]
    assert held == [industrial.TYPES_PACKAGE] == [product_types.__name__]


def test_discovery_walks_every_registered_domains_types_package(tmp_path, monkeypatch):
    from synthetic_ecommerce_data.core import typespec

    _plant_second_domain(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    second = domain.Domain(
        "test_second_128",
        lambda: frozenset({MUG}),
        lambda: {},
        types_package="test_second_128.types",
    )
    monkeypatch.setitem(domain._DOMAINS, second.name, second)
    found = typespec.discover()
    assert found[MUG].module == f"test_second_128.types.kitchen.{MUG}"
    assert "end_mill_square" in found


def test_a_fresh_process_registers_a_second_domains_type_into_its_own_tables(tmp_path):
    """Registration runs once per process, so a fresh one: the second domain's spec lands
    in its own table and core's, and in no industrial table."""
    _plant_second_domain(tmp_path)
    code = (
        "import test_second_128\n"
        "from synthetic_ecommerce_data.core import price, typespec\n"
        "from synthetic_ecommerce_data.domains.industrial import taxonomy, vocab\n"
        "from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES\n"
        f"assert {MUG!r} in typespec.registered()\n"
        f"assert test_second_128.TABLE == {{{MUG!r}: ('Kitchen', 'Mugs')}}\n"
        f"assert {MUG!r} in price.MODELS\n"
        "industrial = (taxonomy.LEAVES, taxonomy.DRAWING, vocab.VOCAB, FIGURES)\n"
        f"assert not any({MUG!r} in table for table in industrial)\n"
        "assert 'end_mill_square' in taxonomy.LEAVES\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
    )
    assert result.returncode == 0, result.stderr


def test_a_spec_outside_every_domains_types_package_is_refused():
    from synthetic_ecommerce_data.core import typespec

    stray = dataclasses.replace(typespec.discover()["end_mill_square"], module="elsewhere.mugs")
    with pytest.raises(typespec.TypeModuleError, match="elsewhere.mugs"):
        typespec.register(stray)


def test_a_fresh_process_finds_the_mark_slot_filled_by_core_drawing_alone():
    """Core no longer imports the industrial figures, whose package fills the mark slot:
    loading core.drawing loads every registered domain's figures instead."""
    code = (
        "from synthetic_ecommerce_data.core.brands import BRAND_BOOK\n"
        "from synthetic_ecommerce_data.core.drawing.brand_mark import mark_for\n"
        "mark_for(BRAND_BOOK[0].name)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
