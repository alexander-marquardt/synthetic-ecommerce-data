"""The retail size parameter (gen#125): a target SKU count, reached from the templates.

``prototypes/retail_drawings/scale.py`` derives styles from the hand-authored
ones until the SKUs reach the target. These tests hold it at :data:`TARGET`, the
templates plus about 4K SKUs of derived styles, and at the ceiling where every
template is exhausted: it reaches the count, stays deterministic, meets the output
standard, adds no duplicate title or clone, keeps every derived fact honest to its
template, and keeps the drawings bounded.
"""

from __future__ import annotations

import collections
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core.standard import check_catalog

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402
from retail_figures import (  # noqa: E402
    GROCERY_INTERSECTION_KEYS,
    committed,
    unheld_named_values,
)
from retail_figures import held as values_held  # noqa: E402

#: The measured totals (``golden-retail/stats.json``, gen#162): never typed here.
FIGURES = committed()
#: The round 4 preview's authored styles, then the scale-only rows (``scale_rows``),
#: then the breadth rows (``breadth_rows``), then the distractor rows (``distractor_rows``:
#: the failure classes' products), then the shirts (``shirt_rows``), then the grocery styles
#: (``grocery.build()``, gen#154), last: no style derives from a shirt or a grocery style.
SCALE_ROWS = FIGURES["templates"]["scale_rows"]["styles"]
AUTHORED = FIGURES["templates"]["authored"]["styles"]
BREADTH_ROWS = FIGURES["templates"]["breadth_rows"]["styles"]
DISTRACTOR_ROWS = FIGURES["templates"]["distractor_rows"]["styles"]
SHIRT_ROWS = FIGURES["templates"]["shirt_rows"]["styles"]
GROCERY_ROWS = FIGURES["templates"]["grocery"]["styles"]
TEMPLATES = (
    AUTHORED + SCALE_ROWS + BREADTH_ROWS + DISTRACTOR_ROWS + SHIRT_ROWS + GROCERY_ROWS
)
#: The SKUs the templates alone hold. A build at or under it takes no seeded draw, so
#: every derived-style test (``pairs``) would pass on an empty list.
TEMPLATE_SKUS = FIGURES["templates"]["all"]["skus"]
#: The derived styles :data:`TARGET` must hold so the ``pairs`` tests read a real sample:
#: round 2's 19K build held 166 (seed 0), and adding templates must not shrink it.
MIN_DERIVED = 150
#: The sample build: the templates, then derived styles to about 4.5K SKUs past them,
#: under the ceiling (:data:`CAPACITY`). It moves with
#: :data:`TEMPLATE_SKUS`, so new templates never empty it. Round 4's deep-SKU templates
#: left 4K at 148 styles, so it went up by 500.
DERIVED_SKUS = 4_500
TARGET = TEMPLATE_SKUS + DERIVED_SKUS
#: Every template exhausted, seed 0: today's ceiling (styles, SKUs). More brands per
#: type, title-visible values or templates raise it; rebuild the figures then.
CAPACITY = (FIGURES["ceiling"]["styles"], FIGURES["ceiling"]["skus"])
#: The grid-clone share the ceiling build may reach (:func:`scale.grid_clones`). The
#: measured share is in the figures: the rest is the headroom the 50K and 100K rounds may spend.
CEILING_GRID_CLONES = 0.152
#: The departments the ceiling build sells in.
DEPARTMENTS = 10
#: The near-duplicate share the ceiling build may reach: the 30K ceiling's share
#: (gen#136), rounded up to the 20K build's. Growth must not dilute it.
CEILING_NEAR_DUPLICATES = 0.028
#: The grocery styles' own near-duplicate share (``scale.distinctness`` over the GRC- styles,
#: styles): the measured share is in the figures, the cap is 4.0%. Flavors of one family share
#: most of a listing by design, so the cap is higher than the one above; it stops the share
#: growing silently.
CEILING_GROCERY_NEAR_DUPLICATES = 0.040


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    return scale.build(TARGET)


@pytest.fixture(scope="module")
def pairs(built) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """(derived style, its template) for every derived style."""
    by_id = {t["product_id"]: t for t in scale.templates()}
    return [(r, by_id[built.template_of[r["product_id"]]]) for r in built.records[TEMPLATES:]]


@pytest.fixture(scope="module")
def ceiling() -> scale.Scaled:
    """Every template exhausted: the build where most derived styles exist."""
    return scale.build(CAPACITY[1] * 2)


@pytest.fixture(scope="module")
def ceiling_pairs(ceiling) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """(derived style, its template) for every derived style of the ceiling build."""
    by_id = {t["product_id"]: t for t in scale.templates()}
    return [
        (r, by_id[ceiling.template_of[r["product_id"]]]) for r in ceiling.records[TEMPLATES:]
    ]


def test_the_size_parameter_reaches_the_target_sku_count(built):
    assert built.skus >= TARGET
    assert built.skus - built.records[-1]["sku_count"] < TARGET
    assert len(built.records) > TEMPLATES
    assert len(built.template_of) == len(built.records) - TEMPLATES


def test_the_target_leaves_the_derived_style_tests_a_sample(built, pairs):
    """New templates raise :data:`TEMPLATE_SKUS`; the pin fails until it is updated, and
    the floor fails if :data:`TARGET` is left behind it."""
    assert sum(t["sku_count"] for t in scale.templates()) == TEMPLATE_SKUS
    assert len(pairs) >= MIN_DERIVED, (len(pairs), MIN_DERIVED)


def test_the_templates_come_first_and_a_small_target_takes_a_prefix(built):
    ids = [t["product_id"] for t in scale.templates()]
    assert [r["product_id"] for r in built.records[:TEMPLATES]] == ids
    small = scale.build(100)
    assert small.template_of == {}
    assert [r["product_id"] for r in small.records] == ids[: len(small.records)]
    assert small.skus >= 100


