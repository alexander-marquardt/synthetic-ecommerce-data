"""A knitwear care cream: "cream" the product, not a shade, beside the cream jumpers (gen#309).

The knitwear depth of #314 carries the color decoys, the jumper dress (Dresses) and the jump leads
(Home, DIY & Car). The one decoy the issue still names is a "cream" that is not a color on a
knitwear page: a care cream for jumpers. It is a real laundry product of an existing type with
ordinary products of its own, its color is the tub's (White), and only its title and description
hold the words "cream" and "jumper". The category policy (Jumpers) and the department policy drop
it.
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
import decoy_product_words as dpw  # noqa: E402
import scale  # noqa: E402
from distractors import tokens  # noqa: E402

QUERY = "cream jumper"
#: The shade words: a care cream's own color is none of them.
SHADES = {"cream", "ivory", "off white", "ecru"}


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


def _rows() -> list:
    return [r for r in dpw.TABLE if r.query == QUERY]


def test_a_care_cream_decoy_targets_cream_jumper() -> None:
    rows = _rows()
    assert rows, "no class 8 decoy targets 'cream jumper'"
    assert all(r.noun == "jumper" and r.policy == "category" and r.cross for r in rows)


def test_its_words_say_cream_and_jumper_and_its_fields_say_a_home_care_product(
    by_id: dict[str, dict],
) -> None:
    rows = _rows()
    assert rows
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        words = set(tokens(doc["title"]))
        assert {"cream", "jumper"} <= words, doc["title"]
        assert doc["category_path"][:2] == ["Cleaning", "Laundry"], doc["category_path"]
        assert "Jumpers" not in doc["category_path"]
        colors = {c["color"].lower() for c in doc["color_options"]}
        assert colors and not colors & SHADES, colors
        assert doc["category_leaf"] == doc["category_path"][-1]


def test_the_new_care_type_has_ordinary_products_of_its_own(by_id: dict[str, dict]) -> None:
    """The cream sits in a type that already exists with ordinary products (no new type)."""
    ids = {f"PLT-{r.code}" for r in _rows()}
    paths = {tuple(by_id[i]["category_path"]) for i in ids}
    assert len(paths) == 1
    ordinary = [i for i, d in by_id.items() if tuple(d["category_path"]) in paths and i not in ids]
    assert len(ordinary) >= 3, ordinary


def test_the_baseline_top_10_for_cream_jumper_holds_the_care_cream(ceiling: list[dict]) -> None:
    ids = {f"PLT-{r.code}" for r in _rows()}
    assert ids
    top = [d["product_id"] for d in br.rank(br.Index(ceiling), QUERY, 10)]
    assert ids & set(top), top
