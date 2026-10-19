"""Mutation rows for the retail jewellery and watches (gen#423), kept out of ``mutation_check.py``.

Each row plants one defect in a line the gen#423 change added and names the test that must go
red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``jewellery 423: ...``
(``--only "jewellery 423:"`` re-runs them). A row is ``(name, file, old, new, test, property)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_jewellery_watches_423.py"
_S = "tests/test_retail_type_specs_351.py"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "a watch's case diameter is stored under the garment size key",
        "jewellery_rows.py",
        'size_key="case_mm"',
        'size_key="size"',
        f'{_T} -k "strap_case_diameter"',
        "a watch SKU states its case diameter as case_mm",
    ),
    (
        "a watch states no audience",
        "jewellery_rows.py",
        '*extra, a("audience", "Audience", who),',
        "*extra,",
        f'{_T} -k "strap_case_diameter"',
        "a watch states who it is for",
    ),
    (
        "a watch states no strap",
        "jewellery_rows.py",
        'a("strap", "Strap", strap), metres(',
        "metres(",
        f'{_T} -k "strap_case_diameter"',
        "a watch states its strap",
    ),
    (
        "a water resistance in metres is stored as metres, not as the core's millimetres",
        "jewellery_rows.py",
        "float(m * 1000)",
        "float(m)",
        f'{_S} -k "meet_the_standard and analog_watch"',
        "a measured value's canonical form is what the core's unit says",
    ),
    (
        "the case diameter option is unknown to the export",
        "jewellery_rows.py",
        'size_key="case_mm"',
        'size_key="case_mmx"',
        f'{_S} -k "meet_the_standard and fitness_band"',
        "every SKU option the build writes has an export entry",
    ),
    (
        "hoop earrings are not an excepted color type",
        "main_colors.py",
        '    "Hoop Earrings": "precious metal: the color is the metal",\n',
        "",
        f"{_T} -k an_earring_color",
        "a metal-colored type declares its exception",
    ),
    (
        "a digital watch decoy no longer carries the word digital",
        "type_specs/digital_watch.py",
        "A simple digital watch that shows",
        "A simple watch that shows",
        f'{_T} -k "text_match_decoys and Digital"',
        "each decoy carries its type's word",
    ),
    (
        "a text-only rank still multiplies by popularity",
        "baseline_rank.py",
        "(popularity(index.catalog[i]) if popular else 1.0)",
        "popularity(index.catalog[i])",
        f'{_T} -k "ranks_its_type_first and silver"',
        "a query-shape test ranks by text score alone, so a seeded sales draw cannot move it",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "jewellery 423"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