def test_the_build_is_deterministic_by_seed():
    # TARGET, not a fixed size: a build at or under TEMPLATE_SKUS takes no seeded draw.
    a, b, c = scale.build(TARGET, seed=3), scale.build(TARGET, seed=3), scale.build(TARGET, seed=4)
    assert a.records == b.records
    assert [r["title"] for r in a.records] != [r["title"] for r in c.records]


def test_the_20k_build_meets_the_output_standard(built):
    assert check_catalog(scale.documents(built)) == []


def test_a_derived_style_adds_no_duplicate_title_and_no_twin(built, pairs):
    titles = collections.Counter(r["title"] for r in built.records)
    twins = collections.Counter(scale.twin_key(r) for r in built.records)
    assert [r["title"] for r, _ in pairs if titles[r["title"]] > 1] == []
    assert [r["product_id"] for r, _ in pairs if twins[scale.twin_key(r)] > 1] == []
    got, authored = scale.distinctness(built.records), scale.distinctness(scale.templates())
    assert (got["duplicate_titles"], got["clones"]) == (
        authored["duplicate_titles"],
        authored["clones"],
    )


def test_few_styles_share_a_results_grid_tile_with_another(built):
    """What a results grid shows is the leaf, the hero picture and the price: a style that
    shares all three with another reads as a clone whatever its brand and range name."""
    main = scale.derivable(built.records)
    report = scale.grid_clones(main)
    assert report["styles"] == len(main)
    assert report["grid_clone_rate"] <= 0.15


def test_few_styles_share_a_results_grid_tile_at_the_ceiling(ceiling):
    """Growth multiplies siblings that share a picture: the ceiling, not only the first
    load, holds the grid-clone share under :data:`CEILING_GRID_CLONES`.

    Guard: a template or pool change that clones tiles past the cap fails here. Metric: the
    ceiling's grid-clone share, in the failure message.
    """
    main = scale.derivable(ceiling.records)
    tiles = collections.Counter(scale.grid_tile(r) for r in main)
    shared = sum(n for n in tiles.values() if n > 1)
    rate = shared / len(main)
    assert scale.grid_clones(main)["grid_clones"] == shared
    assert rate <= CEILING_GRID_CLONES, f"{shared} of {len(main)} styles ({rate:.1%})"


#: The grocery grid-clone share the ceiling build may reach, with a 2-point margin over the
#: measured count in the figures; it was 96.6% (gen#154).
GROCERY_GRID_CLONES = 0.02


def test_grocery_styles_mostly_draw_a_tile_of_their_own(ceiling):
    """A grocery style's tile is its leaf, hero picture and price. The picture names the range,
    the flavor's colour and the style's flavors; the range-name text tells siblings apart,
    and the flavor band is not seen by the gate.

    Guard: this test. Metric: the grocery grid-clone share, in the failure message."""
    groc = [r for r in ceiling.records if r["product_id"].startswith(scale.GROCERY_PREFIX)]
    report = scale.grid_clones(groc)
    assert report["styles"] == GROCERY_ROWS
    assert report["grid_clones"] == FIGURES["near_duplicates"]["grocery_grid_clones"]
    rate = report["grid_clones"] / report["styles"]
    assert rate <= GROCERY_GRID_CLONES, f"{report['grid_clones']} of {GROCERY_ROWS} ({rate:.1%})"


def test_grid_clones_count_every_style_of_a_shared_tile():
    tpls = scale.templates()
    twin = dict(tpls[0], product_id="X-1", brand="Elsewhere")
    report = scale.grid_clones([tpls[0], twin, tpls[1]])
    assert (report["grid_clones"], report["largest_group"]) == (2, 2)
    assert report["grid_clone_rate"] == round(2 / 3, 4)


def test_a_leaf_a_derived_style_joins_never_holds_a_single_price(ceiling, ceiling_pairs):
    """An authored leaf may hold one price (four pyjamas at one price is the author's
    call); a derived style is never priced as its template, so its leaf gains a price."""
    per_leaf = scale.prices_per_leaf(ceiling.records)
    derived = {r["category_leaf"] for r, _ in ceiling_pairs}
    assert len(derived) >= 100
    assert [leaf for leaf in derived if per_leaf["distinct"][leaf] < 2] == []
    assert [r["product_id"] for r, t in ceiling_pairs if r["price"] == t["price"]] == []


def test_a_derived_style_differs_from_its_template_and_siblings_in_a_visible_attribute(
    built, pairs
):
    """A range name and a brand alone are not a style: each derived style changes a value
    the title shows, or the hero color family, against its template and every sibling."""
    by_tpl: dict[str, set[tuple]] = collections.defaultdict(set)
    for t in scale.templates():
        by_tpl[t["product_id"]].add(_signature(t, t))
    same = []
    for r, t in pairs:
        sig = _signature(r, t)
        if sig in by_tpl[t["product_id"]]:
            same.append((r["product_id"], r["title"]))
        by_tpl[t["product_id"]].add(sig)
    assert same == []


def _signature(rec: dict[str, Any], tpl: dict[str, Any]) -> tuple:
    shown = [a["key"] for a in tpl["attributes"]
             if a["key"] != "line" and scale._has_word(tpl["title"], str(a["value"]))]  # fmt: skip
    values = {a["key"]: str(a["value"]) for a in rec["attributes"]}
    hero = (rec.get("color_options") or [{}])[0]
    return (tuple(values[k] for k in shown), hero.get("family", hero.get("color")))


def test_a_derived_price_is_redrawn_inside_its_leafs_band(built, pairs):
    lo_f, hi_f = scale.PRICE_BAND
    band: dict[str, list[float]] = collections.defaultdict(list)
    for t in scale.templates():
        band[t["category_leaf"]].append(t["price"])
    for r, _ in pairs:
        prices = band[r["category_leaf"]]
        assert lo_f * min(prices) <= r["price"] <= hi_f * max(prices), r["product_id"]
        assert r["price"] == min(s["price"] for s in r["skus"])
    moved = sum(r["price"] != t["price"] for r, t in pairs)
    assert moved >= 0.8 * len(pairs)


