"""Seasonal collections, shopper color words and invented characters stay in the build (gen#195).

A shopper types "champagne dress", "duck egg", "rose quartz", "christmas", "halloween" or a
character's name before a category. The color fold had erased those words into plainer ones and
``collections`` was empty on every record. The expected values are written out here, not read
from :mod:`seasonal_rows`, so dropping one from the rows (or folding it again) fails this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402

#: Plain color values, one each, a two-word color included (like Rose Gold).
COLORS = frozenset({
    "Champagne", "Duck Egg", "Navy Blue", "Rust", "Caramel", "Oatmeal", "Stone", "Aubergine",
    "Berry", "Raspberry", "Mint", "Olive", "Amber", "Tortoiseshell", "Rose Quartz",
})  # fmt: skip
COLLECTIONS = frozenset({"Christmas", "Halloween", "Advent", "Summer", "Autumn", "Wedding",
                         "Going Out"})  # fmt: skip
#: Product types that carry a character range as their ``line``.
CHARACTER_TYPES = frozenset({"Cake", "Sweets", "Pyjamas", "Soft Toy"})
#: Never a licensed character: the ranges are invented.
RANGES = frozenset({"Moonmoth Rangers", "Rumblesaur Ridge", "Bramblewood Owls",
                    "Driftwhistle Bay"})  # fmt: skip


def _records() -> list[dict]:
    return scale.templates()


def _facet_colors(records) -> set[str]:
    out: set[str] = set()
    for r in records:
        doc = export.standard_document(r)
        out.update(a["value"] for a in doc["attributes"] if a["key"] == "color")
        out.update(
            a["value"] for v in doc["variants"] for a in v["attributes"] if a["key"] == "color"
        )
    return out


def test_every_shopper_color_word_is_a_plain_color_value_in_the_build():
    records = _records()
    swatches = {c["color"] for r in records for c in r.get("color_options", ())}
    skus = {s["color"] for r in records for s in r["skus"] if "color" in s}
    for where, got in (("swatch", swatches), ("sku", skus), ("facet", _facet_colors(records))):
        assert got >= COLORS, (where, sorted(COLORS - got))
    assert all(colorwords.is_plain(v) for v in COLORS), sorted(
        v for v in COLORS if not colorwords.is_plain(v)
    )


def test_a_two_word_color_is_one_value_and_no_shade_name_field_exists():
    records = _records()
    values = {c["color"] for r in records for c in r.get("color_options", ())}
    assert {"Duck Egg", "Navy Blue", "Rose Quartz"} <= values
    assert not {"Duck", "Egg", "Quartz"} & values
    assert all("shade_name" not in r for r in records)


def test_every_collection_is_on_some_record_and_none_is_a_made_up_value():
    got = {c for r in _records() for c in r["collections"]}
    assert got == COLLECTIONS, sorted(got ^ COLLECTIONS)


def test_a_collection_is_exported_as_an_attribute():
    docs = [export.standard_document(r) for r in _records() if r["collections"]]
    assert docs
    seen = {a["value"] for d in docs for a in d["attributes"] if a["key"] == "collection"}
    assert seen == COLLECTIONS


def test_each_character_type_has_an_invented_line_and_every_range_has_a_cake_or_sweet():
    rows = [r for r in _records() if r["product_type"] in CHARACTER_TYPES]
    lines = {}
    for r in rows:
        for a in r["attributes"]:
            if a["key"] == "line" and a["value"] in RANGES:
                lines.setdefault(r["product_type"], set()).add(a["value"])
    assert set(lines) == CHARACTER_TYPES, sorted(set(lines) ^ CHARACTER_TYPES)
    assert lines["Pyjamas"] == RANGES and lines["Soft Toy"] == RANGES
    assert lines["Cake"] | lines["Sweets"] == RANGES


def test_a_half_word_alone_is_not_a_plain_color_but_its_two_word_color_is():
    assert not any(colorwords.is_plain(w) for w in ("Duck", "Egg", "Quartz"))
    assert colorwords.is_plain("Duck Egg") and colorwords.is_plain("Rose Quartz")
