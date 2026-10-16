"""One key for a scent (gen#273): `scent`, never `fragrance`.

The grocery depth families and the kitchen cleaner key a scent as `scent`; the hand-written
cleaning, gift and decoy rows keyed it `fragrance`, so one policy on the pair
(scent, product type) missed them. A scent is `scent` on a style (and on a SKU that varies by
it), with the display name "Scent". `fragrance_family` (a perfume's family: floral, citrus) is
another concept and keeps its key.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def test_no_style_or_sku_keys_a_scent_as_fragrance(templates):
    styles = [
        r["product_id"] for r in templates if "fragrance" in {a["key"] for a in r["attributes"]}
    ]
    skus = [r["product_id"] for r in templates if any("fragrance" in s for s in r["skus"])]
    assert (styles, skus) == ([], [])


def test_every_scent_attribute_is_named_scent(templates):
    names = {a["name"] for r in templates for a in r["attributes"] if a["key"] == "scent"}
    assert names == {"Scent"}


@pytest.mark.parametrize(
    ("product_id", "value"),
    [
        ("BRD-BTHSPR", "Eucalyptus"),
        ("BRD-CNDBEE", "Amber Woods"),
        ("PLT-LEMGEL", "Lemon & Bergamot"),
    ],
)
def test_a_hand_written_row_states_its_scent_under_scent(templates, product_id, value):
    rec = next(r for r in templates if r["product_id"] == product_id)
    assert {a["value"] for a in rec["attributes"] if a["key"] == "scent"} == {value}


def test_a_perfume_keeps_its_fragrance_family(templates):
    keys = {
        a["key"] for r in templates if r["product_type"] == "Perfume" for a in r["attributes"]
    }
    assert "fragrance_family" in keys
