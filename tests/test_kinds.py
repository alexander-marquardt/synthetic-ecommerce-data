"""What a record is: its product type when it carries one, its names when it does not.

A generated record carries ``product_type`` and is classified by it; since
elastic/prism-industrial-products#103 attribute names no longer identify a
type (``Material`` and ``Size`` are shared). An OBSERVED record carries no
type, so the name signatures still classify those -- and those signatures must
stay unambiguous against the vocabulary, which is checked here rather than
assumed, so a tap is never drawn as a cap screw.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.catalog.config import SMALL
from synthetic_industrial_products.catalog.emit import render_records
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.vocab import VOCAB, names_for
from synthetic_industrial_products.records import BUNDLED
from synthetic_industrial_products.render import DIMENSIONED, kinds

KIND_OF_TYPE = kinds.TYPE_KIND


@pytest.fixture(scope="module")
def catalog():
    return generate(SMALL)


def test_every_product_type_has_a_kind_and_every_kind_a_renderer():
    """The original twelve types have a dimensioned renderer; every type has a figure.

    The newer types (elastic/prism-industrial-products#103) exist only as the
    catalog's own text-free drawings, :mod:`synthetic_industrial_products.drawing`.
    """
    from synthetic_industrial_products.drawing import FIGURES

    assert set(KIND_OF_TYPE) <= set(VOCAB)
    assert set(FIGURES) == set(VOCAB)
    assert set(KIND_OF_TYPE.values()) == set(kinds.SIGNATURES)
    assert set(kinds.SIGNATURES) == set(DIMENSIONED) == set(kinds.KIND_LABELS)


@pytest.mark.parametrize("name", sorted(set().union(*kinds.SIGNATURES.values())))
def test_no_signature_name_belongs_to_a_type_of_another_kind(name):
    """The property the whole dispatch rests on.

    A name may be shared -- ``Screw Head Type`` is on both a cap screw and a
    hex bolt -- as long as every type carrying it draws the same way. A name
    carried by two types that draw differently makes the record ambiguous, and
    ambiguous is what :func:`kinds.classify` refuses rather than guesses at.
    """
    signature_kinds = {k for k, names in kinds.SIGNATURES.items() if name in names}
    assert len(signature_kinds) == 1, f"{name!r} is in more than one signature"
    carriers = {KIND_OF_TYPE[t] for t in KIND_OF_TYPE if name in names_for(t)}
    assert carriers <= signature_kinds, f"{name!r} is published by {carriers}"


def test_every_generated_record_classifies_to_its_own_type(catalog):
    """The live check, over a whole catalog: every record is classified by its type."""
    type_of = {child.sku: line.type_key for line, child in catalog.all_skus()}
    seen = set()
    for record in render_records(catalog):
        expected = KIND_OF_TYPE[type_of[record["sku"]]]
        assert kinds.classify(record) == expected, record["sku"]
        seen.add(expected)
    assert seen == set(kinds.SIGNATURES), "a kind went unexercised"


@pytest.mark.parametrize("sku", sorted(BUNDLED))
def test_every_bundled_record_classifies(sku):
    assert kinds.classify(BUNDLED[sku]) in kinds.SIGNATURES


def test_a_record_with_no_identifying_attribute_is_refused():
    with pytest.raises(kinds.UnknownProductError):
        kinds.classify({"sku": "A", "Colour": "red"})


def test_a_record_that_looks_like_two_things_is_refused_not_resolved():
    """Better no image than the wrong one drawn confidently.

    Resolving this by signature order would make the answer depend on which
    check happened to run first, which is not a property of the record.
    """
    with pytest.raises(kinds.AmbiguousProductError):
        kinds.classify({"sku": "A", "Milling Dia.": '1/4"', "Inside Dia.": '5/16"'})


def test_a_carried_product_type_decides_over_the_names():
    """A generated record's names are shared across types; its type is not."""
    record = {"sku": "A", "product_type": "washer_flat", "Size": "M8", "Material": "Steel"}
    assert kinds.classify(record) == kinds.WASHER


def test_an_unknown_product_type_is_refused():
    with pytest.raises(kinds.UnknownProductError):
        kinds.classify({"sku": "A", "product_type": "widget"})
