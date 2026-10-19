"""The grocery 50K tier (gen#376): more range names, new invented brands, every family at budget.

``grocery.build(50_000)`` used to stop short: a title is a range name plus a flavor, the 10K
build had 50 range names, and a family gave up after ``ATTEMPTS`` misses once its (range, flavor)
pairs were used. The tier draws from more range names (``grocery_rows.TIER_LINES``) and from new
invented brands per family group (``grocery_rows.TIER_BRANDS``, each a ``house_styles`` row), in a
stream of its own, so ``grocery.build()`` (the 10K build the main build uses as templates) does not
move. The tier's counts are read from ``golden-retail/stats.json``, never typed here (gen#162).
"""

from __future__ import annotations

import sys
from collections import Counter
from functools import cache
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core.standard import check_catalog

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import grocery  # noqa: E402
import grocery_rows as gr  # noqa: E402
import house_styles as hs  # noqa: E402
import real_brands  # noqa: E402
from retail_figures import committed  # noqa: E402

TIER = 50_000


@cache
def recs() -> tuple[dict, ...]:
    return tuple(grocery.build(TIER))


@cache
def docs() -> tuple[dict, ...]:
    return tuple(grocery.documents(list(recs())))


def _family(rec: dict) -> str:
    return rec["product_id"].split("-")[1]


def _new_brands() -> set[str]:
    return {b for names in gr.TIER_BRANDS.values() for b in names}


def test_the_tier_reaches_its_target_within_one_percent() -> None:
    skus = sum(r["sku_count"] for r in recs())
    assert abs(skus - TIER) <= TIER * 0.01, skus


def test_every_family_holds_its_budget_share() -> None:
    held: Counter[str] = Counter()
    for r in recs():
        held[_family(r)] += r["sku_count"]
    short = {c: (held[c], b) for c, b in grocery.budgets(TIER).items() if held[c] < b}
    assert short == {}


def test_the_tier_adds_range_names_that_are_new_and_distinct() -> None:
    assert len(gr.TIER_LINES) >= 200
    assert len(set(gr.TIER_LINES)) == len(gr.TIER_LINES)
    assert not set(gr.TIER_LINES) & set(gr.LINES)


def test_every_family_group_gets_a_new_brand() -> None:
    groups = {f.brands for f in gr.FAMILIES}
    assert groups - set(gr.TIER_BRANDS) == set()
    assert all(gr.TIER_BRANDS[g] for g in groups)


def test_each_new_brand_is_invented_owned_and_has_its_own_mark() -> None:
    names = _new_brands()
    assert len(names) >= 16
    old = {b for f in gr.FAMILIES for b in f.brands}
    assert names & old == set()
    assert [n for n in names if n not in gr.OWNERS] == []
    assert [n for n in names if n not in hs.HOUSE_STYLES] == []
    assert [n for n in names if n.lower() in {r.lower() for r in real_brands.KNOWN_REAL}] == []
    marks = Counter(s.mark for s in hs.HOUSE_STYLES.values() if s.mark != hs.NO_MARK)
    assert [n for n in names if marks[hs.HOUSE_STYLES[n].mark] != 1] == []


def test_the_tier_names_its_new_brands_and_the_10k_build_none() -> None:
    used = {r["brand"] for r in recs()}
    assert _new_brands() - used == set()
    ten = {r["brand"] for r in grocery.build()}
    assert ten & _new_brands() == set()


def test_the_10k_build_does_not_read_the_tier_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Emptying the tier's lines and brands moves no style, id or draw of ``build()``."""
    before = grocery.build()
    monkeypatch.setattr(gr, "TIER_LINES", ())
    monkeypatch.setattr(gr, "TIER_BRANDS", {})
    assert grocery.build() == before


def test_no_two_styles_are_twins() -> None:
    titles = Counter(r["title"] for r in recs())
    assert {t: n for t, n in titles.items() if n > 1} == {}


def test_one_drawing_per_style() -> None:
    images = {v["image_id"] for d in docs() for v in d["variants"]}
    assert len(images) == len(docs())


def test_the_nested_and_flat_files_meet_the_output_standard() -> None:
    assert check_catalog(docs()) == []
    rows = grocery.flat(list(docs()))
    assert len(rows) == sum(len(d["variants"]) for d in docs())
    assert all(r["category_path"] and r["title"] for r in rows)


def test_the_committed_figures_pin_the_tiers_counts() -> None:
    """``golden-retail/stats.json`` holds the tier's totals (gen#162): the build equals them."""
    tier = committed().get("grocery_tier_50k", {})
    skus = sum(r["sku_count"] for r in recs())
    assert (tier.get("styles"), tier.get("skus")) == (len(recs()), skus)
    held: Counter[str] = Counter()
    for r in recs():
        held[_family(r)] += 1
    assert {c: f["styles"] for c, f in tier.get("families", {}).items()} == dict(held)
