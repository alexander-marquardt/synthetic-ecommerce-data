"""Mutation rows for the garden hose's text-match decoys (gen#292, gen#294).

They are kept out of ``mutation_check.py``. Each row plants one defect in the hose's decoys, their
drawing or the guard that owes them, and names the test that must go red. ``mutation_check.py``
turns them into ``Mutation`` rows named ``garden hose: ...`` (``--only "garden hose:"`` re-runs
them). A row is ``(name, file, old, new, test, property, root)``; :data:`ALL` holds these, the
type-spec rows and the Mens suits rows (``mutation_rows_suits_215``, gen#215), each with its
prefix, so ``mutation_check.py`` reads one list.
"""

from __future__ import annotations

import mutation_rows_suits_215
import mutation_rows_text_exempt_452
import mutation_rows_toys_424
import mutation_rows_type_specs

_R = "prototypes/retail_drawings"
_T = "tests/test_retail_garden_203.py"
_COPY = "*(_copy(c, k, t, b, col, d) for items in _REAL.values() for c, k, t, b, col, d in items),"
_MAKE = "*(make(c, t, d) for c, _p, make, t, d in _SIBLINGS),"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the hose's real decoys are dropped",
        "garden_rows.py",
        _COPY,
        _COPY.replace("_REAL.values()", "list(_REAL.values())[:-1]"),
        f'{_T} -k "at_least_three_decoys and Hose"',
        "the hose carries three decoys of each class",
        _R,
    ),
    (
        "the hose's sibling products are dropped",
        "garden_rows.py",
        _MAKE,
        _MAKE.replace("in _SIBLINGS", 'in _SIBLINGS if _p != "Garden Hose"'),
        f'{_T} -k "at_least_three_decoys and Hose"',
        "the hose carries three type decoys",
        _R,
    ),
    (
        "the hose's scented candle is no longer an incidental decoy",
        "garden_rows.py",
        '"DCHCND": ("incidental", "garden hose", "Garden Hose")',
        '"DCHCND": ("incidental", "garden hose", "Scented Candle")',
        f'{_T} -k "at_least_three_decoys and Hose"',
        "the hose carries three incidental decoys",
        _R,
    ),
    (
        "the secondary decoys' part color is dropped",
        "kit_garden.py",
        'fill="{pt.fill("connectors", BRASS)}"',
        'fill="{BRASS}"',
        f"{_T} -k a_decoy_title_names_a_color_only_when_the_drawing_shows_it",
        "a hose titled with green connectors draws its connectors green",
        _R,
    ),
    (
        "the named connectors are not marked",
        "kit_garden.py",
        'pt.mark("connectors", block)',
        "block",
        f"{_T} -k a_decoy_title_names_a_color_only_when_the_drawing_shows_it",
        "the named part is marked in the drawing",
        _R,
    ),
    (
        "the hose is exempt from the guard though it holds decoys",
        _T.removeprefix("tests/"),
        '        "Growing Kit",\n        "Plant",',
        '        "Growing Kit",\n        "Garden Hose",\n        "Plant",',
        f'{_T} -k "exempt_garden_type"',
        "an exempt Garden type holds no decoy",
        "tests",
    ),
    (
        "the guard misses the types in the spec files",
        _T.removeprefix("tests/"),
        '{s.product_type for s in type_registry.specs().values() if s.department == "Garden"}',
        "set()",
        f'{_T} -k "registry_lists_exactly"',
        "the guard's Garden types are the build's own",
        "tests",
    ),
]

ALL: list[tuple[str, ...]] = [
    *(("type specs", *row) for row in mutation_rows_type_specs.ROWS),
    *(("garden hose", *row) for row in ROWS),
    *(("suits", *row) for row in mutation_rows_suits_215.ROWS),
    *(("toys depth", *row) for row in mutation_rows_toys_424.ROWS),
    *(("text exempt", *row) for row in mutation_rows_text_exempt_452.ROWS),
]
