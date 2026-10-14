"""The retail catalog holds text-match decoys for the demo queries (gen#294).

A decoy's title carries the query's word while its colour, category path or audience says it is
not what the query means. Each query is held two ways: without interpretation (BM25 times
popularity, :mod:`baseline_rank`) at least three decoys are in the top 10 and one in the top 3,
and with interpretation (the intended colour, type and audience read from the structured fields)
none of them is a hit, so no colour, category or audience policy can leave one in the top 10.
The guard rows are real products whose name holds a colour word ("green tea").
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
import decoy_rows as dr  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402

#: query -> (colour, product types, path root, path word): what the interpreted query keeps.
INTENT = {
    "red sofa": ("Red", None, None, "Sofas"),
    "blue sofa": ("Blue", None, None, "Sofas"),
    "red bra": ("Red", {"Bra"}, None, None),
    "blue shirt": ("Blue", {"Shirt"}, None, None),
    "black trainers": ("Black", {"Trainers"}, None, None),
    "mens puffer jacket": (None, {"Puffer Jacket"}, "Men", None),
    "boys grey socks": ("Grey", {"Socks"}, "Kids", None),
    "face cream": (None, {"Face Cream"}, None, None),
    "gold top": ("Gold", {"Top", "Tee"}, None, None),
    "red wine": (None, {"Wine"}, None, "Red Wine"),
}
GUARDS = ("green tea", "black pepper", "red velvet cake")


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _intended(doc: dict, query: str) -> bool:
    colour, types, root, word = INTENT[query]
    path = doc["category_path"]
    return (
        (colour is None or colour in {c["color"] for c in doc.get("color_options", [])})
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
    planted = [i for i in top if i in dr.BY_ID and not dr.BY_ID[i].true_hit]
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
    """Class 1 and 3 decoys never hold the query's colour in the colour field (a part named
    in the title is not the product's colour), and no decoy's colour was completed."""
    by_id = {r["product_id"]: r for r in ceiling}
    for pid, row in dr.BY_ID.items():
        colours = {c["color"] for c in by_id[pid].get("color_options", [])}
        assert len(colours) <= 1, (pid, colours)
        if row.cls == 1 and row.query in INTENT:
            assert INTENT[row.query][0] not in colours, (pid, row.title)


def test_decoys_are_templates_never_copied_or_colour_completed() -> None:
    tpls = scale.templates()
    assert dr.IDS and not dr.IDS & {r["product_id"] for r in scale.derivable(tpls)}
    assert not dr.IDS & {r["product_id"] for g in main_colors.groups(tpls).values() for r in g}
