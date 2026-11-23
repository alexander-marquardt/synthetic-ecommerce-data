"""Bath and shaving depth in ``Beauty`` (gen#1112, slice 3).

The served index held 417 deodorant SKUs, 292 shower gel SKUs, no razor cartridge and no shave
gel, so 'antiperspirant', 'body wash', 'razor cartridges' and 'shave gel' found nothing. This
slice extends the two existing types and adds two under ``Beauty > Shaving``:

* Deodorant (gen#957's type) gains rows whose title shows a ``protection`` value (Antiperspirant
  or Aluminum-Free) beside the scent and applicator: about 800 SKUs at the ceiling;
* Shower Gel gains derivable rows of its own, titled 'Body Wash', each showing a scent and a
  ``wash_finish`` and sold by volume: about 700 SKUs;
* Razor Cartridges (blade count and strip) and Shave Gel (scent and skin type): about 300
  between them.

The ceiling build must hold 95% of each target. Each new type passes the per-type gates of
gen#1112 slice 1: uniqueness, census, byte-determinism and a golden slice. Rewrite a slice with
``uv run python tests/test_retail_bath_shave_1112.py``.
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
SHAVING = ("Beauty", "Shaving")
#: Each new type's shape, the attribute keys its title shows (its axes) and its SKU quantity.
NEW = {
    "razor_cartridges": ("razor_cartridge_pack", ("blades", "cartridge_strip"), "piece_count"),
    "shave_gel": ("shave_gel_can", ("scent", "skin_type"), "net_volume_ml"),
}
NEW_KEYS = tuple(NEW)
#: The spec rows this slice adds to an existing type: the type's key, the attribute keys their
#: titles show, the shape and the SKU quantity.
EXTENDED = {
    "deodorant": (("scent", "applicator", "protection"), "deodorant", "units_per_pack"),
    "shower_gel": (("scent", "wash_finish"), "body_wash_bottle", "net_volume_ml"),
}
#: 95% of the issue's targets at the ceiling: deodorant to about 800, body wash (Shower Gel) to
#: about 700, razor cartridges and shave gel about 300 between them.
TARGETS = {"Deodorant": 760, "Shower Gel": 665}
NEW_TARGET = 285
PROTECTION = {"Antiperspirant", "Aluminum-Free"}
#: Each query of the PR's list and the product types every title holding it belongs to.
QUERIES = {
    "antiperspirant": {"Deodorant"},
    "body wash": {"Shower Gel"},
    "razor cartridges": {"Razor Cartridges"},
    "shave gel": {"Shave Gel"},
}


def _spec(key: str) -> type_registry.TypeSpec:
    specs = type_registry.specs()
    assert key in specs, f"{key} is not a registered type"
    return specs[key]


def _mine(ceiling, key: str) -> list[dict]:
    return [r for r in ceiling.records if r["product_type"] == _spec(key).product_type]


def _holds(title: str, query: str) -> bool:
    return re.search(rf"\b{re.escape(query)}\b", title, re.I) is not None


def _found(ceiling, query: str) -> set[str]:
    return {r["product_type"] for r in ceiling.records if _holds(r["title"], query)}


def _skus(ceiling, product_type: str) -> int:
    return sum(r["sku_count"] for r in ceiling.records if r["product_type"] == product_type)


def _added(key: str) -> list:
    """The spec rows of ``key`` whose title shows every axis this slice gives it."""
    axes = EXTENDED[key][0]
    rows = [r for r in _spec(key).rows if {k for k, _n, _v in r.attrs} >= set(axes)]
    assert rows, f"{key} has no row with the axes {axes}"
    return rows


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def test_the_two_shaving_types_are_registered() -> None:
    assert sorted(set(NEW_KEYS) - set(type_registry.specs())) == []


@pytest.mark.parametrize("ptype", sorted(TARGETS))
def test_the_ceiling_holds_the_extended_type_near_its_target(ptype: str, ceiling) -> None:
    assert _skus(ceiling, ptype) >= TARGETS[ptype]


def test_the_ceiling_holds_about_300_razor_cartridge_and_shave_gel_skus(ceiling) -> None:
    assert sum(_skus(ceiling, _spec(k).product_type) for k in NEW_KEYS) >= NEW_TARGET


def test_the_ceiling_sells_deodorant_in_both_protections(ceiling) -> None:
    found = {
        str(a["value"])
        for r in _mine(ceiling, "deodorant")
        for a in r["attributes"]
        if a["key"] == "protection"
    }
    assert found == PROTECTION


@pytest.mark.parametrize("query", sorted(QUERIES))
def test_each_query_finds_its_own_family_in_the_whole_catalogue(query: str, ceiling) -> None:
    assert _found(ceiling, query) == QUERIES[query]


@pytest.mark.parametrize("key", sorted(EXTENDED))
def test_the_added_rows_show_their_axes_and_draw_them(key: str) -> None:
    axes, shape, size_key = EXTENDED[key]
    spec = _spec(key)
    assert spec.derivable
    rows = _added(key)
    assert len(rows) >= 3 and len({r.brand for r in rows}) >= 3
    for row in rows:
        assert row.product_type == spec.product_type, row.code
        assert row.shape == shape and shape in kit.shapes(), row.code
        assert row.colorless and row.size_key == size_key, row.code
        values = {k: str(v) for k, _n, v in row.attrs}
        for k in axes:  # the title shows each axis, so the scaled build may swap it
            assert _holds(row.title, values[k]), (row.code, k)
        assert dict(row.params) == {k: values[k].lower() for k in axes}, row.code
    for k in axes:
        assert len({dict((a, str(v)) for a, _n, v in r.attrs)[k] for r in rows}) >= 2, k


def test_the_body_wash_rows_are_titled_body_wash() -> None:
    assert all(_holds(r.title, "Body Wash") for r in _added("shower_gel"))


@pytest.mark.parametrize("key", NEW_KEYS)
def test_the_type_is_a_derivable_shaving_spec_with_its_axes_and_shape(key: str) -> None:
    spec = _spec(key)
    shape, axes, size_key = NEW[key]
    assert spec.department == ROOT
    assert spec.derivable
    assert len(spec.rows) >= 4
    assert len({r.brand for r in spec.rows}) >= 3
    for row in (*spec.rows, *(d.row for d in spec.decoys)):
        assert row.path == (*SHAVING, spec.product_type), row.code
        assert row.product_type == spec.product_type, row.code
        assert row.shape == shape and shape in kit.shapes(), row.code
        assert row.colorless and row.size_key == size_key, row.code
        values = {k: str(v) for k, _n, v in row.attrs}
        assert sorted(values) == sorted(axes), row.code
        for k in axes:
            assert _holds(row.title, values[k]), (row.code, k)
        # Each drawing param is an attribute of the row with its lower-cased value, so a derived
        # style that swaps the value draws what it states (gen#512).
        assert dict(row.params) == {k: v.lower() for k, v in values.items()}, row.code
        prices = [p for _s, p in row.sizes]
        assert prices == sorted(prices) and len(set(prices)) == len(prices), row.code
    for k in axes:
        assert len({dict((a, str(v)) for a, _n, v in r.attrs)[k] for r in spec.rows}) >= 2, k


#: Every param a shape of this slice reads, and the values its rows give it.
DRAWN = [
    ("razor_cartridge_pack", "blades", ("3-blade", "4-blade", "5-blade")),
    ("razor_cartridge_pack", "cartridge_strip", ("aloe", "shea", "charcoal", "cooling")),
    ("shave_gel_can", "scent", ("aloe vera", "menthol", "sandalwood", "unscented", "coconut")),
    ("shave_gel_can", "skin_type", ("sensitive", "normal", "dry")),
    ("body_wash_bottle", "wash_finish", ("creamy", "foaming", "exfoliating", "silky")),
    ("body_wash_bottle", "scent", ("coconut", "lavender", "honey", "mint")),
    ("deodorant", "protection", ("antiperspirant", "aluminum-free")),
]


@pytest.mark.parametrize(("shape", "param", "values"), DRAWN)
def test_each_param_value_of_the_shape_draws_a_different_figure(shape, param, values) -> None:
    """A param no drawing shows would let a derived style state what its picture does not."""
    fill = kit.Fill("solid", "#ffffff", "#2a2a2e")
    drawn = {kit.render(shape, fill, uid="f", params={param: v}) for v in values}
    assert len(drawn) == len(values)


@pytest.mark.parametrize("key", (*NEW_KEYS, *EXTENDED))
def test_no_title_or_description_makes_a_medical_claim(key: str) -> None:
    """The new types' documents and the rows this slice adds to an existing type."""
    docs = _spec(key).docs() if key in NEW else [r.doc() for r in _added(key)]
    claims = [
        f"{d['product_id']}: {m.group(0)!r}"
        for d in docs
        for m in [CLAIM.search(f"{d['title']} {d['description']}")]
        if m
    ]
    assert docs and claims == []


