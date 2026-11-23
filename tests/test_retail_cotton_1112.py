"""Cotton: cotton pads, cotton buds and cotton wool under ``Beauty`` (gen#1112, slice 2).

The served index held no cotton pad, bud or wool, so 'cotton pads' found nothing and 'pads' found
only incontinence pads. This slice adds three Beauty types under ``Beauty > Cotton``, each a
derivable spec drawn by its own shape of :mod:`kit_beauty_cotton`. A style's SKUs are its pack
counts (its weights, for cotton wool), and its title shows its axes: a pad's shape and texture, a
bud's stem and tip, the wool's form and grade. The issue asks for about 250 SKUs between them;
the ceiling build must hold 95% of that.

Each type also passes the per-type gates of gen#1112 slice 1 (``tests/test_retail_feminine_care_
1112.py``): uniqueness, census, byte-determinism and a golden slice. Rewrite a slice with
``uv run python tests/test_retail_cotton_1112.py``.
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
import re
import subprocess
import sys

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core.letter_case import sentence_case
from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry
from test_retail_health_vitamins_968 import _DIGEST, CLAIM, SLICES, _slice_path, _slice_text

ROOT = "Beauty"
PARENT = ("Beauty", "Cotton")
#: Each type's shape, the attribute keys its title shows (its axes) and its SKU quantity.
TYPES = {
    "cotton_pads": ("cotton_pad_pack", ("pad_shape", "pad_texture"), "piece_count"),
    "cotton_buds": ("cotton_bud_tub", ("bud_stem", "bud_tip"), "piece_count"),
    "cotton_wool": ("cotton_wool_bag", ("wool_form", "cotton_grade"), "net_weight_g"),
}
KEYS = tuple(TYPES)
#: About 250 SKUs between the three (the issue's target), 95% of it at the ceiling.
TARGET = 238
#: The departments where 'pads' names a personal-care pad (elsewhere it is a mop's or a polisher's).
CARE = ("Beauty", "Health")
#: The pad families of gen#1112: cotton (this slice), sanitary (slice 1) and incontinence.
PAD_FAMILIES = {"Cotton Pads", "Sanitary Pads", "Incontinence Pads"}
#: Each query of the PR's list and the product types every title holding it belongs to.
QUERIES = {
    "cotton pads": {"Cotton Pads"},
    "cotton buds": {"Cotton Buds"},
    "cotton wool": {"Cotton Wool"},
}


def _spec(key: str) -> type_registry.TypeSpec:
    specs = type_registry.specs()
    assert key in specs, f"{key} is not a registered type"
    return specs[key]


def _mine(ceiling, key: str) -> list[dict]:
    return [r for r in ceiling.records if r["product_type"] == _spec(key).product_type]


def _holds(title: str, query: str) -> bool:
    return re.search(rf"\b{re.escape(query)}\b", title, re.I) is not None


def _found(ceiling, query: str, roots: tuple[str, ...] | None = None) -> set[str]:
    return {
        r["product_type"]
        for r in ceiling.records
        if (roots is None or r["category_path"][0] in roots) and _holds(r["title"], query)
    }


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def test_the_three_cotton_types_are_registered() -> None:
    assert sorted(set(KEYS) - set(type_registry.specs())) == []


def test_the_ceiling_holds_about_250_cotton_skus(ceiling) -> None:
    skus = sum(r["sku_count"] for r in ceiling.records if tuple(r["category_path"][:2]) == PARENT)
    assert skus >= TARGET


@pytest.mark.parametrize("query", sorted(QUERIES))
def test_each_cotton_query_finds_its_own_family_in_the_whole_catalogue(query: str, ceiling) -> None:
    assert _found(ceiling, query) == QUERIES[query]


def test_pads_finds_the_cotton_sanitary_and_incontinence_families(ceiling) -> None:
    """'pads' in Beauty and Health finds a pad family only: cotton and incontinence pads, and
    sanitary pads whenever slice 1's type is registered (then three families)."""
    want = {"Cotton Pads", "Incontinence Pads"}
    if any(s.product_type == "Sanitary Pads" for s in type_registry.specs().values()):
        want.add("Sanitary Pads")
    found = _found(ceiling, "pads", CARE)
    assert found <= PAD_FAMILIES
    assert found == want


