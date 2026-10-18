"""Medical and period lingerie, and lamp shades as a leaf of their own (gen#329).

The probe of 2026-10-15 found types a general retailer's failure classes need and the catalogue
lacked. Elasticated-waist trousers (``test_retail_elasticated_waist_329``), chinos (gen#310) and
plimsolls (gen#216) are on main; this file holds the rest: a mastectomy bra, more nursing and
post-surgery bras, period pants as a type, and "Lamp Shade" titles in the Lampshades leaf. The
floors are written out here, not read from the rows, so dropping rows fails this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_apparel  # noqa: E402
import facet_leaves  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402

BRAS = ("Womens", "Lingerie", "Bras")
PERIOD = ("Womens", "Lingerie", "Period Pants")
SHADES = ("Home", "Lighting", "Lampshades")
MAIN = ("Red", "Blue", "Green", "Yellow", "Black", "White")


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _leaf(templates: list[dict], path: tuple[str, ...]) -> list[dict]:
    return [r for r in templates if tuple(r["category_path"]) == path]


def _real(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["product_id"] not in decoy_apparel.ids()]


def _attr(rec: dict, key: str) -> set[str]:
    return {a["value"] for a in rec["attributes"] if a["key"] == key}


@pytest.mark.parametrize(
    ("leaf", "floor"), [("Mastectomy Bras", 4), ("Nursing Bras", 4), ("Post-Surgery Bras", 4)]
)
def test_a_purpose_bra_leaf_holds_a_floor_of_real_products(templates, leaf, floor):
    assert len(_real(_leaf(templates, (*BRAS, leaf)))) >= floor


def test_mastectomy_bras_are_a_purpose_node_that_stays_under_bras():
    assert "Mastectomy Bras" in facet_leaves.PURPOSE_BRAS
    assert "Mastectomy Bras" in facet_leaves.BRA_LEAVES


def test_every_mastectomy_bra_says_so_in_its_title_and_has_pocketed_cups(templates):
    rows = _real(_leaf(templates, (*BRAS, "Mastectomy Bras")))
    assert rows
    for r in rows:
        assert "mastectomy" in r["title"].lower(), r["title"]
        assert "pocket" in r["description"].lower(), r["product_id"]


def test_a_post_surgery_bra_names_the_mastectomy_it_follows(templates):
    rows = _real(_leaf(templates, (*BRAS, "Post-Surgery Bras")))
    assert sum("mastectomy" in r["description"].lower() for r in rows) >= 2


def test_period_pants_are_a_registered_type_in_lingerie():
    spec = type_registry.specs().get("period_pants")
    assert spec is not None
    assert (spec.department, spec.product_type) == ("Lingerie & Nightwear", "Period Pants")
    assert spec.apparel is not None and spec.apparel.compounds


def test_period_pants_hold_a_floor_in_their_own_leaf(templates):
    rows = _real(_leaf(templates, PERIOD))
    assert len(rows) >= 8, len(rows)
    assert {r["product_type"] for r in rows} == {"Period Pants"}
    assert all("period pants" in r["title"].lower() for r in rows)
    titles = [r["title"] for r in rows]
    assert len(set(titles)) == len(titles)


def test_period_pants_state_an_absorbency_and_cover_every_level(templates):
    rows = _real(_leaf(templates, PERIOD))
    assert rows
    levels = set()
    for r in rows:
        got = _attr(r, "absorbency")
        assert len(got) == 1, r["product_id"]
        levels |= got
    assert {"Light", "Medium", "Heavy", "Overnight"} <= levels


def test_period_pants_are_sold_in_the_main_colors(templates):
    colors = {s["color"] for r in _leaf(templates, PERIOD) for s in r["skus"]}
    assert set(MAIN) <= colors, sorted(set(MAIN) - colors)


def test_period_pants_carry_text_match_decoys_of_every_class(templates):
    decoys = [r for r in _leaf(templates, PERIOD) if r["product_id"] in decoy_apparel.ids()]
    assert len(decoys) >= 21, len(decoys)


def test_the_lampshades_leaf_has_lamp_shade_titles_in_two_words(templates):
    rows = _leaf(templates, SHADES)
    assert len(rows) >= 9, len(rows)
    two = [r for r in rows if "lamp shade" in r["title"].lower()]
    assert len(two) >= 4, [r["title"] for r in rows]
    assert {r["product_type"] for r in rows} == {"Lampshade"}


def test_the_two_word_lamp_shades_are_sold_in_distinct_forms(templates):
    two = [r for r in _leaf(templates, SHADES) if "lamp shade" in r["title"].lower()]
    forms = {dict(r["drawing"]["params"]).get("form") for r in two}
    assert len(forms) >= 3, forms
    assert all(_attr(r, "fitting") for r in two)
