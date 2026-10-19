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


@pytest.fixture(autouse=True)
def prefixes_restored():
    """Leave ``ids.PREFIXES`` as the test found it, so a claim made here does not outlive it."""
    saved = dict(ids.PREFIXES)
    yield
    ids.PREFIXES.clear()
    ids.PREFIXES.update(saved)


def minter_for(prefix, type_key="bolt"):
    """A minter whose domain has claimed ``prefix``; the empty prefix is industrial's."""
    domain = "industrial" if prefix == "" else f"test_domain_{prefix}"
    ids.claim_prefix(domain, prefix)
    return ids.IdMinter(domain, type_key, BLOCK)


def test_an_unprefixed_minter_issues_the_industrial_part_numbers():
    minter = minter_for("")
    issued = [minter.new_sku() for _ in range(5)]
    assert issued == [typespec.part_number(BLOCK, n) for n in range(1, 6)]


def test_an_unprefixed_product_id_keeps_the_industrial_shape():
    minter = minter_for("")
    assert minter.product_id("ABC", "S1", 7) == "ABC-S1-1234-0007"


def test_a_prefixed_minter_leads_its_sku_and_product_id_with_the_prefix():
    minter = minter_for("R")
    assert re.fullmatch(r"R\d{10}", minter.new_sku())
    assert minter.product_id("ABC", "S1", 7) == "R-ABC-S1-1234-0007"


def test_two_domains_never_issue_the_same_sku_or_product_id():
    a = minter_for("")
    b = minter_for("R")
    c = minter_for("RX")
    skus = [m.new_sku() for m in (a, b, c) for _ in range(200)]
    assert len(set(skus)) == len(skus)
    product_ids = {m.product_id("ABC", "S1", 7) for m in (a, b, c)}
    assert len(product_ids) == 3


def test_the_product_index_counts_up_from_one_per_minter():
    minter = minter_for("")
    assert [minter.next_index() for _ in range(3)] == [1, 2, 3]
    assert minter_for("R").next_index() == 1


def test_an_exhausted_sequence_is_refused():
    minter = minter_for("")
    minter._sequence = typespec.SEQUENCE_SPACE  # noqa: SLF001
    with pytest.raises(ValueError, match="used all"):
        minter.new_sku()


@pytest.mark.parametrize(
    "prefix",
    ["r", "1", "ABC", "R-", "R1", " ", "Ä"],
    ids=["lowercase", "digit", "three-letters", "hyphen", "letter-digit", "space", "non-ascii"],
)
def test_a_prefix_that_could_pass_for_a_digit_or_a_brand_code_is_refused(prefix):
    with pytest.raises(ValueError, match="prefix"):
        ids.check_prefix(prefix)
    with pytest.raises(ValueError, match="prefix"):
        ids.claim_prefix("test_domain_bad", prefix)
    with pytest.raises(ValueError, match="not claimed"):
        ids.IdMinter("test_domain_bad", "bolt", BLOCK)


def test_a_minter_for_a_domain_that_claimed_no_prefix_cannot_be_built():
    with pytest.raises(ValueError, match="test_domain_unclaimed.*not claimed"):
        ids.IdMinter("test_domain_unclaimed", "bolt", BLOCK)


def test_a_minter_takes_the_prefix_its_domain_claimed_and_no_other():
    ids.claim_prefix("test_domain_q", "ZQ")
    ids.claim_prefix("test_domain_w", "ZW")
    minter = ids.IdMinter("test_domain_q", "bolt", BLOCK)
    assert minter.prefix == "ZQ"
    assert minter.product_id("ABC", "S1", 7) == "ZQ-ABC-S1-1234-0007"
    assert ids.IdMinter("test_domain_w", "bolt", BLOCK).prefix == "ZW"


def test_a_bare_prefix_is_not_a_domain():
    """The prefix a minter is built from must be a claimed domain, never a prefix string."""
    with pytest.raises(ValueError, match="not claimed"):
        ids.IdMinter("ZY", "bolt", BLOCK)


@pytest.mark.parametrize("prefix", ["", "R", "RX"])
def test_the_empty_prefix_and_one_or_two_capitals_are_accepted(prefix):
    ids.check_prefix(prefix)


def test_two_domains_cannot_hold_one_prefix(prefixes_restored):
    ids.claim_prefix("test_domain_a", "ZA")
    try:
        ids.claim_prefix("test_domain_a", "ZA")  # the same domain again is no clash
    except ValueError:
        refused_itself = True
    else:
        refused_itself = False
    assert not refused_itself
    with pytest.raises(ValueError, match="ZA"):
        ids.claim_prefix("test_domain_b", "ZA")


def test_a_domain_cannot_re_claim_a_different_prefix(prefixes_restored):
    ids.claim_prefix("d", "ZB")
    with pytest.raises(ValueError, match="already mints"):
        ids.claim_prefix("d", "ZC")
    assert ids.PREFIXES["d"] == "ZB"


def test_a_second_domain_cannot_claim_the_empty_prefix_industrial_holds(prefixes_restored):
    assert ids.PREFIXES.get("industrial") == ""
    with pytest.raises(ValueError, match="industrial"):
        ids.claim_prefix("test_domain_c", "")
    assert "test_domain_c" not in ids.PREFIXES


def test_the_industrial_generator_mints_through_core_with_the_empty_prefix():
    generator = Generator(SMALL, "screw_socket_head")
    assert isinstance(getattr(generator, "minter", None), ids.IdMinter)
    assert generator.minter.prefix == ""
    assert not hasattr(generator, "_new_sku")
    assert not hasattr(generator, "_product_id")
    assert ids.PREFIXES.get("industrial") == ""
