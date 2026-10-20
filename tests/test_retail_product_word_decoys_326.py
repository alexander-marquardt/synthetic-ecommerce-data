"""Class-8 text-match decoys: a title holds the shopper's product noun on another product (gen#326).

"red dress" must never meet a product that is not a dress but says so in its title: Dress for
Success shoes, a doll in a red dress, a french dressing. The structured fields are the truth (the
category path, the product type, the color and the drawing); only the title carries the noun.
The department, category and color policies fix every row, and the docs table says which.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_product_words as dpw  # noqa: E402
import export  # noqa: E402
import house_styles  # noqa: E402
import image_release  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
from distractors import tokens  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

#: The nouns the issue names: each carries at least two class-8 decoys.
MIN_NOUNS = (
    "dress",
    "shoe",
    "boot",
    "coat",
    "jacket",
    "jumper",
    "skirt",
    "suit",
    "bra",
    "trainer",
    "hat",
    "belt",
    "tie",
    "sofa",
)
#: The ten queries the PR body reports the prototype's top 10 for.
QUERIES = (
    "red dress",
    "black dress",
    "blue sofa",
    "black boots",
    "white trainers",
    "red jumper",
    "black ties",
    "navy suit",
    "white coat",
    "black shoes",
)
#: noun -> the category node of the product the noun really names (a decoy never sits in it).
TRUE_NODE = {
    "dress": "Dresses",
    "shoe": "Shoes",
    "boot": "Boots",
    "coat": "Coats & Jackets",
    "jacket": "Coats & Jackets",
    "jumper": "Jumpers",
    "skirt": "Skirts",
    "suit": "Suits & Tailoring",
    "bra": "Bras",
    "trainer": "Trainers",
    "hat": "Hats",
    "belt": "Belts",
    "tie": "Ties",
    "sofa": "Sofas",
    "pump": "Pumps",
    "cap": "Caps",
    # the Sports & Outdoors nouns of the #368 rows: the node of the sports product
    "block": "Yoga Blocks",
    # the nouns of the #352 rows
    "bicycle": "Bikes",
    "helmet": "Bike Helmets",
    "kayak": "Kayaks",
    "scooter": "Kick Scooters",
    "skateboard": "Skateboards",
    "strap": "Yoga Straps",
    "band": "Resistance Bands",
    "resistance": "Resistance Bands",
    "lantern": "Lanterns",
    "roll": "Roll Mats",
    "bat": "Baseball Bats",
    "baseball": "Baseballs",
    "glove": "Baseball Gloves",
    "batting": "Batting Helmets",
    "swim": "Swim Caps",
    "kickboard": "Kickboards",
    "armband": "Swim Armbands",
    "football": "Footballs",
    "tenni": "Tennis Rackets",
    "badminton": "Badminton Sets",
    "picnic": "Picnic Blankets",  # gen#217
    # the first-increment Sports & Outdoors nouns of the #375 rows
    "tent": "Tents",
    "sleeping": "Sleeping Bags",
    "camping": "Camping Chairs",
    "yoga": "Yoga Mats",
    "dumbbell": "Dumbbells",
    "kettlebell": "Kettlebells",
    "foam": "Foam Rollers",
    # the Gifts nouns of the #425 rows: the node of the gift
    "mug": "Mugs & Drinkware",
    "card": "Greeting Cards",
    "notebook": "Notebooks",
    "box": "Money Boxes",
    "hamper": "Pamper Hampers",
    # the large appliances of gen#334; the washing machine's leaf is "Laundry", a node the
    # Cleaning tree has too, so its decoys are kept out of the department node instead
    "fridge": "Fridges & Freezers",
    "dishwasher": "Dishwashers",
    "washing": "Large Appliances",
}
POLICIES = ("category", "department", "color")


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def test_every_noun_has_two_decoys_and_six_cross_department_rows() -> None:
    assert dpw.TABLE, "the class-8 table is empty"
    for noun in MIN_NOUNS:
        assert sum(r.noun == noun for r in dpw.TABLE) >= 2, noun
    assert sum(r.cross for r in dpw.TABLE) >= 6


def test_every_title_is_short_and_holds_the_noun_and_the_query(by_id: dict[str, dict]) -> None:
    assert dpw.TABLE
    for pid, row in dpw.BY_ID.items():
        if not row.decoy:
            continue
        title = by_id[pid]["title"]
        assert len(title.split()) <= 5, title
        assert not row.noun or row.noun in tokens(title), (pid, title)
        text = set(tokens(title)) | set(tokens(by_id[pid]["description"]))
        assert set(tokens(row.query)) <= text, (pid, row.query)


def test_the_fields_say_the_product_is_not_what_the_noun_names(by_id: dict[str, dict]) -> None:
    assert dpw.TABLE
    for pid, row in dpw.BY_ID.items():
        if not row.decoy or not row.noun:
            continue
        doc = by_id[pid]
        assert TRUE_NODE[row.noun] not in doc["category_path"], (pid, doc["category_path"])
        assert tokens(doc["product_type"]) != tokens(TRUE_NODE[row.noun]), pid
        assert doc["category_leaf"] == doc["category_path"][-1]


def test_a_cross_department_row_sits_under_another_root(by_id: dict[str, dict]) -> None:
    rows = [(p, r) for p, r in dpw.BY_ID.items() if r.cross]
    assert rows
    for pid, _ in rows:
        assert by_id[pid]["category_path"][0] not in ("Womens", "Mens", "Kids"), pid
    assert any(by_id[p]["category_path"][0] == "Food & Drink" for p, _ in rows)
    assert len({by_id[p]["category_path"][0] for p, _ in rows}) >= 3


def test_every_row_names_the_policy_that_fixes_it() -> None:
    assert dpw.TABLE
    for row in dpw.TABLE:
        assert row.policy.split(":")[0] in (*POLICIES, "special"), row.policy
        if row.policy.startswith("special"):
            assert row.sibling, row.code  # a special policy is proved on a sibling query


def test_the_drawing_shows_the_true_product_and_the_named_detail(by_id: dict[str, dict]) -> None:
    assert dpw.TABLE
    for pid, row in dpw.BY_ID.items():
        doc = by_id[pid]
        assert doc["drawing"]["shape"] == row.shape, pid
        svg = image_release.render(doc, doc["skus"][0]).decode()
        assert "<svg" in svg
        if row.detail:
            hexv = dpw.COLORS[row.detail]
            assert doc["drawing"]["params"][row.detail_param] == hexv, pid
            assert hexv in svg, (pid, row.detail)
        if row.color != row.detail:
            assert doc["drawing"]["base"] == dpw.COLORS[row.color], pid


def test_the_detail_is_the_only_color_the_title_names() -> None:
    detailed = [r for r in dpw.TABLE if r.detail]
    assert len(detailed) >= 2
    for row in detailed:
        words = {w.lower() for w in re.findall(r"[A-Za-z]+", row.title)}
        named = words & {c.lower() for c in dpw.COLORS}
        assert named == {row.detail.lower()}, (row.code, row.title)


@pytest.mark.timeout(900)  # three standard checks over the 10**6 ceiling: 172 s on a light shard
def test_a_detail_color_is_exempt_by_decoy_id_and_an_ordinary_product_is_not(
    ceiling: list[dict],
) -> None:
    """Dress for Success, Red Laces (color Black) passes the standard as a declared decoy; the same
    document under an ordinary id, naming Red with color Black, is still refused."""
    detailed = [r for r in dpw.TABLE if r.detail]
    assert detailed
    docs = [export.standard_document(r) for r in ceiling]  # the pools the check reads
    decoys = [d for d in docs if d["product_id"] in dpw.TEXT_EXEMPT]
    assert len(decoys) == len(detailed)
    assert check_catalog(docs, text_exempt=scale.TEXT_EXEMPT) == []
    # the exemption is keyed on the id: leave the class-8 ids out and each of them is refused
    refused = check_catalog(docs, text_exempt=scale.TEXT_EXEMPT - dpw.TEXT_EXEMPT)
    assert {p.split(":")[0] for p in refused} == dpw.TEXT_EXEMPT, refused
    ordinary = json.loads(json.dumps(decoys[0]).replace("PLT-", "ORDINARY-8-"))
    refused = check_catalog([*docs, ordinary], text_exempt=scale.TEXT_EXEMPT)
    assert [p for p in refused if p.startswith("ORDINARY-8")], refused


def test_each_new_real_type_has_a_floor_of_its_own() -> None:
    assert dpw.FLOOR and dpw.NEW_TYPES
    for ptype in dpw.NEW_TYPES:
        assert sum(r.ptype == ptype for r in dpw.FLOOR) >= 3, ptype


@pytest.mark.parametrize("query", QUERIES)
def test_the_baseline_top_10_holds_a_class_8_decoy(index: br.Index, query: str) -> None:
    top = [d["product_id"] for d in br.rank(index, query, 10)]
    assert any(i in dpw.BY_ID and dpw.BY_ID[i].decoy for i in top), (query, top)


def test_blue_bull_is_a_color_word_brand_on_footwear_in_every_color_but_blue(
    by_id: dict[str, dict],
) -> None:
    rows = [r for r in dpw.TABLE if r.brand == "Blue Bull"]
    assert {r.color for r in rows} >= {"White", "Black", "Red"}
    assert "Blue" not in {r.color for r in rows}
    for pid, row in dpw.BY_ID.items():
        if row.brand != "Blue Bull":
            continue
        doc = by_id[pid]
        assert doc["brand"] == "Blue Bull" and doc["title"].startswith("Blue Bull")
        assert doc["category_path"][1] == "Shoes", pid
    style = house_styles.HOUSE_STYLES["Blue Bull"]
    others = [s for b, s in house_styles.HOUSE_STYLES.items() if b != "Blue Bull"]
    assert style.mark not in {s.mark for s in others}
    assert house_styles.lockup_key(style) not in {house_styles.lockup_key(s) for s in others}


def test_the_rows_are_templates_no_derived_style_copies_or_color_completes() -> None:
    tpls = scale.templates()
    assert dpw.IDS and not dpw.IDS & {r["product_id"] for r in scale.derivable(tpls)}
    assert not dpw.IDS & {r["product_id"] for g in main_colors.groups(tpls).values() for r in g}


def test_the_docs_table_lists_every_row_with_its_policy() -> None:
    path = ROOT / "docs" / "retail-product-word-decoys.md"
    assert path.exists() and dpw.TABLE
    doc = path.read_text(encoding="utf-8")
    table = dpw.table_markdown()
    assert table in doc
    assert len(table.splitlines()) == len(dpw.TABLE) + 2
    assert all(r.policy in line for r, line in zip(dpw.TABLE, table.splitlines()[2:], strict=True))
