"""Mutation rows for the named parts of gen#447 (a title that names a part draws it).

Each row plants one defect in ``named_parts``, the part table of ``details`` or the decoy clone and
names the test that must go red. ``mutation_row.discover`` finds this file by glob; the rows are
named ``named parts: ...`` (``--only "named parts:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501  (a row quotes the whole line it breaks)
from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"
_T = "prototypes/retail_drawings/test_shape_honesty.py"
_NP = "named_parts.py"
_DT = "details.py"
_NEW = "a_new_part_is_one_the_shape_shows"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "apply draws no part",
        _NP,
        '            drawing["detail"] = {"part": got[1], "color": hex_}\n',
        "            pass\n",
        f'{_T} -k "a_reported_title_names_a_part_its_drawing_shows and PLT-DXH03"',
        "a title that names a collar draws a collar",
        _R,
    ),
    (
        "apply draws every part red",
        _NP,
        'drawing, hex_ = tpl["drawing"], DETAIL_HEX[got[0]]',
        'drawing, hex_ = tpl["drawing"], DETAIL_HEX["Red"]',
        f'{_T} -k "a_reported_title_names_a_part_its_drawing_shows and PLT-DXH03"',
        "the part is drawn in the color the title names",
        _R,
    ),
    (
        "apply leaves a shoe's laces undrawn",
        _NP,
        'if got[1] == "laces" and drawing["shape"] == "shoe":',
        "if False:",
        f"{_T} -k every_apparel_title_that_names_a_part_draws_it",
        "a title that names laces draws them in that color",
        _R,
    ),
    (
        "the guard lets a stitching title by",
        _NP,
        'TOO_FINE = re.compile(r"\\b(Stitching|Piping)\\b")',
        'TOO_FINE = re.compile(r"\\b(Piping)\\b")',
        f"{_T} -k the_guard_refuses_a_part_not_drawn_and_a_trim_too_fine",
        "no garment names a trim too fine to see",
        _R,
    ),
    (
        "the guard accepts a part in the wrong color",
        _NP,
        'ok = drawing.get("detail") == {"part": part, "color": hex_}',
        'ok = (drawing.get("detail") or {}).get("part") == part',
        f"{_T} -k the_guard_refuses_a_part_not_drawn_and_a_trim_too_fine",
        "the guard checks the color as well as the part",
        _R,
    ),
    (
        "a row's trim is always the first part",
        _NP,
        "return parts[i % len(parts)].title()",
        "return parts[0].title()",
        f"{_T} -k a_trim_part_is_one_the_shape_shows",
        "the i-th trim of a shape is picked",
        _R,
    ),
    (
        "a trim is picked from the authored shape, not the drawn one",
        _NP,
        "    shape = leaf_shapes.shape_of(ptype, shape)\n",
        "",
        f"{_T} -k a_trim_is_picked_from_the_shape_a_leaf_rule_draws",
        "a trim is a part of the shape the row is drawn with",
        _R,
    ),
    (
        "the bra shows no band",
        _DT,
        '"band": free(("M50,226 L140,231 M350,226 L260,231", 6.0)),',
        "",
        f'{_T} -k "{_NEW} and bra-band"',
        "a bra shows its underband",
        _R,
    ),
    (
        "the bra shows no cups",
        _DT,
        '"cups": shapes(',
        '"cupz": shapes(',
        f'{_T} -k "{_NEW} and bra-cups"',
        "a bra shows its cups",
        _R,
    ),
    (
        "the blouse shows no collar",
        _DT,
        '"collar": shapes(\n            "M166,62',
        '"collr": shapes(\n            "M166,62',
        f'{_T} -k "{_NEW} and blouse-collar"',
        "a blouse shows its collar",
        _R,
    ),
    (
        "the blouse shows no buttons",
        _DT,
        '"buttons": shapes(',
        '"buttonz": shapes(',
        f'{_T} -k "{_NEW} and blouse-buttons"',
        "a blouse shows its buttons",
        _R,
    ),
    (
        "the blouse shows no pocket",
        _DT,
        '"pocket": shapes("M224,150',
        '"pocketz": shapes("M224,150',
        f'{_T} -k "{_NEW} and blouse-pocket"',
        "a blouse shows its pocket",
        _R,
    ),
    (
        "the dinner suit shows no cuffs",
        _DT,
        '"dinner_suit": {"cuffs": HEM}',
        '"dinner_suit": {}',
        f'{_T} -k "{_NEW} and dinner_suit-cuffs"',
        "a dinner suit shows its trouser cuffs",
        _R,
    ),
    (
        "a decoy clone keeps its exemplar's named part",
        "decoy_apparel.py",
        'if k not in ("accents", "detail")',
        'if k not in ("accents",)',
        "tests/test_retail_apparel_decoys_311.py -k a_range_name_never_holds_a_color",
        "a class 6 or 7 clone colors no part",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "named parts"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
