"""The retail build's measured totals (gen#162, gen#536).

A total the retail build measures (styles, SKUs, a department's or a grocery family's
styles, the grocery attribute-value counts, the near-duplicate rate) moves with every
grocery or type pull request. Typed into a test, the README or a docstring, it put every
such PR on the same lines; committed as ``golden-retail/stats.json`` it put every PR on that
file (gen#373 rolled it at the merge, and a merge that did not roll it left main red).

Nothing is committed now. A test reads a total with :func:`figures`, which measures the
current tree (seed 0, every template exhausted) once for the test run: one measurement shared
by every pytest worker through the directory ``RETAIL_FIGURES_CACHE`` names (``conftest.py``
makes it for the run), and the session fixture ``retail_figures_measured`` hands the result to
a test that wants it as an argument. ``scripts/build_derived.py`` writes the same figures to
``stats.json`` and ``docs/figures.md`` as a CI artifact.

What stays in a test is an invariant, not a total: no twins in a family, every allergen
derived from the ingredients, and a cap such as ``CEILING_NEAR_DUPLICATES``.
"""

from __future__ import annotations

import collections
import fcntl
import json
import os
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import accessory_rows  # noqa: E402
import appliance_rows  # noqa: E402
import breadth_rows  # noqa: E402
import color_word_brand_rows  # noqa: E402
import colorgroup_rows  # noqa: E402
import cups_plural_rows  # noqa: E402
import decor_rows  # noqa: E402
import decoy_apparel  # noqa: E402
import decoy_product_words  # noqa: E402
import decoy_rows  # noqa: E402
import distractor_rows  # noqa: E402
import export  # noqa: E402
import garden_rows  # noqa: E402
import grocery  # noqa: E402
import household_rows  # noqa: E402
import knitwear_rows  # noqa: E402
import lighting_rows  # noqa: E402
import lowerbody_rows  # noqa: E402
import main_colors  # noqa: E402
import mens_depth_rows  # noqa: E402
import neckline_rows  # noqa: E402
import needs_rows  # noqa: E402
import nike_rows  # noqa: E402
import scale  # noqa: E402
import scale_rows  # noqa: E402
import school_rows  # noqa: E402
import seasonal_rows  # noqa: E402
import shirt_rows  # noqa: E402
import sofa_rows  # noqa: E402
import sports_rows  # noqa: E402
import thin_leaf_rows  # noqa: E402
import toys_rows  # noqa: E402
import type_registry  # noqa: E402
import underwear_rows  # noqa: E402
import womens_depth_rows  # noqa: E402
from build_preview4 import samples  # noqa: E402

#: The directory the pytest workers of one run share their one measurement through.
CACHE_ENV = "RETAIL_FIGURES_CACHE"
#: More SKUs than the templates can reach, so ``scale.build`` runs to its ceiling.
EXHAUST = 10_000_000
#: The grocery tier whose totals are pinned (``grocery.build`` past ``grocery.TARGET``, gen#376).
TIER_SKUS = 50_000

#: Grocery keys whose style attribute is the INTERSECTION of the SKUs' lists, not the union.
GROCERY_INTERSECTION_KEYS = ("dietary", "may_contain")


_MEMO: dict[str, Any] = {}


def figures() -> dict[str, Any]:
    """The figures of this tree's build: what a test or a doc points at instead of restating.

    Measured once per process, and once per pytest run when ``RETAIL_FIGURES_CACHE`` names a
    directory: the workers take a lock there, the first measures and writes ``figures.json``,
    the others read it.
    """
    if "figures" not in _MEMO:
        cache = os.environ.get(CACHE_ENV)
        if not cache:
            _MEMO["figures"] = measure()
        else:
            with open(Path(cache) / "lock", "a+") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                shared = Path(cache) / "figures.json"
                if not shared.is_file():
                    shared.write_text(render(measure()), encoding="utf-8")
                _MEMO["figures"] = json.loads(shared.read_text("utf-8"))
    return _MEMO["figures"]


def grocery_records(records: list[dict]) -> list[dict]:
    return [r for r in records if r["product_id"].startswith(scale.GROCERY_PREFIX)]


