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

:func:`ceiling` is the build those figures measure, shared the same way (gen#539). In CI the
``ceiling-catalogue`` job fills that directory once per run (``scripts/build_ceiling.py``) and
every shard downloads it, so no test worker measures or builds.

What stays in a test is an invariant, not a total: no twins in a family, every allergen
derived from the ingredients, and a cap such as ``CEILING_NEAR_DUPLICATES``.
"""

from __future__ import annotations

import collections
import fcntl
import json
import os
import pickle
from pathlib import Path
from typing import Any

from synthetic_ecommerce_data.domains.retail import (
    collision_words,
    decoy_apparel,
    export,
    grocery,
    kit,
    main_colors,
    scale,
    type_registry,
)
from synthetic_ecommerce_data.domains.retail.build_preview4 import samples

HERE = Path(__file__).resolve().parent


#: The directory the pytest workers of one run share their one measurement through.
CACHE_ENV = "RETAIL_FIGURES_CACHE"
#: The two files a measurement leaves in that directory, and ``ceiling-catalogue`` uploads.
FIGURES_FILE = "figures.json"
CEILING_FILE = "ceiling.pickle"
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
                shared = Path(cache) / FIGURES_FILE
                if not shared.is_file():
                    shared.write_text(render(measure()), encoding="utf-8")
                _MEMO["figures"] = json.loads(shared.read_text("utf-8"))
    return _MEMO["figures"]


def ceiling() -> scale.Scaled:
    """Every template exhausted (seed 0): the build where most derived styles exist.

    Built once per process, and once per pytest run or CI run when ``RETAIL_FIGURES_CACHE`` names
    a directory, as :func:`figures` does. The directory holds a pickle because the build's tuples
    do not survive JSON, and it comes from this run on this tree. Its lock is its own:
    :func:`measure` asks for this build while :func:`figures` holds that one.

    Every caller shares one object: a test reads it and never edits it.
    """
    if "ceiling" not in _MEMO:
        cache = os.environ.get(CACHE_ENV)
        if not cache:
            _MEMO["ceiling"] = scale.build(EXHAUST)
        else:
            with open(Path(cache) / "ceiling.lock", "a+") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                shared = Path(cache) / CEILING_FILE
                if not shared.is_file():
                    shared.write_bytes(pickle.dumps(scale.build(EXHAUST), pickle.HIGHEST_PROTOCOL))
                _MEMO["ceiling"] = pickle.loads(shared.read_bytes())
            # The pickle imports no row module, so the shapes it draws are not registered yet.
            kit.register_all()
    return _MEMO["ceiling"]


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
        # Every row module and the specs, by name, in build order (gen#413).
        **{
            name: (
                type_registry.docs(skip={r["product_id"] for r in authored})
                if name == type_registry.SPEC_SOURCE
                else scale.source_docs(name)
            )
            for name in type_registry.BUILD_SOURCES[1:-1]
        },
        "decoy_apparel": [r for r in scale.templates(baseline=False)
                          if r["product_id"] in decoy_apparel.IDS],
        "plain_rows": [r for r in main_colors.author_plain(scale.templates(baseline=False))
                       if r["product_id"] in {p[1] for p in main_colors.PLAIN_STYLES}],
        "grocery": grocery.build(),
    }
    built = ceiling()
    main = scale.derivable(built.records)
    groc = grocery_records(built.records)
    food = [r for r in built.records if r["department"][0] == "Food & Drink"]
    families: dict[str, list[dict]] = collections.defaultdict(list)
    for r in groc:
        families[r["product_id"].split("-")[1]].append(r)
    departments = collections.Counter(scale._department(r) for r in main)
    templates = scale.templates()
    before_grocery = templates[: len(templates) - len(parts["grocery"])]
    main_food = [r for r in before_grocery if r["department"][0] == "Food & Drink"]
    checked, wrong = unheld_named_values(groc)
    drawings = {export.drawing_id(r, s) for r in built.records for s in r["skus"]}
    return {
        "templates": {
            **{name: _count(recs) for name, recs in parts.items()},
            "all": _count(templates),
            "authored_drawings": len(
                {export.drawing_id(r, s) for r in authored for s in r["skus"]}
            ),
            "before_grocery": _count(before_grocery),
            "main_food": _count(main_food),
        },
        "ceiling": {
            **_count(built.records),
            "derived_styles": len(built.template_of),
            "drawings": len(drawings),
            "non_grocery": _count(main),
            "grocery": _count(groc),
            "food_and_drink": _count(food),
            # The store's departments are the top level of the category tree (gen#281).
            "top_levels": {
                root: _count([r for r in built.records if r["category_path"][0] == root])
                for root in sorted({r["category_path"][0] for r in built.records})
            },
        },
        # Styles per sense of each collision word, over the templates (gen#273).
        "collision_words": collision_words.count(templates),
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
        f"Derived styles: {ceiling['derived_styles']:,}. "
        f"Distinct drawings: {ceiling['drawings']:,}.",
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