@pytest.mark.parametrize("key", KEYS)
def test_the_type_is_a_derivable_beauty_spec_with_its_axes_and_shape(key: str) -> None:
    spec = _spec(key)
    shape, axes, size_key = TYPES[key]
    assert spec.department == ROOT
    assert spec.derivable
    assert len(spec.rows) >= 5
    assert len({r.brand for r in spec.rows}) >= 3
    for row in (*spec.rows, *(d.row for d in spec.decoys)):
        assert row.path == (*PARENT, spec.product_type), row.code
        assert row.product_type == spec.product_type, row.code
        assert row.shape == shape and shape in kit.shapes(), row.code
        assert row.colorless and row.size_key == size_key, row.code
        values = {k: str(v) for k, _n, v in row.attrs}
        assert sorted(values) == sorted(axes), row.code
        for k in axes:  # the title shows each axis, so the scaled build may swap it
            assert _holds(row.title, values[k]), (row.code, k)
        # Each drawing param is an attribute of the row with its lower-cased value, so a derived
        # style that swaps the value draws what it states (gen#512).
        assert dict(row.params) == {k: v.lower() for k, v in values.items()}, row.code
        prices = [p for _s, p in row.sizes]
        assert prices == sorted(prices) and len(set(prices)) == len(prices), row.code
    for k in axes:  # every axis has two values or more across the type's rows
        assert len({dict((a, str(v)) for a, _n, v in r.attrs)[k] for r in spec.rows}) >= 2, k


@pytest.mark.parametrize("key", KEYS)
def test_each_param_value_of_the_shape_draws_a_different_figure(key: str) -> None:
    """A param no drawing shows would let a derived style state what its picture does not."""
    spec = _spec(key)
    fill = kit.Fill("solid", "#ffffff", "#2a2a2e")
    for param in {p for r in spec.rows for p, _v in r.params}:
        values = sorted({v for r in spec.rows for p, v in r.params if p == param})
        drawn = {v: kit.render(TYPES[key][0], fill, uid="f", params={param: v}) for v in values}
        assert len(drawn) >= 2
        assert len(set(drawn.values())) == len(drawn), (param, sorted(drawn))


@pytest.mark.parametrize("key", KEYS)
def test_no_title_or_description_makes_a_medical_claim(key: str) -> None:
    docs = _spec(key).docs()
    claims = [
        f"{d['product_id']}: {m.group(0)!r}"
        for d in docs
        for m in [CLAIM.search(f"{d['title']} {d['description']}")]
        if m
    ]
    assert docs and claims == []


@pytest.mark.parametrize("key", KEYS)
def test_the_type_plants_text_match_decoys(key: str) -> None:
    decoys = _spec(key).decoys
    assert len(decoys) >= 2
    assert all(1 <= d.cls <= 7 for d in decoys)
    for d in decoys:
        assert d.query.split()[0].lower() in d.row.title.lower(), d.row.code


@pytest.mark.parametrize("key", KEYS)
def test_the_ceiling_sells_the_type_with_derived_styles(key: str, ceiling) -> None:
    assert len(_mine(ceiling, key)) > 3 * len(_spec(key).rows)


@pytest.mark.parametrize("key", KEYS)
def test_uniqueness_no_id_sku_or_title_is_shared_within_the_type(key: str, ceiling) -> None:
    mine = _mine(ceiling, key)
    for field in ("product_id", "title"):
        values = [r[field] for r in mine]
        assert [v for v, n in collections.Counter(values).items() if n > 1] == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert [s for s, n in collections.Counter(skus).items() if n > 1] == []


@pytest.mark.parametrize("key", KEYS)
def test_census_the_type_meets_the_output_standard_under_beauty(key: str, ceiling) -> None:
    docs = scale.documents(scale.Scaled(_mine(ceiling, key), {}))
    assert check_catalog(docs, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    assert {tuple(d["category_path"][:2]) for d in docs} == {tuple(map(sentence_case, PARENT))}


@pytest.mark.parametrize("key", KEYS)
def test_byte_determinism_two_hash_seeds_build_the_same_bytes(key: str) -> None:
    docs = sorted(_spec(key).docs(), key=lambda d: d["product_id"])
    digests = set()
    for seed in ("0", "1"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        out = subprocess.run(
            [sys.executable, "-c", _DIGEST, key],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        digests.add(out.stdout.strip())
    here = hashlib.sha256(json.dumps(docs, sort_keys=True).encode()).hexdigest()
    assert digests == {here}


@pytest.mark.parametrize("key", KEYS)
def test_the_committed_golden_slice_is_a_fresh_build(key: str) -> None:
    _spec(key)
    path = _slice_path(key)
    assert path.is_file(), f"no golden slice at {path}: run this file as a script"
    assert path.read_text(encoding="utf-8") == _slice_text(key)


if __name__ == "__main__":
    SLICES.mkdir(parents=True, exist_ok=True)
    for _key in KEYS:
        _slice_path(_key).write_text(_slice_text(_key), encoding="utf-8")
        print(_slice_path(_key))
