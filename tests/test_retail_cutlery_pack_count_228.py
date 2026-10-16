"""A cutlery style's image shows no pack count that a SKU of the style does not sell (gen#228).

Image ids are one per product and color, so every pack size of a style shares one picture. A
style sold as a Set of 4, 6 and 8 therefore cannot draw four pieces: the Set of 6 and the Set of 8
SKUs would show the wrong number. The honest drawing is one piece, with no count, unless the
style sells exactly one pack size, when the drawn count is that size.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
sys.path.insert(0, str(HERE))

import kit  # noqa: E402
import tableware_rows  # noqa: E402

CUTLERY = [d for d in tableware_rows.docs() if d["product_type"] == "Cutlery"]


def _packs(doc: dict) -> set[int]:
    """The piece counts the style's SKUs sell: ``Single`` is 1, ``Set of 6`` is 6."""
    return {
        1 if s["pack_size"] == "Single" else int(re.sub(r"\D", "", s["pack_size"]))
        for s in doc["skus"]
    }


MULTI_PACK = [d for d in CUTLERY if len(_packs(d)) > 1]


def _drawn(doc: dict) -> int:
    return int(doc["drawing"]["params"].get("count", "1"))


def test_the_cutlery_rows_sell_several_pack_sizes() -> None:
    """Guard on the guard: the styles below are multi-pack, so the check is not vacuous."""
    assert len(CUTLERY) >= 6
    assert sum(len(_packs(d)) > 1 for d in CUTLERY) >= 5


@pytest.mark.parametrize("doc", CUTLERY, ids=lambda d: d["product_id"])
def test_a_cutlery_image_draws_no_count_its_skus_do_not_sell(doc: dict) -> None:
    packs = _packs(doc)
    drawn = _drawn(doc)
    assert drawn == 1 or packs == {drawn}, (
        f"{doc['product_id']} draws {drawn} pieces but sells packs of {sorted(packs)}"
    )


@pytest.mark.parametrize("doc", MULTI_PACK, ids=lambda d: d["product_id"])
def test_a_multi_pack_cutlery_style_renders_one_piece(doc: dict) -> None:
    drawing = doc["drawing"]
    fill = kit.Fill("solid", drawing["base"], drawing["accent"], drawing["third"])
    svg = kit.render(drawing["shape"], fill, drawing["label"], params=drawing["params"])
    assert svg.count('class="piece"') == 1, doc["product_id"]
