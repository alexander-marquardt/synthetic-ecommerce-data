"""Kids dresses and coats: product floors per leaf (gen#310, the Kids slice).

The Kids tree held one girls' dress and two or three real boys' coats, no girls' coat and no
leaf over thirty products, while the issue asks for "school uniform ... plus dresses and coats"
on top of the Womens and Mens floors. It gives no number for the two Kids groups, so the floors
below are this slice's own (thirty real products each, the "under 30 per leaf" the issue calls
thin) and are written out here, not read from the rows module, so dropping rows fails this file.
They are counted over :func:`scale.templates` and, like the Womens floors, once without the
text-match decoys, which are no answer to "girls parka".

School uniform (103 products against the issue's 80) is pinned by ``test_retail_school_205.py``.
The text-match decoys of the Dress and Coat types are the apparel census's (``decoy_apparel``,
gen#311), pinned by ``test_retail_apparel_decoys_311.py``.
"""

from __future__ import annotations

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

#: leaf -> the floor of distinct products that are not text-match decoys.
FLOORS = {
    ("Kids", "Girls", "Dresses"): 30,
    ("Kids", "Girls", "Coats & Jackets"): 30,
    ("Kids", "Boys", "Coats & Jackets"): 30,
}
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}
SCHOOL_AGES = {"3-4 Yrs", "5-6 Yrs", "7-8 Yrs", "9-10 Yrs", "11-12 Yrs", "13-14 Yrs", "15-16 Yrs"}


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _new_rows(templates) -> list[dict]:
    import kids_depth_rows

    ids = kids_depth_rows.product_ids()
    return [r for r in templates if r["product_id"] in ids]


def _attr(rec: dict, key: str) -> str:
    return next((a["value"] for a in rec["attributes"] if a["key"] == key), "")


@pytest.mark.parametrize("leaf", FLOORS, ids=lambda p: " > ".join(p[1:]))
def test_every_kids_leaf_meets_its_floor_without_decoys(templates, leaf):
    n = len(
        {
            r["product_id"]
            for r in templates
            if tuple(r["category_path"]) == leaf and r["product_id"] not in _DECOYS
        }
    )
    name = " > ".join(leaf)
    assert n >= FLOORS[leaf], f"{name}: {n} products besides decoys, floor {FLOORS[leaf]}"


def test_the_module_adds_rows_to_the_three_leaves(templates):
    rows = _new_rows(templates)
    assert {tuple(r["category_path"]) for r in rows} == set(FLOORS)
    assert len(rows) >= 70


def test_every_new_title_is_unique_and_names_its_audience(templates):
    rows = _new_rows(templates)
    titles = [r["title"] for r in rows]
    assert titles and len(set(titles)) == len(titles), "a title repeats"
    for r in rows:
        who = "Boys" if r["category_path"][1] == "Boys" else "Girls"
        assert r["title"].startswith(f"{who} "), r["title"]
        words = [w.lower() for w in r["title"].split()]
        assert len(words) == len(set(words)), r["title"]  # no "Wool Blend Wool Coat"


def test_every_new_product_states_fit_material_and_its_type(templates):
    rows = _new_rows(templates)
    assert rows
    for r in rows:
        keys = {a["key"] for a in r["attributes"]}
        assert {"fit", "material", "sleeve_length"} <= keys, (r["product_id"], keys)
        assert r["product_type"] in {"Dress", "Coat"}, r["product_id"]
        assert r["audience"] == "kids", r["product_id"]


def test_a_new_dress_states_its_neckline(templates):
    dresses = [r for r in _new_rows(templates) if r["product_type"] == "Dress"]
    assert len(dresses) >= 25
    assert not [r["product_id"] for r in dresses if not r.get("neckline")]


def test_a_new_dress_states_the_neckline_its_description_names(templates):
    """The row states the neckline itself; ``neckline_rows.complete`` would only guess one."""
    import kids_depth_rows

    said = {phrase: fact for fact, phrase in kids_depth_rows.NECKS.values()}
    dresses = [r for r in _new_rows(templates) if r["product_type"] == "Dress"]
    wrong = []
    for r in dresses:
        named = [fact for phrase, fact in said.items() if f"with {phrase}," in r["description"]]
        if named != [r["neckline"]]:
            wrong.append((r["product_id"], named, r["neckline"]))
    assert not wrong, wrong[:5]


def test_a_sleeve_the_title_names_is_the_sleeve_attribute(templates):
    said = {"Sleeveless": "Sleeveless", "Short Sleeve": "Short", "Long Sleeve": "Long"}
    seen = set()
    for r in _new_rows(templates):
        for words, value in said.items():
            if words in r["title"]:
                assert _attr(r, "sleeve_length") == value, r["title"]
                seen.add(words)
    assert seen == set(said)


