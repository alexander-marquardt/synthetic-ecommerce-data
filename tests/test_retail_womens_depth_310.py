"""Womens clothing depth: product floors per leaf (gen#310, the Womens slice).

The Womens tree held 117 dresses over eight leaves, 41 blouses and shirts, 56 coats and jackets,
43 skirts and no camisoles, vest tops, tunics, trench coats, wool coats or rain macs, so ranking,
facets and policies had little to choose between. The floors below are the issue's, written out
here and not read from the rows module, so dropping rows fails this file. They are counted over
:func:`scale.templates`: every row is a template, and a derived style only adds to them.

The text-match decoys of these types are the apparel census's (``decoy_apparel``, gen#311): every
type below is planned there, and ``test_retail_apparel_decoys_311.py`` pins three per class.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_apparel  # noqa: E402
import decoy_product_words  # noqa: E402
import decoy_rows  # noqa: E402
import scale  # noqa: E402

_DECOYS = decoy_apparel.ids() | decoy_rows.IDS | decoy_product_words.IDS

D = ("Womens", "Dresses")
#: group -> (category path prefixes, the floor of distinct products), from the issue.
FLOORS = {
    "dresses": ((D,), 200),
    "blouses and shirts": ((("Womens", "Shirts & Blouses"), ("Womens", "Tops", "Shirts")), 80),
    "coats and jackets": ((("Womens", "Coats & Jackets"),), 80),
    "skirts": ((("Womens", "Skirts"),), 80),
    "tops": ((("Womens", "Tops", "Camisoles"), ("Womens", "Tops", "Vest Tops"),
              ("Womens", "Tops", "Tunics"), ("Womens", "Tops", "Jersey Tops"),
              ("Womens", "Tops", "Long Sleeve Tops"), ("Womens", "Tops", "T-Shirts"),
              ("Womens", "Tops", "Bodysuits")), 80),
    "nightwear and lingerie beyond bras": (
        (("Womens", "Nightwear"), ("Womens", "Lingerie", "Knickers"),
         ("Womens", "Lingerie", "Shapewear"), ("Womens", "Lingerie", "Slips"),
         ("Womens", "Lingerie", "Vests")), 60),
}
#: The groups whose floor is also met without the text-match decoys: the ranking needs real
#: products to choose between.
REAL_FLOORS = {"dresses": 180, "blouses and shirts": 75, "coats and jackets": 70, "skirts": 70}
#: leaf -> the floor of its own, counted over products that are not text-match decoys (a decoy is
#: no answer to "womens puffer jacket"): the dress shapes the issue names, the coats and the new
#: top leaves.
LEAF_FLOORS = {
    D + ("Midi Dresses",): 20, D + ("Maxi Dresses",): 20, D + ("Mini Dresses",): 12,
    D + ("Wrap Dresses",): 18, D + ("Shirt Dresses",): 18, D + ("Tea Dresses",): 12,
    D + ("Jumper Dresses",): 10, D + ("Slip Dresses",): 10, D + ("Shift Dresses",): 10,
    D + ("Bodycon Dresses",): 10, D + ("Occasion Dresses",): 10,
    ("Womens", "Coats & Jackets", "Wool Coats"): 8,
    ("Womens", "Coats & Jackets", "Trench Coats"): 8,
    ("Womens", "Coats & Jackets", "Rain Macs"): 8,
    ("Womens", "Coats & Jackets", "Puffer Jackets"): 8,
    ("Womens", "Coats & Jackets", "Blazers"): 6,
    ("Womens", "Tops", "Camisoles"): 10, ("Womens", "Tops", "Vest Tops"): 10,
    ("Womens", "Tops", "Tunics"): 10,
}
#: The leaves a shopper reads a neckline on, and the ones a sleeve length.
NECKLINE_LEAVES = (D, ("Womens", "Tops", "Camisoles"), ("Womens", "Tops", "Vest Tops"),
                   ("Womens", "Tops", "Tunics"), ("Womens", "Shirts & Blouses"))
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _under(rec: dict, prefixes) -> bool:
    return any(tuple(rec["category_path"][: len(p)]) == p for p in prefixes)


def _decoy(rec: dict) -> bool:
    return rec["product_id"] in _DECOYS


@pytest.mark.parametrize("group", FLOORS)
def test_every_group_meets_its_product_floor(templates, group):
    prefixes, floor = FLOORS[group]
    n = len({r["product_id"] for r in templates if _under(r, prefixes)})
    assert n >= floor, f"{group}: {n} products, floor {floor}"


@pytest.mark.parametrize("group", REAL_FLOORS)
def test_every_group_meets_a_floor_without_its_decoys(templates, group):
    prefixes, _ = FLOORS[group]
    n = len({r["product_id"] for r in templates if _under(r, prefixes) and not _decoy(r)})
    assert n >= REAL_FLOORS[group], f"{group}: {n} products besides decoys"


@pytest.mark.parametrize("leaf", LEAF_FLOORS, ids=lambda p: " > ".join(p[1:]))
def test_every_named_leaf_has_its_own_floor(templates, leaf):
    n = len({r["product_id"] for r in templates
             if tuple(r["category_path"]) == leaf and not _decoy(r)})
    name = " > ".join(leaf)
    assert n >= LEAF_FLOORS[leaf], f"{name}: {n} products besides decoys, floor {LEAF_FLOORS[leaf]}"


@pytest.mark.parametrize("leaf", NECKLINE_LEAVES, ids=lambda p: " > ".join(p[1:]))
def test_a_new_product_states_its_neckline_or_collar(templates, leaf):
    """Every product of the new rows in a leaf where a neckline applies carries one (#181)."""
    import womens_depth_rows

    ids = womens_depth_rows.product_ids()
    rows = [r for r in templates if r["product_id"] in ids and _under(r, (leaf,))]
    assert rows, leaf
    bare = [r["product_id"] for r in rows if not r.get("neckline")]
    assert not bare, bare


def test_every_new_product_states_fit_material_and_a_real_title(templates):
    import womens_depth_rows

    ids = womens_depth_rows.product_ids()
    rows = [r for r in templates if r["product_id"] in ids]
    assert len(rows) >= 200
    titles = [r["title"] for r in rows]
    assert len(set(titles)) == len(titles), "a title repeats"
    for r in rows:
        keys = {a["key"] for a in r["attributes"]}
        assert "fit" in keys and keys & {"material", "fabric"}, (r["product_id"], keys)
        assert r["title"].startswith("Womens "), r["title"]


def test_every_new_product_sells_the_six_main_colors(templates):
    import womens_depth_rows

    ids = womens_depth_rows.product_ids()
    for r in templates:
        if r["product_id"] in ids:
            have = {o["color"] for o in r["color_options"]}
            assert len(have) >= 2, r["product_id"]
    by = {r["product_id"]: {o["color"] for o in r["color_options"]} for r in templates
          if r["product_id"] in ids}
    seen = set().union(*by.values())
    assert seen >= MAIN, MAIN - seen


def test_the_new_rows_are_left_out_of_the_derivation(templates):
    import womens_depth_rows

    ids = womens_depth_rows.product_ids()
    assert ids
    derived = {r["product_id"] for r in scale.derivable(templates)}
    assert not ids & derived


def _new_rows(templates) -> list[dict]:
    import womens_depth_rows

    ids = womens_depth_rows.product_ids()
    return [r for r in templates if r["product_id"] in ids]


def _attr(rec: dict, key: str) -> str:
    return next((a["value"] for a in rec["attributes"] if a["key"] == key), "")


#: The Womens `fit` values before this slice: the facet gains none (Belted, Straight and Tailored
#: are features or cuts a title names, not fit values).
FITS = {"Boxy", "Classic", "Fitted", "Oversized", "Regular", "Relaxed", "Slim"}


def test_a_title_reads_as_a_shop_writes_it(templates):
    """No "Fitted Fit", no "Belted Fit", no neckline word "Collar" in front of a sleeve."""
    pattern = re.compile(r"\b(?:Fitted|Belted|Straight|Tailored) Fit\b|\bCollar (?:\w+ )*Sleeve")
    bad = [r["title"] for r in _new_rows(templates) if pattern.search(r["title"])]
    assert not bad, bad[:3]


def test_the_new_rows_add_no_value_to_the_fit_facet(templates):
    assert {_attr(r, "fit") for r in _new_rows(templates)} <= FITS


def test_the_waist_phrase_follows_the_shape_of_the_dress(templates):
    """A fitted waist only on a Fitted dress; a shift hangs straight and says so."""
    dresses = [r for r in _new_rows(templates) if r["category_path"][1] == "Dresses"]
    assert dresses
    for r in dresses:
        shaped = r["category_leaf"] in {"Shift Dresses", "Bodycon Dresses"}
        said = "fitted waist" in r["description"]
        assert said == (_attr(r, "fit") == "Fitted" and not shaped), (r["title"], r["description"])
    for r in dresses:
        if r["category_leaf"] == "Shift Dresses":
            assert "straight shape" in r["description"], r["description"]


STRETCH_FABRICS = ("jersey", "modal", "stretch", "ribbed", "scuba", "knit", "ponte", "rib")


def test_the_stretch_phrase_follows_the_fabric(templates):
    """Only a fabric that stretches is called stretchy: not georgette, silk blend, lace, linen."""
    for r in _new_rows(templates):
        if "stretch" in r["description"].lower():
            fabric = (_attr(r, "material") or _attr(r, "fabric")).lower()
            assert any(w in fabric for w in STRETCH_FABRICS), (r["title"], r["description"])


CLOSURE = {"A-Line": "side zip", "Pleated": "elastic waist", "Pencil": "back zip",
           "Wrap": "tie waist", "Tiered": "elastic waist"}
WAIST_TYPE = {"A-Line": "Zip", "Pleated": "Elastic", "Pencil": "Zip", "Wrap": "Tie",
              "Tiered": "Elastic"}


def test_a_skirt_closes_the_way_its_kind_does(templates):
    """A wrap ties and has no zip; every new skirt states its waist type and lining."""
    skirts = [r for r in _new_rows(templates) if r["category_path"][1] == "Skirts"]
    assert len(skirts) >= 50
    for r in skirts:
        shape = _attr(r, "skirt_shape")
        assert CLOSURE[shape] in r["description"], (r["title"], r["description"])
        assert _attr(r, "waist_type") == WAIST_TYPE[shape], r["title"]
        assert _attr(r, "lining"), r["title"]
        assert " shape and a " not in r["description"], r["description"]
        if shape == "Wrap":
            assert "zip" not in r["description"].lower(), r["description"]


def test_a_feature_of_a_coat_is_in_its_title_and_its_description(templates):
    belted = [r for r in _new_rows(templates) if "Belted" in r["title"]]
    assert belted
    assert all("belt" in r["description"] for r in belted)