def held(style: dict, key: str) -> set[str]:
    """The lowercased values of ``key`` over a style's SKUs (a list-valued key is flattened)."""
    return {
        str(x).lower()
        for s in style["skus"]
        if key in s
        for x in (s[key] if isinstance(s[key], (list, tuple)) else [s[key]])
    }


def unheld_named_values(groc: list[dict]) -> tuple[int, collections.Counter[str]]:
    """``(keys checked, by key: words a title or description names that no SKU carries)``."""
    vocab: dict[str, set[str]] = collections.defaultdict(set)
    for r in groc:
        for a in r["attributes"]:
            if any(a["key"] in s for s in r["skus"]):
                vocab[a["key"]].update(p.strip() for p in str(a["value"]).split(","))
    checked = 0
    wrong: collections.Counter[str] = collections.Counter()
    for r in groc:
        text = f"{r['title']} {r['description']}"
        for key, words in vocab.items():
            have = held(r, key)
            if not have:
                continue
            checked += 1
            unheld = (v for v in words if v.lower() not in have)
            wrong[key] += sum(1 for v in unheld if scale._has_word(text, v))
    return checked, wrong


def _count(records: list[dict]) -> dict[str, int]:
    return {"styles": len(records), "skus": sum(r["sku_count"] for r in records)}


def tier_figures() -> dict[str, Any]:
    """The grocery 50K tier's totals (gen#376): ``grocery.build(50_000)``, seed 0, by family."""
    recs = grocery.build(TIER_SKUS)
    families: dict[str, list[dict]] = collections.defaultdict(list)
    for r in recs:
        families[r["product_id"].split("-")[1]].append(r)
    return {
        **_count(recs),
        "brands": len({r["brand"] for r in recs}),
        "families": {code: _count(rs) for code, rs in sorted(families.items())},
    }


