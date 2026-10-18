"""A product of two colors carries ONE color value, written in words (gen#514).

``Blue and White``, never ``Blue / White`` and never a list of both colors (a list would put
a mostly blue product into a White filter). Held at the splitter, at each document layer
(nested product and variant entries, flat per-SKU) and on the ceiling build.
"""

from __future__ import annotations

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

#: Written out here on purpose: the test does not read the generator's own word list.
TWO_COLOR = re.compile(r"^[A-Z][a-z]+( [A-Z][a-z]+)? and [A-Z][a-z]+( [A-Z][a-z]+)?$")
#: The three values the live catalogue held with a slash, and what the maintainer ruled.
RULED = {"Blue and White", "Blue and Yellow", "Navy and White"}


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    return scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)


@pytest.fixture(scope="module")
def nested(built: scale.Scaled) -> list[dict[str, Any]]:
    return scale.documents(built)


def _colors(documents: list[dict[str, Any]]) -> set[str]:
    values: set[str] = set()
    for doc in documents:
        for entries in (doc["attributes"], *(v["attributes"] for v in doc["variants"])):
            values |= {e["value"] for e in entries if e["key"] == "color"}
    return values


def test_the_splitter_writes_a_wash_with_a_second_color_in_words() -> None:
    assert colorwords.split("Mid Wash and Yellow") == ("Blue and Yellow", "Mid Wash")


def test_no_color_value_holds_a_slash_or_an_ampersand(nested: list[dict[str, Any]]) -> None:
    bad = {v for v in _colors(nested) if "/" in v or "&" in v}
    assert sorted(bad) == []


def test_no_flat_color_value_holds_a_slash_or_an_ampersand(nested: list[dict[str, Any]]) -> None:
    bad = {
        a["value"]
        for row in scale.flat(nested)
        for a in row["attributes"]
        if a["key"] == "color" and ("/" in a["value"] or "&" in a["value"])
    }
    assert sorted(bad) == []


def test_a_two_color_value_reads_a_and_b(nested: list[dict[str, Any]]) -> None:
    two = {v for v in _colors(nested) | _colors(export.documents()) if " and " in v}
    assert two >= RULED
    assert sorted(v for v in two if not TWO_COLOR.match(v)) == []


def test_the_exported_retail_build_holds_the_ruled_values() -> None:
    values = _colors(export.documents())
    assert values >= RULED
    assert sorted(v for v in values if "/" in v) == []
