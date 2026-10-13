"""The retail build's measured totals, written to ``golden-retail/stats.json`` (gen#162).

A total the retail build measures (styles, SKUs, a department's or a grocery family's
styles, the grocery attribute-value counts, the near-duplicate rate) moves with every
grocery or type pull request. Typed into a test, the README or a docstring, it put every
such PR on the same lines, so each conflicted with the last to merge and had to be
re-measured by hand. The industrial catalog solved this in #115 (``figures`` in
``golden-catalog/stats.json``); this is the Retail half.

``python3 prototypes/retail_drawings/retail_figures.py`` rebuilds the file (seed 0, every
template exhausted). ``tests/test_retail_figures_162.py`` rebuilds it too and compares,
so a total that moves reds there naming that command, and refuses a test or doc that
restates one. A test reads a total with :func:`committed`.

What stays in a test is an invariant, not a total: no twins in a family, every allergen
derived from the ingredients, and a cap such as ``CEILING_NEAR_DUPLICATES``.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import appliance_rows  # noqa: E402
import breadth_rows  # noqa: E402
import distractor_rows  # noqa: E402
import export  # noqa: E402
import grocery  # noqa: E402
import household_rows  # noqa: E402
import lighting_rows  # noqa: E402
import lowerbody_rows  # noqa: E402
import scale  # noqa: E402
import scale_rows  # noqa: E402
import seasonal_rows  # noqa: E402
import shirt_rows  # noqa: E402
import sofa_rows  # noqa: E402
import toys_rows  # noqa: E402
import underwear_rows  # noqa: E402
from build_preview4 import samples  # noqa: E402

STATS = HERE.parents[1] / "golden-retail" / "stats.json"
REBUILD = "python3 prototypes/retail_drawings/retail_figures.py"
#: More SKUs than the templates can reach, so ``scale.build`` runs to its ceiling.
EXHAUST = 10_000_000

#: Grocery keys whose style attribute is the INTERSECTION of the SKUs' lists, not the union.
GROCERY_INTERSECTION_KEYS = ("dietary", "may_contain")


def committed() -> dict[str, Any]:
    """The committed figures: what a test or a doc points at instead of restating."""
    return json.loads(STATS.read_text("utf-8"))


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


def measure() -> dict[str, Any]:
    """Every total, from the seed-0 build run to its ceiling."""
    authored = [r for recs in samples().values() for r in recs]
    parts = {
        "authored": authored,
        "scale_rows": scale_rows.docs(),
        "breadth_rows": breadth_rows.docs(),
        "distractor_rows": distractor_rows.docs(),
        "shirt_rows": shirt_rows.docs(),
        "household_rows": household_rows.docs(),
        "lowerbody_rows": lowerbody_rows.docs(),
        "lighting_rows": lighting_rows.docs(),
        "sofa_rows": sofa_rows.docs(),
        "appliance_rows": appliance_rows.docs(),
        "underwear_rows": underwear_rows.docs(),
        "toys_rows": toys_rows.docs(),
        "seasonal_rows": seasonal_rows.docs(),
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
            "food_and_drink_tree": {
                tree: sum(
                    r["sku_count"] for r in food if r["category_path"][0] == tree
                )
                for tree in sorted({r["category_path"][0] for r in food})
            },
        },
        "departments": dict(sorted(departments.items())),
        "grocery_families": {code: _count(recs) for code, recs in sorted(families.items())},
        "grocery_values": {
            "checked": checked,
            "named_but_not_carried": dict(sorted((k, n) for k, n in wrong.items() if n)),
        },
        "near_duplicates": {
            "non_grocery": scale.distinctness(main, sample=len(main))["near_duplicate_rate"],
            "grocery": scale.distinctness(groc, sample=len(groc))["near_duplicate_rate"],
            "non_grocery_grid_clone_rate": scale.grid_clones(main)["grid_clone_rate"],
            "grocery_grid_clones": scale.grid_clones(groc)["grid_clones"],
        },
    }


def render(figures: dict[str, Any]) -> str:
    return json.dumps(figures, indent=1, sort_keys=True) + "\n"


def main() -> int:
    STATS.parent.mkdir(exist_ok=True)
    STATS.write_text(render(measure()), encoding="utf-8")
    print(f"wrote {STATS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
