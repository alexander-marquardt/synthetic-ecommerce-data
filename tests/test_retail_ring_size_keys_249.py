"""A ring's size keys are its own, not the garment and footwear ``size_uk``/``size_us`` (gen#249).

Rings were sold under ``size_uk`` as a letter (J, L, N, P, R) and ``size_us`` as a number, the
two keys clothing and footwear hold as numbers: one key then carried two kinds of value, which
the deployment-wide naming rule forbids (a key is shared only when its values are the same
kind: colour yes, thread size against garment size no). A UK ring letter and a US ring number
are a third and a fourth kind, so a ring states ``ring_size_uk`` and ``ring_size_us``.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import accessory_rows  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402
import variants  # noqa: E402

RING_ROWS = [r for r in accessory_rows.ROWS if r.product_type == "Ring"]
GARMENT_KEYS = ("size_uk", "size_eu", "size_us")
RING_KEYS = ("ring_size_uk", "ring_size_us")


def _entries(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return [*doc["attributes"], *(e for v in doc["variants"] for e in v["attributes"])]


@cache
def _docs() -> tuple[dict[str, Any], ...]:
    return tuple(export.standard_document(rec) for rec in scale.templates())


def test_there_are_ring_styles_to_check() -> None:
    assert len(RING_ROWS) >= 5


@pytest.mark.parametrize("row", RING_ROWS, ids=lambda r: r.code)
def test_a_ring_sku_states_ring_size_keys_and_no_garment_size_key(
    row: accessory_rows.ARow,
) -> None:
    for sku in row.skus():
        assert set(RING_KEYS) <= set(sku), sku
        assert not set(GARMENT_KEYS) & set(sku), sku


@pytest.mark.parametrize("row", RING_ROWS, ids=lambda r: r.code)
def test_a_ring_export_carries_the_ring_keys_and_no_garment_size_key(
    row: accessory_rows.ARow,
) -> None:
    keys = {e["key"] for e in _entries(export.standard_document(row.doc()))}
    assert set(RING_KEYS) <= keys
    assert not set(GARMENT_KEYS) & keys


def test_the_ring_keys_are_named_for_a_ring() -> None:
    names = {e["key"]: e["name"] for d in _docs() for e in _entries(d) if e["key"] in RING_KEYS}
    assert names == {"ring_size_uk": "Ring size (UK)", "ring_size_us": "Ring size (US)"}


def test_the_garment_and_footwear_size_keys_never_hold_a_ring_letter() -> None:
    """The kind check: a lone letter under a garment size key is a ring size on the wrong key.

    Only the single letters of the ring scale are pinned: a bra's ``30B`` and a bed's
    ``King`` sit on the same garment keys and are a separate question (see the PR body)."""
    letters = {
        (d["product_id"], e["key"], e["value"])
        for d in _docs()
        for e in _entries(d)
        if e["key"] in GARMENT_KEYS and len(e["value"]) == 1 and e["value"].isalpha()
    }
    assert letters == set()


def test_the_ring_keys_are_held_by_rings_alone() -> None:
    other = {
        d["product_id"]
        for d in _docs()
        if d["product_type"] != "Ring" and {e["key"] for e in _entries(d)} & set(RING_KEYS)
    }
    assert other == set()


def test_a_ring_s_size_options_are_listed_under_the_ring_keys() -> None:
    assert set(RING_KEYS) <= set(variants.SIZE_KEYS)
    for row in RING_ROWS:
        options = row.doc()["size_options"]
        assert set(RING_KEYS) <= set(options), row.code
        assert not set(GARMENT_KEYS) & set(options), row.code
