"""A style word in a title agrees with the garment's neckline, length, sleeves, material (gen#511).

"Red Coat Dress" (a decoy cloned from a boat-neck mini in crepe) is no real product: a coat dress
is tailored, with a collar, lapels or a V neck, at knee or midi length. ``style_table`` declares
what each style word allows; these tests hold the generated catalog to it. The pairs below are
written out here, not read from the table, so loosening the table does not loosen the test.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_apparel  # noqa: E402
import neckline_rows  # noqa: E402
import scale  # noqa: E402
import style_table  # noqa: E402


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates(baseline=False)


def _doc(
    title: str,
    *,
    ptype: str = "Dress",
    neckline: str | None = None,
    length: str | None = None,
    material: str | None = None,
    sleeve: str | None = None,
) -> dict:
    attrs = [
        {"key": k, "name": k, "value": v}
        for k, v in (("length", length), ("material", material), ("sleeve_length", sleeve))
        if v
    ]
    return {
        "product_id": "X",
        "title": title,
        "product_type": ptype,
        "neckline": neckline,
        "attributes": attrs,
    }


#: (title, neckline, length, material) a real garment of the style can carry.
REAL = [
    ("Navy Coat Dress", "v-neck", "Midi", "Wool Blend"),
    ("Navy Coat Dress", "collared", "Knee", "Ponte"),
    ("Blue Shirt Dress", "collared", "Midi", "Cotton Poplin"),
    ("Petite Wrap Midi Dress", "v-neck", "Midi", "Jersey"),
    ("Womens Slip Dress", "square", "Midi", "Satin"),
    ("Womens Maxi Dress", "round", "Maxi", "Viscose"),
    ("Womens Mini Dress", "boat", "Mini", "Crepe"),
    ("Grey Jumper Dress", "high", "Mini", "Cable Knit"),
    ("Womens T-Shirt Dress", "crew", None, "Cotton Jersey"),
]
#: The pairs the issue names as outside the table, and the rest of the dress words.
IMPOSSIBLE = [
    ("Red Coat Dress", "boat", "Mini", "Crepe", "coat"),
    ("Red Coat Dress", "v-neck", "Mini", "Wool Blend", "coat"),
    ("Red Coat Dress", "v-neck", "Midi", "Satin", "coat"),
    ("Womens Maxi Dress", "round", "Mini", "Viscose", "maxi"),
    ("Womens Midi Dress", "round", "Maxi", "Viscose", "midi"),
    ("Womens Mini Dress", "round", "Midi", "Viscose", "mini"),
    ("Blue Shirt Dress", "boat", "Midi", "Cotton Poplin", "shirt"),
    ("Blue Shirt Dress", "collared", "Midi", "Crepe", "shirt"),
    ("Petite Wrap Midi Dress", "crew", "Midi", "Jersey", "wrap"),
    ("Womens Slip Dress", "high", "Midi", "Satin", "slip"),
    ("Womens Bodycon Dress", "boat", "Mini", "Scuba", "bodycon"),
    ("Grey Jumper Dress", "high", "Mini", "Linen Blend", "jumper"),
    ("Womens T-Shirt Dress", "collared", None, "Cotton Jersey", "t-shirt"),
]


@pytest.mark.parametrize(("title", "neck", "length", "material"), REAL)
def test_a_real_garment_of_each_style_passes(title, neck, length, material):
    assert (
        style_table.violations(_doc(title, neckline=neck, length=length, material=material)) == []
    )


@pytest.mark.parametrize(("title", "neck", "length", "material", "word"), IMPOSSIBLE)
def test_an_impossible_pair_is_named(title, neck, length, material, word):
    found = style_table.violations(_doc(title, neckline=neck, length=length, material=material))
    assert any(v.startswith(f"{word}:") for v in found), (title, found)


def test_t_shirt_is_not_the_shirt_style():
    """ "T-Shirt Dress" carries a crew neck: the shirt style (a collar) must not read it."""
    assert (
        style_table.violations(_doc("Womens T-Shirt Dress", neckline="crew", material="Modal"))
        == []
    )


def test_a_top_style_word_fixes_the_neckline_and_the_sleeve():
    assert style_table.violations(_doc("Red Polo Jumper", ptype="Jumper", neckline="crew"))
    assert style_table.violations(_doc("Red Vest Top", ptype="Top", sleeve="Short"))
    assert style_table.violations(_doc("Red Camisole", ptype="Top", sleeve="Long"))
    assert not style_table.violations(_doc("Red Vest Top", ptype="Top", sleeve="Sleeveless"))
    assert not style_table.violations(_doc("Red Polo Jumper", ptype="Jumper", neckline="collared"))


def test_the_named_dress_styles_are_declared():
    declared = {s.word for s in style_table.STYLES}
    named = {"coat", "shirt", "wrap", "tea", "slip", "shift", "bodycon", "maxi", "midi", "mini"}
    assert named <= declared, named - declared


def test_no_generated_document_leaves_its_style_table(templates):
    """The guard: over the whole generated catalog, decoys included, no title style word sits
    beside a neckline, length, sleeve or material its table does not allow."""
    bad = {
        d["product_id"]: (d["title"], style_table.violations(d))
        for d in templates
        if style_table.violations(d)
    }
    assert not bad, (len(bad), list(bad.items())[:5])


def test_a_coat_dress_decoy_is_tailored_and_knee_or_midi(templates):
    """The issue's case: every "Coat Dress" of the catalog has a collar or V neck and a knee or
    midi length."""
    coats = [
        d for d in templates if "coat dress" in d["title"].lower() and d["product_type"] == "Dress"
    ]
    assert coats
    for d in coats:
        assert d["neckline"] in {"collared", "v-neck"}, (d["product_id"], d["title"], d["neckline"])
        assert style_table.length_of(d) in {None, "Knee", "Midi"}, (d["product_id"], d["title"])


@pytest.mark.parametrize(
    "title",
    [
        "Button Front Tea Dress",
        "Tiered Slip Dress",
        "Smart Wrap Dress",
        "Classic Shirt Dress",
        "Coat Dress",
    ],
)
def test_a_dress_that_states_no_neckline_draws_one_its_style_allows(title):
    """``neckline_rows.complete`` chose among six necklines by the id alone; a dress now chooses
    among those its style allows."""
    recs = [
        {
            "product_id": f"BRD-T{i:04d}",
            "title": title,
            "description": "",
            "product_type": "Dress",
            "drawing": {"shape": "dress"},
            "attributes": [],
        }
        for i in range(200)
    ]
    for done in neckline_rows.complete(recs):
        assert style_table.violations(done) == [], (done["title"], done["neckline"])


def test_a_title_length_word_is_the_length_attribute(templates):
    """ "Midi Dress" is length Midi: a facet on Garment length finds it."""
    for d in templates:
        for word in ("Midi", "Maxi", "Mini"):
            if d["product_type"] == "Dress" and f"{word} Dress" in d["title"]:
                assert style_table.length_of(d) == word, (d["product_id"], d["title"])


def test_a_decoy_exemplar_is_chosen_inside_the_table(templates):
    """The compounds of class 2 are drawn only from exemplars their style allows."""
    base = [d for d in templates if d["product_id"] not in decoy_apparel.ids()]
    for row in decoy_apparel.build(base):
        assert style_table.violations(row.doc) == [], (row.pid, row.doc["title"])
