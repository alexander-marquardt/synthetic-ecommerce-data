"""The retail catalog holds the distractors of three failure classes (gen#125).

On the 76K-SKU build, "mattress topper", "balloon jeans" and "petite sale" did not
fail without a policy: the catalog lacked the products that win. Each test holds that
the distractors exist, out-signal the true answers, and win the no-policy baseline
(:mod:`baseline_rank`: BM25 times popularity). The four classes that already failed
(gift bag, boat neck, bomber, cups) are held too, so growing the catalog cannot undo them.
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
import distractor_rows as dr  # noqa: E402
import scale  # noqa: E402


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _templates(**match: str) -> list[dict]:
    return [t for t in scale.templates() if all(t.get(k) == v for k, v in match.items())]


def _out_signals(distractors: list[dict], answers: list[dict]) -> None:
    assert distractors and answers
    for key in ("sold_last_5_days", "review_count"):
        assert min(d[key] for d in distractors) > max(a.get(key, 0) for a in answers), key


def test_the_mattress_siblings_out_sell_every_topper() -> None:
    new = {s.code: s.doc() for s in dr.STYLES}
    kinds = [d for d in new.values() if d["product_type"] != "Mattress Topper"
             and d["category_path"][1] == "Bedding"]  # fmt: skip
    protectors = [d for d in kinds if d["product_type"] == "Mattress Protector"]
    assert (len(protectors), len([d for d in kinds if d["product_type"] == "Mattress"]),
            len([d for d in kinds if d["product_type"] == "Pillow Protector"])) == (24, 8, 6)
    assert sum("topper" in d["title"].lower() for d in protectors) == 6
    toppers = _templates(product_type="Mattress Topper")
    assert len(toppers) >= 12
    _out_signals(kinds, toppers)


def test_a_mattress_topper_search_without_a_policy_leads_with_protectors(index) -> None:
    top = br.rank(index, "mattress topper", 10)
    assert {d["product_type"] for d in top} == {"Mattress Protector"}
    assert not any(d["product_type"] == "Mattress Topper" for d in top)


def test_the_barrels_out_sell_the_balloon_jeans_and_say_balloon() -> None:
    barrels = [d for d in (s.doc() for s in dr.STYLES) if d.get("leg_style") == "barrel"]
    assert len(barrels) == 19
    assert sum(d["audience"] == "kids" for d in barrels) == 4
    assert sum(d["product_type"] == "Trousers" for d in barrels) == 3
    assert all("balloon" in d["description"].lower() for d in barrels)
    balloons = [t for t in scale.templates() if t.get("leg_style") == "balloon"]
    assert len(balloons) >= 6
    assert len(barrels) > 2 * len(balloons)
    _out_signals(barrels, balloons)


def test_a_balloon_jeans_search_without_a_policy_returns_barrels_first(index) -> None:
    top = br.rank(index, "balloon jeans", 10)
    assert [d["leg_style"] for d in top].count("barrel") == 10


def test_petite_is_a_substantial_set_with_a_minority_on_sale(ceiling) -> None:
    petite = [d for d in ceiling if "petite" in d.get("size_range", ())]
    assert len(petite) >= 150
    assert sum(d["sku_count"] for d in petite) >= 2000
    on_sale = [d for d in petite if d.get("was_price")]
    assert 0.1 < len(on_sale) / len(petite) < 0.25


def test_sale_items_outside_petite_never_say_petite(ceiling) -> None:
    sale = [d for d in ceiling if d.get("was_price") and "petite" not in d.get("size_range", ())]
    assert len(sale) >= 60
    assert not [d["product_id"] for d in sale
                if "petite" in f"{d['title']} {d['description']}".lower()]  # fmt: skip


def test_a_petite_sale_search_without_a_policy_shows_nothing_both_petite_and_on_sale(index) -> None:
    top = br.rank(index, "petite sale", 10)
    # Without a policy the ranker cannot honour the pair. A derived style that happens to be
    # both (one seeded draw in the ceiling build) may reach the ten; it never leads them, and
    # the sale state does not drive the order (gen#275 moved the draw).
    both = [d for d in top if d.get("was_price") and "petite" in d.get("size_range", ())]
    assert len(both) <= 1 and top[0] not in both
    assert sum(not d.get("was_price") for d in top) >= 9


def test_the_new_rows_are_deterministic() -> None:
    assert [s.doc() for s in dr.STYLES] == [s.doc() for s in dr.STYLES]
    assert dr.docs() == dr.docs()
    assert len({s.code for s in dr.STYLES}) == len(dr.STYLES)
    a, b = scale.build(10**6, seed=0).records, scale.build(10**6, seed=0).records
    assert a == b
    ix = br.Index(a)
    assert [d["product_id"] for d in br.rank(ix, "petite sale")] == \
        [d["product_id"] for d in br.rank(ix, "petite sale")]  # fmt: skip


def test_the_classes_that_already_failed_still_fail_without_a_policy(index) -> None:
    gift = br.rank(index, "gift bag", 10)
    # A Gift Wrap item that is a bag is the class; a wrap roll is not.
    assert not [d for d in gift if d["category_path"][1] == "Gift Wrap"
                and "bag" in d["title"].lower()]  # fmt: skip
    boat = br.rank(index, "womens boat neck top", 3)
    assert not [d for d in boat if d.get("neckline") in ("boat", "slash")]
    bomber = br.rank(index, "check contrast bomber jacket", 3)
    assert not [d for d in bomber if d["product_type"] == "Bomber Jacket"
                and d.get("pattern") == "check"]  # fmt: skip
    cups = br.rank(index, "cups", 3)
    # Asserts only: a Bra is still in the top 3, so the class still fails (the grocery fold
    # put a Mug first, so the exact list is not pinned).
    assert "Bra" in [d["product_type"] for d in cups]
