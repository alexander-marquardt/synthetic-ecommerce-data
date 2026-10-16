"""Mutation rows for the retail accessory types (gen#422), kept out of ``mutation_check.py``.

Each row plants one defect in a type's spec, drawing or the guard that owes it, and names the test
that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``accessories: ...``
(``--only "accessories:"`` re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

_R = "prototypes/retail_drawings"
_S = "type_specs/sunglasses.py"
_T = "tests/test_retail_sunglasses_422.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "sunglasses: every pair is drawn as an aviator",
        _S,
        'd, (cx, cy), scale, drop = _FRAMES.get(frame, _FRAMES["aviator"])',
        'd, (cx, cy), scale, drop = _FRAMES["aviator"]',
        f'{_T} -k "frame_and_each_lens_draws_differently"',
        "the frame param changes the drawing",
        _R,
    ),
    (
        "sunglasses: every lens is painted polarised",
        _S,
        'else _LENS.get(lens, _LENS["polarised"])',
        'else _LENS["polarised"]',
        f'{_T} -k "painted_in_its_own_tint"',
        "the lens param changes the lens fill",
        _R,
    ),
    (
        "sunglasses: a pair states no UV400",
        _S,
        'a("uv400", "UV400", uv)',
        'a("uv400", "UV400", "No")',
        f'{_T} -k "uv400"',
        "every pair of the type states UV400",
        _R,
    ),
    (
        "sunglasses: white is not offered",
        _S,
        "_SIX = (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)",
        "_SIX = (BLACK, RED, BLUE, GREEN, YELLOW)",
        f'{_T} -k "six_main_colors"',
        "the six main colors are offered across the type",
        _R,
    ),
    (
        "sunglasses: a top-level Accessories root",
        _S,
        '_PATH = ("Womens", "Accessories", "Sunglasses")',
        '_PATH = ("Accessories", "Sunglasses")',
        f'{_T} -k "womens_accessories"',
        "the type sits under Womens > Accessories, never a root",
        _R,
    ),
    (
        "sunglasses: a pair is for women only",
        _S,
        'a("audience", "Audience", "Unisex")',
        'a("audience", "Audience", "Womens")',
        f'{_T} -k "two_brands_and_unisex"',
        "a pair is unisex",
        _R,
    ),
    (
        "sunglasses: the drawing's lens is not the row's lens",
        _S,
        'params=(("frame", frame), ("lens", lens))',
        'params=(("frame", frame), ("lens", "Gradient"))',
        f'{_T} -k "param_values_match"',
        "the drawing params equal the structured entries",
        _R,
    ),
    (
        "sunglasses: the UV400 decoy has UV protection",
        _S,
        '(BLACK,), uv="No")),',
        '(BLACK,), uv="Yes")),',
        f'{_T} -k "text_match_decoys"',
        "a class 4 decoy names UV400 and has none",
        _R,
    ),
]
