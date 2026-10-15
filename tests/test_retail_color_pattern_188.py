"""A pattern is a ``pattern``, never part of a ``color`` (gen#188).

The authored shades keep their words ("Navy Stripe", "Grey Check", "Light Wash"): they are
swatch names, titles and image ids. The catalogue a shopper filters splits them. "Navy
Stripe" is color Navy and pattern Stripe, so a "navy" filter finds it and a "stripe" filter
finds it; a denim wash is the pattern of a Blue pair. Held at the splitter, at each document
layer (nested product and variant entries, flat per-SKU), and on the ceiling build.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402 -- the prototype's own directory is its import root
import export  # noqa: E402
import scale  # noqa: E402

#: Written out here on purpose: the test does not read the splitter's own word list.
PATTERN_WORD = re.compile(
    r"stripe|check|gingham|polka|\bdot\b|\bspot\b|print|leopard|marl|lace|wash|rinse|floral",
    re.IGNORECASE,
)


@pytest.mark.parametrize(
    ("authored", "color", "pattern"),
    [
        ("Navy Stripe", "Navy", "Stripe"),
        ("Grey Check", "Grey", "Check"),
        ("Black Polka Dot", "Black", "Polka Dot"),
        ("Red Gingham", "Red", "Gingham"),
        ("Brown Leopard", "Brown", "Leopard"),
        ("Pink Spot", "Pink", "Spot"),
        ("Cream Print", "Cream", "Print"),
        ("Grey Marl", "Grey", "Marl"),
        ("Ivory Lace", "Ivory", "Lace"),
        ("Light Wash", "Blue", "Light Wash"),
        ("Mid Wash", "Blue", "Mid Wash"),
        ("Bleach Wash", "Blue", "Bleach Wash"),
        ("Grey Wash", "Grey", "Grey Wash"),
        ("Rinse", "Blue", "Rinse"),
        ("Washed Black", "Black", "Washed"),
        ("Mid Wash / Yellow", "Blue / Yellow", "Mid Wash"),
        ("Navy", "Navy", None),
        ("Dark Red", "Dark Red", None),
        ("2N", "2N", None),
    ],
)
def test_split_gives_the_plain_color_and_the_pattern(
    authored: str, color: str, pattern: str | None
) -> None:
    assert colorwords.split(authored) == (color, pattern)


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    """Every template, then a few thousand SKUs of derived styles."""
    return scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)


@pytest.fixture(scope="module")
def nested(built: scale.Scaled) -> list[dict[str, Any]]:
    return scale.documents(built)


def _values(entries: list[dict[str, Any]], key: str) -> list[str]:
    return [e["value"] for e in entries if e["key"] == key]


def test_no_color_value_holds_a_pattern_word(nested: list[dict[str, Any]]) -> None:
    bad = set()
    for doc in nested:
        for entries in (doc["attributes"], *(v["attributes"] for v in doc["variants"])):
            bad |= {v for v in _values(entries, "color") if PATTERN_WORD.search(v)}
    assert sorted(bad) == []


def test_no_flat_color_value_holds_a_pattern_word(nested: list[dict[str, Any]]) -> None:
    bad = {
        a["value"]
        for row in scale.flat(nested)
        for a in row["attributes"]
        if a["key"] == "color" and PATTERN_WORD.search(a["value"])
    }
    assert sorted(bad) == []


def test_a_navy_stripe_sku_is_navy_with_pattern_stripe(
    built: scale.Scaled, nested: list[dict[str, Any]]
) -> None:
    skus = {s["sku"] for r in built.records for s in r["skus"] if s.get("color") == "Navy Stripe"}
    assert skus, "the build has no Navy Stripe SKU"
    seen = 0
    for doc in nested:
        for v in doc["variants"]:
            if v["sku"] in skus:
                seen += 1
                assert _values(v["attributes"], "color") == ["Navy"]
                assert _values(v["attributes"], "pattern") == ["Stripe"]
    assert seen == len(skus)


def test_every_split_sku_carries_its_pattern(
    built: scale.Scaled, nested: list[dict[str, Any]]
) -> None:
    want = {
        s["sku"]: colorwords.split(s["color"])[1]
        for r in built.records
        for s in r["skus"]
        if "color" in s and PATTERN_WORD.search(s["color"])
    }
    assert len(want) > 1000
    got = {
        v["sku"]: _values(v["attributes"], "pattern")
        for doc in nested
        for v in doc["variants"]
        if v["sku"] in want
    }
    assert {k: v for k, v in got.items() if v != [want[k]]} == {}


def test_a_style_lists_each_split_pattern_on_the_product(
    built: scale.Scaled, nested: list[dict[str, Any]]
) -> None:
    by_id = {d["product_id"]: d for d in nested}
    checked = 0
    for r in built.records:
        patterns = {
            colorwords.split(s["color"])[1] for s in r["skus"] if "color" in s
        } - {None}
        for p in patterns:
            checked += 1
            assert p.title() in _values(by_id[r["product_id"]]["attributes"], "pattern")
    assert checked > 100


def test_a_plain_color_stays_a_main_color(nested: list[dict[str, Any]]) -> None:
    """A split color is one of the colors the main-color policies know (gen#275)."""
    words = colorwords.COLOR_WORDS | colorwords.MODIFIERS
    bad = set()
    for doc in nested:
        for v in doc["variants"]:
            for c in _values(v["attributes"], "color"):
                if not colorwords.is_plain(c) or not any(w in words for w in c.split()):
                    bad.add(c)
    assert sorted(bad) == []


def test_the_authored_export_splits_too() -> None:
    blob = json.dumps(export.documents(), ensure_ascii=False)
    color = r'"key": "color", "name": "Color", "value": "[^"]*'
    assert not re.search(color + "(Stripe|Check|Wash)", blob)