def measure() -> dict[str, Any]:
    """Every total, from the seed-0 build run to its ceiling."""
    authored = [r for recs in samples().values() for r in recs]
    parts = {
        "authored": authored,
        "scale_rows": scale_rows.docs(),
        "breadth_rows": breadth_rows.docs(),
        "distractor_rows": distractor_rows.docs(),
        "decoy_rows": decoy_rows.docs(),
        "decoy_product_words": decoy_product_words.docs(),
        "shirt_rows": shirt_rows.docs(),
        "accessory_rows": accessory_rows.docs(),
        "sports_rows": sports_rows.docs(),
        "garden_rows": garden_rows.docs(),
        "decor_rows": decor_rows.docs(),
        "school_rows": school_rows.docs(),
        "household_rows": household_rows.docs(),
        "lowerbody_rows": lowerbody_rows.docs(),
        "lighting_rows": lighting_rows.docs(),
        "sofa_rows": sofa_rows.docs(),
        "appliance_rows": appliance_rows.docs(),
        "underwear_rows": underwear_rows.docs(),
        "toys_rows": toys_rows.docs(),
        "seasonal_rows": seasonal_rows.docs(),
        "colorgroup_rows": colorgroup_rows.docs(),
        "mens_depth_rows": mens_depth_rows.docs(),
        "womens_depth_rows": womens_depth_rows.docs(),
        "color_word_brand_rows": color_word_brand_rows.docs(),
        "knitwear_rows": knitwear_rows.docs(),
        "neckline_rows": neckline_rows.docs(),
        "thin_leaf_rows": thin_leaf_rows.docs(),
        "needs_rows": needs_rows.docs(),
        "cups_plural_rows": cups_plural_rows.docs(),
        "nike_rows": nike_rows.docs(),
        "type_specs": type_registry.docs(),
        "decoy_apparel": [r for r in scale.templates(baseline=False)
                          if r["product_id"] in decoy_apparel.IDS],
        "plain_rows": [r for r in main_colors.author_plain(scale.templates(baseline=False))
                       if r["product_id"] in {p[1] for p in main_colors.PLAIN_STYLES}],
        "grocery": grocery.build(),
    }
    ceiling = scale.build(EXHAUST)
    main = scale.derivable(ceiling.records)
    groc = grocery_records(ceiling.records)
    food = [r for r in ceiling.records if r["department"][0] == "Food & Drink"]
    families: dict[str, list[dict]] = collections.defaultdict(list)
    for r in groc:
        families[r["product_id"].split("-")[1]].append(r)
    departments = collections.Counter(scale._department(r) for r in main)
    templates = scale.templates()
    before_grocery = templates[: len(templates) - len(parts["grocery"])]
    main_food = [r for r in before_grocery if r["department"][0] == "Food & Drink"]
    checked, wrong = unheld_named_values(groc)
    images = {export.image_id(r, s) for r in ceiling.records for s in r["skus"]}
    return {
        "templates": {
            **{name: _count(recs) for name, recs in parts.items()},
            "all": _count(templates),
            "authored_images": len({export.image_id(r, s) for r in authored for s in r["skus"]}),
            "before_grocery": _count(before_grocery),
            "main_food": _count(main_food),
        },
        "ceiling": {
            **_count(ceiling.records),
            "derived_styles": len(ceiling.template_of),
            "images": len(images),
            "non_grocery": _count(main),
            "grocery": _count(groc),
            "food_and_drink": _count(food),
            # The store's departments are the top level of the category tree (gen#281).
            "top_levels": {
                root: _count([r for r in ceiling.records if r["category_path"][0] == root])
                for root in sorted({r["category_path"][0] for r in ceiling.records})
            },
        },
        "departments": dict(sorted(departments.items())),
        "grocery_families": {code: _count(recs) for code, recs in sorted(families.items())},
        "grocery_values": {
            "checked": checked,
            "named_but_not_carried": dict(sorted((k, n) for k, n in wrong.items() if n)),
        },
        "grocery_tier_50k": tier_figures(),
        "near_duplicates": {
            "non_grocery": scale.distinctness(main, sample=len(main))["near_duplicate_rate"],
            "grocery": scale.distinctness(groc, sample=len(groc))["near_duplicate_rate"],
            "non_grocery_grid_clone_rate": scale.grid_clones(main)["grid_clone_rate"],
            "grocery_grid_clones": scale.grid_clones(groc)["grid_clones"],
        },
    }


def render(figures: dict[str, Any]) -> str:
    return json.dumps(figures, indent=1, sort_keys=True) + "\n"


def markdown(data: dict[str, Any]) -> str:
    """``docs/figures.md``: the figures as a page, built with the stats and never committed."""
    ceiling = data["ceiling"]

    def row(name: str, count: dict[str, int]) -> str:
        return f"| {name} | {count['styles']:,} | {count['skus']:,} |"

    lines = [
        "# Retail build figures",
        "",
        "Generated by `scripts/build_derived.py` from the tree's seed-0 build run to its ceiling.",
        "CI uploads it with `stats.json` as the `derived` artifact; it is not committed (gen#536).",
        "",
        "## The ceiling build",
        "",
        "| Figure | Styles | SKUs |",
        "|---|---:|---:|",
        row("Whole build", ceiling),
        row("Non-grocery", ceiling["non_grocery"]),
        row("Grocery", ceiling["grocery"]),
        row("Food and drink", ceiling["food_and_drink"]),
        "",
        f"Derived styles: {ceiling['derived_styles']:,}. Distinct images: {ceiling['images']:,}.",
        "",
        "## Top-level departments",
        "",
        "| Department | Styles | SKUs |",
        "|---|---:|---:|",
        *(row(name, count) for name, count in ceiling["top_levels"].items()),
        "",
        "## Templates",
        "",
        "| Template set | Styles | SKUs |",
        "|---|---:|---:|",
        *(
            row(name, count)
            for name, count in data["templates"].items()
            if isinstance(count, dict)
        ),
        "",
        "## Near-duplicates",
        "",
        "| Measure | Value |",
        "|---|---:|",
        *(f"| {name} | {value} |" for name, value in data["near_duplicates"].items()),
        "",
    ]
    return "\n".join(lines)
