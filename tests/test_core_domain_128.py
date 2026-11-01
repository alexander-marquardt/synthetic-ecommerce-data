"""A domain registers its tables with core, and core reads them without importing it (#128).

Core used to answer "is this a product type?" (an image id's first segment), "which
brand family is this type in?" and "how is this type drawn?" from industrial tables it
imported, so a record of any other domain's type was refused. These tests register a
second, test-only domain and check that core accepts and draws its type through the
registry alone.
"""

from __future__ import annotations

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


SECOND = domain.Domain(
    name="test_second_128",
    product_types=lambda: frozenset({MUG}),
    brand_families=lambda: {MUG: "abrasive"},
    figures=lambda: {MUG: (_mug, (3.0, 4.0))},
    pack_types=lambda: frozenset({MUG}),
)


@pytest.fixture
def second_domain(monkeypatch):
    monkeypatch.setitem(domain._DOMAINS, SECOND.name, SECOND)
    return SECOND


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
    other = domain.Domain(SECOND.name, lambda: frozenset(), lambda: {})
    assert _clashes(other)
    assert not _clashes(SECOND)  # the same object again is not a clash


def test_the_industrial_domain_registers_its_figures():
    assert domain.figure("end_mill_square") == FIGURES["end_mill_square"]
    assert all(domain.is_pack_type(t) for t in PACK_TYPES)
    plain = next(t for t in FIGURES if t not in PACK_TYPES)
    assert not domain.is_pack_type(plain)


def test_core_draws_a_second_domains_figure(second_domain):
    svg, source = drawing.draw_sku(MUG, BRAND_BOOK[0].name, {})
    assert source == "record"
    assert drawing.svg_problems(svg) == []


def test_core_reads_a_second_domains_pack_types(second_domain):
    one, _ = drawing.draw_sku(MUG, BRAND_BOOK[0].name, {"Units per Pack": "1"})
    three, _ = drawing.draw_sku(MUG, BRAND_BOOK[0].name, {"Units per Pack": "3"})
    assert one != three


def test_a_type_no_domain_draws_is_an_unknown_type():
    with pytest.raises(drawing.UnknownTypeError, match=MUG):
        drawing.draw_sku(MUG, BRAND_BOOK[0].name, {})
