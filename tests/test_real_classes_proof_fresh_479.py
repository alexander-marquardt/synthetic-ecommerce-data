"""The committed real_classes proof is the proof of the records the build makes now (gen#479).

``prototypes/retail_drawings/real_classes_proof.json`` is what Elasticsearch answered for the
class rows over one corpus, and carries that corpus's fingerprint. ``prototypes/`` holds its
own test files and the pre-merge run does not collect them, so a corpus change that moved the
fingerprint left the proof stale and nothing was red: seven tests of
``test_real_classes.py`` failed on main for a day before anyone ran them.

This file is collected, so a pull request that changes an indexed field of the corpus fails
here until ``prototypes/retail_drawings/es_proof.py`` is run against an Elasticsearch and the
proof is committed with it. The drawing is not indexed and does not count (``fingerprint``).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import real_classes as rc  # noqa: E402

PROOF = RETAIL / "real_classes_proof.json"
REGENERATE = "python prototypes/retail_drawings/es_proof.py --host http://127.0.0.1:9201"


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
