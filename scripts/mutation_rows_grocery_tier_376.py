"""Mutation rows for the grocery 50K tier of gen#376, in their own file.

Each row plants one defect in the tier's code or data and names the test of
``tests/test_grocery_50k_tier_376.py`` that must go red. ``mutation_row.discover`` finds this file
by glob; ``--only "grocery tier:"`` re-runs the rows.
"""

from __future__ import annotations

from mutation_row import RETAIL_DRAWINGS, Row

PREFIX = "grocery tier"
_T = "tests/test_grocery_50k_tier_376.py"

#: (name, file, old, new, test, property)
_ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the tier is never entered",
        "grocery.py",
        "    tier = skus > TARGET\n",
        "    tier = False\n",
        f"{_T} -k reaches_its_target",
        "a build past the 10K target is the tier and reaches its target",
    ),
    (
        "the tier shares the target over the core families only",
        "grocery.py",
        "if skus > TARGET or not f.depth)",
        "if not f.depth)",
        f"{_T} -k reaches_its_target",
        "the tier's budgets add up to its target, depth families included",
    ),
    (
        "the tier draws no extra range names",
        "grocery.py",
        "lines = (*LINES, *grocery_rows.TIER_LINES) if tier else LINES",
        "lines = LINES",
        f"{_T} -k holds_its_budget_share",
        "the extra range names let every family reach its budget",
    ),
    (
        "the tier draws no new brands",
        "grocery.py",
        "extra = grocery_rows.TIER_BRANDS.get(fam.brands, ()) if tier else ()",
        "extra = ()",
        f"{_T} -k names_its_new_brands",
        "the tier names the new invented brands",
    ),
    (
        "the 10K build draws the new brands too",
        "grocery.py",
        "extra = grocery_rows.TIER_BRANDS.get(fam.brands, ()) if tier else ()",
        "extra = grocery_rows.TIER_BRANDS.get(fam.brands, ())",
        f"{_T} -k 10k_build",
        "the 10K build reads none of the tier's data",
    ),
    (
        "the tier's figures measure another size",
        "retail_figures.py",
        "TIER_SKUS = 50_000",
        "TIER_SKUS = 40_000",
        f"{_T} -k figures_pin_the_tiers_counts",
        "the measured figures hold the 50K tier's totals",
    ),
    (
        "a new brand reuses another brand's mark",
        "grocery_brand_styles.py",
        '"round", "furrow"',
        '"round", "sprout"',
        f"{_T} -k own_mark",
        "each new brand has a mark no other brand uses",
    ),
    (
        "a new brand has no owner",
        "grocery_rows.py",
        '    "Fellbeck Roasters": "third_party",\n',
        "",
        f"{_T} -k own_mark",
        "each new brand has an OWNERS entry",
    ),
    (
        "a family group gets no new brand",
        "grocery_rows.py",
        '    _DAIRY: ("Wetherly Creamery",),\n',
        "",
        f"{_T} -k family_group_gets",
        "every family group gets a new brand",
    ),
]


def rows() -> list[Row]:
    return [Row(n, f, o, w, t, p, RETAIL_DRAWINGS) for n, f, o, w, t, p in _ROWS]
