"""Every retail mug is one document filed at two category paths (gen#602).

A mug sat at ``Home > Kitchen & dining > Drinkware > Mugs`` or at ``Gifts > Mugs & drinkware``,
never both, so a shopper who browsed one tree missed the mugs of the other. A product now carries
``category_paths``: its primary ``category_path`` first, then each further path it is also filed at.
The mugs are the worked example (``docs/retail-prototype.md``, "A product at several category
paths"). The prism projection (``category_path_joined``) is the union of the cumulative paths, so
both facets count a mug once and a filter on either path finds all of them.

The decoy mugs of ``decor_rows`` (a cat ornament, a thank-you card) keep their one path: they are
there to be the wrong answer to "mug".
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decor_rows  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core import emit, standard  # noqa: E402
from synthetic_ecommerce_data.prism import index  # noqa: E402

CEILING = 10_000_000  # more SKUs than the templates reach, so ``scale.build`` runs to its ceiling
HOME = ("Home", "Kitchen & dining", "Drinkware", "Mugs")
GIFTS = ("Gifts", "Mugs & drinkware")
SEP = index.PATH_SEPARATOR
HOME_JOINED, GIFTS_JOINED = SEP.join(HOME), SEP.join(GIFTS)


@pytest.fixture(scope="module")
def documents() -> list[dict]:
    return scale.documents(scale.build(CEILING))


@pytest.fixture(scope="module")
def mugs(documents: list[dict]) -> list[dict]:
    """Every shipped document at either mug path, the decoys apart."""
    decoys = decor_rows.decoy_ids()
    return [
        d for d in documents
        if tuple(d["category_path"]) in (HOME, GIFTS) and d["product_id"] not in decoys
    ]  # fmt: skip


@pytest.fixture(scope="module")
def decoy_mugs(documents: list[dict]) -> list[dict]:
    return [
        d for d in documents
        if tuple(d["category_path"]) == HOME and d["product_id"] in decor_rows.decoy_ids()
    ]  # fmt: skip


def _paths(doc: dict) -> list[tuple[str, ...]]:
    return [tuple(p) for p in doc.get("category_paths", [])]


def test_the_build_holds_mugs_at_both_paths(mugs: list[dict]) -> None:
    roots = {tuple(d["category_path"]) for d in mugs}
    assert roots == {HOME, GIFTS}
    assert len(mugs) >= 22


def test_every_mug_is_one_document_carrying_both_paths(mugs: list[dict]) -> None:
    bad = {d["product_id"]: _paths(d) for d in mugs if set(_paths(d)) != {HOME, GIFTS}}
    assert bad == {}, f"mugs that do not carry both paths: {sorted(bad)[:5]}"
    for d in mugs:
        assert _paths(d)[0] == tuple(d["category_path"]), d["product_id"]  # the primary leads
        assert len(_paths(d)) == 2, d["product_id"]


def test_a_mug_is_listed_once(mugs: list[dict]) -> None:
    ids = [d["product_id"] for d in mugs]
    assert len(ids) == len(set(ids))


def test_the_decoy_mugs_keep_their_one_path(decoy_mugs: list[dict]) -> None:
    assert len(decoy_mugs) == 2
    assert all("category_paths" not in d for d in decoy_mugs)


def test_a_mug_document_passes_the_standard(mugs: list[dict]) -> None:
    assert [p for d in mugs[:40] for p in standard.check_document(d)] == []


def _rows(docs: list[dict]) -> list[dict]:
    return [
        index.project(r)
        for d in docs
        for r in standard.flat_documents(d, export.NUMERIC_FACTS)
    ]


def test_both_category_facets_count_each_mug_once_and_a_filter_finds_all(mugs: list[dict]) -> None:
    rows = _rows(mugs)
    for row in rows:
        joined = row[index.CATEGORY_PATH_FIELD]
        assert len(joined) == len(set(joined)), row["sku"]
        assert HOME_JOINED in joined and GIFTS_JOINED in joined, row["sku"]
    want = {d["product_id"] for d in mugs}
    for value in (HOME_JOINED, GIFTS_JOINED):
        found = {r["product_id"] for r in rows if value in r[index.CATEGORY_PATH_FIELD]}
        assert found == want, value


def test_a_single_path_row_projects_as_before() -> None:
    row = {"category_path": ["Home", "Bedding", "Duvets"]}
    assert index.project(row)[index.CATEGORY_PATH_FIELD] == [
        "Home", "Home/Bedding", "Home/Bedding/Duvets",
    ]  # fmt: skip


def test_the_projection_is_the_union_of_the_cumulative_paths() -> None:
    a, b = ["Home", "Kitchen", "Mugs"], ["Home", "Kitchen", "Cups"]
    row = {"category_path": a, "category_paths": [a, b, ["Gifts", "Mugs"]]}
    assert index.project(row)[index.CATEGORY_PATH_FIELD] == [
        "Home", "Home/Kitchen", "Home/Kitchen/Mugs", "Home/Kitchen/Cups", "Gifts", "Gifts/Mugs",
    ]  # fmt: skip


def test_both_mappings_know_the_field() -> None:
    assert "category_paths" in emit.NESTED_MAPPING["mappings"]["properties"]
    assert "category_paths" in emit.FLAT_MAPPING["mappings"]["properties"]


# --- the standard accepts a two-path product and refuses a malformed second path -------------


def _real_problems(doc: dict) -> list[str]:
    """The findings about ``category_paths`` itself: not "is not a field of the standard", which
    refuses every shape alike and would pass a check that looks at nothing."""
    return [p for p in standard.check_document(doc) if "is not a field" not in p]


@pytest.fixture(scope="module")
def two_path(mugs: list[dict]) -> dict:
    return mugs[0]


def test_a_two_path_product_passes_the_standard(two_path: dict) -> None:
    doc = {**two_path, "category_paths": [list(HOME), list(GIFTS)]}
    assert standard.check_document(doc) == []


@pytest.mark.parametrize(
    "second",
    [[], ["Gifts", ""], ["Gifts", 7], "Gifts/Mugs", list(HOME)],
    ids=["empty", "empty-node", "non-string-node", "not-a-list", "repeats-the-primary"],
)
def test_a_malformed_second_path_fails_the_standard(two_path: dict, second: object) -> None:
    doc = {**two_path, "category_paths": [list(HOME), second]}
    assert len(_real_problems(doc)) >= 1


def test_the_primary_path_must_lead(two_path: dict) -> None:
    doc = {**two_path, "category_paths": [list(GIFTS), list(HOME)]}
    assert len(_real_problems(doc)) >= 1
