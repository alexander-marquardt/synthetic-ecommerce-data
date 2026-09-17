"""What a record is, read off its attribute names, and never off two.

The renderer picks a drawing from the attribute NAMES a record publishes,
because that is what a catalog in this vertical actually carries. That only
works while the names it keys on belong to one product type each. This is
where that is checked against the vocabulary rather than assumed, so a
vocabulary change that made a signature ambiguous fails here -- loudly, with
the offending name -- instead of quietly drawing a tap as a cap screw.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.catalog.config import SMALL
from synthetic_industrial_products.catalog.emit import render_records
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.vocab import VOCAB, names_for
from synthetic_industrial_products.records import BUNDLED
from synthetic_industrial_products.render import DIMENSIONED, kinds

#: Which drawing each catalog product type gets. Two pairs share one: a square
#: and a ball nose end mill are one renderer, and so are a socket cap screw and
#: a hex bolt -- the corpus shares those types' vocabularies because they are
#: the same kind of thing.
KIND_OF_TYPE: dict[str, str] = {
    "end_mill_square": kinds.END_MILL,
    "end_mill_ball": kinds.END_MILL,
    "drill_jobber": kinds.DRILL,
    "tap_spiral_point": kinds.TAP,
    "screw_socket_head": kinds.FASTENER,
    "screw_flat_head": kinds.FASTENER,
    "bolt_hex": kinds.FASTENER,
    "washer_flat": kinds.WASHER,
    "hammer_ball_pein": kinds.HAMMER,
    "abrasive_flap_disc": kinds.FLAP_DISC,
}


@pytest.fixture(scope="module")
def catalog():
    return generate(SMALL)


def test_every_product_type_has_a_kind_and_every_kind_a_renderer():
    assert set(KIND_OF_TYPE) == set(VOCAB)
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
    carriers = {KIND_OF_TYPE[t] for t in VOCAB if name in names_for(t)}
    assert carriers <= signature_kinds, f"{name!r} is published by {carriers}"


@pytest.mark.parametrize("type_key", sorted(VOCAB))
def test_every_type_publishes_at_least_one_signature_name_unconditionally(type_key):
    """Sparsity must not be able to make a record unidentifiable.

    A signature that only ever matched optional attributes would classify most
    records and silently fail on the ragged ones, which are exactly the records
    the type drawing exists for.
    """
    always = {spec.name for spec in VOCAB[type_key] if spec.presence >= 1.0}
    assert always & kinds.SIGNATURES[KIND_OF_TYPE[type_key]]


def test_every_generated_record_classifies_to_its_own_type(catalog):
    """The live check, over a whole catalog rather than over the vocabulary."""
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
        kinds.classify({"sku": "A", "Milling Dia.": '1/4"', "Washer Size": "M8"})
