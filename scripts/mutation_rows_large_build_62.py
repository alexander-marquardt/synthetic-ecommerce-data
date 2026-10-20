"""Mutation rows for the large build's name and the SKU totals no prose types (gen#62).

Each row plants one defect on a line the fix changed and names the test that must go red. Found by
``mutation_row.discover``; ``--only "large build:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "large build"

_T = "tests/test_large_build_name_62.py"
_CONFIG = "core/config.py"
_ROOT = "."


def rows() -> list[Row]:
    return [
        Row(
            "the setting holds another line count",
            _CONFIG,
            "LARGE_BUILD_LINES = 39000",
            "LARGE_BUILD_LINES = 40000",
            f"{_T}::test_the_large_build_setting_is_named_for_the_lines_it_holds",
            "the setting is the line count the README's command passes",
        ),
        Row(
            "the config types a SKU total again",
            _CONFIG,
            "#: total of this build grows with every one, which is",
            "#: total of this build is 99,929 SKUs with every one, which is",
            f"{_T}::test_the_config_types_no_sku_total_of_a_build",
            "a SKU total typed in a config comment is refused",
        ),
        Row(
            "the README names the setting by its retired name",
            "README.md",
            "(`config.LARGE_BUILD_LINES`) is the large build's line count",
            "(`config.HUNDRED_K_LINES`) is the large build's line count",
            f"{_T}::test_no_doc_names_the_setting_by_a_sku_total",
            "a doc naming the retired setting is refused",
            _ROOT,
        ),
        Row(
            "the README promises a total in the large build's section",
            "README.md",
            "it was first chosen to give 100,000 SKUs and no\nlonger promises a total.",
            "it lands at about 100,000 SKUs and no\nlonger promises a total.",
            f"{_T}::test_the_readme_does_not_promise_the_large_build_lands_at_a_sku_total",
            "a promised total in the section is refused",
            _ROOT,
        ),
        Row(
            "the README intro promises a total",
            "README.md",
            "a large build whose SKU total is measured",
            "about 100K SKUs",
            f"{_T}::test_the_readme_does_not_promise_the_large_build_lands_at_a_sku_total",
            "a promised total in the intro is refused",
            _ROOT,
        ),
    ]
