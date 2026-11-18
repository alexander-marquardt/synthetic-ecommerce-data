"""Eye care, incontinence and mobility aids: three more Health types, each with its own shape
(gen#968, slice 3).

Slices 1 and 2 put ``Health`` on the closed department lists with vitamins, minerals, first aid
and health monitors. This cut of slice 3 adds eye drops under ``Health > Eye Care``, incontinence
pads under ``Health > Incontinence`` and walking sticks under ``Health > Mobility Aids``. Each type
is drawn by a shape of :mod:`kit_health_care`, sold over the counter only, with invented brands
and no medical or efficacy claim in any title or description.

Each type passes the per-type gates the issue names, on its own (``docs/retail-health.md``):
uniqueness, census, byte-determinism and a golden slice, read as in slice 1's
``tests/test_retail_health_vitamins_968.py``, whose helpers this file reuses. Rewrite a slice
with ``uv run python tests/test_retail_health_care_968.py``.
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
import subprocess
import sys

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core.letter_case import sentence_case
from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry
from test_retail_health_vitamins_968 import _DIGEST, CLAIM, SLICES, _slice_path, _slice_text

ROOT = "Health"
#: Each type's parent node and the shape that draws it.
TYPES = {
    "eye_drops": (("Health", "Eye Care"), "eye_drop_bottle"),
    "incontinence_pads": (("Health", "Incontinence"), "pad_pack"),
    "walking_sticks": (("Health", "Mobility Aids"), "walking_stick"),
}
KEYS = tuple(TYPES)


def _spec(key: str) -> type_registry.TypeSpec:
    return type_registry.specs()[key]


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def test_the_three_eye_care_incontinence_and_mobility_types_are_registered() -> None:
    assert sorted(set(KEYS) - set(type_registry.specs())) == []


@pytest.mark.parametrize("key", KEYS)
def test_the_type_is_a_derivable_health_spec_drawn_by_its_own_shape(key: str) -> None:
    spec = _spec(key)
    parent, shape = TYPES[key]
    assert spec.department == ROOT
    assert spec.derivable
    assert len(spec.rows) >= 4
    assert len({r.brand for r in spec.rows}) >= 2
    for row in (*spec.rows, *(d.row for d in spec.decoys)):
        assert row.path[:2] == parent, row.code
        assert row.product_type == spec.product_type, row.code
        assert row.shape == shape and shape in kit.SHAPES, row.code
        assert row.colorless, row.code
        # Each drawing param is an attribute value of the row, so a derived style that swaps
        # the value draws what it states (gen#512).
        values = {str(v).lower() for _k, _n, v in row.attrs}
        assert row.params and all(v in values for _p, v in row.params), row.code
        prices = [p for _s, p in row.sizes]
        assert prices == sorted(prices) and len(set(prices)) == len(prices), row.code


@pytest.mark.parametrize("shape", sorted({s for _p, s in TYPES.values()}))
def test_each_param_value_of_a_shape_draws_a_different_figure(shape: str) -> None:
    """A param no drawing shows would let a derived style state what its picture does not."""
    rows = [r for k in KEYS for r in (*_spec(k).rows, *(d.row for d in _spec(k).decoys))
            if r.shape == shape]  # fmt: skip
    fill = kit.Fill("solid", "#ffffff", "#2a2a2e")
    drawn: dict[str, str] = {}
    for row in rows:
        for param, value in row.params:
            drawn[value] = kit.render(shape, fill, uid="h", params={param: value})
    assert len(drawn) >= 2
    assert len(set(drawn.values())) == len(drawn), sorted(drawn)


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
    mine = [r for r in ceiling.records if r["product_type"] == _spec(key).product_type]
    assert len(mine) > len(_spec(key).rows)  # derived styles reach the ceiling


@pytest.mark.parametrize("key", KEYS)
def test_uniqueness_no_id_sku_or_title_is_shared_within_the_type(key: str, ceiling) -> None:
    mine = [r for r in ceiling.records if r["product_type"] == _spec(key).product_type]
    for field in ("product_id", "title"):
        values = [r[field] for r in mine]
        assert [v for v, n in collections.Counter(values).items() if n > 1] == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert [s for s, n in collections.Counter(skus).items() if n > 1] == []


@pytest.mark.parametrize("key", KEYS)
def test_census_the_type_meets_the_output_standard_under_health(key: str, ceiling) -> None:
    mine = [r for r in ceiling.records if r["product_type"] == _spec(key).product_type]
    docs = scale.documents(scale.Scaled(mine, {}))
    assert check_catalog(docs, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    parent = TYPES[key][0]
    assert {tuple(d["category_path"][:2]) for d in docs} == {tuple(map(sentence_case, parent))}


@pytest.mark.parametrize("key", KEYS)
def test_byte_determinism_two_hash_seeds_build_the_same_bytes(key: str) -> None:
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
    here = hashlib.sha256(
        json.dumps(
            sorted(_spec(key).docs(), key=lambda d: d["product_id"]), sort_keys=True
        ).encode()
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