def test_a_premium_value_costs_more_and_a_cheaper_one_less():
    up = scale.price_factor({"upper_material": ("Synthetic", "Leather")})
    down = scale.price_factor({"upper_material": ("Leather", "Synthetic")})
    assert down < 1.0 < up
    assert scale.price_factor({}) == 1.0
    assert scale.price_factor({"wash": ("Rinse", "Stone")}) == 1.0


def test_a_price_point_is_a_retail_one():
    assert [scale.price_point(p) for p in (1.13, 7.3, 18.2, 41.6, 263.0)] == [
        1.15,
        7.5,
        18.0,
        42.0,
        265.0,
    ]


def test_a_value_another_attribute_shares_never_varies():
    """A leather sole on a leather loafer: a swap cannot tell whose word "Leather" is."""

    def entry(key: str, value: str) -> dict[str, Any]:
        return {"key": key, "name": key.title(), "value": value}

    rec = {
        "category_path": ["Women", "Shoes", "Loafers"],
        "category_leaf": "Loafers",
        "product_type": "Loafers",
        "title": "Leather Penny Loafers",
        "description": "Hand-finished leather loafers with a round toe.",
        "attributes": [
            entry("upper_material", "Leather"),
            entry("sole", "Leather"),
            entry("toe", "Round"),
        ],  # fmt: skip
    }
    pools = {("Loafers", k): (v, v + "x") for k, v in
             (("upper_material", "Leather"), ("sole", "Leather"), ("toe", "Round"))}  # fmt: skip
    assert scale.variable_keys(rec, pools) == ["toe"]


def test_a_swap_reads_the_and_spelling_of_an_ampersand():
    text = "Easy-on trainers with two hook and loop straps."
    assert (
        scale._swap(text, "Hook & Loop", "Lace-Up") == "Easy-on trainers with two lace-up straps."
    )
    assert scale._swap("Kids' Hook & Loop Trainers", "Hook & Loop", "Buckle") == (
        "Kids' Buckle Trainers"
    )


def _changed(r: dict[str, Any], t: dict[str, Any]) -> dict[str, tuple[str, str]]:
    new = {a["key"]: str(a["value"]) for a in r["attributes"]}
    return {
        a["key"]: (str(a["value"]), new[a["key"]])
        for a in t["attributes"]
        if a["key"] != "line" and new[a["key"]] != str(a["value"])
    }


def test_a_changed_value_is_rewritten_in_the_description(pairs):
    rewritten = 0
    for r, t in pairs:
        for old, new in _changed(r, t).values():
            if not scale._has_word(t["description"], old):
                continue
            assert scale._has_word(r["description"], new), (r["product_id"], r["description"])
            assert not scale._has_word(r["description"], old), (r["product_id"], old)
            rewritten += 1
    assert rewritten >= 20


def _string_fields(drawing: dict[str, Any]) -> dict[str, str]:
    """Every string field of a drawing, ``params`` included: ``("params", p)`` or the key."""
    out: dict[Any, str] = {k: v for k, v in drawing.items() if isinstance(v, str)}
    out |= {("params", p): v for p, v in (drawing.get("params") or {}).items()
            if isinstance(v, str)}  # fmt: skip
    return out


def test_a_changed_value_is_redrawn_in_the_picture(ceiling_pairs):
    """Every string field of the drawing, top level and ``params``, follows a changed value:
    a graphic tee carries its ``motif`` at the top level, not in ``params``. It reads the
    ceiling, whose derived styles start with TARGET's: 88 motif styles to TARGET's 3."""
    redrawn = top_level = 0
    drawn = _motif_drawn()  # the drawn motif may not be the value: Cherry draws cherries
    for r, t in ceiling_pairs:
        changed = {old.lower(): new for old, new in _changed(r, t).values()}
        motif = {a["value"].lower(): a["value"] for a in t["attributes"] if a["key"] == "motif"}
        mine = _string_fields(r["drawing"])
        for p, v in _string_fields(t["drawing"]).items():
            if p in ("base", "accent", "third", "pattern", "label") or p not in mine:
                continue  # the hero swatch, the motif's ink and a duvet's tog: see their tests
            was = next(iter(motif)) if p == "motif" else v.lower()
            if was in changed:
                want = drawn[changed[was]] if p == "motif" else changed[was]
                assert mine[p].lower() == want.lower(), (r["product_id"], p)
                redrawn += 1
                top_level += not isinstance(p, tuple)
            else:
                assert mine[p] == v, (r["product_id"], p)
    assert redrawn >= 20
    assert top_level >= 1, "no style changed a top-level drawing field: the motif goes untested"


def _motif_drawn() -> dict[str, str]:
    """A ``motif`` attribute value -> the drawing motif its templates draw (Cherry: cherries)."""
    out: dict[str, str] = {}
    for t in scale.templates():
        for a in t["attributes"]:
            if a["key"] == "motif":
                motif = t["drawing"]["motif"]
                assert out.setdefault(str(a["value"]), motif) == motif
    return out


def _motif_words(value: str, drawn: str) -> set[str]:
    low = value.lower()
    return {low, drawn, f"{low}s", f"{low}es", f"{low[:-1]}ies"}


