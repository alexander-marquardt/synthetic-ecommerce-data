"""The Health department and its first two types, vitamins and minerals (gen#968, slice 1).

The retail catalogue had no Health department: a ``terms`` count on the top level of
``category_path`` found none, where the 500K mix plans 5,000 (``docs/catalogue-mix-837.md``).
This slice puts ``Health`` on the closed department list and adds the first two types under
``Health > Vitamins & Supplements``: tubs of tablets and capsules sold by count, over the counter
only, with invented brands and no medical or efficacy claim in any title or description.

Each type passes the per-type gates the issue names, on its own (``docs/retail-health.md``):
uniqueness (no id, SKU or title shared within the type at the ceiling), census (registered,
in its department and tree, decoys planted, the output standard), byte-determinism (two
processes under two hash seeds build the same bytes) and a golden slice (the committed documents
are a fresh build). Rewrite a slice with ``uv run python tests/test_retail_health_vitamins_968.py``.
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import departments as core_departments
from synthetic_ecommerce_data.core.letter_case import sentence_case
from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import departments, scale, type_registry

KEYS = ("vitamins", "minerals")
ROOT = "Health"
PARENT = ("Health", "Vitamins & Supplements")
SLICES = Path(__file__).parent / "data" / "golden_slices"
#: Words that would make a title or description a medical or efficacy claim (the issue's
#: "Over the counter only": no prescription product, no claim).
CLAIM = re.compile(
    r"\b(cure|cures|treat|treats|treatment|prevent|prevents|boost|boosts|immun\w*|heal\w*|"
    r"relie\w*|clinical\w*|doctor|prescription|disease|deficien\w*|protect\w*|support\w*)\b",
    re.I,
)


def _spec(key: str) -> type_registry.TypeSpec:
    return type_registry.specs()[key]


def _ids(key: str) -> frozenset[str]:
    spec = _spec(key)
    return frozenset(r.product_id for r in (*spec.rows, *(d.row for d in spec.decoys)))


def _slice_text(key: str) -> str:
    docs = sorted(_spec(key).docs(), key=lambda d: d["product_id"])
    return "".join(json.dumps(d, sort_keys=True, ensure_ascii=False) + "\n" for d in docs)


def _slice_path(key: str) -> Path:
    return SLICES / f"retail_{key}.jsonl"


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def test_health_is_on_the_closed_department_lists() -> None:
    assert ROOT in core_departments.RETAIL
    assert ROOT in departments.RETAIL


@pytest.mark.parametrize("key", KEYS)
def test_the_type_is_a_health_spec_under_vitamins_and_supplements(key: str) -> None:
    spec = _spec(key)
    assert spec.department == ROOT
    assert spec.derivable
    rows = [*spec.rows, *(d.row for d in spec.decoys)]
    assert len(spec.rows) >= 4
    assert {r.path[:2] for r in rows} == {PARENT}
    assert {r.product_type for r in rows} == {spec.product_type}
    assert len({r.brand for r in spec.rows}) >= 2


@pytest.mark.parametrize("key", KEYS)
def test_every_style_is_a_tub_sold_by_count_and_a_bigger_tub_costs_more(key: str) -> None:
    for row in _spec(key).rows:
        assert row.shape == "tub" and row.colorless, row.code
        assert re.search(r"\b(Tablets|Capsules)\b", row.title), row.code
        assert row.size_key == "piece_count", row.code
        counts = [int(n) for n, _ in row.sizes]
        prices = [p for _, p in row.sizes]
        assert len(counts) >= 2 and counts == sorted(counts), row.code
        assert prices == sorted(prices) and len(set(prices)) == len(prices), row.code


@pytest.mark.parametrize("key", KEYS)
def test_no_title_or_description_makes_a_medical_claim(key: str, ceiling) -> None:
    ids = _ids(key)
    ptype = _spec(key).product_type
    mine = [r for r in ceiling.records if r["product_id"] in ids or r["product_type"] == ptype]
    claims = [r["product_id"] for r in mine if CLAIM.search(f"{r['title']} {r['description']}")]
    assert mine and claims == []


@pytest.mark.parametrize("key", KEYS)
def test_each_type_carries_text_match_decoys(key: str) -> None:
    decoys = _spec(key).decoys
    assert len(decoys) >= 2
    assert all(1 <= d.cls <= 7 for d in decoys)
    for d in decoys:
        assert d.query.split()[0].lower() in d.row.title.lower(), d.row.code


def test_the_ceiling_holds_health_skus(ceiling) -> None:
    counts = collections.Counter()
    for r in ceiling.records:
        counts[r["category_path"][0]] += r["sku_count"]
    assert counts[ROOT] > 0


@pytest.mark.parametrize("key", KEYS)
def test_uniqueness_no_id_sku_or_title_is_shared_within_the_type(key: str, ceiling) -> None:
    ptype = _spec(key).product_type
    mine = [r for r in ceiling.records if r["product_type"] == ptype]
    assert len(mine) > len(_spec(key).rows)  # derived styles reach the ceiling
    pids = [r["product_id"] for r in mine]
    titles = [r["title"] for r in mine]
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert [p for p, n in collections.Counter(pids).items() if n > 1] == []
    assert [t for t, n in collections.Counter(titles).items() if n > 1] == []
    assert [s for s, n in collections.Counter(skus).items() if n > 1] == []


@pytest.mark.parametrize("key", KEYS)
def test_census_the_type_meets_the_output_standard_under_health(key: str, ceiling) -> None:
    ptype = _spec(key).product_type
    mine = [r for r in ceiling.records if r["product_type"] == ptype]
    docs = scale.documents(scale.Scaled(mine, {}))
    # A spec's text-match decoys contradict their own fields on purpose (scale.TEXT_EXEMPT).
    assert check_catalog(docs, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    # A published node is sentence case (core/letter_case.py): "Vitamins & supplements".
    assert {d["category_path"][0] for d in docs} == {ROOT}
    assert {tuple(d["category_path"][:2]) for d in docs} == {tuple(map(sentence_case, PARENT))}


_DIGEST = (
    "import hashlib, json, sys; "
    "from synthetic_ecommerce_data.domains.retail import type_registry; "
    "docs = sorted(type_registry.specs()[sys.argv[1]].docs(), key=lambda d: d['product_id']); "
    "print(hashlib.sha256(json.dumps(docs, sort_keys=True).encode()).hexdigest())"
)


@pytest.mark.parametrize("key", KEYS)
def test_byte_determinism_two_hash_seeds_build_the_same_bytes(key: str) -> None:
    digests = set()
    for seed in ("0", "1"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        out = subprocess.run(
            [sys.executable, "-c", _DIGEST, key], env=env, capture_output=True, text=True,
            check=True,
        )
        digests.add(out.stdout.strip())
    here = hashlib.sha256(
        json.dumps(sorted(_spec(key).docs(), key=lambda d: d["product_id"]), sort_keys=True)
        .encode()
    ).hexdigest()
    assert digests == {here}


@pytest.mark.parametrize("key", KEYS)
def test_the_committed_golden_slice_is_a_fresh_build(key: str) -> None:
    path = _slice_path(key)
    assert path.is_file(), f"no golden slice at {path}: run this file as a script"
    assert path.read_text(encoding="utf-8") == _slice_text(key)


if __name__ == "__main__":
    SLICES.mkdir(parents=True, exist_ok=True)
    for _key in KEYS:
        _slice_path(_key).write_text(_slice_text(_key), encoding="utf-8")
        print(_slice_path(_key))
