"""Class 8 decoys: a line named after a fit or a shape on a product without it (gen#434, gap 4).

Without these, "balloon jeans", "high rise jeans" and "plunge bra" find only products that carry
the attribute, so the leg fit, rise and bra shape policies have nothing to remove. A class 8
decoy is a "Balloon Lane" line on a straight leg: the word is the line's name, the attribute is
the true one (#404). Every value of the three attributes the catalog holds gets three, and the
no-policy baseline (:mod:`baseline_rank`) ranks them in the top 10 of the value's query.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_apparel as da  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402

PER_VALUE = 3
#: A jean whose text says "cropped" also carries the Cropped fit (``facet_leaves.CROPPED``), so a
#: line named Cropped would be a right fit, not a decoy.
NOT_PLANTED = {"leg_fit": {"Cropped"}}
KINDS = {  # attribute key -> the query a value is looked for with, on the type that holds it
    "leg_fit": ("Jeans", "{} jeans"),
    "rise": ("Jeans", "{} rise jeans"),
    "bra_shape": ("Bra", "{} bra"),
}


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


@pytest.fixture(scope="module")
def rows() -> list[da.Row]:
    body = [d for d in scale.templates(baseline=False) if d["product_id"] not in da.IDS]
    return [r for r in da.build(body) if r.cls == 8]


def _values(ceiling: list[dict]) -> dict[str, set[str]]:
    """Every value of each kind the live (not decoy) products of its type carry, as exported."""
    out: dict[str, set[str]] = {k: set() for k in KINDS}
    for rec in ceiling:
        if rec["product_id"] in da.IDS:
            continue
        for key, (ptype, _) in KINDS.items():
            if rec["product_type"] == ptype:
                out[key] |= {
                    str(a["value"])
                    for a in export.standard_document(rec)["attributes"]
                    if a["key"] == key
                }
    return {k: v - NOT_PLANTED.get(k, set()) for k, v in out.items()}


def test_every_value_of_leg_fit_rise_and_bra_shape_has_three_class_8_decoys(
    rows: list[da.Row], ceiling: list[dict]
) -> None:
    values = _values(ceiling)
    assert {len(v) > 2 for v in values.values()} == {True}, values
    for key, (_, query) in KINDS.items():
        for value in sorted(values[key]):
            got = [r for r in rows if r.query == query.format(value.lower())]
            assert len(got) >= PER_VALUE, (key, value, len(got))


def test_a_class_8_decoy_names_the_word_and_its_attribute_is_another(
    rows: list[da.Row], ceiling: list[dict]
) -> None:
    by_id = {r["product_id"]: r for r in ceiling}
    assert rows and {r.pid for r in rows} <= da.IDS == {p for p in by_id if p in da.IDS}
    for r in rows:
        doc = export.standard_document(by_id[r.pid])
        assert r.word in doc["title"].lower(), (r.pid, r.word, doc["title"])
        held = {str(a["value"]).lower() for a in doc["attributes"]}
        assert r.word not in held, (r.pid, r.word, held)
        assert doc["category_leaf"].lower() != f"{r.word} jeans", (r.pid, doc["category_leaf"])


@pytest.mark.parametrize("key", sorted(KINDS))
def test_the_baseline_ranks_three_decoys_in_the_top_10_of_every_value(
    key: str, rows: list[da.Row], ceiling: list[dict], index: br.Index
) -> None:
    asked = {r.pid: r.query for r in rows}
    _, query = KINDS[key]
    for value in sorted(_values(ceiling)[key]):
        q = query.format(value.lower())
        top = [d["product_id"] for d in br.rank(index, q, 10)]
        # the decoys planted for THIS word: "barrel" decoys also read as "balloon" (a synonym)
        assert len([p for p in top if asked.get(p) == q]) >= PER_VALUE, (key, value, top)
