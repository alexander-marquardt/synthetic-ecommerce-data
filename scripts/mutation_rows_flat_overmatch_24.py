"""Mutation rows for the flat over-match figure the README points at (gen#24).

Each row plants one defect on a changed line of ``flat_overmatch_figures`` or of the build that
writes it, and names the test that must go red. Found by ``mutation_row.discover``;
``--only "flat overmatch:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "flat overmatch"

_T = "tests/test_readme_measurements_24.py"
_COUNT = f"{_T}::test_the_overmatch_counts_a_value_on_another_attribute_only_as_matching"
_DERIVE = "prism/derive.py"


def rows() -> list[Row]:
    return [
        Row(
            "the publishing count matches the name or the value",
            _DERIVE,
            'a["name"] == OVERMATCH_ATTRIBUTE and a["value"] == OVERMATCH_VALUE',
            'a["name"] == OVERMATCH_ATTRIBUTE or a["value"] == OVERMATCH_VALUE',
            _COUNT,
            "publishing counts the value on the attribute itself",
        ),
        Row(
            "the matching count ignores the value",
            _DERIVE,
            "            a[\"value\"] == OVERMATCH_VALUE for a in attributes\n        ):",
            "            True for a in attributes\n        ):",
            _COUNT,
            "matching needs the value anywhere in the array",
        ),
        Row(
            "the matching count ignores the attribute name",
            _DERIVE,
            'if any(a["name"] == OVERMATCH_ATTRIBUTE for a in attributes) and any(',
            "if any(True for a in attributes) and any(",
            _COUNT,
            "matching needs the attribute name anywhere in the array",
        ),
        Row(
            "the build drops the over-match figure",
            "generate_cli.py",
            '        "flat_overmatch": flat_overmatch_figures(flat),\n',
            "",
            "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build[stats.json]",
            "the build writes the flat over-match into stats.json",
        ),
    ]
