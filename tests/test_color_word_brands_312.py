"""Color-word brands and color-named lines beyond clothing (gen#312, decoy class 7).

A brand or line name holds a color word the product is not: a "Green Harrow" tin of yellow
sweetcorn, a "Black Larch" orange drill. The expected values are written out here, not read
from the rows module, so dropping a brand, a department or a house style from the rows fails
this file. The counts are taken over :func:`scale.templates`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import build_preview  # noqa: E402
import color_word_brand_rows as cw_rows  # noqa: E402
import house_styles  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core import standard  # noqa: E402

BRANDS = {
    "Green Harrow": "green", "Yellow Skerry": "yellow", "Black Larch": "black",
    "Silver Sedge": "silver", "Blue Heddon": "blue", "Red Linnet": "red",
}  # fmt: skip
#: Color-named lines of an uncolored brand: the line attribute holds the name.
LINES = {"Red Cask": "red", "Black Cask": "black", "Blue Cask": "blue",
         "Black Cherry": "black", "Belgian White": "white"}  # fmt: skip
COLORS = ("red", "blue", "green", "yellow", "black", "white", "silver", "grey", "gold")
#: Well-known brands and trade names no invented name may equal or contain.
WELL_KNOWN = (
    "green giant", "green valley", "yellow tail", "black & decker", "black and decker",
    "black diamond", "silver spoon", "blue diamond", "red wing", "red bull", "red robin",
    "johnnie walker", "red label", "black label", "blue label", "pink lady", "blue moon",
    "black cat", "red tractor", "yellow pages", "green shield", "silver cross", "blue band",
)  # fmt: skip
DEPARTMENTS = ("food", "drink", "home", "garden", "tools")


@pytest.fixture(scope="module")
def decoys() -> list[dict]:
    """The templates whose brand is a color-word brand or whose line is a color-named line."""
    out = []
    for r in scale.templates():
        line = next((a["value"] for a in r["attributes"] if a["key"] == "line"), None)
        if r["brand"] in BRANDS or line in LINES:
            out.append(r)
    return out


def _bucket(r: dict) -> str:
    path = tuple(r["category_path"])
    if path[0] == "Food & Drink":
        return "drink" if path[1] in ("Beer, Wine & Spirits", "Soft Drinks") else "food"
    if path[:2] == ("Home", "DIY & Tools"):
        return "tools"
    return "garden" if path[0] == "Garden" else "home"


def _name(r: dict) -> str:
    line = next((a["value"] for a in r["attributes"] if a["key"] == "line"), None)
    return r["brand"] if r["brand"] in BRANDS else line


def _word(r: dict) -> str:
    return (BRANDS.get(r["brand"]) or LINES[_name(r)]).lower()


def _true_colors(r: dict) -> set[str]:
    """What the document states about the product's color: SKU colors and a wine style."""
    out = {s["color"].lower() for s in r["skus"] if s.get("color")}
    out |= {a["value"].lower() for a in r["attributes"] if a["key"] == "wine_style"}
    return out


def test_the_rows_are_all_in_the_templates(decoys):
    assert len(decoys) == len(cw_rows.ROWS) >= 20


@pytest.mark.parametrize("dept", DEPARTMENTS)
def test_each_department_has_at_least_three_decoys(decoys, dept):
    assert len([r for r in decoys if _bucket(r) == dept]) >= 3


def test_every_brand_sells_in_two_departments_at_least(decoys):
    for brand in BRANDS:
        assert len({_bucket(r) for r in decoys if r["brand"] == brand}) >= 2, brand


def test_every_color_line_is_present(decoys):
    names = {_name(r) for r in decoys}
    assert set(LINES) <= names


def test_the_color_word_sits_in_a_short_title_and_in_the_brand_or_line(decoys):
    for r in decoys:
        title = r["title"]
        assert len(title.split()) <= 5, title
        assert _name(r) in title, title
        assert _word(r) in title.lower() or _name(r) in title