def test_the_sleeve_a_description_names_is_the_sleeve_attribute(templates):
    """Dresses and coats alike: the description says the sleeve the attribute states."""
    said = {"Long": "long sleeves", "Short": "short sleeves", "Sleeveless": "no sleeves"}
    kinds = set()
    for r in _new_rows(templates):
        named = [v for v, words in said.items() if words in r["description"]]
        assert named == [_attr(r, "sleeve_length")], (r["product_id"], named, r["description"])
        kinds.add(r["product_type"])
    assert kinds == {"Dress", "Coat"}


def test_the_material_a_product_states_is_in_its_title(templates):
    rows = _new_rows(templates)
    assert rows
    wrong = [
        (r["product_id"], _attr(r, "material"), r["title"])
        for r in rows
        if not _attr(r, "material") or _attr(r, "material").lower() not in r["title"].lower()
    ]
    assert not wrong, wrong[:5]


def test_the_fit_a_product_states_is_the_fit_its_description_names(templates):
    rows = _new_rows(templates)
    assert rows
    wrong = []
    for r in rows:
        named = [f for f in ("Regular", "Relaxed") if f"{f.lower()} fit" in r["description"]]
        if named != [_attr(r, "fit")]:
            wrong.append((r["product_id"], named, _attr(r, "fit")))
    assert not wrong, wrong[:5]


def test_a_coat_description_with_a_list_ends_it_with_and(templates):
    """A coat's tails hold no comma, so the last comma of its list must be followed by "and".

    "with long sleeves, a longline length, a double-breasted front" reads as a missing "and"."""
    bad = []
    for r in (r for r in _new_rows(templates) if r["product_type"] == "Coat"):
        clause = r["description"].split(" with ", 1)[1].rstrip(".")
        if "," in clause and " and " not in clause.rsplit(",", 1)[1]:
            bad.append((r["product_id"], r["description"]))
    assert not bad, bad[:3]


@pytest.mark.parametrize("leaf", FLOORS, ids=lambda p: " > ".join(p[1:]))
def test_the_module_adds_thirty_rows_to_each_leaf(templates, leaf):
    n = len([r for r in _new_rows(templates) if tuple(r["category_path"]) == leaf])
    assert n >= 30, (leaf, n)


def test_a_new_product_sells_in_school_ages_and_at_least_two_colors(templates):
    rows = _new_rows(templates)
    assert rows
    for r in rows:
        sizes = {s["size"] for s in r["skus"]}
        assert sizes and sizes <= SCHOOL_AGES, (r["product_id"], sizes)
        assert len({o["color"] for o in r["color_options"]}) >= 2, r["product_id"]


def test_the_new_rows_sell_the_main_colors_between_them(templates):
    seen = {o["color"] for r in _new_rows(templates) for o in r["color_options"]}
    assert seen >= MAIN, MAIN - seen


def test_the_new_rows_are_left_out_of_the_derivation(templates):
    import kids_depth_rows

    ids = kids_depth_rows.product_ids()
    assert ids
    assert not ids & {r["product_id"] for r in scale.derivable(templates)}


def test_a_coat_leaf_holds_the_spellings_a_shopper_types(templates):
    """ "trench" and "pea coat" (the issue) are real coats in the Kids leaves."""
    titles = " | ".join(r["title"] for r in _new_rows(templates))
    for word in ("Trench Coat", "Pea Coat", "Parka", "Rain Mac", "Padded Coat"):
        assert word in titles, word


def test_the_new_rows_take_no_text_match_decoys_with_them(templates):
    """A type's decoys clone the first exemplars of its pool in product-id order, so a batch of
    new rows that sorts early would take every Dress and Coat decoy into the Kids leaves. The Womens
    dresses keep theirs, and the Kids leaves hold only the decoys they held before (the boys'
    bomber jackets)."""
    for leaf in (("Kids", "Girls", "Dresses"), ("Kids", "Girls", "Coats & Jackets")):
        held = [
            r["title"]
            for r in templates
            if tuple(r["category_path"]) == leaf and r["product_id"] in _DECOYS
        ]
        assert not held, (leaf, held[:3])
    womens = [
        r
        for r in templates
        if r["category_path"][:2] == ["Womens", "Dresses"] and r["product_id"] in _DECOYS
    ]
    assert len(womens) >= 20, len(womens)


def test_the_new_rows_leave_every_other_template_as_it_was(templates, monkeypatch):
    """The rows sit outside the seeded filler stream. Counted by the main-color pass and the sale
    share, they took a Kids dress's added colors and seven Kids styles' sale, so the derivation
    drew other fillers and a Kids tee pushed the "oranges" washing-up liquid out of the top
    twelve (``test_grocery_plural_nonfood_decoys_445``)."""
    import kids_depth_rows

    ids = kids_depth_rows.product_ids()
    monkeypatch.setattr(kids_depth_rows, "docs", lambda: [])
    without = scale.templates()
    assert [r for r in templates if r["product_id"] not in ids] == without
