"""Mutation rows for the industrial seed decoys of gen#462, in their own file.

Each row plants one defect in the seed table, a decoy module or the guard's term matcher and names
the test of ``tests/test_industrial_seed_decoys_462.py`` that must go red.
``mutation_row.discover`` finds this file by glob and the harness names them as rows named
``industrial seed decoys: ...`` (``--only "industrial seed decoys:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_I = "domains/industrial"
_T = "tests/test_industrial_seed_decoys_462.py"
_SRC = "src/synthetic_ecommerce_data"
_SEED = f"{_T}::test_each_seed_has_two_decoy_lines"
_D = f"{_I}/product_types/decoys"
_TERM = f"{_T}::test_a_term_is_a_whole_word_with_an_optional_plural"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "lock nuts keep one decoy",
        f"{_I}/seed_decoys.py",
        '    "lock nuts": ("conduit_pliers", "spanner_wrenches"),\n',
        '    "lock nuts": ("conduit_pliers",),\n',
        f"{_SEED}[lock-nuts]",
        "every seed has at least two decoy lines",
        _SRC,
    ),
    (
        "a 1/2 end mill decoy loses the end mill from its title",
        f"{_D}/milling_tool_holders.py",
        'item="End Mill Holder"',
        'item="Tool Holder"',
        f"{_SEED}[1-2-endmill]",
        "a listed decoy holds every term of its seed in one SKU title",
        _SRC,
    ),
    (
        "a dowel pin decoy loses the dowel from its title",
        f"{_D}/pin_pullers.py",
        'item="Dowel Pin Puller"',
        'item="Pin Puller"',
        f"{_SEED}[dowel-pins]",
        "a listed decoy holds every term of its seed in one SKU title",
        _SRC,
    ),
    (
        "a hex key decoy sits under the Hex Keys node",
        f"{_D}/wrench_organizers.py",
        '"Tool Storage", "Wrench Organizers"',
        '"Hex Keys", "Wrench Organizers"',
        f"{_SEED}[hex-keys]",
        "a decoy's category path never names the seed's own category",
        _SRC,
    ),
    (
        "a washer decoy serves no seed",
        f"{_I}/seed_decoys.py",
        '    "washers": ("sems_bolts", "serrated_flange_nuts", "circle_cutters"),\n',
        '    "washers": ("sems_bolts", "serrated_flange_nuts"),\n',
        f"{_T}::test_every_decoy_type_serves_a_seed",
        "every decoy module serves a seed",
        _SRC,
    ),
    (
        "the nuts seed is dropped",
        f"{_I}/seed_decoys.py",
        '    "nuts": (("nut",), ("nuts",)),\n',
        "",
        f"{_T}::test_the_seed_table_names_every_query_of_the_issue",
        "the seed table names every query of the issue",
        _SRC,
    ),
    (
        "a section drops a query",
        f"{_I}/seed_decoys.py",
        '    "Item nouns": ("o-rings", "screws", "bolts", "washers", "nuts"),\n',
        '    "Item nouns": ("o-rings", "screws", "bolts", "washers"),\n',
        f"{_T}::test_the_sections_partition_the_seeds",
        "the sections hold every seed once",
        _SRC,
    ),
    (
        "a term matches inside a longer word",
        _T.removeprefix("tests/"),
        "(?:e?s)?(?!\\w)",
        "(?:e?s)?",
        f"{_TERM}[longer-word]",
        "a seed term is a whole word",
        "tests",
    ),
    (
        "a term no longer takes a plural ending",
        _T.removeprefix("tests/"),
        "(?:e?s)?(?!\\w)",
        "(?!\\w)",
        f"{_TERM}[plural]",
        "a seed term matches its plural",
        "tests",
    ),
    (
        "a term matches inside a number",
        _T.removeprefix("tests/"),
        "(?<!\\w){re.escape(term)}",
        "{re.escape(term)}",
        f"{_TERM}[inside-a-number]",
        "a seed term is a whole word",
        "tests",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "industrial seed decoys"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
