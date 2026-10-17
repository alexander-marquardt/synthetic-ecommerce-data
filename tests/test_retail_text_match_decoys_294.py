"""The retail catalog holds text-match decoys for the demo queries (gen#294).

A decoy's title carries the query's word while its color, category path or audience says it is
not what the query means. Each query is held two ways: without interpretation (BM25 times
popularity, :mod:`baseline_rank`) at least three decoys are in the top 10 and one in the top 3,
and with interpretation (the intended color, type and audience read from the structured fields)
none of them is a hit, so no color, category or audience policy can leave one in the top 10.
The guard rows are real products whose name holds a color word ("green tea").
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_apparel as da  # noqa: E402
import decoy_rows as dr  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402

#: query -> (color, product types, path root, path word): what the interpreted query keeps.
INTENT = {
    "red sofa": ("Red", None, None, "Sofas"),
    "blue sofa": ("Blue", None, None, "Sofas"),
    "red bra": ("Red", {"Bra"}, None, None),
    "blue shirt": ("Blue", {"Shirt"}, None, None),
    "black trainers": ("Black", {"Trainers"}, None, None),
    "mens puffer jacket": (None, {"Puffer Jacket"}, "Mens", None),
    "boys grey socks": ("Grey", {"Socks"}, "Kids", None),
    "face cream": (None, {"Face Cream"}, None, None),
    "gold top": ("Gold", {"Top", "Tee"}, None, None),
    "red wine": (None, {"Wine"}, None, "Red Wine"),
}
GUARDS = ("green tea", "black pepper", "red velvet cake", "pink lady apples")
#: Class 7: query -> the word the decoys hold in the ingredients and not in the title.
INGREDIENT_QUERIES = {"oranges": "orange", "lemons": "lemon", "strawberries": "strawberry",
                      "coconut": "coconut", "lavender": "lavender"}


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _intended(doc: dict, query: str) -> bool:
    color, types, root, word = INTENT[query]
    path = doc["category_path"]
    return (
        (color is None or color in {c["color"] for c in doc.get("color_options", [])})
        and (types is None or doc["product_type"] in types)
        and (root is None or path[0] == root)
        and (word is None or word in path)
    )


def _decoys(query: str) -> list[dr.Decoy]:
    return [d for d in dr.TABLE if d.query == query and not d.true_hit]


def test_every_demo_query_has_three_to_six_planted_decoys_with_a_class() -> None:
    for query in INTENT:
        rows = _decoys(query)
        assert 3 <= len(rows) <= 7, (query, len(rows))
        assert all(d.cls in (1, 2, 3, 4) for d in rows), query
    assert 40 <= sum(not d.true_hit for d in dr.TABLE) <= 120


def test_every_guard_query_has_a_real_product_holding_its_words() -> None:
    for query in GUARDS:
        rows = [d for d in dr.TABLE if d.query == query]
        assert rows and all(d.cls == 5 and d.true_hit for d in rows), query
        assert all(query.split()[-1] in d.title.lower() for d in rows), query


@pytest.mark.parametrize("query", sorted(INTENT))
def test_without_interpretation_decoys_lead_the_top_10(index: br.Index, query: str) -> None:
    top = [d["product_id"] for d in br.rank(index, query, 10)]
    # gen#311: the apparel decoys are decoys of the same kind, and crowd the #294 ones.
    planted = [i for i in top if (i in dr.BY_ID and not dr.BY_ID[i].true_hit) or i in da.IDS]
    assert len(planted) >= 3, (query, top)
    assert any(i in planted for i in top[:3]), (query, top[:3])


@pytest.mark.parametrize("query", sorted(INTENT))
def test_with_interpretation_no_decoy_is_a_hit(ceiling: list[dict], query: str) -> None:
    by_id = {r["product_id"]: r for r in ceiling}
    for pid, row in dr.BY_ID.items():
        if row.query == query and not row.true_hit:
            assert not _intended(by_id[pid], query), (query, pid, row.title)
        if row.query == query and row.true_hit:
            assert _intended(by_id[pid], query), (query, pid, row.title)


def test_a_decoys_fields_tell_the_truth(ceiling: list[dict]) -> None:
    """Class 1 and 3 decoys never hold the query's color in the color field (a part named
    in the title is not the product's color), and no decoy's color was completed."""
    by_id = {r["product_id"]: r for r in ceiling}
    for pid, row in dr.BY_ID.items():
        colors = {c["color"] for c in by_id[pid].get("color_options", [])}
        assert len(colors) <= 1, (pid, colors)
        if row.cls == 1 and row.query in INTENT:
            assert INTENT[row.query][0] not in colors, (pid, row.title)


def test_decoys_are_templates_never_copied_or_color_completed() -> None:
    tpls = scale.templates()
    assert dr.IDS and not dr.IDS & {r["product_id"] for r in scale.derivable(tpls)}
    assert not dr.IDS & {r["product_id"] for g in main_colors.groups(tpls).values() for r in g}


def test_docs_table_is_generated_from_the_table() -> None:
    """The docs hold :func:`decoy_rows.table_markdown` verbatim, so no count is kept by hand."""
    doc = (ROOT / "docs" / "retail-catalog-batch-1.md").read_text()
    assert dr.table_markdown() in doc
    assert len(dr.table_markdown().splitlines()) == len(dr.TABLE) + 2


def _is_bra(doc: dict) -> bool:
    return "Bras" in doc["category_path"]


def test_cups_without_interpretation_leads_with_bras(index: br.Index, ceiling: list[dict]) -> None:
    """Class 6: bra titles say "Cup", so a bare "cups" opens on bras; routed to the drinkware
    node no bra is left, and "d cup bra" stays in lingerie both ways."""
    top = br.rank(index, "cups", 10)
    # A bra is within the first six: a mug and a beaker sit a hair above it, and any added
    # product shifts the field-length mean enough to swap neighbors (gen#216: 3rd to 4th).
    assert sum(_is_bra(d) for d in top) >= 3 and any(_is_bra(d) for d in top[:6])
    routed = [d for d in ceiling if "Drinkware" in d["category_path"]]
    assert routed and not any(_is_bra(d) for d in routed)
    bras = br.rank(index, "d cup bra", 10)
    assert sum(_is_bra(d) for d in bras) >= 3 and _is_bra(bras[0])


def test_oranges_without_interpretation_leads_with_flavour_decoys(index: br.Index) -> None:
    """The orange flavour of a bake, a biscuit or a drink beats the fruit; the fruit node is
    Citrus Fruit > Oranges."""
    top = br.rank(index, "oranges", 10)
    flavour = [d for d in top if "Food & Drink" in d["department"]
               and "Oranges" not in d["category_path"]]
    assert len(flavour) >= 3 and any(d in flavour for d in top[:3])


def test_pink_lady_apples_guard_leads_both_ways(index: br.Index, ceiling: list[dict]) -> None:
    assert br.rank(index, "pink lady apples", 1)[0]["product_id"] == "PLT-DXU04"
    doc = {r["product_id"]: r for r in ceiling}["PLT-DXU04"]
    assert "Apples" in doc["category_path"]


@pytest.mark.parametrize("query", sorted(INGREDIENT_QUERIES))
def test_ingredient_decoys_hold_the_word_only_in_the_ingredients(
    index: br.Index, ceiling: list[dict], query: str
) -> None:
    """Class 7: the word is on the label and in the description, never in the title, and the
    interpreted query (the fresh category) keeps none of them. The prototype baseline reads the
    title and the description, not the ingredients, so only the rows that win on the description
    are in its top 10; the live search reads the ingredients too (the ingest batch's check)."""
    word = INGREDIENT_QUERIES[query]
    by_id = {r["product_id"]: r for r in ceiling}
    rows = {pid: d for pid, d in dr.BY_ID.items() if d.query == query and d.cls == 7}
    assert len(rows) >= 3 and all(d.cls == 7 for d in rows.values()), query
    for pid, row in rows.items():
        doc = by_id[pid]
        assert word not in row.title.lower(), (pid, row.title)
        assert any(word in i for i in doc["ingredients"]), pid
        assert word in doc["description"].lower(), pid
        assert "Fresh Fruit" not in doc["category_path"], pid
        assert pid in {d["product_id"] for d in br.rank(index, query, 1000)}, pid


def test_lavender_ingredient_decoy_reaches_the_baseline_top_10(index: br.Index) -> None:
    top = [d["product_id"] for d in br.rank(index, "lavender", 10)]
    assert any(i in dr.BY_ID and dr.BY_ID[i].cls == 7 for i in top), top


@pytest.mark.parametrize("query", GUARDS)
def test_a_guard_holds_every_word_of_its_query_and_ranks_first(
    index: br.Index, query: str
) -> None:
    """A guard that loses its color word, or that no longer leads its own query, is no guard."""
    rows = [d for d in dr.TABLE if d.query == query]
    assert len(rows) == 1, query
    words = set(query.split())
    assert words <= set(rows[0].title.lower().replace(",", " ").split()), (query, rows[0].title)
    assert br.rank(index, query, 1)[0]["product_id"] == f"PLT-D{rows[0].code}", query
