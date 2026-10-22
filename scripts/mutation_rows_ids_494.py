"""Mutation rows for the id minter built from a claimed domain (gen#494).

Each row plants one defect on a changed line of ``core/ids.py`` or of the industrial generator's
claim, and names the test that must go red. Found by ``mutation_row.discover``; ``--only "id
minter:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "id minter"

_T = "tests/test_core_ids_128.py"
_IDS = "core/ids.py"
_GEN = "domains/industrial/generate.py"


def rows() -> list[Row]:
    return [
        Row(
            "a minter is built for a domain that claimed no prefix",
            _IDS,
            "if domain not in PREFIXES:",
            "if False:",
            f"{_T}::test_a_minter_for_a_domain_that_claimed_no_prefix_cannot_be_built",
            "no claim, no minter",
        ),
        Row(
            "the minter ignores the prefix its domain claimed",
            _IDS,
            "self.prefix = PREFIXES[domain]",
            'self.prefix = ""',
            f"{_T}::test_a_minter_takes_the_prefix_its_domain_claimed_and_no_other",
            "a minter wears its own domain's prefix",
        ),
        Row(
            "the minter reads another domain's prefix",
            _IDS,
            "self.prefix = PREFIXES[domain]",
            'self.prefix = next(iter(PREFIXES.values()))',
            f"{_T}::test_a_minter_takes_the_prefix_its_domain_claimed_and_no_other",
            "a minter wears its own domain's prefix",
        ),
        Row(
            "the industrial domain never claims its prefix",
            _GEN,
            "ids.claim_prefix(ID_DOMAIN, ID_PREFIX)",
            "pass",
            f"{_T}::test_the_industrial_generator_mints_through_core_with_the_empty_prefix",
            "the industrial generator mints behind a claimed prefix",
        ),
    ]
