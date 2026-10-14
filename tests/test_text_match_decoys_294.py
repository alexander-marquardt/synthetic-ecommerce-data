"""Text-match decoys for "chocolate without peanuts", and one canonical allergen form (gen#294).

Text search ignores "without": it scores a product that holds BOTH words highest, which is
the wrong answer. The grocery build plants three kinds of chocolate row so the failure shows
without a policy and the ingredient fields (``facets.ingredient_base``, ``facets.contains``,
``facets.may_contain``) are the one source of truth the exclusion reads:

- decoys with ``peanut`` in the title;
- decoys with no ``peanut`` anywhere in the text, only in the ingredient fields;
- right answers, some of which say "peanut-free" or "no peanuts" in the title (a word text
  search cannot tell from a peanut product) and carry no peanut in any ingredient field.

The base ingredient is ``peanuts`` (plural, gen#295). ``facets.contains`` and
``facets.may_contain`` use exactly the value ``facets.ingredient_base`` uses for the same
ingredient; an allergen that names a group of ingredients keeps its group name.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import grocery  # noqa: E402
import grocery_ingredients as gi  # noqa: E402
import scale  # noqa: E402

BASE_PEANUT = "peanuts"
FIELDS = ("ingredient_base", "contains", "may_contain")
CHOCOLATE_LEAVES = ("Chocolate Bars", "Chocolate Boxes")


@cache
def _flat() -> tuple[dict, ...]:
    return tuple(grocery.flat(grocery.documents(grocery.build(grocery.TARGET))))


@cache
def _styles() -> dict[str, dict]:
    """Per style: its title, brand, leaf and the union of each ingredient field over its SKUs."""
    out: dict[str, dict] = {}
    for r in _flat():
        s = out.setdefault(r["product_id"], {
            "title": r["title"], "description": r.get("text", ""), "brand": r["brand"],
            "leaf": r["category_leaf"], "fields": {f: set() for f in FIELDS}})
        for f in FIELDS:
            s["fields"][f] |= set(r["facets"].get(f, ()))
    return out


def _has_peanut(style: dict, fields: tuple[str, ...] = FIELDS) -> bool:
    return any(BASE_PEANUT in style["fields"][f] for f in fields)


def _chocolate() -> dict[str, dict]:
    return {p: s for p, s in _styles().items() if s["leaf"] in CHOCOLATE_LEAVES}


@pytest.mark.parametrize("field", ["contains", "may_contain"])
def test_contains_and_may_contain_use_the_ingredient_base_values(field: str) -> None:
    allowed = set(gi.BASE.values()) | set(gi.ALLERGEN_GROUPS)
    seen = {v for r in _flat() for v in r["facets"].get(field, ())}
    assert seen, field
    assert sorted(seen - allowed) == []
    assert BASE_PEANUT in seen


def test_peanut_decoys_say_peanut_in_the_title_and_hold_it_in_the_ingredients() -> None:
    decoys = {p: s for p, s in _chocolate().items() if "peanut" in s["title"].lower()
              and "free" not in s["title"].lower() and "no peanuts" not in s["title"].lower()}
    assert len(decoys) >= 8
    assert len({s["brand"] for s in decoys.values()}) >= 3
    for p, s in decoys.items():
        assert BASE_PEANUT in s["fields"]["ingredient_base"], p
        assert BASE_PEANUT in s["fields"]["contains"], p


def test_peanut_only_in_the_ingredients_decoys_say_nothing_in_the_text() -> None:
    hidden = {p: s for p, s in _chocolate().items() if "peanut" not in s["title"].lower()
              and "peanut" not in s["description"].lower()
              and BASE_PEANUT in s["fields"]["ingredient_base"]}
    assert len(hidden) >= 2, sorted(hidden)
    traces = [p for p, s in _chocolate().items() if BASE_PEANUT in s["fields"]["may_contain"]
              and BASE_PEANUT not in s["fields"]["ingredient_base"]]
    assert len(traces) >= 1


def _says_peanut_free(s: dict) -> bool:
    text = f"{s['title']} {s['description']}".lower()
    return "peanut-free" in text or "no peanuts" in text


def test_peanut_free_rows_say_so_and_the_ingredient_exclusion_keeps_them() -> None:
    free = {p: s for p, s in _chocolate().items() if _says_peanut_free(s)}
    assert len(free) >= 3, sorted(free)
    kept = {p for p, s in _chocolate().items() if not _has_peanut(s)}
    assert set(free) <= kept
    assert not [p for p, s in free.items() if _has_peanut(s)]


def test_the_ingredient_exclusion_leaves_at_least_ten_chocolate_results() -> None:
    kept = [p for p, s in _chocolate().items() if not _has_peanut(s)]
    assert len(kept) >= 10


def test_chocolate_without_peanuts_ranks_peanut_products_in_the_top_ten_without_a_policy() -> None:
    styles = _styles()
    top = br.rank(br.Index(scale.build(10**6).records), "chocolate without peanuts", 10)
    decoys = [d["product_id"] for d in top
              if d["product_id"] in styles and _has_peanut(styles[d["product_id"]])
              and styles[d["product_id"]]["leaf"] in CHOCOLATE_LEAVES]  # fmt: skip
    assert len(decoys) >= 3, [d["title"] for d in top]
    assert any(_says_peanut_free(styles[p]) for p in
               (d["product_id"] for d in top if d["product_id"] in styles))


def test_guard_rows_hold_peanuts_outside_chocolate() -> None:
    guards = {p: s for p, s in _styles().items() if s["leaf"] not in CHOCOLATE_LEAVES
              and BASE_PEANUT in s["fields"]["ingredient_base"]
              and ("peanut butter" in s["title"].lower() or "salted peanuts" in s["title"].lower())}
    assert any("peanut butter" in s["title"].lower() for s in guards.values())
    assert any("salted peanuts" in s["title"].lower() for s in guards.values())
