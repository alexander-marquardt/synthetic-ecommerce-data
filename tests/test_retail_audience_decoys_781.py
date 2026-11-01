"""An audience decoy uses a phrase a shopper really meets, on a type where it is real (#781).

Class 3 of :mod:`decoy_apparel` put the same audience words on every clothing, footwear and
lingerie type ("Brown Mens-Style Bra", "Red Mens-Style School Shoes"). Now
``decoy_apparel_words.AUDIENCE_TYPES`` names each type an audience decoy may sit on, with its
department and its one phrase (Boyfriend, Menswear-Inspired, Mini-Me), and the sibling audience
moves into the description, where real copy names it. The data is the repository's templates.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import decoy_apparel as da
from synthetic_ecommerce_data.domains.retail import decoy_rows as dr
from synthetic_ecommerce_data.domains.retail import scale
from synthetic_ecommerce_data.domains.retail.decoy_apparel_words import AUDIENCE_TYPES

#: A word that names who a garment is for, as a title spells it.
AUDIENCE_WORD = re.compile(
    r"(?<![\w'])(mens|men's|womens|women's|boys|girls|kids|boyfriend|menswear|mini-me)(?![\w'])",
    re.IGNORECASE,
)
#: The words a department's own titles carry ("Womens Puffer Jacket" in Womens is no decoy).
OWN = {
    "Womens": {"womens", "women's"},
    "Mens": {"mens", "men's"},
    "Kids": {"kids", "boys", "girls"},
}
#: The issue's types: lingerie, swimwear, babywear, school shoes and safety boots.
NEVER = {"Bra", "Knickers", "Slip", "Shapewear", "Swimsuit", "Tankini",
         "Bikini Top", "Bikini Bottoms", "Kids Swimsuit", "Swim Shorts",
         "Baby Bodysuit", "Sleepsuit", "All-in-One", "School Shoes", "Safety Boots"}  # fmt: skip
#: The reviewed phrases, held apart from the generator's table: a type joins only with a phrase
#: real titles use there (the maintainer's ruling on #781), and none leaves unnoticed.
REVIEWED = {
    "Jeans": ("Womens", "Boyfriend"),
    "Shirt": ("Womens", "Boyfriend"),
    "Tee": ("Womens", "Boyfriend"),
    "Cardigan": ("Womens", "Boyfriend"),
    "Jumper": ("Womens", "Boyfriend"),
    "Shorts": ("Womens", "Boyfriend"),
    "Trousers": ("Womens", "Menswear-Inspired"),
    "Suit Jacket": ("Womens", "Menswear-Inspired"),
    "Dress": ("Womens", "Mini-Me"),
    "Puffer Jacket": ("Kids", "Mini-Me"),
    "Pyjamas": ("Kids", "Mini-Me"),
    "Sweatshirt": ("Kids", "Mini-Me"),
}


def test_the_table_is_the_reviewed_list() -> None:
    assert {t: (a.root, a.phrase) for t, a in AUDIENCE_TYPES.items()} == REVIEWED


@pytest.fixture(scope="module")
def rows() -> list[da.Row]:
    body = [d for d in scale.templates(baseline=False) if d["product_id"] not in da.IDS]
    return da.build(body)


@pytest.fixture(scope="module")
def decoy_docs(rows: list[da.Row]) -> list[dict]:
    """Every planted decoy's clothing, footwear or lingerie document, from both generators."""
    return [d for d in [r.doc for r in rows] + dr.docs() if d["category_path"][0] in OWN]


def _strays(doc: dict) -> set[str]:
    """The audience words of ``doc``'s title that are not its own department's."""
    found = {w.lower() for w in AUDIENCE_WORD.findall(doc["title"])}
    return found - OWN[doc["category_path"][0]]


def test_no_decoy_title_pairs_an_audience_word_with_a_type_outside_the_table(
    decoy_docs: list[dict],
) -> None:
    bad = []
    for doc in decoy_docs:
        strays = _strays(doc)
        if not strays:
            continue
        entry = AUDIENCE_TYPES.get(doc["product_type"])
        if (
            entry is None
            or entry.root != doc["category_path"][0]
            or not all(w in entry.phrase.lower() for w in strays)
        ):
            bad.append((doc["product_id"], doc["product_type"], doc["title"]))
    assert not bad, bad[:20]


def test_no_lingerie_swimwear_babywear_school_shoe_or_safety_boot_holds_another_audience(
    decoy_docs: list[dict],
) -> None:
    planned = {t.product_type for t in da.types()}
    assert planned >= NEVER, NEVER - planned
    assert not NEVER & set(AUDIENCE_TYPES)
    bad = [d["title"] for d in decoy_docs if d["product_type"] in NEVER and _strays(d)]
    assert not bad, bad[:20]


def test_class_3_sits_on_every_table_type_and_on_no_other(rows: list[da.Row]) -> None:
    """The trap stays where it is real: three decoys a table type, in its department."""
    got: dict[str, list[da.Row]] = {}
    for r in rows:
        if r.cls == 3:
            got.setdefault(r.product_type, []).append(r)
    assert set(got) == set(AUDIENCE_TYPES), set(got) ^ set(AUDIENCE_TYPES)
    for ptype, rs in got.items():
        entry = AUDIENCE_TYPES[ptype]
        assert len(rs) >= 3, (ptype, len(rs))
        assert {r.doc["category_path"][0] for r in rs} == {entry.root}, ptype
        assert all(entry.phrase in r.title for r in rs), (ptype, [r.title for r in rs])
        if entry.fit:  # "Boyfriend Jeans" names a leg fit: only a boyfriend jean carries it
            assert {da._fit(r.doc) for r in rs} == {entry.phrase}, (ptype, [r.title for r in rs])


def test_an_audience_decoy_names_its_sibling_in_the_description_only(rows: list[da.Row]) -> None:
    """The query's audience word ("mens jeans") is in the description, never the title, and
    the audience field keeps the decoy's own department."""
    threes = [r for r in rows if r.cls == 3]
    assert threes
    for r in threes:
        entry = AUDIENCE_TYPES.get(r.product_type)
        assert entry, (r.pid, r.title)
        assert r.word == entry.word and r.query.startswith(f"{entry.word} "), r.pid
        assert re.search(rf"\b{entry.word}\b", r.doc["description"]), (r.pid, r.doc["description"])
        assert not re.search(rf"\b{entry.word}\b", r.title.lower()), (r.pid, r.title)
