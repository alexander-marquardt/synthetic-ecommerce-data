"""A knitwear care cream: "cream" the product, not a shade, beside the cream jumpers (gen#309).

The knitwear depth of #314 carries the colour decoys, the jumper dress (Dresses) and the jump leads
(Home, DIY & Car). The one decoy the issue still names is a "cream" that is not a colour on a
knitwear page: a care cream for jumpers. It is a real Home product of a type with a floor of
ordinary products, its colour is the tub's (White), and only its title and description hold the
words "cream" and "jumper". The category policy (Jumpers) and the department policy drop it.
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
#: The shade words: a care cream's own colour is none of them.
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
        assert doc["category_path"][:2] == ["Home", "Laundry"], doc["category_path"]
        assert "Jumpers" not in doc["category_path"]
        colours = {a["value"].lower() for a in doc["attributes"] if a["key"] == "color"}
        assert colours and not colours & SHADES, colours
        assert doc["category_leaf"] == doc["category_path"][-1]


def test_the_new_care_type_has_ordinary_products_of_its_own(by_id: dict[str, dict]) -> None:
    leaf = {by_id[f"PLT-{r.code}"]["category_leaf"] for r in _rows()}
    assert len(leaf) == 1
    ordinary = [r for r in dpw.FLOOR if by_id[f"PLT-{r.code}"]["category_leaf"] in leaf]
    assert len(ordinary) >= 3, ordinary


def test_the_baseline_top_10_for_cream_jumper_holds_the_care_cream(ceiling: list[dict]) -> None:
    ids = {f"PLT-{r.code}" for r in _rows()}
    assert ids
    top = [d["product_id"] for d in br.rank(br.Index(ceiling), QUERY, 10)]
    assert ids & set(top), top
