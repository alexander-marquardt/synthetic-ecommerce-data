"""Mutation rows for the industrial attribute clean-up (#497), kept out of ``mutation_check.py``.

``tests/test_attribute_cleanup_497.py`` reads the committed ``golden-catalog/nested.jsonl``, so a
row plants the defect IN that file (``root="golden-catalog"``): a removed key back on a product, a
merged-away key, one key under two names, a restated type, a repeated standard, a length in an
angle, 0.875 for 7/8, "Countersunk Head" for Flat. Each must turn the named guard red. The source
side of the same change is held by ``tests/test_catalog_golden.py``, which holds the golden equal to
a fresh build.

The golden file is one long line per product, so a planted text must match exactly once: each row
grows its text leftwards from the entry it changes until it does (``_unique``).
"""

from __future__ import annotations

import json
from pathlib import Path

_GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog" / "nested.jsonl"
_FILE = "nested.jsonl"
_TEST = "tests/test_attribute_cleanup_497.py"

_TEXT: str | None = None


def _text() -> str:
    global _TEXT
    if _TEXT is None:
        _TEXT = _GOLDEN.read_text("utf-8")
    return _TEXT


def _entry(key: str, value: str | None = None) -> str:
    """The first entry (product or variant) of ``key`` (and ``value``), as golden text."""
    for line in _text().splitlines():
        product = json.loads(line)
        pools = [product["attributes"], *(variant["attributes"] for variant in product["variants"])]
        for pool in pools:
            for entry in pool:
                if entry["key"] == key and (value is None or entry["value"] == value):
                    return json.dumps(entry, ensure_ascii=False)
    raise LookupError(f"no {key!r} entry in the golden")


def _unique(old: str, new: str) -> tuple[str, str]:
    """``old`` and ``new`` with the same left context added, so ``old`` occurs once."""
    text = _text()
    at = text.index(old)
    reach = 0
    while text.count(text[at - reach : at + len(old)]) != 1:
        reach += 20
        if reach > at:
            raise LookupError(f"cannot make {old[:60]!r} unique")
    context = text[at - reach : at]
    return context + old, context + new


def _row(
    name: str, old: str, new: str, prop: str, test: str
) -> tuple[str, str, str, str, str, str, str]:
    old, new = _unique(old, new)
    return (name, _FILE, old, new, f"{_TEST} -k {test}", prop, "golden-catalog")


def _rows() -> list[tuple[str, str, str, str, str, str, str]]:
    grade = _entry("wheel_grade", "Coarse")
    standard = _entry("standards")
    arbor = _entry("arbor_hole", "7/8")
    flat = _entry("head_type", "Flat")
    helix = _entry("helix_angle")
    stock = _entry("stock_fit")
    entry = json.loads(grade)

    def swap(**changes: str) -> str:
        return json.dumps({**entry, **changes}, ensure_ascii=False)

    helix_bad = json.dumps({**json.loads(helix), "value": '1-1/4"'}, ensure_ascii=False)
    standard_twice = standard + ", " + standard
    return [
        _row(
            "the Item attribute is back on a product",
            grade,
            swap(key="item", name="Item", value="Flap Disc"),
            "no product carries an Item, End Mill Style, Tap Style, Lock Type or Insert Material",
            "no_removed_key",
        ),
        _row(
            "Dimension Type is back beside Measurement System",
            grade,
            swap(key="dimension_type", name="Dimension Type", value="Metric"),
            "a merged-away key is never published",
            "no_merged_away_key",
        ),
        _row(
            "one key is shown under two display names",
            grade,
            swap(name="Grade of Wheel"),
            "one key has one display name",
            "one_key_has_one_display_name",
        ),
        _row(
            "Wheel Grade is spelled as the bolt's Grade on one product",
            grade,
            swap(key="grade", name="Grade"),
            "a wheel's coarseness and a bolt's strength are two keys",
            "grade_and_wheel_grade",
        ),
        _row(
            "a Type value repeats the product type",
            grade,
            swap(key="type", name="Type", value="Set Screw"),
            "a Type value never restates the product type",
            "a_type_value_never_restates",
        ),
        _row(
            "a product publishes the same standard twice",
            standard,
            standard_twice,
            "a standard is published once per product",
            "a_standard_is_published_once",
        ),
        _row(
            "a helix angle holds a length",
            helix,
            helix_bad,
            "an angle holds no length",
            "an_angle_holds_no_length",
        ),
        _row(
            "an arbor hole is 0.875 again",
            arbor,
            json.dumps({**json.loads(arbor), "value": "0.875"}, ensure_ascii=False),
            "an arbor hole has one spelling",
            "an_arbor_hole",
        ),
        _row(
            "a flat head is Countersunk Head again",
            flat,
            json.dumps({**json.loads(flat), "value": "Countersunk Head"}, ensure_ascii=False),
            "one spelling for a flat head",
            "a_head_type_has_one_spelling",
        ),
        _row(
            "key stock's tolerance class is Fit again",
            stock,
            json.dumps({**json.loads(stock), "key": "fit", "name": "Fit"}, ensure_ascii=False),
            "key stock's fit is Stock Fit",
            "key_stock_tolerance_class",
        ),
    ]


ROWS = _rows()