def test_a_motif_style_draws_and_describes_its_own_motif(ceiling_pairs):
    """The picture draws the motif, count and placement the attributes name, and the
    description never names the template's motif once the style changed it ("Cherry Graphic
    Mug" -> an orange one must not say "a big pair of cherries"). The ceiling build holds
    88 derived motif styles (seed 0); :data:`TARGET` holds 3."""
    from build_preview import drawing_svg  # noqa: PLC0415

    drawn = _motif_drawn()
    styles = changed = 0
    for r, t in ceiling_pairs:
        if "motif" not in r["drawing"]:
            continue
        styles += 1
        mine = {a["key"]: str(a["value"]) for a in r["attributes"]}
        theirs = {a["key"]: str(a["value"]) for a in t["attributes"]}
        d = r["drawing"]
        assert (d["motif"], str(d["count"]), d["placement"]) == (
            drawn[mine["motif"]],
            mine["motif_count"],
            mine["print_placement"],
        ), (r["product_id"], r["title"])
        # Count and placement shape the text ("one big", "scattered"): they never vary.
        assert (mine["motif_count"], mine["print_placement"]) == (
            theirs["motif_count"],
            theirs["print_placement"],
        ), r["product_id"]
        if mine["motif"] == theirs["motif"]:
            continue
        changed += 1
        old = t["drawing"]["motif"]
        assert drawing_svg(r) != drawing_svg(r | {"drawing": d | {"motif": old}}), r["product_id"]
        stale = [w for w in _motif_words(theirs["motif"], old)
                 if scale._has_word(r["description"], w)]  # fmt: skip
        assert stale == [], (r["product_id"], r["description"])
        assert scale._has_word(r["description"], mine["motif"]), (r["product_id"], r["description"])
        assert not re.search(r"\b[Aa] [aeiou]", r["description"]), r["description"]
    assert styles >= 80  # 88 at the ceiling, seed 0
    assert changed >= 75  # 86


def test_a_style_that_changes_no_shown_value_carries_its_hero_color_in_its_title(
    ceiling_pairs,
):
    """A style whose title-shown values equal its template's or an earlier sibling's differs
    from it in the hero color alone: its title says so, in the listing convention "…, Navy".
    Most are derived styles whose hero color sets them apart."""
    taken: dict[str, set[tuple]] = collections.defaultdict(set)
    for t in scale.templates():
        taken[t["product_id"]].add(_signature(t, t)[0])
    colored = []
    for r, t in ceiling_pairs:
        shown = _signature(r, t)[0]
        if shown in taken[t["product_id"]]:
            hero = (r.get("color_options") or [{}])[0].get("color")
            assert hero and r["title"].endswith(f", {hero}"), (r["product_id"], r["title"])
            colored.append(r["product_id"])
        taken[t["product_id"]].add(shown)
    assert len(colored) >= 1_000


def test_a_redrawn_print_motif_takes_its_plural_and_article():
    """A print's title says its motif in the plural, and a vowel motif takes "an": no build
    style at :data:`TARGET` reaches either, so the record is made here."""
    import copy  # noqa: PLC0415

    tpl = next(t for t in scale.templates() if t["product_id"] == "PLT-TTW-STRAWBERRY")
    rec = copy.deepcopy(tpl)
    scale._redraw_motif(rec, "Strawberry", "Orange")
    assert rec["title"] == "Oranges Print Tea Towels, Set of 2"
    assert rec["description"] == "An orange print: oranges scattered on tea towels."
    assert rec["drawing"]["motif"] == "orange"
    assert rec["drawing"]["count"] == tpl["drawing"]["count"]


def test_a_shown_in_color_is_the_hero_the_picture_draws(ceiling_pairs):
    """A sofa drawn in its Sage hero but described "Shown in cream" contradicts its picture:
    a derived description names its own hero. One derived style says it, at the ceiling and
    at :data:`TARGET` alike (seed 0)."""
    shown = 0
    for r, t in ceiling_pairs:
        if not re.search(r"\bshown in\b", t["description"], re.IGNORECASE):
            continue
        shown += 1
        hero = r["color_options"][0]["color"]
        assert f"shown in {hero.lower()}" in r["description"].lower(), r["description"]
    assert shown >= 1


def test_every_brand_in_the_build_has_a_house_style(built):
    """A brand the build adds (:data:`scale.EXTRA_BRANDS`) draws in its own declared style:
    without a row, rendering its image raises ``KeyError``."""
    import house_styles  # noqa: PLC0415

    brands = {r["brand"] for r in built.records}
    brands |= {b for pool in scale.EXTRA_BRANDS.values() for b in pool}
    assert sorted(brands - set(house_styles.HOUSE_STYLES)) == []


def test_a_smaller_build_is_a_prefix_of_a_larger_one(built, ceiling):
    """The first load and the ceiling are prefixes of one sequence, derived styles included:
    a load can grow without renaming a style it already shipped."""
    assert len(built.records) > TEMPLATES
    assert built.records == ceiling.records[: len(built.records)]


def test_a_derived_style_carries_no_bestseller_badge(pairs):
    assert [r["product_id"] for r, _ in pairs if "Bestseller" in r.get("badges", ())] == []
    assert any(r.get("badges") for r, _ in pairs)


