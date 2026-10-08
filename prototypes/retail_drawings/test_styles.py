"""gen#125 ruling: one catalog document per STYLE, its color x size SKUs nested.

A style is one product with a color selector and a size selector; every
color x size combination it is sold in is a SKU inside it. The product's
``color_options`` and ``size_options`` are derived from its SKUs, never
authored, so they cannot disagree with them. One swatch per color, kept on
the color option.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import class_rows as cr  # noqa: E402
import real_classes as rc  # noqa: E402
import variants as vr  # noqa: E402

CORPUS = rc.corpus()
BY_ID = {d["product_id"]: d for d in CORPUS}


def _distinct(values) -> list:
    out: list = []
    for v in values:
        if v not in out:
            out.append(v)
    return out


def test_every_style_is_one_product_document() -> None:
    ids = Counter(d["product_id"] for d in CORPUS)
    assert [pid for pid, n in ids.items() if n > 1] == []
    assert [d["product_id"] for d in CORPUS if "variant_group" in d or "style_id" in d] == []
    for fam, styles in vr.FAMILIES.items():
        for s in styles:
            assert len(vr.style_docs(fam, s)) == 1, (fam, s.code)
    styles = {s.code for row in cr.ROWS for s in (*row.targets, *(x for x, _ in row.distractors))}
    assert len(styles) == 102
    assert [c for c in sorted(styles) if f"PLT-{c}" not in BY_ID] == []


def test_the_rulings_worked_example_is_one_product_holding_11_skus() -> None:
    """A crew-neck tee in navy (S-XL), white (S-XL) and heather grey (S-L)."""
    tee = BY_ID.get("PLT-CRWTEE")
    assert tee is not None, "the worked example is not in the corpus"
    skus = tee.get("skus", [])
    assert len(skus) == tee.get("sku_count") == 11
    assert Counter(s.get("color") for s in skus) == {"Navy": 4, "White": 4, "Heather Grey": 3}
    assert [s.get("size") for s in skus if s.get("color") == "Heather Grey"] == ["S", "M", "L"]
    assert [o["color"] for o in tee.get("color_options", [])] == ["Navy", "White", "Heather Grey"]
    assert tee.get("size_options") == {"size": ["S", "M", "L", "XL"]}
    assert len({s["sku"] for s in skus}) == 11


def test_option_lists_are_the_sku_set() -> None:
    sized = 0
    for d in CORPUS:
        skus = d.get("skus") or []
        assert skus and d.get("sku_count") == len(skus), d["product_id"]
        colors = _distinct(s["color"] for s in skus if "color" in s)
        assert [o["color"] for o in d.get("color_options", [])] == colors, d["product_id"]
        for o in d.get("color_options", []):
            assert o["hex"].startswith("#") and len(o["hex"]) == 7, (d["product_id"], o)
        sizes = {
            k: _distinct(s[k] for s in skus if k in s)
            for k in vr.SIZE_KEYS
            if any(k in s for s in skus)
        }
        assert d.get("size_options", {}) == sizes, d["product_id"]
        sized += bool(sizes)
        assert d["price"] == min(s["price"] for s in skus), d["product_id"]
    assert sized > 100
