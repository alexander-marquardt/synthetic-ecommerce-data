"""Slice B of gen#125: sale signals, badges, the full category path, classes 10 to 13
and two cross-domain word collisions.

Run: ``uv run pytest prototypes/retail_drawings/test_signals_and_paths.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import real_classes as rc  # noqa: E402

CLASS_DOCS = rc.class_docs()
CORPUS = rc.corpus()
GOLDEN = HERE.parents[1] / "golden-catalog" / "nested.jsonl"


def _one(code: str) -> dict:
    """The one product document of style ``code``."""
    docs = [d for d in CLASS_DOCS if d["product_id"] == f"PLT-{code}"]
    assert len(docs) == 1, code
    return docs[0]


def _colors(d: dict) -> set[str]:
    return {s["color"] for s in d["skus"] if "color" in s}


def _row(query: str) -> rc.ClassRow:
    rows = [r for r in rc.ROWS if r.query == query]
    assert len(rows) == 1, query
    return rows[0]


def _collision(word: str) -> dict:
    rows = [c for c in rc.COLLISIONS if c["word"] == word]
    assert len(rows) == 1, word
    return rows[0]


def _codes(row: rc.ClassRow) -> tuple[list[str], list[str]]:
    return [s.code for s in row.targets], [s.code for s, _ in row.distractors]


def test_the_new_rows_are_classes_10_to_14() -> None:
    rows = [r for r in rc.ROWS if 10 <= r.n <= 14]
    assert [(r.n, r.query, len(r.targets), len(r.distractors)) for r in rows] == [
        (10, "beer", 3, 5),
        (11, "oranges", 3, 6),
        (12, "face cream", 3, 8),
        (13, "single bed", 3, 5),
        (14, "rose gold", 5, 5),
    ]


# --------------------------------------------------------------------------
# (1) Signals and sale
# --------------------------------------------------------------------------


def test_discount_pct_is_derived_from_price_and_was_price_on_sale_docs_only() -> None:
    sale = [d for d in CLASS_DOCS if "was_price" in d]
    assert len(sale) == 10
    for d in CLASS_DOCS:
        if "was_price" in d:
            assert d["discount_pct"] == round(100 * (d["was_price"] - d["price"]) / d["was_price"])
            assert "On sale" in d["promotion"] and 0 < d["discount_pct"] < 100
        else:
            assert "discount_pct" not in d, d["product_id"]
            assert "promotion" not in d, d["product_id"]


def test_every_class_doc_carries_the_online_only_and_badge_flags() -> None:
    for d in CLASS_DOCS:
        assert "offer" not in d and isinstance(d["online_only"], bool)
        assert isinstance(d["trending"], bool)
        assert d["brand_owner"] in rc.BRAND_OWNERS, d["brand"]
    assert sum(d["online_only"] for d in CLASS_DOCS) == 4
    assert sum(d["trending"] for d in CLASS_DOCS) == 3
    # A multi-buy has no was-price, so no promotion: it becomes its own field later (gen#189).
    assert "promotion" not in next(d for d in CLASS_DOCS if d["product_id"] == "PLT-BRTROP")


def test_third_party_brands_are_over_represented_in_sales() -> None:
    sales = [d for d in CLASS_DOCS if "promotion" in d]
    assert len(sales) == 10
    # The sale rows are pinned to the live-ES proof (``real_classes_proof.json`` fingerprints
    # their brands and titles), so they do not move with the catalogue: gen#236 gave the four
    # brands that held two owners the third-party owner their names read as, 17 docs moved from
    # own to third party, and the share of all docs went from 27/123 to 44/123 while the sales
    # stayed at 4 of 10 (1.1 times the share, where it was 1.8). So the floor is a count that
    # does not depend on the denominator: a ratio would go red on a catalogue change and not
    # on the sales.
    assert sum(d["brand_owner"] == "third_party" for d in sales) >= 4
    edit = [d for d in CLASS_DOCS if d.get("sub_collection")]
    assert {d["sub_collection"] for d in edit} == {"The Active Edit", "The Weekend Edit"}
    assert all(d["brand_owner"] == "third_party" for d in edit)


def test_badges_are_bestseller_trending_and_online_only_in_one_order() -> None:
    for d in CLASS_DOCS:
        want = [
            label
            for label, on in (
                ("Bestseller", d["bestseller_rank"] <= rc.BESTSELLER_TOP),
                ("Trending", d["trending"]),
                ("Online Only", d["online_only"]),
            )
            if on
        ]
        assert d["badges"] == want, d["product_id"]
    assert sum("Bestseller" in d["badges"] for d in CLASS_DOCS) == rc.BESTSELLER_TOP


def test_the_new_docs_leave_the_bestseller_top_15_of_the_old_rows_alone() -> None:
    new = {
        s.code for r in rc.ROWS if r.n >= 10 for s in (*r.targets, *(x for x, _ in r.distractors))
    }
    new |= {s.code for s in rc.OFFERS}
    top = [d for d in CLASS_DOCS if d["bestseller_rank"] <= rc.BESTSELLER_TOP]
    assert len(top) == rc.BESTSELLER_TOP
    assert not any(d["product_id"][4:] in new for d in top)


# --------------------------------------------------------------------------
# (2) The full category path
# --------------------------------------------------------------------------


def test_every_doc_has_a_full_category_path_of_clean_shopper_terms() -> None:
    assert rc.check_category_paths(CORPUS) == []
    for d in CLASS_DOCS:
        assert d["category_leaf"] == d["category_path"][-1]
        assert len(d["category_path"]) >= 3
    deepest = max(CLASS_DOCS, key=lambda d: len(d["category_path"]))
    assert len(deepest["category_path"]) == 5


def test_the_index_projects_every_ancestor_as_its_own_joined_value() -> None:
    orange = rc.index_doc(_one("ORBLOD"))
    assert orange["category_path_joined"] == [
        "Food & Drink",
        "Food & Drink/Fruit & Vegetables",
        "Food & Drink/Fruit & Vegetables/Fresh Fruit",
        "Food & Drink/Fruit & Vegetables/Fresh Fruit/Citrus Fruit",
        "Food & Drink/Fruit & Vegetables/Fresh Fruit/Citrus Fruit/Oranges",
    ]
    for d in CORPUS:
        joined = rc.index_doc(d)["category_path_joined"]
        assert joined[-1].split(rc.PATH_SEPARATOR) == d["category_path"]
    props = rc.index_body()["mappings"]["properties"]
    for key in ("category_path", "category_leaf", "category_path_joined", "brand_owner", "badges"):
        assert props[key] == {"type": "keyword"}, key


def test_the_category_check_refuses_a_joined_name_a_bucket_and_a_leaf_that_is_a_parent() -> None:
    base = {"product_id": "X", "category_path": ["Home", "Bedding", "Duvets"]}
    assert rc.check_category_paths([base]) == []
    joined = {**base, "category_path": ["Home", "Bedding > Duvets", "Duvets"]}
    slash = {**base, "category_path": ["Home", "Bedding/Duvets", "Duvets"]}
    bucket = {**base, "category_path": ["Home", "Sale", "Duvets"]}
    short = {**base, "category_path": ["Home", "Duvets"]}
    parent = {**base, "product_id": "Y", "category_path": ["Home", "Bedding"]}
    deeper = {**base, "product_id": "Z", "category_path": ["Home", "Sleep", "Bedding", "Pads"]}
    assert len(rc.check_category_paths([joined])) == 1
    assert len(rc.check_category_paths([slash])) == 1
    assert len(rc.check_category_paths([bucket])) == 1
    assert len(rc.check_category_paths([short])) == 1
    assert len(rc.check_category_paths([base, {**parent, "category_path": [
        "Home", "Bedding", "Duvets", "Winter"]}])) == 1  # fmt: skip
    assert len(rc.check_category_paths([base, deeper])) == 1


def test_the_category_check_takes_a_two_path_product_and_refuses_a_malformed_second_path() -> None:
    """A product at several paths (``category_paths``, gen#602) is held to the same tree rules on
    every path: the mug is filed at a Home path and a Gifts path."""
    home = ["Home", "Kitchen", "Mugs"]
    gifts = ["Gifts", "Drinkware", "Mugs"]
    mug = {"product_id": "M", "category_path": home, "category_paths": [home, gifts]}
    assert rc.check_category_paths([mug]) == []
    assert rc.check_category_paths([mug, {**mug, "product_id": "N"}]) == []
    for second in (["Gifts", "Mugs"], ["Gifts", "Sale", "Mugs"], ["Gifts", "A/B", "Mugs"],
                   ["Gifts", "", "Mugs"]):  # fmt: skip
        bad = {**mug, "category_paths": [home, second]}
        assert len(rc.check_category_paths([bad])) == 1, second
    parent = {"product_id": "P", "category_path": ["Gifts", "Drinkware", "Mugs", "Travel"]}
    assert len(rc.check_category_paths([mug, parent])) == 1  # the second path is now a parent
    odd = {**mug, "category_paths": [home, "Gifts/Mugs"]}
    assert len(rc.check_category_paths([odd])) == 1
    off = {**mug, "category_paths": [gifts, home]}
    assert len(rc.check_category_paths([off])) == 1  # the primary path leads


# --------------------------------------------------------------------------
# (3) Classes 10 to 13
# --------------------------------------------------------------------------


def test_beer_carries_abv_as_an_attribute_and_only_some_titles_state_it() -> None:
    beers = [d for d in CLASS_DOCS if d["product_type"] == "Beer"]
    assert len(beers) == 3
    for d in beers:
        abv = [a for a in d["attributes"] if a["key"] == "abv"]
        assert abv == [{"key": "abv", "name": "ABV (%)", "value": str(d["abv"])}]
        # A volume is on the product (one size) or on every SKU (three or more, gen#347).
        if "unit_size" in d:
            assert d["unit_measure"] == "ml" and d["unit_size"] > 0
            assert not any("net_volume_ml" in s for s in d["skus"])
        else:
            assert all(s["net_volume_ml"] > 0 for s in d["skus"])
    assert sum(f"{d['abv']}%" in d["title"] for d in beers) == 2
    targets, distractors = _codes(_row("beer"))
    types = {_one(c)["product_type"] for c in distractors}
    assert types == {"Ginger Beer", "Root Beer", "Battered Fish", "Chips", "Bread"}
    assert all("beer" in _one(c)["title"].lower() for c in distractors)


def test_oranges_has_flavour_and_color_distractors_and_a_type_only_true_hit() -> None:
    row = _row("oranges")
    targets, distractors = _codes(row)
    peel = _one("OREASY")
    assert peel["category_leaf"] == "Oranges" and row.is_intended(peel)
    assert "orange" not in (peel["title"] + peel["description"]).lower()
    flavours = [_one(c) for c in distractors if _one(c)["department"] == ["Food & Drink"]]
    assert len(flavours) == 4
    swatches = {c: _one(c).get("color_options", ()) for c in distractors}
    colored = [_one(c) for c, sw in swatches.items() if any(o["family"] == "orange" for o in sw)]
    assert {d["department"][0] for d in colored} == {"Clothing", "Garden"}


def test_face_cream_meets_a_cream_color_near_types_and_a_line_named_cream() -> None:
    _, distractors = _codes(_row("face cream"))
    docs = [_one(c) for c in distractors]
    cream = {d["department"][0] for d in docs if "Cream" in _colors(d)}
    assert cream == {"Home", "Clothing"}
    assert {d["category_path"][1] for d in docs if "Cream" in _colors(d)} == {
        "Furniture", "Bedding", "Knitwear"}  # fmt: skip
    near = {d["product_type"] for d in docs if d["department"] == ["Beauty"]}
    assert near == {"Face Powder", "Skin Tint", "Face Oil", "Sun Cream", "Body Oil"}
    line = [d for d in docs if d.get("product_line")]
    assert [(d["product_line"], d["product_type"]) for d in line] == [
        ("Velvetmere Cream", "Body Oil")
    ]


def test_beds_are_sized_on_the_shared_bed_size_vocabulary_and_some_have_no_single() -> None:
    assert set(rc.BED_SIZES) < set(rc.BED_SIZE_DIMS)
    assert len(rc.BED_SIZE_DIMS) == 5
    beds = [d for d in CLASS_DOCS if d["product_type"] in ("Bed", "Chairbed", "Sofa Bed")]
    assert len(beds) == 8
    for d in beds:
        for s in d["skus"]:
            assert (s["width_cm"], s["length_cm"]) == rc.BED_SIZE_DIMS[s["bed_size"]]
            assert s["price"] > 0 and s["in_stock"] is True
        prices = [s["price"] for s in d["skus"]]
        assert prices == sorted(prices)
    single = rc.BED_SIZES[0]
    without = [d for d in beds if single not in {s["bed_size"] for s in d["skus"]}]
    assert len(without) == 4
    assert all(not _row("single bed").is_intended(d) for d in without)


def test_the_single_bed_policy_is_a_nested_size_filter_and_a_type_boost() -> None:
    body = rc.policy_body(_row("single bed"))
    filters = body["query"]["function_score"]["query"]["bool"]["filter"]
    assert filters == [
        {"nested": {"path": "skus", "query": {"bool": {
            "filter": [{"terms": {"skus.bed_size": [rc.BED_SIZES[0]]}}],
            "must_not": [{"term": {"skus.in_stock": False}}]}}}}
    ]  # fmt: skip


def test_a_routed_policy_recalls_and_boosts_the_named_category_node() -> None:
    body = rc.policy_body(_row("oranges"))
    fs = body["query"]["function_score"]
    node = "Food & Drink/Fruit & Vegetables/Fresh Fruit/Citrus Fruit/Oranges"
    assert fs["query"]["bool"]["should"][1] == {
        "constant_score": {"filter": {"term": {"category_path_joined": node}}}
    }
    assert fs["query"]["bool"]["minimum_should_match"] == 1
    assert fs["functions"][-1] == {"filter": {"term": {"category_path_joined": node}},
                                   "weight": rc.ROUTE_WEIGHT}  # fmt: skip
    assert sum(r.policy.route is not None for r in rc.ROWS) == 4


def test_rose_gold_is_one_color_value_and_the_finish_of_every_metal_good() -> None:
    rose = [d for d in CLASS_DOCS if "Rose Gold" in _colors(d)]
    assert sorted(d["product_type"] for d in rose) == [
        "Earrings", "Highlighter", "Table Lamp", "Watch", "Wireless Charger"]  # fmt: skip
    metal = [d for d in CLASS_DOCS if any("finish" in s for s in d["skus"])]
    # The five rose gold goods, the link watch and the class 15 trophy cup.
    assert len(metal) == 7
    for d in metal:
        # Every SKU of a metal good: its finish IS its color.
        assert all(s["finish"] == s["color"].lower() for s in d["skus"]), d["product_id"]
        assert not any(a["key"] == "finish" for a in d["attributes"])
    assert set().union(*(_colors(d) for d in metal)) == set(rc.FINISHES)
    # A make-up shade carries the color but is no metal: no finish on its SKU.
    assert [d["product_type"] for d in rose if d not in metal] == ["Highlighter"]


def test_rose_bouquets_and_rose_quartz_hold_both_words_but_not_the_color() -> None:
    _, distractors = _codes(_row("rose gold"))
    docs = [_one(c) for c in distractors]
    words = [d for d in docs if {"rose", "gold"} <= set(d["title"].lower().split())]
    assert sorted(d["product_type"] for d in words) == ["Bouquet", "Bouquet", "Earrings"]
    assert all("Rose Gold" not in _colors(d) for d in docs)
    hoop = _one("RQHOOP")
    assert {a["key"]: a["value"] for a in hoop["attributes"]} == {"stone": "rose quartz"}
    assert [(s["color"], s["finish"]) for s in hoop["skus"]] == [("Yellow Gold", "yellow gold")]


def test_the_rose_gold_policy_filters_on_the_color_value_as_one_term() -> None:
    body = rc.policy_body(_row("rose gold"))
    bool_q = body["query"]["function_score"]["query"]["bool"]
    assert bool_q["filter"] == [{"nested": {"path": "skus", "query": {"bool": {
        "filter": [{"terms": {"skus.color": ["Rose Gold"]}}],
        "must_not": [{"term": {"skus.in_stock": False}}]}}}}]  # fmt: skip
    assert rc.index_body()["mappings"]["properties"]["skus"]["properties"]["color"] == {
        "type": "keyword"}  # fmt: skip


# --------------------------------------------------------------------------
# (4) Collisions with the industrial domain and inside retail
# --------------------------------------------------------------------------


def _industrial_keys() -> set[str]:
    keys = set()
    with GOLDEN.open(encoding="utf-8") as fh:
        for line in fh:
            keys |= {a["key"] for a in json.loads(line).get("attributes", [])}
    return keys


def test_thread_is_a_bedding_count_here_and_a_pitch_in_industrial() -> None:
    thread = _collision("thread")
    industrial = _industrial_keys()
    assert set(thread["industrial_keys"]) <= industrial
    # The industrial golden catalog keys a screw thread by size ("1/4-20"), not pitch.
    assert "thread_size" in thread["industrial_keys"]
    retail = {a["key"] for d in CLASS_DOCS for a in d["attributes"] if "thread" in a["key"]}
    assert retail == {"thread_count"} and not retail & industrial
    sheets = [d for d in CLASS_DOCS if any(a["key"] == "thread_count" for a in d["attributes"])]
    # One duvet cover style, its two colors SKUs of the one product.
    assert len(sheets) == 1 and len(_colors(sheets[0])) == 2
    for d in sheets:
        count = next(a for a in d["attributes"] if a["key"] == "thread_count")
        assert count == {"key": "thread_count", "name": "Thread Count", "value": "400"}


def test_honey_is_a_food_and_no_lipstick_shade_carries_the_word() -> None:
    """The lipstick's "Wild Honey" is the plain color Tan (gen#150): one sense is left."""
    assert [c for c in rc.COLLISIONS if c["word"] == "honey"] == []
    shades = [d for d in CLASS_DOCS if any("honey" in c.lower() for c in _colors(d))]
    food = [d for d in CLASS_DOCS if d["product_type"] == "Honey"]
    assert shades == []
    assert len(food) == 1 and food[0]["department"] == ["Food & Drink"]
    assert _colors(food[0]) == set() and "color_options" not in food[0]