def test_the_cli_refuses_a_target_below_one():
    done = subprocess.run(
        [sys.executable, str(RETAIL / "scale.py"), "--skus", "0"],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert done.returncode == 2
    assert "--skus must be at least 1" in done.stderr


def test_a_derived_style_keeps_its_place_and_every_value_that_names_it(pairs):
    for r, t in pairs:
        assert [r[k] for k in ("category_path", "category_leaf", "product_type", "department")] == [
            t[k] for k in ("category_path", "category_leaf", "product_type", "department")
        ]
        names = " ".join([*t["category_path"], t["product_type"]])
        frozen = scale.FROZEN_KEYS - {"line"}
        kept = {
            (a["key"], str(a["value"]))
            for a in t["attributes"]
            if a["key"] in frozen or scale._has_word(names, str(a["value"]))
        }
        assert kept <= {(a["key"], str(a["value"])) for a in r["attributes"]}, r["product_id"]
        assert [a["key"] for a in r["attributes"]] == [a["key"] for a in t["attributes"]]


def test_only_a_value_free_of_the_leaf_the_unit_and_a_longer_word_may_vary():
    def entry(key: str, value: str, **extra: Any) -> dict[str, Any]:
        return {"key": key, "name": key.title(), "value": value, **extra}

    rec = {
        "category_path": ["Women", "Jeans", "Skinny Jeans"],
        "category_leaf": "Skinny Jeans",
        "product_type": "Jeans",
        "title": "The Harrow Skinny Jeans, 2pk",
        "description": "A rinse wash skinny fit.",
        "attributes": [
            entry("leg_fit", "Skinny"),
            entry("wash", "Rinse"),
            entry("pack", "2"),
            entry("inside_leg", "30", unit_code="INH"),
            entry("audience", "Womens"),
        ],
    }
    pools = {("Skinny Jeans", a["key"]): (a["value"], a["value"] + "x") for a in rec["attributes"]}
    assert scale.variable_keys(rec, pools) == ["wash"]


def test_a_changed_value_is_rewritten_in_the_title(pairs):
    rewritten = 0
    for r, t in pairs:
        new = {a["key"]: str(a["value"]) for a in r["attributes"]}
        for a in t["attributes"]:
            old = str(a["value"])
            if a["key"] == "line" or new[a["key"]] == old or not scale._has_word(t["title"], old):
                continue
            assert scale._has_word(r["title"], new[a["key"]]), (
                r["product_id"],
                r["title"],
                new[a["key"]],
            )
            rewritten += 1
    assert rewritten > 0


def test_a_derived_style_carries_its_range_name_in_title_and_line(pairs):
    for r, _ in pairs:
        assert r["product_line"] in scale.RANGE_NAMES
        assert scale._has_word(r["title"], r["product_line"])
        lines = [a["value"] for a in r["attributes"] if a["key"] == "line"]
        assert lines in ([], [r["product_line"]])


def test_skus_are_the_templates_size_run_times_a_color_subset(pairs):
    def runs(rec: dict, skip: set[str]) -> dict[Any, list[dict]]:
        out: dict[Any, list[dict]] = collections.defaultdict(list)
        for s in rec["skus"]:
            out[s.get("color")].append(
                {k: v for k, v in s.items() if k not in ("sku", "price", *skip)}
            )
        return out

    for r, t in pairs:
        # A value the derived style changed is rewritten in its SKUs too (a shoe's upper
        # material, ``scale._sku_values``): that key differs by design.
        before = {a["key"]: a["value"] for a in t["attributes"]}
        changed = {a["key"] for a in r["attributes"] if before.get(a["key"]) != a["value"]}
        mine, theirs = runs(r, changed), runs(t, changed)
        assert mine and set(mine) <= set(theirs)
        assert all(mine[c] == theirs[c] for c in mine), r["product_id"]
        assert [s["sku"] for s in r["skus"]] == [
            f"{r['product_id']}-{n:03d}" for n in range(1, len(r["skus"]) + 1)
        ]


def test_every_leaf_keeps_products_with_a_long_tail(built):
    report = scale.coverage(built.records)
    assert report["leaves"] == len({t["category_leaf"] for t in scale.templates()})
    sizes = report["leaf_size"]
    assert sizes["min"] >= 1
    assert sizes["max"] >= 5 * sizes["median"]
    assert set(report["skus_per_style_by_department"]) == {
        str(t["department"][0]) for t in scale.templates()
    }


def test_the_drawings_stay_bounded(built):
    authored = scale.coverage(scale.templates())["images"]["distinct_drawings"]
    assert scale.coverage(built.records)["images"]["distinct_drawings"] <= 2 * authored


def test_the_cli_writes_the_report_and_the_documents(tmp_path):
    out, report = tmp_path / "retail.jsonl", tmp_path / "report.json"
    argv = ["--skus", "8000", "--out", str(out), "--report", str(report)]
    done = subprocess.run(
        [sys.executable, str(RETAIL / "scale.py"), *argv],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-2000:]
    got = json.loads(report.read_text(encoding="utf-8"))
    assert got["reached_target"] is True
    assert got["standard_problems"] == 0
    assert got["coverage"]["skus"] >= 8000
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == got["coverage"]["styles"]
    assert sum(json.loads(line)["variant_count"] for line in lines) == got["coverage"]["skus"]


def test_a_target_past_the_capacity_stops_there_and_the_cli_says_so(tmp_path):
    report = tmp_path / "report.json"
    done = subprocess.run(
        [sys.executable, str(RETAIL / "scale.py"), "--skus", "100000", "--report", str(report)],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert done.returncode == 2, done.stderr[-2000:]
    assert f"short: {CAPACITY[1]} SKUs of 100000" in done.stderr
    got = json.loads(report.read_text(encoding="utf-8"))
    assert got["reached_target"] is False
    assert got["standard_problems"] == 0
    assert (got["coverage"]["styles"], got["coverage"]["skus"]) == CAPACITY


def test_the_derivable_styles_hold_the_near_duplicate_share_at_the_ceiling(ceiling):
    """The share is read over the non-grocery styles, as the other population gates are
    (``scale.derivable``): a grocery family's flavors share most of a listing by design and
    are capped apart in ``test_the_grocery_styles_hold_their_own_near_duplicate_cap``."""
    main = scale.derivable(ceiling.records)
    rate = scale.distinctness(main)["near_duplicate_rate"]
    assert rate <= CEILING_NEAR_DUPLICATES, f"{rate:.1%} of a sample of {len(main)} styles"


def test_the_grocery_styles_hold_their_own_near_duplicate_cap(ceiling):
    """Guard: grocery's near-duplicate share (measured in the figures) stays under
    :data:`CEILING_GROCERY_NEAR_DUPLICATES` (4.0%), so it cannot grow silently.

    Read over EVERY grocery style, not the default 500 sample: the sample's draw moves with
    the style count, and adding 74 beer and orange styles moved it by over a point while the
    whole population stayed put (sampling noise of about one point at this size)."""
    groc = _grocery(ceiling.records)
    rate = scale.distinctness(groc, sample=len(groc))["near_duplicate_rate"]
    assert rate == FIGURES["near_duplicates"]["grocery"]
    assert rate <= CEILING_GROCERY_NEAR_DUPLICATES, f"{rate:.1%} of all {len(groc)} styles"


def _grocery(records):
    return [r for r in records if r["product_id"].startswith(scale.GROCERY_PREFIX)]


#: Grocery keys whose style attribute is the INTERSECTION of the SKUs' lists (what every SKU
#: is free from, may contain, or is suitable for), not the union the clothing keys use
#: (:data:`retail_figures.GROCERY_INTERSECTION_KEYS`).


def test_grocery_style_attributes_list_the_values_of_their_skus(ceiling):
    """Like-for-like with the clothing union test above. Grocery attributes are one entry per
    value (not comma-joined) and some SKU keys are lists, so values are grouped by key. The one
    exception: the allergen keys (:data:`GROCERY_INTERSECTION_KEYS`) hold the values EVERY SKU
    shares, asserted as exactly that intersection."""
    checked = 0
    wrong = []
    for r in _grocery(ceiling.records):
        style: dict[str, set[str]] = collections.defaultdict(set)
        for a in r["attributes"]:
            style[a["key"]].update(v.strip().lower() for v in str(a["value"]).split(","))
        for key, values in style.items():
            held = values_held(r, key)
            if not held:
                continue
            checked += 1
            if key in GROCERY_INTERSECTION_KEYS:
                lists = [values_held({"skus": [s]}, key) for s in r["skus"] if key in s]
                held = set.intersection(*lists)
            if values != held:
                wrong.append((r["product_id"], key, sorted(values), sorted(held)))
    assert checked >= 11_000
    assert wrong == []


#: Grocery keys a title or description may name beyond the SKUs' own values, with the measured
#: number of styles-words in the figures (ceiling, seed 0). The text names the PRODUCT
#: ("Coconut Milk", "milk chocolate"), which is not a claim about one SKU's selector or
#: allergen list; a "variety" can be the head noun of another ("Oranges" in "Blood Oranges").
#: Every other SKU-carried key (dietary) is held strictly.
GROCERY_NAMED_EXCEPTIONS = FIGURES["grocery_values"]["named_but_not_carried"]


def test_no_grocery_title_or_description_names_a_value_no_sku_carries(ceiling):
    """Like-for-like with the clothing test above, over grocery. The keys in
    :data:`GROCERY_NAMED_EXCEPTIONS` are measured and capped (an ingredient or product word is
    not an allergen or selector claim); any other SKU-carried key must have none."""
    checked, wrong = unheld_named_values(_grocery(ceiling.records))
    assert checked == FIGURES["grocery_values"]["checked"]
    assert {k: n for k, n in wrong.items() if n and k not in GROCERY_NAMED_EXCEPTIONS} == {}
    assert {k: n for k, n in wrong.items() if n > GROCERY_NAMED_EXCEPTIONS.get(k, 0)} == {}


def test_no_department_falls_under_half_its_fair_share_of_styles(ceiling):
    """A general retailer sells in every department: at the ceiling, each holds at least
    half of an even split of the styles (``breadth_rows`` keeps it there).

    Guard: a template change that starves a department fails here. Metric: the smallest
    department's share of the fair split, in the failure message.
    """
    styles = collections.Counter(scale._department(r) for r in scale.derivable(ceiling.records))
    assert len(styles) == DEPARTMENTS, sorted(styles)
    fair = sum(styles.values()) / DEPARTMENTS
    smallest, n = min(styles.items(), key=lambda kv: kv[1])
    assert n >= fair / 2, f"{smallest}: {n} styles, {n / fair:.0%} of a fair {fair:.0f}"


def test_every_scale_only_row_opens_a_leaf_or_a_title_value_its_leaf_lacked():
    """A ``scale_rows`` template adds capacity only through what the authored styles lack."""
    rows = scale.scale_rows.docs()
    assert len(rows) == SCALE_ROWS
    authored = scale.templates()[:AUTHORED]
    have = {
        (t["category_leaf"], a["key"], str(a["value"])) for t in authored for a in t["attributes"]
    }
    leaves = {t["category_leaf"] for t in authored}
    seen: set[tuple[str, str]] = set()
    for r in rows:
        if r["product_id"].startswith("FTW-"):  # a closure, toe or lining the title shows
            title = {(a["key"], str(a["value"])) for a in r["attributes"]
                     if a["key"] in ("closure", "toe", "lining")
                     and scale._has_word(r["title"], str(a["value"]))
                     and (r["category_leaf"], a["key"], str(a["value"])) not in have}  # fmt: skip
        else:
            title = {(a["key"], str(a["value"])) for a in r["attributes"]
                     if a["key"] in ("rise", "wiring")}  # fmt: skip
        assert len(title) == 1, r["product_id"]
        ((key, value),) = title
        assert r["category_leaf"] not in leaves or (r["category_leaf"], key, value) not in have, (
            r["product_id"]
        )
        assert (r["category_leaf"], value) not in seen, r["product_id"]
        seen.add((r["category_leaf"], value))


#: The ``scale_rows.FOOTWEAR`` rows (growth round 4).
FOOTWEAR_ROWS = 13


def test_a_scale_only_shoe_comes_in_a_material_its_leaf_already_sells():
    """A derived shoe rewrites its style's material but not its SKUs' (#145), so a new
    footwear row keeps to a material its leaf's authored styles carry."""
    rows = getattr(scale.scale_rows, "FOOTWEAR", ())
    assert len(rows) == FOOTWEAR_ROWS
    sold: dict[str, set[str]] = collections.defaultdict(set)
    for t in scale.templates()[:AUTHORED]:
        sold[t["category_leaf"]] |= {
            s["upper_material"] for s in t["skus"] if "upper_material" in s
        }
    for s in rows:
        d = s.doc()
        assert {k["upper_material"] for k in d["skus"]} <= sold[d["category_leaf"]], d["product_id"]


def test_a_scale_only_bra_describes_its_own_straps_and_fastening():
    """A front-fastening, sleep or bandeau bra has no three-row hook and eye back."""
    rows = scale.scale_rows
    bras = [s for s in rows.FAMILIES["Bras"] if isinstance(s, rows.Bra)]
    own = [s for s in bras if s.fitting != rows.HOOK_BACK]
    assert len(own) == 26
    for s in bras:
        (doc,) = rows.style_docs("Bras", s)
        assert f"with {s.fitting}, in " in doc["description"], s.code
    front = [s for s in own if s.kind in ("Front Fastening", "Sleep")]
    for s in front:
        (doc,) = rows.style_docs("Bras", s)
        assert "hook and eye" not in doc["description"], s.code
    assert len(front) == 3


def test_the_invented_names_are_new_and_never_repeat():
    """An extra brand already on a template adds nothing to its pool, and a repeated
    range name gives two styles the same head."""
    tpl_brands = {t["brand"] for t in scale.derivable(scale.templates())}
    extra = [b for pool in scale.EXTRA_BRANDS.values() for b in pool]
    assert len(extra) == len(set(extra))
    assert sorted(set(extra) & tpl_brands) == []
    assert len(scale.RANGE_NAMES) == len(set(scale.RANGE_NAMES))
    words = {w for b in tpl_brands | set(extra) for w in b.split()}
    assert sorted(set(scale.RANGE_NAMES) & words) == []


def test_a_color_titled_style_carries_only_its_title_color_in_every_sku(ceiling_pairs):
    """A listing whose title names a color IS that color: every SKU of a style titled
    "…, Sage" is Sage, in all its sizes."""
    seen = 0
    for r, t in ceiling_pairs:
        hero = (r.get("color_options") or [{}])[0].get("color")
        if not (hero and r["title"].endswith(f", {hero}")):
            continue
        seen += 1
        assert {s.get("color") for s in r["skus"]} == {hero}, r["product_id"]
        assert [c["color"] for c in r["color_options"]] == [hero], r["product_id"]
        sizes = {s.get("size") for s in t["skus"] if s.get("color") == hero}
        assert {s.get("size") for s in r["skus"]} == sizes, r["product_id"]
    assert seen >= 100


def test_a_duvets_drawn_tog_is_its_tog_attribute(built):
    duvets = 0
    for r in built.records:
        tog = next((str(a["value"]) for a in r["attributes"] if a["key"] == "tog"), None)
        if tog is None:
            continue
        duvets += 1
        assert r["drawing"]["label"].lower() == f"{tog} tog".lower(), r["product_id"]
    assert duvets >= 2


#: The attribute keys whose value is a word a title or description may say. A record whose
#: text names another record's value of the key (a "Herbal" title on an Assam, a "Spiral"
#: description on a Bush) contradicts its own SKUs. Add a key here when a new template
#: names one.
SAID_ATTRIBUTES = (
    "blend", "form", "variety", "fruit", "origin", "power", "charm", "flower_form", "flavor",
    "pasta_shape", "fabric", "toe", "lining",
)  # fmt: skip
#: Words that say a value without being it: (key, word) -> the values the word is true of.
#: Herbal teas are the blends that hold no tea leaf; a cone is clipped to a point and a
#: spiral is trained round a cane.
SAID_BY_WORD: dict[tuple[str, str], set[str]] = {
    ("blend", "herbal"): {"Peppermint", "Rooibos"},
    ("form", "point"): {"Cone"},
    ("form", "cane"): {"Spiral"},
}


def test_no_title_or_description_says_a_value_its_own_skus_contradict(ceiling):
    values: dict[str, set[str]] = collections.defaultdict(set)
    for r in scale.derivable(ceiling.records):
        for a in r["attributes"]:
            if a["key"] in SAID_ATTRIBUTES:
                values[a["key"]].add(str(a["value"]))
    checked = 0
    wrong = []
    for r in scale.derivable(ceiling.records):
        own = {a["key"]: str(a["value"]) for a in r["attributes"]}
        text = f"{r['title']} {r['description']}"
        for key in SAID_ATTRIBUTES:
            if key not in own:
                continue
            checked += 1
            wrong += [
                (r["product_id"], key, v, r["title"])
                for v in values[key] - {own[key]}
                if scale._has_word(text, v) and not scale._has_word(own[key], v)
            ]
        for (key, word), true_of in SAID_BY_WORD.items():
            if key in own and scale._has_word(text, word) and own[key] not in true_of:
                wrong.append((r["product_id"], key, word, r["title"]))
    assert checked >= 300
    assert wrong == []


def test_every_style_attribute_its_skus_carry_lists_exactly_their_values(ceiling):
    """A style attribute whose key its SKUs also carry (a shoe's ``upper_material``)
    lists exactly the values those SKUs hold, comma-joined: a derived shoe titled
    "Leather" whose SKUs all say canvas is refused (gen#145). Every key is compared,
    not a fixed list, so a key that becomes SKU-carried later is covered too."""
    checked = 0
    wrong = []
    for r in scale.derivable(ceiling.records):
        for a in r["attributes"]:
            sku_values = {str(s[a["key"]]).lower() for s in r["skus"] if a["key"] in s}
            if not sku_values:
                continue
            checked += 1
            style_values = {v.strip().lower() for v in str(a["value"]).split(",")}
            if style_values != sku_values:
                wrong.append((r["product_id"], a["key"], a["value"], sorted(sku_values)))
    assert checked >= 240
    assert wrong == []


def test_no_title_or_description_names_a_value_no_sku_carries(ceiling):
    """A word naming a value of a SKU-carried attribute (a shoe's ``upper_material``) in the
    title or description must be a value some SKU of that style holds: a ballet pump drawn
    in patent only is not "Leather" (gen#148). Every SKU-carried key is compared, not a fixed
    list. The color names are not the material ("Black Leather" is a color) and nor is the
    sole ("a rubber sole" on a suede boot), so both are cut from the text first."""
    vocab: dict[str, set[str]] = collections.defaultdict(set)
    for r in scale.derivable(ceiling.records):
        for a in r["attributes"]:
            if any(a["key"] in s for s in r["skus"]):
                vocab[a["key"]].update(p.strip() for p in str(a["value"]).split(","))
    checked = 0
    wrong = []
    for r in scale.derivable(ceiling.records):
        text = f"{r['title']} {r['description']}"
        for c in r.get("color_options", ()):
            text = text.replace(c["color"], " ")
        text = re.sub(r"\b[\w-]+ (?:outsole|sole)s?\b", " ", text, flags=re.IGNORECASE)
        for key, words in vocab.items():
            held = {str(s[key]).lower() for s in r["skus"] if key in s}
            if not held:
                continue
            checked += 1
            wrong += [
                (r["product_id"], key, v, sorted(held), r["title"])
                for v in sorted(words)
                if v.lower() not in held and scale._has_word(text, v)
            ]
    assert checked >= 240
    assert wrong == []


#: The nouns a title or description counts a style's SKUs in ("in 12 washes", "three
#: sizes"), each with the SKU key it counts. A count of a key the SKUs do not carry
#: ("40 Washes" on a laundry liquid counts loads) is not a SKU count and is skipped.
#: Add a noun here when a new template counts one.
COUNTED_NOUNS = {
    "wash": "color", "washes": "color", "color": "color", "colors": "color",
    "colorway": "color", "colorways": "color", "print": "color", "prints": "color",
    "shade": "color", "shades": "color", "size": "size", "sizes": "size",
    "fit": "fit", "fits": "fit", "length": "length", "lengths": "length",
}  # fmt: skip
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}  # fmt: skip
#: Words that may stand between the count and the noun and still count it: "4 leg
#: lengths". Any other word makes it a different phrase: "2 Orange print" is a pack of
#: two in one print.
COUNT_QUALIFIERS = ("leg",)
#: "in 12 washes", "in 4 leg lengths": a count, an optional qualifier, a counted noun.
COUNT_PHRASE = re.compile(
    rf"\b(\d+|{'|'.join(NUMBER_WORDS)})\s+(?:(?:{'|'.join(COUNT_QUALIFIERS)})\s+)?"
    rf"({'|'.join(COUNTED_NOUNS)})\b",
    re.I,
)


@pytest.mark.parametrize(
    ("text", "n", "restated"),
    [
        ("in 12 washes and 4 leg lengths.", 1, "in one wash and 4 leg lengths."),
        ("in 12 washes and 4 leg lengths.", 3, "in 3 washes and 4 leg lengths."),
        ("in three prints and three sizes", 2, "in two prints and three sizes"),
        ("in three prints and three sizes", 1, "in one print and three sizes"),
        ("Three Prints", 2, "Two Prints"),
        ("3 Washes", 1, "One Wash"),
        ("in four colors", 13, "in 13 colors"),
        ("five pockets, 40 minutes", 1, "five pockets, 40 minutes"),
    ],
)
def test_a_colorway_count_is_restated_in_the_templates_form(text, n, restated):
    """The derived builds reach only "one wash" and "N washes"; these reach the rest."""
    assert scale._restate_color_count(text, n) == restated


@pytest.mark.parametrize("build", ["built", "ceiling"])
def test_no_title_or_description_states_a_count_its_own_skus_contradict(build, request):
    """gen#143: a derived jeans style kept its template's "in 4 washes" with one colorway."""
    checked = 0
    wrong = []
    for r in request.getfixturevalue(build).records:
        for m in COUNT_PHRASE.finditer(f"{r['title']} {r['description']}"):
            key = COUNTED_NOUNS[m.group(2).lower()]
            if not any(key in s for s in r["skus"]):
                continue
            checked += 1
            said = m.group(1).lower()
            n = int(said) if said.isdigit() else NUMBER_WORDS[said]
            have = len({s.get(key) for s in r["skus"]})
            if n != have:
                wrong.append((r["product_id"], m.group(0), have))
    assert checked >= 200
    assert wrong == []


#: A counted noun after a single "1"/"one": the plural of a count that is one.
SINGULAR_PLURALS = ("lengths", "washes", "prints", "colors", "colorways", "shades", "sizes")
#: Words whose article follows the sound, not the letter ("an hour", "a uniform").
ARTICLE_EXCEPTIONS = {"hour", "honest", "heir", "uniform", "unit", "union", "one", "european"}


@pytest.mark.parametrize("build", ["built", "ceiling"])
def test_no_title_or_description_counts_one_of_a_plural(build, request):
    """"1 leg lengths": a template with a single length printed a plural after the 1."""
    pattern = re.compile(rf"\b(?:1|one)\s+(?:\w+\s+)?(?:{'|'.join(SINGULAR_PLURALS)})\b", re.I)
    hits = [
        (r["product_id"], m.group(0))
        for r in request.getfixturevalue(build).records
        for m in pattern.finditer(f"{r['title']} {r['description']}")
    ]
    assert not hits, hits[:5]


@pytest.mark.parametrize("build", ["built", "ceiling"])
def test_every_article_agrees_with_the_word_after_it(build, request):
    """"an pointed toe", "a almond toe": a swapped value left its old article behind."""
    pattern = re.compile(r"\b(an?)\s+([a-z]+)", re.I)
    wrong = []
    for r in request.getfixturevalue(build).records:
        for m in pattern.finditer(f"{r['title']} {r['description']}"):
            art, word = m.group(1).lower(), m.group(2).lower()
            if word in ARTICLE_EXCEPTIONS:
                continue
            if art != scale._article(word):
                wrong.append((r["product_id"], m.group(0)))
    assert not wrong, wrong[:5]


@pytest.mark.parametrize(
    ("text", "old", "new", "swapped"),
    [
        ("Courts with an pointed toe", "pointed", "almond", "Courts with an almond toe"),
        ("Courts with a round toe", "round", "almond", "Courts with an almond toe"),
        ("A round toe", "round", "pointed", "A pointed toe"),
        ("An almond toe", "almond", "round", "A round toe"),
    ],
)
def test_swap_makes_the_article_agree_with_the_new_word(text, old, new, swapped):
    assert scale._swap(text, old, new) == swapped


def test_jeggings_are_drawn_apart_from_skinny_jeans():
    from kit_garments import FITS  # noqa: PLC0415

    assert FITS["jegging"] != FITS["skinny"]


def test_the_readme_states_the_derived_sku_pin():
    readme = (ROOT / "README.md").read_text()
    m = re.search(r"plus\s+([\d,]+)\s+\(its", readme)
    assert m, "README no longer states the derived-SKU pin next to test_retail_scale.py"
    assert int(m.group(1).replace(",", "")) == DERIVED_SKUS
