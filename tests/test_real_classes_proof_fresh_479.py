"""The committed real_classes proof is the proof of the records the build makes now (gen#479).

``domains/retail/real_classes_proof.json`` is what Elasticsearch answered for the
class rows over one corpus, and carries that corpus's fingerprint. ``prototypes/`` holds its
own test files, which the pre-merge run did not collect until gen#362, so a corpus change
that moved the fingerprint left the proof stale and nothing was red: seven tests of
``test_real_classes.py`` failed on main for a day before anyone ran them.

This file is collected, so a pull request that changes an indexed field of the corpus fails
here until ``domains/retail/es_proof.py`` is run against an Elasticsearch and the
proof is committed with it. The drawing is not indexed and does not count (``fingerprint``).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import real_classes as rc

RETAIL = (
    Path(__file__).resolve().parents[1] / "src" / "synthetic_ecommerce_data" / "domains" / "retail"
)


PROOF = RETAIL / "real_classes_proof.json"
REGENERATE = "python -m synthetic_ecommerce_data.domains.retail.es_proof --host http://127.0.0.1:9201"


@pytest.fixture(scope="module")
def corpus() -> list[dict]:
    return rc.corpus()


def test_the_committed_proof_was_taken_over_the_corpus_the_build_makes(corpus):
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    assert proof["fingerprint"] == rc.fingerprint(corpus), (
        f"real_classes_proof.json is stale: regenerate it with `{REGENERATE}` and commit it"
    )
    assert proof["docs"] == len(corpus)


def test_the_committed_proof_holds_its_claim_for_every_row(corpus):
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    assert rc.verdicts(proof, corpus) == []
