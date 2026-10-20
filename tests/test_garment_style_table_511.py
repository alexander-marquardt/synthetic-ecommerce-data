"""A style word in a title agrees with the garment's neckline, length, sleeves, material (gen#511).

"Red Coat Dress" (a decoy cloned from a boat-neck mini in crepe) is no real product: a coat dress
is tailored, with a collar, lapels or a V neck, at knee or midi length. ``style_table`` declares
what each style word allows; these tests hold the generated catalog to it. The pairs below are
written out here, not read from the table, so loosening the table does not loosen the test.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

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
    # one attribute outside the table at a time, the other three inside it
    ("Red Coat Dress", "boat", "Midi", "Wool Blend", "coat"),
    ("Red Coat Dress", "round", "Knee", "Ponte", "coat"),
    ("Red Coat Dress", "v-neck", "Maxi", "Wool Blend", "coat"),
    ("Cream Blazer Dress", "boat", "Midi", "Crepe", "blazer"),
    ("Blue Shirt Dress", "round", "Midi", "Cotton Poplin", "shirt"),
    ("Blue Shirt Dress", "v-neck", "Midi", "Cotton Poplin", "shirt"),
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


@pytest.mark.parametrize(
    "neck", ["boat", "round", "square", "crew", "high", "halter", "cowl", "slash"]
)
def test_a_coat_dress_allows_only_a_collar_or_a_v_neck(neck):
    """The issue's headline pair: "coat + boat", and every other neckline, with a knee length in a
    coating fabric (the other attributes inside the table)."""
    doc = _doc("Red Coat Dress", neckline=neck, length="Knee", material="Wool Blend")
    assert any(v.startswith("coat:") for v in style_table.violations(doc)), neck


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


def _by_id(templates: list[dict], pid: str) -> dict:
    return next(d for d in templates if d["product_id"] == pid)


def test_the_issue_dress_is_a_tailored_coat_dress(templates):
    """PLT-DA08203 was "Red Coat Dress", a boat-neck mini in cotton poplin (the issue). It keeps its
    title, its word and its color, and is now a v-neck, Midi, Crepe dress."""
    d = _by_id(templates, "PLT-DA08203")
    assert d["title"] == "Red Coat Dress"
    assert d["neckline"] == "v-neck"
    assert style_table.length_of(d) == "Midi"
    assert style_table.material_of(d) == "Crepe"
    assert style_table.violations(d) == []


@pytest.mark.parametrize(
    ("pid", "title"),
    [
        ("PLT-DA10201", "Brown Polo Jumper"),
        ("PLT-DA19201", "Cream Polo T-Shirt"),
        ("PLT-DA22204", "Pink Polo Top"),
        ("PLT-DA08204", "Cream Blazer Dress"),
        ("PLT-DA20202", "Pink Shirt Dress"),
    ],
)
def test_a_style_decoy_keeps_its_title_and_its_neckline_is_the_styles(templates, pid, title):
    """The polo, blazer and shirt decoys are still in the catalog under their own words: the style
    table moves the exemplar or the neckline, never the word or the color."""
    d = _by_id(templates, pid)
    assert d["title"] == title
    assert d["neckline"] in {"collared", "v-neck"}, (pid, d["neckline"])
    assert style_table.violations(d) == []


def _top(title: str, ptype: str, shape: str) -> dict:
    return {
        "product_id": "BRD-TOP001",
        "title": title,
        "description": "",
        "product_type": ptype,
        "drawing": {"shape": shape, "params": {"neckline": "crew"}},
        "attributes": [],
    }


@pytest.mark.parametrize(
    ("title", "ptype", "shape"),
    [
        ("Red Polo Top", "Top", "top"),
        ("Red Polo T-Shirt", "T-Shirt", "tshirt"),
        ("Red Polo Jumper", "Jumper", "sweatshirt"),
        ("Black Knitted Polo Top", "Knitted Top", "top"),
    ],
)
def test_a_polo_top_is_collared_whatever_its_picture_draws(title, ptype, shape):
    """The picture says crew; the title says polo, and the title's neckline is the shopper truth."""
    done = neckline_rows.complete([_top(title, ptype, shape)])[0]
    assert done["neckline"] == "collared"
    plain = neckline_rows.complete([_top(title.replace("Polo ", ""), ptype, shape)])[0]
    assert plain["neckline"] == "crew"


def _exemplar(*, neckline: str, length: str, material: str) -> dict:
    ex = _doc("Boat Dress", neckline=neckline, length=length, material=material)
    return {**ex, "description": "", "drawing": {"shape": "dress"}}


def test_an_exemplar_fits_a_title_by_its_length_and_material_not_its_old_neckline():
    """A clone's neckline is drawn from its own title, so a boat-neck exemplar can carry "Coat
    Dress"; its length and material are the clone's, so a Mini or a jersey one cannot."""
    title = "Red Coat Dress"
    fit = _exemplar(neckline="boat", length="Midi", material="Crepe")
    assert decoy_apparel._fits({"desc": ""}, fit, title)
    for bad in (
        _exemplar(neckline="boat", length="Mini", material="Crepe"),
        _exemplar(neckline="boat", length="Midi", material="Jersey"),
    ):
        assert not decoy_apparel._fits({"desc": ""}, bad, title)


def test_a_crew_neck_exemplar_fits_a_polo_title():
    ex = {**_top("Crew Jumper", "Jumper", "sweatshirt"), "neckline": "crew"}
    assert decoy_apparel._fits({"desc": ""}, ex, "Brown Polo Jumper")


def test_a_clone_drops_a_neckline_its_title_forbids_and_keeps_the_rest():
    polo = {"title": "Red Polo Top", "product_type": "Top", "neckline": "crew"}
    assert "neckline" not in decoy_apparel._retitled(polo)
    assert decoy_apparel._retitled({**polo, "neckline": "collared"})["neckline"] == "collared"
    plain = {**polo, "title": "Red Top"}
    assert decoy_apparel._retitled(plain) == plain
    coat = {"title": "Red Coat Dress", "product_type": "Dress", "neckline": "boat"}
    assert "neckline" not in decoy_apparel._retitled(coat)


def test_a_restyle_keeps_the_word_and_color_or_fails(monkeypatch):
    """The next exemplar that carries the planned word and color; none is an error, never a
    different word and color (the old fallback drew "White Tunic Dress" for "Red Coat Dress")."""
    plan = {"title": "Red Coat Dress", "word": "coat", "color": "Red"}
    tunic = {"title": "White Tunic Dress", "word": "tunic", "color": "White"}
    carried = {"a": [tunic], "b": [tunic, plan], "c": [plan]}
    monkeypatch.setattr(
        decoy_apparel,
        "_candidates",
        lambda cls, spec, ex, used, words, *, styled=False, want=None: carried[ex],
    )
    spec = SimpleNamespace(product_type="Dress")
    ex, o = decoy_apparel._restyle(2, spec, ["a", "b", "c"], 0, plan, set(), set())
    assert (ex, o) == ("b", plan)
    ex, o = decoy_apparel._restyle(2, spec, ["a", "b", "c"], 2, plan, set(), set())
    assert (ex, o) == ("c", plan)
    carried["b"], carried["c"] = [tunic], [tunic]
    with pytest.raises(ValueError, match="Red Coat Dress"):
        decoy_apparel._restyle(2, spec, ["a", "b", "c"], 0, plan, set(), set())