@pytest.mark.parametrize("key", NEW_KEYS)
def test_the_type_plants_text_match_decoys(key: str) -> None:
    decoys = _spec(key).decoys
    assert len(decoys) >= 2
    assert all(1 <= d.cls <= 7 for d in decoys)
    for d in decoys:
        assert d.query.split()[0].lower() in d.row.title.lower(), d.row.code


@pytest.mark.parametrize("key", NEW_KEYS)
def test_the_ceiling_sells_the_type_with_derived_styles(key: str, ceiling) -> None:
    assert len(_mine(ceiling, key)) > 3 * len(_spec(key).rows)


@pytest.mark.parametrize("key", (*NEW_KEYS, *EXTENDED))
def test_uniqueness_no_id_sku_or_title_is_shared_within_the_type(key: str, ceiling) -> None:
    mine = _mine(ceiling, key)
    for field in ("product_id", "title"):
        values = [r[field] for r in mine]
        assert [v for v, n in collections.Counter(values).items() if n > 1] == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert [s for s, n in collections.Counter(skus).items() if n > 1] == []


@pytest.mark.parametrize("key", NEW_KEYS)
def test_census_the_type_meets_the_output_standard_under_shaving(key: str, ceiling) -> None:
    docs = scale.documents(scale.Scaled(_mine(ceiling, key), {}))
    assert check_catalog(docs, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    assert {tuple(d["category_path"][:2]) for d in docs} == {tuple(map(sentence_case, SHAVING))}


@pytest.mark.parametrize("key", (*NEW_KEYS, *EXTENDED))
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


@pytest.mark.parametrize("key", NEW_KEYS)
def test_the_committed_golden_slice_is_a_fresh_build(key: str) -> None:
    _spec(key)
    path = _slice_path(key)
    assert path.is_file(), f"no golden slice at {path}: run this file as a script"
    assert path.read_text(encoding="utf-8") == _slice_text(key)


if __name__ == "__main__":
    SLICES.mkdir(parents=True, exist_ok=True)
    for _key in NEW_KEYS:
        _slice_path(_key).write_text(_slice_text(_key), encoding="utf-8")
        print(_slice_path(_key))
