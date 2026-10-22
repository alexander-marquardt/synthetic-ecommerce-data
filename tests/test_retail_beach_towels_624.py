"""The real beach towels vary in material, weave and feature, with longer titles (gen#624).

One "Cotton Velour Beach Towel" repeated 13 times gave the shopper no choice and let a short
decoy title outrank every real towel. The real towels are authored rows
(``type_specs/beach_towel.py``): each title has 7 to 12 words and names its material, weave and
feature, and each named component is an attribute a filter can use.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import breadth_rows  # noqa: E402
import scale  # noqa: E402
from type_specs import beach_towel as beach_towel_rows  # noqa: E402

LEAF = "Beach Towels"


def _rows() -> tuple:
    rows = beach_towel_rows.ROWS
    assert len(rows) >= 10, f"only {len(rows)} real beach towels"
    return rows


def _words(title: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", title)


def _attr(row, key: str) -> str:
    return next((a[2] for a in row.attrs if a[0] == key), "")


def test_every_real_title_has_seven_to_twelve_words() -> None:
    off = {r.title: len(_words(r.title)) for r in _rows() if not 7 <= len(_words(r.title)) <= 12}
    assert off == {}


def test_four_materials_and_four_weave_or_feature_words_are_in_use() -> None:
    rows = _rows()
    assert len({_attr(r, "material") for r in rows}) >= 4
    assert len({_attr(r, "weave") for r in rows}) >= 4
    assert len({_attr(r, "feature") for r in rows}) >= 4


def test_every_named_component_is_an_attribute_and_every_attribute_is_named() -> None:
    off = []
    for r in _rows():
        title = " ".join(_words(r.title)).lower()
        for key in ("material", "weave", "feature"):
            value = _attr(r, key)
            if not value or " ".join(_words(value)).lower() not in title:
                off.append((r.code, key, value))
        size = _attr(r, "dimensions")
        if not re.fullmatch(r"\d+ x \d+ cm", size):
            off.append((r.code, "dimensions", size))
    assert off == []


def test_some_titles_name_the_color_or_print_and_others_leave_it_out() -> None:
    rows = _rows()
    named = [r for r in rows if len(r.colors) == 1 and r.colors[0][0].lower() in r.title.lower()]
    assert 2 <= len(named) < len(rows) - 2
    assert any(len(r.colors) >= 3 for r in rows)


def test_the_single_velour_template_is_gone_from_the_breadth_rows() -> None:
    assert [r.code for r in breadth_rows.BREADTH_34 if r.path[-1] == LEAF] == []
    assert "BRD-BCHTWL" not in {d["product_id"] for d in breadth_rows.docs()}


def test_the_towels_are_templates_and_not_derived() -> None:
    ids = {f"BRD-{r.code}" for r in _rows()}
    tpls = scale.templates()
    assert {d["product_id"] for d in tpls if d["category_leaf"] == LEAF} == ids
    assert not ids & {d["product_id"] for d in scale.derivable(tpls)}


def test_every_towel_keeps_its_product_type_and_category_path() -> None:
    docs = beach_towel_rows.SPEC.docs()
    assert len(docs) == len(_rows())
    path = ["Home", "Bathroom", "Beach Towels"]
    off = [
        (d["product_id"], d["product_type"], d["category_path"])
        for d in docs
        if d["product_type"] != "Beach Towel" or d["category_path"] != path
    ]
    assert off == []
    assert {r.product_type for r in _rows()} == {"Beach Towel"}
