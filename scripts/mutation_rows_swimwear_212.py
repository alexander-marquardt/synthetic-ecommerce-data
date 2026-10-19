"""Mutation rows for the swimwear types of gen#212, in their own file.

Each row plants one defect in a spec, a row helper or a drawing of gen#212 and names the test that
must go red. ``mutation_row.discover`` finds this file by glob and the harness names them as rows
named ``swimwear: ...`` (``--only "swimwear:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501  (a row quotes the whole source line it changes)
from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"
_T = "tests/test_retail_swimwear_212.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a bikini bottom's tie side is no longer drawn",
        "swimwear_rows.py",
        '("tie_side", "Tie side", tie, "tie_side")',
        '("tie_side", "Tie side", tie)',
        f"{_T} -k drawing_shows_the_marks",
        "a tie side the record states is drawn as two ties",
        _R,
    ),
    (
        "a swimsuit loses its cup axis",
        "swimwear_rows.py",
        'axis=("cup_size", CUPS)',
        "axis=None",
        f"{_T} -k swimsuit_sku_states",
        "every swimsuit SKU states its cup size",
        _R,
    ),
    (
        "a UPF swimsuit is stated but not drawn",
        "swimwear_rows.py",
        '("uv_protection", "UV protection", "UPF 50+" if upf == "yes" else "None", "upf", upf)',
        '("uv_protection", "UV protection", "UPF 50+" if upf == "yes" else "None", "upf", "no")',
        f"{_T} -k drawing_shows_the_marks",
        "a UPF claim the record states is drawn as a badge",
        _R,
    ),
    (
        "the period swimwear absorbency is not drawn",
        "swimwear_rows.py",
        '("absorbency", "Absorbency", absorbency, "absorbency")',
        '("absorbency", "Absorbency", absorbency)',
        f"{_T} -k drawing_shows_the_marks",
        "a moderate absorbency draws two absorbent layers",
        _R,
    ),
    (
        "swim shorts leave the Swimwear node",
        "swimwear_rows.py",
        'SHORTS = ("Mens", "Swimwear", "Swim Shorts")',
        'SHORTS = ("Mens", "Swimming", "Swim Shorts")',
        f"{_T} -k swimwear_node",
        "every swimwear type nests under a Swimwear node",
        _R,
    ),
    (
        "the changing robe loses its only yellow",
        "swimwear_rows.py",
        '"Knee", 60.0, "A hooded changing robe with a waterproof shell and a warm fleece lining.", (BLACK, BLUE, GREEN, RED, YELLOW, WHITE))',
        '"Knee", 60.0, "A hooded changing robe with a waterproof shell and a warm fleece lining.", (BLACK, BLUE, GREEN, RED, WHITE))',
        f"{_T} -k six_main_colors",
        "every swimwear type sells the six main colors",
        _R,
    ),
    (
        "the tankini medium support loses its shelf band",
        "kit_swimwear.py",
        '    if support == "medium":\n        out += [_g("shelf-band"',
        '    if support == "never":\n        out += [_g("shelf-band"',
        f"{_T} -k drawing_shows_the_marks",
        "a medium support tankini draws its shelf band",
        _R,
    ),
    (
        "the cover-up loses a style",
        "type_specs/cover_up.py",
        "rows=swimwear_rows.COVER_ROWS",
        "rows=swimwear_rows.COVER_ROWS[:2]",
        f"{_T} -k three_styles_from_three_brands",
        "every type has three styles",
        _R,
    ),
    (
        "the swimsuit spec is renamed",
        "type_specs/swimsuit.py",
        'product_type="Swimsuit"',
        'product_type="Swimsuits"',
        f"{_T} -k registered_spec",
        "the spec's product type names the type",
        _R,
    ),
    (
        "a robe's fleece lining is never drawn as fleece",
        "kit_swimwear.py",
        'for i in range(8)) if lining == "fleece" else',
        'for i in range(8)) if lining == "never" else',
        f"{_T} -k every_param_axis",
        "a lining the record states is the lining drawn",
        _R,
    ),
    (
        "a kids' short sleeve is drawn to the wrist",
        "kit_swimwear.py",
        "{96 if sleeve == 'short' else 214} L{x + 26},{104 if sleeve == 'short' else 220} L134,142 Z\",",
        "{214} L{x + 26},{220} L134,142 Z\",",
        f"{_T} -k short_sleeve_ends_high",
        "a short sleeve the record states is drawn short",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "swimwear"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
