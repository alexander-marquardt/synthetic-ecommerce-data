"""The guarantee the README makes, checked.

*No generated record may match a reference record on its full attribute tuple.*

Two things have to be true for this test to be worth anything, and both are
asserted below: the comparison has to actually fire (a test that compares
against an empty reference set passes trivially), and it has to tolerate the
legitimate agreement that standards compliance forces.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.catalog import noncopy
from synthetic_industrial_products.catalog.config import SMALL, GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.model import Attribute
from synthetic_industrial_products.records import FIXTURES


@pytest.fixture(scope="module")
def catalog():
    return generate(GeneratorConfig(lines=120, seed=4242))


def test_the_reference_set_is_not_empty():
    """Guard against the trivial pass.

    Every other test in this file compares against these sets. If they were
    empty -- a missing data file, a builder that silently found nothing -- the
    non-copying assertions would all pass while proving nothing at all.
    """
    assert len(noncopy.reference_tuple_hashes()) >= 100
    assert len(noncopy.REFERENCE_SKUS) >= 300
    assert len(noncopy.reference_dimension_hashes()) >= 100


def test_no_generated_record_matches_a_reference_record_on_its_full_tuple(catalog):
    audit = noncopy.audit(catalog)
    assert audit["full_tuple_collisions"] == []
    assert audit["n_skus_checked"] > 500


def test_no_generated_sku_wears_a_reference_sku_code(catalog):
    audit = noncopy.audit(catalog)
    assert audit["sku_collisions"] == []


def test_the_bundled_fixtures_are_in_the_reference_set(catalog):
    """records.FIXTURES are reference records, and are compared against directly.

    The hash file is built from the derived statistics AND from these, so the
    committed hashes and the live objects cannot drift apart.
    """
    for record in FIXTURES.values():
        assert noncopy.fingerprint_mapping(record) in noncopy.reference_tuple_hashes()


def test_no_generated_record_matches_a_bundled_fixture(catalog):
    """The live comparison, not the hashed one."""
    fixture_prints = {noncopy.fingerprint_mapping(record) for record in FIXTURES.values()}
    for line, child in catalog.all_skus():
        merged = catalog.merged_attributes(line, child)
        assert noncopy.fingerprint(merged) not in fixture_prints


def test_the_check_would_actually_catch_a_copy():
    """Feed it a reference record and it must say so.

    Without this, a bug that made every fingerprint unique -- a stray random
    value in the tuple, say -- would turn the guarantee into a tautology and
    nothing would notice.
    """
    reference = FIXTURES["26LD37"]
    as_attributes = [
        Attribute(name=name, value=value) for name, value in reference.items() if name != "sku"
    ]
    assert noncopy.matches_reference(as_attributes)


def test_standards_agreement_alone_is_not_a_copy():
    """Sharing a standards-fixed dimension must NOT trip the guarantee.

    A #10 flat head cap screw has a 0.411" head whoever makes it. A record
    that agrees with the reference on that one field, and differs elsewhere,
    is a different product -- and the full-tuple comparison has to say so.
    """
    reference = FIXTURES["26LD37"]
    near_miss = [
        Attribute(name=name, value=value) for name, value in reference.items() if name != "sku"
    ]
    # Same standards-fixed head, different finish: a different product.
    near_miss.append(Attribute(name="Fastener Finish", value="Black Oxide"))
    assert not noncopy.matches_reference(near_miss)
    assert ("Head Dia.", "0.411 in") in noncopy.pairs_of(near_miss)


def test_the_fingerprint_ignores_attribute_order():
    left = [Attribute("B", "2"), Attribute("A", "1")]
    right = [Attribute("A", "1"), Attribute("B", "2")]
    assert noncopy.fingerprint(left) == noncopy.fingerprint(right)


def test_a_multivalued_attribute_fingerprints_by_its_values_not_its_order():
    left = [Attribute("Standards", "ISO 4762", values=("ISO 4762", "DIN 912"))]
    right = [Attribute("Standards", "DIN 912", values=("DIN 912", "ISO 4762"))]
    assert noncopy.fingerprint(left) == noncopy.fingerprint(right)


def test_the_audit_reports_verbatim_dimension_tuple_reuse(catalog):
    """The four-dimension tuples are a second, narrower compilation.

    Overlap here is not a breach of the README's promise -- that is about the
    full tuple -- but it is worth knowing, so the audit counts it rather than
    staying silent. The generator builds geometry from the conventional series
    rather than sampling the observed tuples, so this should stay small.
    """
    audit = noncopy.audit(catalog)
    hits = audit["verbatim_dimension_tuple_collisions"]
    assert len(hits) <= 0.02 * audit["n_skus_checked"], (
        f"{len(hits)} of {audit['n_skus_checked']} generated tools reproduce an "
        "observed dimension tuple verbatim"
    )


def test_a_small_catalog_is_still_clean():
    audit = noncopy.audit(generate(SMALL))
    assert audit["full_tuple_collisions"] == []
    assert audit["sku_collisions"] == []