def test_no_attribute_states_the_color_word(decoys):
    """The color field, the wine style and the packaging color stay true: none is the word."""
    for r in decoys:
        assert _word(r) not in _true_colors(r), r["title"]
    # Every SKU-colored type (home, garden, tools) states a color that is not the word.
    for r in decoys:
        if _bucket(r) in ("home", "tools"):
            assert _true_colors(r), r["title"]


def test_the_rows_state_their_true_color_and_the_word(decoys):
    by_id = {f"BRD-{row.code}": row for row in cw_rows.ROWS}
    for r in decoys:
        row = by_id[r["product_id"]]
        assert row.color_word.lower() == _word(r)
        assert row.true_color.lower() != row.color_word.lower()
        assert row.fix == "generic" or row.fix.startswith("special: ")
        for c in _true_colors(r):
            assert c != row.color_word.lower()


def test_every_name_is_invented(decoys):
    names = {_name(r).lower() for r in decoys}
    for n in names:
        assert not any(w in n or n in w for w in WELL_KNOWN), n
    assert set(cw_rows.BRANDS) == set(BRANDS)


def test_a_spirit_tier_is_the_same_amber(decoys):
    tiers = [r for r in decoys if _name(r).endswith(" Cask")]
    assert len(tiers) == 3
    assert {r["product_type"] for r in tiers} == {"Whisky"}
    assert {r["drawing"]["base"] for r in tiers} == {tiers[0]["drawing"]["base"]}


def test_every_brand_has_a_dedicated_lockup_house_style():
    for brand in BRANDS:
        style = house_styles.HOUSE_STYLES[brand]
        assert style.layout != "mark_only", brand
        assert style.mark in house_styles.MARKS
        assert brand in cw_rows.color_word_brand_styles.STYLES


def _lockup_text(rec: dict) -> str:
    svg = build_preview.drawing_svg(rec)
    overlay = svg.split('<g class="brand">', 1)[1]
    return "".join(re.findall(r"<text[^>]*>([^<]*)</text>", overlay))


def test_a_drawing_lockup_text_equals_the_brand_field(decoys):
    for r in decoys:
        if r["brand"] not in BRANDS:
            continue
        style = house_styles.HOUSE_STYLES[r["brand"]]
        assert _lockup_text(r) == house_styles._cased(style, r["brand"]), r["title"]
        assert style.case in ("title", "smallcaps")


def test_the_docs_table_is_the_generated_one():
    text = (ROOT / "docs" / "retail-color-word-brands.md").read_text()
    inner = text.split(cw_rows.DOCS_BEGIN, 1)[1].split(cw_rows.DOCS_END, 1)[0]
    assert inner.strip() == cw_rows.table()
    for brand in BRANDS:
        assert brand in text.split("## Invented brands", 1)[1]


def test_the_rows_stay_out_of_the_derived_styles():
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not (cw_rows.product_ids() & kept)


def test_the_standard_reads_a_brand_as_a_name_not_a_claim(decoys):
    """A green cushion from "Red Linnet" contradicts nothing: the brand is a name."""
    templates = scale.templates()
    docs = scale.documents(scale.build(sum(len(r["skus"]) for r in templates)))
    pools = standard.value_pools(docs)
    mine = [d for d in docs if d["brand"] in BRANDS]
    assert len(mine) >= 18
    for d in mine:
        assert standard.text_contradictions(d, pools) == [], d["title"]


def test_a_built_decoy_offers_exactly_its_one_true_color(decoys):
    """The completer adds main colors to a type that lacks them; a decoy whose color field is
    its one true color takes none (Silver Sedge towel: Navy, not seven colors)."""
    templates = scale.templates()
    docs = scale.documents(scale.build(sum(len(r["skus"]) for r in templates)))
    by_title = {d["title"]: d for d in docs}
    true = {f"BRD-{row.code}": row.true_color for row in cw_rows.ROWS}
    checked = 0
    for r in decoys:
        if not any(s.get("color") for s in r["skus"]):
            continue  # a colorless product (food, drink, bulbs) has no color to offer
        want = {true[r["product_id"]]}
        doc = by_title[r["title"]]
        got = {a["value"] for v in doc["variants"] for a in v["attributes"] if a["key"] == "color"}
        assert got == want, r["title"]
        checked += 1
    assert checked >= 5
