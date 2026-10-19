"""Mutant rows that plant a defect in the committed ``golden-catalog/``, anchored by rule (#50).

A row quotes a committed line verbatim, so a regeneration used to break all five at once and each
was re-anchored by hand. The anchor is now the first product line, in catalog order, with more than
one variant; ``scripts/measure_pins.py`` finds it, checks that every text below occurs exactly once
in its file, and writes it to ``tests/data/golden_pins.json``. This file reads the fixture and
builds each text from it, so the next regeneration edits nothing here.
"""

from __future__ import annotations

import golden_pins
from mutation_row import Row

PREFIX = "golden anchors"

_TEST = "tests/test_catalog_golden.py::"


def _unique(name: str, text: str) -> str:
    """``text``, after checking it occurs once in the committed ``name``."""
    found = (golden_pins.GOLDEN / name).read_text("utf-8").count(text)
    if found != 1:
        raise LookupError(
            f"{text[:80]!r} occurs {found} times in {name}, not once: run {golden_pins.REGENERATE}"
        )
    return text


def rows() -> list[Row]:
    anchor = golden_pins.load()["anchor"]
    image_url, detail_url, sku_at, count_at = (
        _unique(name, text) for name, text in golden_pins.anchor_needles(anchor)
    )
    product_id = anchor["product_id"]
    missing_line = product_id.rsplit("-", 1)[0] + "-9999"
    url_key = image_url.split('"image_url": ', 1)[0]
    blank_url = url_key + '"image_url": ""'
    no_detail = detail_url.split(', "image_detail_url"', 1)[0]
    image_property = "every document carries a NON-EMPTY image url at both profiles"
    return [
        Row(
            "blank one card image url in the committed catalog",
            "flat.jsonl",
            image_url,
            blank_url,
            _TEST + "test_every_flat_document_carries_an_image_url",
            image_property,
            "golden-catalog",
            "A",
        ),
        Row(
            "drop the detail image url from one committed nested variant",
            "nested.jsonl",
            detail_url,
            no_detail,
            _TEST + "test_every_nested_line_and_variant_carries_an_image_url",
            image_property,
            "golden-catalog",
            "B",
        ),
        Row(
            "duplicate a sku in the committed flat catalog",
            "flat.jsonl",
            sku_at,
            sku_at.replace(anchor["first_sku"], anchor["second_sku"]),
            _TEST + "test_flat_holds_one_document_per_sku",
            "flat.jsonl is one document per distinct sku",
            "golden-catalog",
        ),
        Row(
            "point one committed document at a product line that does not exist",
            "flat.jsonl",
            sku_at,
            sku_at.replace(product_id, missing_line),
            _TEST + "test_flat_covers_exactly_the_product_lines",
            "the catalog spans exactly the committed number of products",
            "golden-catalog",
        ),
        Row(
            "publish a variant_count that disagrees with its own variants array",
            "nested.jsonl",
            count_at,
            count_at.replace(
                f'"variant_count": {anchor["variant_count"]}',
                f'"variant_count": {anchor["variant_count"] + 1}',
            ),
            _TEST + "test_nested_lines_account_for_every_sku",
            "the nested lines account for every sku",
            "golden-catalog",
        ),
    ]
