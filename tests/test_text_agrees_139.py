"""The title and description coherence check runs on industrial (gen#139).

``standard.check_catalog(..., text_agrees=True)`` failed 259 documents of the industrial golden
and none of the sampled ones was a contradiction. Each exemption below is a pair: the document
that was a false positive is silent, and the SAME document with one true incoherence planted in
its text is still reported, so a check that was loosened until quiet fails here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core import standard
from synthetic_ecommerce_data.domains.industrial import hammers

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog" / "nested.jsonl"


def _doc(pid: str, key: str, value: str, text: str, *, title: str = "A part") -> dict[str, Any]:
    return {
        "product_id": pid,
        "category_leaf": "Parts",
        "title": title,
        "attributes": [{"key": key, "value": value}],
        "variants": [{"sku": f"{pid}-1", "description": text}],
    }


def _verdict(key: str, pool: list[str], value: str, text: str) -> list[str]:
    """What the check says of one document whose ``key`` is ``value`` and whose leaf also
    holds a document for each of ``pool``'s other values."""
    others = [_doc(f"O{n}", key, v, "plain") for n, v in enumerate(pool) if v != value]
    docs = [_doc("P-1", key, value, text), *others]
    return standard.text_contradictions(docs[0], standard.value_pools(docs))


#: (key, the leaf's values, the doc's value, the text that was a false positive, the sentence
#: that plants a true incoherence beside it, the value that sentence names).
EXEMPTIONS = {
    "inside-own-value": (
        "material",
        ["Steel", "Brass", "18-8 Stainless Steel"],
        "18-8 Stainless Steel",
        "Stainless steel resists corrosion.",
        "A brass fitting.",
        "Brass",
    ),
    "words-of-own-value": (
        "application",
        ["Grinding", "Polishing", "Cutting & Grinding"],
        "Cutting & Grinding",
        "For grinding and surface preparation.",
        "A polishing wheel.",
        "Polishing",
    ),
    "comparison": (
        "grade",
        ["Grade 5", "Grade 8"],
        "Grade 8",
        "Higher strength than Grade 5.",
        "A Grade 5 nut.",
        "Grade 5",
    ),
    "comparison-decimal-grade": (
        "grade",
        ["Class 8.8", "Class 10.9", "Class 8"],
        "Class 10.9",
        "Higher strength than 8.8, like Class 8 bolts. Tightened with a wrench.",
        "A Class 8 nut.",
        "Class 8",
    ),
    "equivalence": (
        "standards",
        ["ISO 4762", "DIN 912", "ISO 3506-1"],
        "ISO 3506-1",
        "Equivalent to DIN 912 / ISO 4762.",
        "Made to DIN 912.",
        "DIN 912",
    ),
    "tolerance-class": (
        "standards",
        ["ISO 15", "ISO 492", "ABMA 20"],
        "ISO 15",
        "Bore 7.992-8.000mm (ISO 492 Normal class).",
        "Conforms to ABMA 20.",
        "ABMA 20",
    ),
}


@pytest.mark.parametrize("case", sorted(EXEMPTIONS))
def test_the_false_positive_is_silent(case: str) -> None:
    key, pool, value, text, _, _ = EXEMPTIONS[case]
    assert _verdict(key, pool, value, text) == []


@pytest.mark.parametrize("case", sorted(EXEMPTIONS))
def test_a_true_incoherence_planted_on_the_same_doc_is_still_reported(case: str) -> None:
    key, pool, value, text, plant, named = EXEMPTIONS[case]
    problems = _verdict(key, pool, value, f"{text} {plant}")
    assert len(problems) == 1, problems
    assert problems[0].startswith("P-1: ") and repr(named) in problems[0] and key in problems[0]


def test_the_planted_incoherence_alone_is_reported_in_the_title_too() -> None:
    doc = _doc("P-1", "grade", "Grade 8", "plain", title="A Grade 5 nut")
    other = _doc("O-1", "grade", "Grade 5", "plain")
    problems = standard.text_contradictions(doc, standard.value_pools([doc, other]))
    assert len(problems) == 1 and "'Grade 5'" in problems[0]


# -- the industrial golden -------------------------------------------------------------------


@pytest.fixture(scope="module")
def golden() -> list[dict[str, Any]]:
    with GOLDEN.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def test_the_industrial_golden_has_no_contradicting_text(golden) -> None:
    problems = standard.check_catalog(golden, text_exempt=hammers.decoy_ids(golden))
    assert problems == [], f"{len(problems)} problems, e.g. {problems[:5]}"


def test_every_finding_the_golden_would_have_without_the_decoy_exemption_is_a_decoy(
    golden,
) -> None:
    """A decoy names a material the line does not have, by design (gen#294): the one exemption
    is by id, and the ids are the decoys', never a document that merely differs."""
    decoys = hammers.decoy_ids(golden)
    assert decoys
    flagged = {p.split(":")[0] for p in standard.check_catalog(golden)}
    assert flagged and flagged <= decoys, sorted(flagged - decoys)[:5]


def test_a_hammer_that_is_no_decoy_is_still_checked(golden) -> None:
    decoys = hammers.decoy_ids(golden)
    plain = next(
        d for d in golden if d["category_leaf"] == "Hammers" and d["product_id"] not in decoys
    )
    # A claim, not "Hickory-Look": a value before a hyphen is no claim (gen#187).
    planted = {**plain, "title": f"{plain['title']}, Hickory Handle"}
    handle = next(e["value"] for e in plain["attributes"] if e["key"] == "handle_material")
    assert handle != "Hickory"
    problems = standard.check_catalog([*golden, planted], text_exempt=decoys)
    assert any("'Hickory'" in p for p in problems), problems[:3]
    hyphen = {**plain, "title": f"{plain['title']}, Hickory-Look"}
    again = standard.check_catalog([*golden, hyphen], text_exempt=decoys)
    assert not any("'Hickory'" in p for p in again), again[:3]


@pytest.mark.parametrize(
    ("title", "decoy"),
    [
        pytest.param("Lantern Rock Core BP98 -- Ball Pein Hammer, Hickory-Look", True, id="look"),
        pytest.param("Claw Hammer, Sledge Series", True, id="series"),
        pytest.param("Claw Hammer, Hickory Creek", True, id="creek"),
        pytest.param(
            "Pennock & Hale Shop FH12 -- General Purpose Framing Hammer", False, id="plain"
        ),
        pytest.param("Claw Hammer, 16 oz", False, id="weight"),
    ],
)
def test_the_decoy_title_predicate(title: str, decoy: bool) -> None:
    assert hammers.is_decoy_title(title) is decoy


def test_a_milled_face_is_said_only_of_a_milled_face(golden) -> None:
    """The framing kind's use line said it of every framing hammer, a smooth face included."""
    said = [
        d
        for d in golden
        if any(re.search(r"\bmilled face\b", v.get("description", ""), re.I) for v in d["variants"])
    ]
    faces = {e["value"] for d in said for e in d["attributes"] if e["key"] == "face_type"}
    assert faces <= {"Milled"}, faces


@pytest.mark.parametrize("kind", sorted(hammers.KINDS))
def test_a_use_line_says_milled_only_of_a_kind_whose_every_face_is_milled(kind: str) -> None:
    """A use line is told of every product of the kind: the face it names is every one's."""
    spec = hammers.KINDS[kind]
    if any(re.search(r"\bmilled\b", line, re.IGNORECASE) for line in spec.use_lines):
        assert spec.faces == ("Milled",), spec.faces
