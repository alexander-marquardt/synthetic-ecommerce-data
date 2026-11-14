"""Electronics audio, slice 1 (gen#956): headphones, portable speakers and soundbars.

The Electronics department held 1,166 SKUs at the ceiling build, against the 14,000 the 500K mix
plans (``docs/catalogue-mix-837.md``), and a shopper searching for headphones or a speaker found
little. Slice 1 adds three derivable types under ``Electronics > Audio``, each a spec of its own
(``type_specs/headphones.py``, ``portable_speaker.py``, ``soundbar.py``) drawn by
:mod:`kit_audio`. These checks hold the slice's Done-when: the ceiling build has at least 4,500
SKUs under the department; each type's styles have unique ids, titles, SKUs and twin keys; the
rows and their drawings are the same on every call; and a golden slice pins each type's first
derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import audio_rows, kit, scale, type_registry

TYPES = ("Headphones", "Portable Speaker", "Soundbar")
KEYS = {"Headphones": "headphones", "Portable Speaker": "portable_speaker", "Soundbar": "soundbar"}
#: The slice's floor at the ceiling build (the gate comment of gen#956).
FLOOR = 4_500


@pytest.fixture(scope="module")
def electronics() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == audio_rows.ROOT]


def test_the_ceiling_build_holds_the_slice_floor_of_electronics_skus(electronics) -> None:
    skus = sum(r["sku_count"] for r in electronics)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(electronics) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in electronics if r["product_id"] in derived}
    assert kinds >= set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_sits_under_audio(electronics, ptype) -> None:
    mine = [r for r in electronics if r["product_type"] == ptype]
    assert mine
    assert {tuple(r["category_path"][:2]) for r in mine} == {(audio_rows.ROOT, "Audio")}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(electronics, ptype) -> None:
    mine = [r for r in electronics if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


@pytest.mark.parametrize(
    ("shape", "param", "one", "other"),
    [
        ("headphones", "fit", "over-ear", "on-ear"),
        ("headphones", "connection", "wireless", "wired"),
        ("portable_speaker", "speaker_size", "mini", "large"),
        ("soundbar", "channels", "2.0", "5.1"),
    ],
)
def test_a_param_changes_the_drawing(shape, param, one, other) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    assert kit.render(shape, fill, params={param: one}) != kit.render(
        shape, fill, params={param: other}
    )


def _golden(electronics: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in electronics
                   if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {  # fmt: skip
    "Headphones": [
        ("BRD-00158C009A1C", "Woldscliffe Wired On-Ear Studio Headphones", 2, 130.0),
        ("BRD-00584B99872D", "Rudborough Bass Boost USB-C Headphones", 2, 90.0),
        ("BRD-019BC6280FF4", "Shelgarth USB-C Over-Ear Hi-Res Headphones", 6, 60.0),
    ],
    "Portable Speaker": [
        ("BRD-007B2C3AFCCB", "Wigwick Waterproof Bluetooth Speaker with Built-In Mic", 8, 59.0),
        ("BRD-00E2C61EB6D9", "Hulington Mini Splash-Proof Bluetooth Speaker", 12, 26.0),
        ("BRD-03384A7AF87A",
         "Rosfield Compact Splash-Proof Bluetooth Speaker with Built-In Mic", 12, 56.0),
    ],
    "Soundbar": [
        ("BRD-00E223234E14", "Glenwick 5.1 Channel Bluetooth Soundbar", 6, 375.0),
        ("BRD-0152E9BC8020", "Clevethorpe Compact 3.1 Channel Optical Soundbar", 6, 410.0),
        ("BRD-01EF816FCCD6", "Yeldhill Compact 2.0 Channel Bluetooth Soundbar", 4, 250.0),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(electronics, ptype) -> None:
    assert _golden(electronics, ptype) == GOLDEN[ptype]
