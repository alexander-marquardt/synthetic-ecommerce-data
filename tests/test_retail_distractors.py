"""The retail catalog holds the distractors of three failure classes (gen#125).

On the 76K-SKU build, "mattress topper", "balloon jeans" and "petite sale" did not
fail without a policy: the catalog lacked the products that win. Each test holds that
the distractors exist, out-signal the true answers, and win the no-policy baseline
(:mod:`baseline_rank`: BM25 times popularity). The four classes that already failed
(gift bag, boat neck, bomber, cups) are held too, and so is "steak" (gen#264: steak knives
lead, beef steaks follow), so growing the catalog cannot undo them.
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
import kit  # noqa: E402
import kit_tableware  # noqa: E402
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
    assert not [d for d in top if d.get("was_price") and "petite" in d.get("size_range", ())]
    assert sum(not d.get("was_price") for d in top) == 10


def _steak_knife(doc: dict) -> bool:
    return doc["title"].lower().startswith(("steak knife", "steak knives"))


def _beef_steaks(catalog: list[dict]) -> list[dict]:
    return [d for d in catalog if d["product_type"] == "Meat" and "steak" in d["title"].lower()
            and d["category_path"][:2] == ["Food & Drink", "Meat & Fish"]]  # fmt: skip


def test_the_steak_rows_are_the_distractors_and_the_true_answers(ceiling) -> None:
    knives = [d for d in ceiling if d["product_type"] == "Cutlery" and _steak_knife(d)]
    assert len(knives) >= 6
    assert sum(len(d["title"].split()) <= 5 for d in knives) >= 2
    assert all(d["description"].lower().count("steak") >= 1 for d in knives)
    steaks = _beef_steaks(ceiling)
    cuts = {c for c in ("sirloin", "ribeye", "fillet", "rump", "chuck", "t-bone", "flank", "skirt")
            if any(c in d["title"].lower() for d in steaks)}  # fmt: skip
    assert len(cuts) == 8, cuts
    assert len(steaks) >= 6
    # Honest text: a steak title runs to four words or more and says "steak" once.
    assert all(len(d["title"].split()) >= 4 and d["title"].lower().count("steak") == 1
               for d in steaks)  # fmt: skip
    assert {d["product_id"] for d in dr.docs() if "steak" in d["title"].lower()} >= \
        {f"PLT-DSK{n:02d}" for n in range(1, 11)}  # fmt: skip
    tuna = [d for d in ceiling if "tuna steak" in d["title"].lower()]
    assert tuna and all(d["category_path"][:3] == ["Food & Drink", "Food Cupboard", "Tinned"]
                        for d in tuna)  # fmt: skip


def test_a_steak_search_without_a_policy_leads_with_knives(index) -> None:
    """A knife must lead on purpose: it is the planted demo collision (a food noun modifying a
    tool), which a policy later redirects to the beef node. If a beef steak led here, the
    collision would not exist and the policy would have nothing to fix."""
    top = br.rank(index, "steak", 20)
    first = top[0]
    assert first["department"] != ["Food & Drink"] and first["product_type"] == "Cutlery"
    # A knife leads, branded or not: the title names steak knives, not necessarily first (a
    # brand-prefixed tableware template out-sells the planted rows, and either is the collision).
    assert any(p in first["title"].lower() for p in ("steak knife", "steak knives"))
    # Steaks are in the top 20, so a policy has somewhere to send the shopper.
    assert [d for d in top if d["product_type"] == "Meat"]


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
    steak = br.rank(index, "steak", 1)
    assert steak[0]["category_path"][0] != "Food & Drink"


_FILL = kit.Fill("solid", "#123456", "#654321")


def _cutlery(**params: str) -> str:
    base = {"piece": "steak knife", "handle": "wooden", "count": "1", "edge": "serrated"}
    return kit.render("cutlery_piece", _FILL, uid="c", params={**base, **params})


def test_the_steak_tray_paints_the_records_color_and_shows_its_label() -> None:
    svg = kit.render("steak_tray", _FILL, label="Ribeye", uid="t")
    assert "#123456" in svg and "Ribeye" in svg
    assert 'class="lean"' in svg
    striped = kit.render("steak_tray", kit.Fill("stripe", "#abcdef", "#fedcba"), uid="s")
    assert "url(#fill-s)" in striped


def test_the_grill_press_is_a_slab_in_the_records_color_with_a_handle() -> None:
    svg = kit.render("grill_press", _FILL, uid="g")
    assert 'class="slab"' in svg and 'class="handle"' in svg and "#123456" in svg


def test_a_straight_edge_steak_knife_draws_differently_from_a_serrated_one() -> None:
    assert _cutlery(edge="straight") != _cutlery(edge="serrated")
    # Each steak-knife row's drawn edge is the edge its attribute states.
    for s in dr.STEAK_KNIVES:
        stated = {k: v for k, _, v in s.extra}["edge"].lower()
        assert dict(s.params)["edge"] == stated, s.code


def test_a_knife_and_fork_set_fans_forks_among_its_knives() -> None:
    fork = kit_tableware._cutlery_head("fork", 340 - 285, 1.0, "#123456")[0]
    both = _cutlery(piece="steak knife and fork", count="4")
    knives = _cutlery(piece="steak knife", count="4")
    assert fork in both and fork not in knives
    assert both.count('class="piece"') == 4


def test_the_steak_knife_rows_state_what_they_draw() -> None:
    for s in dr.STEAK_KNIVES:
        attrs = {k: v for k, _, v in s.extra}
        # The handle attribute names the handle drawn; a black one is "Black", not "Plain".
        assert attrs["handle"].lower() == dict(s.params)["handle"], s.code
        if "Black" in s.title:
            assert attrs["handle"] == "Black", s.code
        # The title's set size is the pack the row sells.
        if "Set of" in s.title:
            assert f"Set of {s.units_per_pack}" in s.title, s.code


def test_each_beef_cut_has_its_own_description(ceiling) -> None:
    cuts = ("Sirloin", "Ribeye", "Fillet", "Rump", "Chuck", "T-Bone", "Flank", "Skirt")
    by_cut: dict[str, set[str]] = {}
    for d in _beef_steaks(ceiling):
        cut = next(c for c in cuts if c in d["title"])
        by_cut.setdefault(cut, set()).add(d["description"].split(". ")[1])
    assert set(by_cut) == set(cuts)
    assert all(len(v) == 1 for v in by_cut.values()), by_cut
    assert len({next(iter(v)) for v in by_cut.values()}) == 8
