"""Every product carries a seeded 0-100 ``merchandising_score`` (gen#182).

Pinned for both catalogs: the field is on every product and every flat document, an
integer in [0, 100], the same for the same seed; it follows the product's volume loosely
(a rank correlation that is neither about 1 nor about 0); and a few percent of products are
"strategic pushes": a high score on weak popularity.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import emit, merchandising
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.model import Catalog
from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.industrial.generate import generate

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import scale  # noqa: E402

#: The rank correlation of the score with popularity must sit in this band: below it the
#: score would not follow popularity at all, above it boosting on it would reorder nothing.
CORRELATION_BAND = (0.15, 0.70)
#: Products scoring at least :data:`merchandising.PUSH_FLOOR` on below-median popularity,
#: as a share of all products: "a few percent".
PUSH_SHARE_BAND = (0.01, 0.07)


def ranks(values: list[float]) -> list[float]:
    """1-based ranks, a tie sharing the mean of the ranks it spans."""
    order = sorted(range(len(values)), key=values.__getitem__)
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return out


def spearman(a: list[float], b: list[float]) -> float:
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb, strict=True))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (va * vb)


def push_share(scores: list[int], popularity: list[float]) -> float:
    median = sorted(popularity)[len(popularity) // 2]
    pushed = sum(
        1 for s, p in zip(scores, popularity, strict=True)
        if s >= merchandising.PUSH_FLOOR and p < median
    )  # fmt: skip
    return pushed / len(scores)


# ---------------------------------------------------------------- the function


def test_the_score_is_fixed_by_seed_key_and_signal():
    again = [merchandising.merchandising_score(7, f"P{i}", i / 100) for i in range(100)]
    assert again == [merchandising.merchandising_score(7, f"P{i}", i / 100) for i in range(100)]
    other = [merchandising.merchandising_score(8, f"P{i}", i / 100) for i in range(100)]
    assert other != again, "a different seed gives different scores"


def test_the_score_is_an_integer_in_range_at_every_signal():
    for signal in (None, 0.0, 0.2, 0.39, 0.4, 0.7, 1.0):
        for i in range(300):
            score = merchandising.merchandising_score(1, f"K{i}", signal)
            assert type(score) is int
            assert 0 <= score <= 100


def test_only_a_weak_signal_can_be_a_push():
    strong = [merchandising.merchandising_score(1, f"K{i}", 0.5) for i in range(2000)]
    none = [merchandising.merchandising_score(1, f"K{i}", None) for i in range(2000)]
    weak = [merchandising.merchandising_score(1, f"K{i}", 0.1) for i in range(2000)]
    # 0.5 * 0.5 + 0.5 * free is at most 75, so nothing at or past the floor without a push
    assert max(strong) < merchandising.PUSH_FLOOR
    assert sum(s >= merchandising.PUSH_FLOOR for s in none) > 0  # free draw alone reaches it
    pushed = sum(s >= merchandising.PUSH_FLOOR for s in weak) / len(weak)
    assert 0.12 < pushed < 0.3, "about PUSH_OF_WEAK of weak-signal products are pushes"


def test_the_blend_ignores_a_missing_part_and_is_none_without_any():
    assert merchandising.blend([(1.0, None), (2.0, None)]) is None
    assert merchandising.blend([(1.0, 0.0), (3.0, 1.0)]) == 0.75
    assert merchandising.blend([(1.0, None), (3.0, 0.5)]) == 0.5


def test_a_log_signal_is_clipped_to_unit_range():
    assert merchandising.log_signal(0, 100) == 0.0
    assert merchandising.log_signal(-5, 100) == 0.0
    assert merchandising.log_signal(100, 100) == 1.0
    assert merchandising.log_signal(10**6, 100) == 1.0
    assert 0.0 < merchandising.log_signal(10, 100) < 1.0


# ------------------------------------------------------------------ industrial

INDUSTRIAL = generate(SMALL)


def test_industrial_is_deterministic_per_seed():
    first = [d["merchandising_score"] for d in emit.iter_nested(INDUSTRIAL)]
    assert first == [d["merchandising_score"] for d in emit.iter_nested(generate(SMALL))]
    reseeded = generate(dataclasses.replace(SMALL, seed=SMALL.seed + 1))
    assert first != [d["merchandising_score"] for d in emit.iter_nested(reseeded)]


def _scores_by_sku(catalog) -> dict[str, float]:
    return {d["sku"]: d["facets_num"]["merchandising_score"] for d in emit.iter_flat(catalog)}


def test_industrial_score_is_the_products_own_in_every_build_that_holds_it():
    """A SKU scores the same alone, in two different subsets and in the whole build,
    and with its lines rewrapped in a bare ``Catalog`` as the golden-slice gates do:
    nothing about the rest of the build enters it (gen#183)."""
    whole = generate(SMALL)
    types = sorted({line.type_key for line in whole.lines})
    key = types[0]
    full = _scores_by_sku(whole)
    builds = {
        "alone": generate(SMALL, [key]),
        "with the next type": generate(SMALL, [key, types[1]]),
        "with the last type": generate(SMALL, [key, types[-1]]),
        "rewrapped": Catalog(lines=tuple(line for line in whole.lines if line.type_key == key)),
    }
    for name, build in builds.items():
        part = _scores_by_sku(build)
        assert part, f"the {name} build is empty"
        moved = {
            sku: (full.get(sku), score) for sku, score in part.items() if full.get(sku) != score
        }
        assert not moved, (
            f"{name}: {len(moved)} SKU(s) score differently, e.g. {list(moved.items())[:3]}"
        )


def test_industrial_every_product_and_flat_document_carries_it_in_range():
    nested = list(emit.iter_nested(INDUSTRIAL))
    flat = list(emit.iter_flat(INDUSTRIAL))
    assert nested and flat
    for doc in nested:
        assert type(doc["merchandising_score"]) is int
        assert 0 <= doc["merchandising_score"] <= 100
    by_product = {d["product_id"]: d["merchandising_score"] for d in nested}
    for row in flat:
        assert row["facets_num"]["merchandising_score"] == by_product[row["product_id"]]
        assert "merchandising_score" not in row["facets"], "a ranking signal is not a shopper facet"


def test_industrial_score_follows_stock_loosely_with_a_few_pushes():
    lines = INDUSTRIAL.lines
    scores = [emit.line_merchandising_score(line) for line in lines]
    stock = [sum(c.stock for c in line.children) / len(line.children) for line in lines]
    rho = spearman([float(s) for s in scores], stock)
    assert CORRELATION_BAND[0] <= rho <= CORRELATION_BAND[1], rho
    assert PUSH_SHARE_BAND[0] <= push_share(scores, stock) <= PUSH_SHARE_BAND[1]


# ---------------------------------------------------------------------- retail


@pytest.fixture(scope="module")
def retail():
    scaled = scale.build(40000)  # the sample floors below: templates carry more SKUs each (gen#275)
    records = scaled.records
    return records, [export.standard_document(r) for r in records]


def test_retail_every_product_carries_it_in_range_and_it_passes_the_standard(retail):
    records, docs = retail
    assert len(docs) > 1000
    assert check_catalog(docs, one_class_per_key=True, text_exempt=scale.DECOY_IDS) == []
    assert all(type(d["merchandising_score"]) is int for d in docs)
    assert all(0 <= d["merchandising_score"] <= 100 for d in docs)


def test_retail_is_deterministic(retail):
    records, docs = retail
    assert [d["merchandising_score"] for d in docs] == [export.merchandising(r) for r in records]
    assert [d["merchandising_score"] for d in docs] == [
        export.standard_document(r)["merchandising_score"] for r in records
    ]


def test_retail_flat_documents_carry_it_in_facets_num(retail):
    _, docs = retail
    flat = scale.flat(docs[:60])
    by_product = {d["product_id"]: d["merchandising_score"] for d in docs}
    assert flat
    for row in flat:
        assert row["facets_num"]["merchandising_score"] == by_product[row["product_id"]]


def test_retail_score_follows_sales_loosely_with_a_few_pushes(retail):
    records, docs = retail
    pairs = [
        (d["merchandising_score"], r["sold_last_5_days"])
        for r, d in zip(records, docs, strict=True)
        if "sold_last_5_days" in r
    ]
    scores, sold = [float(p[0]) for p in pairs], [float(p[1]) for p in pairs]
    assert len(pairs) > 800
    rho = spearman(scores, sold)
    assert CORRELATION_BAND[0] <= rho <= CORRELATION_BAND[1], rho
    assert PUSH_SHARE_BAND[0] <= push_share([int(s) for s in scores], sold) <= PUSH_SHARE_BAND[1]


def test_retail_round_four_records_without_sales_still_get_a_score():
    docs = export.documents()
    bare = [d for d in docs if not any(e["key"] == "sold_last_5_days" for e in d["attributes"])]
    assert bare, "the build holds records that state no sales"
    assert all(0 <= d["merchandising_score"] <= 100 for d in bare)
