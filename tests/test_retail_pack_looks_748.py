"""Two beauty products of different lines draw different packs, and a product keeps one (gen#748).

A foundation, a face cream, a moisturiser, a bath salt and a perfume each drew one pack, so a page
of separate products read as a grouping failure. These tests read what the release draws: a SKU's
image with its colors and words taken out is the picture a line owns.
"""

from __future__ import annotations

import copy
import itertools
import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    scale,
)
from synthetic_ecommerce_data.domains.retail.line_grammar_families.beauty import (
    LEADS,
    NUMBERS,
    SUBS,
)

TEMPLATES = {
    "Foundation": "BEA-FNDFTH",
    "Face Cream": "PLT-FCDAYC",
    "Moisturiser": "BEA-TNTMST",
    "Bath Salts": "BRD-BSLLAV",
    "Perfume": "BRD-PERJAS",
}
RECORDS = {r["product_id"]: r for r in scale.templates()}
KINDS = sorted(TEMPLATES)


def _product(kind: str, line: str | None = "Renew 2", title: str = "A Pack") -> dict:
    """A copy of ``kind``'s template on ``line``, under ``title``."""
    rec = copy.deepcopy(RECORDS[TEMPLATES[kind]])
    rec["product_line"], rec["title"] = line, title
    return rec


def _outline(rec: dict, sku: dict) -> str:
    """What ``sku``'s image draws, with its colors, its words, its size and its ids gone."""
    svg = image_release.render(rec, sku, styled=False).decode().replace(rec["product_id"], "ID")
    svg = re.sub(r"<(text|title)\b.*?</\1>", "", svg, flags=re.S)
    svg = re.sub(r'<g class="pack"[^>]*>|(?<=/>)</g>', "", svg)
    return re.sub(r'#[0-9a-fA-F]{3,8}\b', "", svg)


def _spec(rec: dict) -> dict:
    return export.drawing_spec(rec, rec["skus"][0]).get("params", {})


@pytest.mark.parametrize("kind", KINDS)
def test_two_lines_of_a_kind_draw_two_outlines(kind: str) -> None:
    one, other = _product(kind, "Renew 2"), _product(kind, "Radiance Pro 7")
    assert _outline(one, one["skus"][0]) != _outline(other, other["skus"][0])


@pytest.mark.parametrize("kind", KINDS)
def test_two_titles_with_no_model_draw_two_outlines(kind: str) -> None:
    one, other = _product(kind, None, "Rose Veil"), _product(kind, None, "Night Harbor")
    assert _outline(one, one["skus"][0]) != _outline(other, other["skus"][0])


@pytest.mark.parametrize("kind", KINDS)
def test_every_model_of_the_grammar_has_a_look_of_its_own(kind: str) -> None:
    subs = ("", *(f"{s} " for s in SUBS))
    lines = [f"{a} {b}{n}" for a, b, n in itertools.product(LEADS, subs, NUMBERS)]
    assert len({str(_spec(_product(kind, line))) for line in lines}) == len(lines)
