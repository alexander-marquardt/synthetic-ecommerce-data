"""Mutation rows for the bolt's page pack (gen#86), kept out of ``mutation_check.py``.

Each row plants one defect in how a bolt's pack is drawn per group page and priced within a size,
and names the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``bolt page pack: ...`` (``--only "bolt page pack:"`` re-runs them). A row is
``(name, file, old, new, test, direction, property, root)``.
"""

from __future__ import annotations

SRC = "src/synthetic_ecommerce_data"

ROWS: list[tuple[str, str, str, str, str, str, str, str]] = [
    (
        "a page's lines draw a pack each",
        "core/price.py",
        'random.Random(f"{seed}:pack-page:{type_key}:{brand}:{sorted(held)}")',
        'random.Random(f"{seed}:pack-page:{type_key}:{brand}:{random.random()}")',
        "tests/test_bolt_page_pack.py -k every_line_of_a_page_shares_one_pack",
        "A",
        "every size of a page shares one pack",
        SRC,
    ),
    (
        "the page pack ignores the census counts",
        "core/price.py",
        "    return _pack_at(type_key, u)",
        "    return 100",
        "tests/test_bolt_page_pack.py -k page_pack_follows_the_census_counts",
        "A",
        "the page pack follows the census counts",
        SRC,
    ),
    (
        "the pack elasticity drifts from the census ratio",
        "core/price.py",
        '{"bolt_hex": 0.659}',
        '{"bolt_hex": 0.223}',
        "tests/test_bolt_page_pack.py -k elasticity_is_the_census_ratio",
        "A",
        "the elasticity is the census ratio's",
        SRC,
    ),
    (
        "the fit's slope-only spread leaves the pack out",
        "fit_price_model.py",
        "ls * b.log_length + b.pack)",
        "ls * b.log_length)",
        "tests/test_fit_price_model.py -k page_pack_spread",
        "A",
        "the fit's spread counts the pack",
        "scripts",
    ),
]
