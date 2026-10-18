"""Product ids and SKUs are minted by core behind a per-domain prefix (#128).

The industrial domain keeps the empty prefix, so its ids are the ones the
golden catalog pins. A second domain mints under its own prefix and cannot
issue an id the industrial domain (or another domain) already issued.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.core import ids, typespec
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.domains.industrial.generate import Generator

BLOCK = 1234


def test_an_unprefixed_minter_issues_the_industrial_part_numbers():
    minter = ids.IdMinter("", "bolt", BLOCK)
    issued = [minter.new_sku() for _ in range(5)]
    assert issued == [typespec.part_number(BLOCK, n) for n in range(1, 6)]


def test_an_unprefixed_product_id_keeps_the_industrial_shape():
    minter = ids.IdMinter("", "bolt", BLOCK)
    assert minter.product_id("ABC", "S1", 7) == "ABC-S1-1234-0007"


def test_a_prefixed_minter_leads_its_sku_and_product_id_with_the_prefix():
    minter = ids.IdMinter("R", "bolt", BLOCK)
    assert re.fullmatch(r"R\d{10}", minter.new_sku())
    assert minter.product_id("ABC", "S1", 7) == "R-ABC-S1-1234-0007"


def test_two_domains_never_issue_the_same_sku_or_product_id():
    a = ids.IdMinter("", "bolt", BLOCK)
    b = ids.IdMinter("R", "bolt", BLOCK)
    c = ids.IdMinter("RX", "bolt", BLOCK)
    skus = [m.new_sku() for m in (a, b, c) for _ in range(200)]
    assert len(set(skus)) == len(skus)
    product_ids = {m.product_id("ABC", "S1", 7) for m in (a, b, c)}
    assert len(product_ids) == 3


def test_the_product_index_counts_up_from_one_per_minter():
    minter = ids.IdMinter("", "bolt", BLOCK)
    assert [minter.next_index() for _ in range(3)] == [1, 2, 3]
    assert ids.IdMinter("R", "bolt", BLOCK).next_index() == 1


def test_an_exhausted_sequence_is_refused():
    minter = ids.IdMinter("", "bolt", BLOCK)
    minter._sequence = typespec.SEQUENCE_SPACE  # noqa: SLF001
    with pytest.raises(ValueError, match="used all"):
        minter.new_sku()


@pytest.mark.parametrize("prefix", ["r", "1", "ABC", "R-", "R1", " ", "Ä"])
def test_a_prefix_that_could_pass_for_a_digit_or_a_brand_code_is_refused(prefix):
    with pytest.raises(ValueError, match="prefix"):
        ids.check_prefix(prefix)
    with pytest.raises(ValueError, match="prefix"):
        ids.IdMinter(prefix, "bolt", BLOCK)


@pytest.mark.parametrize("prefix", ["", "R", "RX"])
def test_the_empty_prefix_and_one_or_two_capitals_are_accepted(prefix):
    ids.check_prefix(prefix)


@pytest.fixture
def prefixes_restored():
    """Leave ``ids.PREFIXES`` as the test found it, so a claim made here does not outlive it."""
    saved = dict(ids.PREFIXES)
    yield
    ids.PREFIXES.clear()
    ids.PREFIXES.update(saved)


def test_two_domains_cannot_hold_one_prefix(prefixes_restored):
    ids.claim_prefix("test_domain_a", "ZA")
    ids.claim_prefix("test_domain_a", "ZA")  # the same domain again is no clash
    with pytest.raises(ValueError, match="ZA"):
        ids.claim_prefix("test_domain_b", "ZA")


def test_a_domain_cannot_re_claim_a_different_prefix(prefixes_restored):
    ids.claim_prefix("d", "ZB")
    with pytest.raises(ValueError, match="already mints"):
        ids.claim_prefix("d", "ZC")
    assert ids.PREFIXES["d"] == "ZB"


def test_a_second_domain_cannot_claim_the_empty_prefix_industrial_holds(prefixes_restored):
    assert ids.PREFIXES["industrial"] == ""
    with pytest.raises(ValueError, match="industrial"):
        ids.claim_prefix("test_domain_c", "")
    assert "test_domain_c" not in ids.PREFIXES


def test_the_industrial_generator_mints_through_core_with_the_empty_prefix():
    generator = Generator(SMALL, "screw_socket_head")
    assert isinstance(getattr(generator, "minter", None), ids.IdMinter)
    assert generator.minter.prefix == ""
    assert not hasattr(generator, "_new_sku")
    assert not hasattr(generator, "_product_id")
    assert ids.PREFIXES["industrial"] == ""
