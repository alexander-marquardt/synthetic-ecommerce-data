"""Mutation rows for the click-clack sofa bed drawing (gen#223), kept out of ``mutation_check.py``.

Each row breaks one part of the click-clack branch of ``kit_seating.sofa_bed`` (the seat per
seat, the upright back, one sofa's depth, the hinge line) and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``sofa bed: ...`` (``--only "sofa
bed:"`` re-runs them). A row is ``(name, file, old, new, test, property)``; every file is under
``prototypes/retail_drawings``.
"""

from __future__ import annotations

_SOFA = "tests/test_retail_seating_196.py -k a_click_clack_draws_a_sofa"
_HINGE = "tests/test_retail_seating_196.py -k a_click_clack_is_a_sofa_deep"
_FILE = "kit_seating.py"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the click-clack draws one seat cushion however many seats",
        _FILE,
        "*_cushions(0.0, width, n, BASE, CUSHION, 0.0, z_hinge),",
        "*_cushions(0.0, width, 1, BASE, CUSHION, 0.0, z_hinge),",
        _SOFA,
        "a click-clack shows one seat cushion per seat",
    ),
    (
        "the click-clack draws no back cushion",
        _FILE,
        "*_cushions(0.0, width, n, CUSHION - 2, BACK, z_hinge, DEPTH - 14),",
        "",
        _SOFA,
        "a click-clack shows an upright back cushion per seat",
    ),
    (
        "the click-clack frame is two sofas deep again",
        _FILE,
        "Box(0.0, width, LEG, BASE, 0.0, DEPTH, FRAME),",
        "Box(0.0, width, LEG, BASE, 0.0, DEPTH * 2, FRAME),",
        _HINGE,
        "a click-clack is one sofa deep, not a double-depth bed",
    ),
    (
        "the click-clack hinge line sits on the front edge of the seat",
        _FILE,
        "sheet.p(1.0, CUSHION, z_hinge)} L{sheet.p(width - 1, CUSHION, z_hinge)}",
        "sheet.p(1.0, CUSHION, 0.0)} L{sheet.p(width - 1, CUSHION, 0.0)}",
        _HINGE,
        "the hinge line is marked where the back meets the seat",
    ),
    (
        "the click-clack draws no hinge line",
        _FILE,
        "        return _draw(boxes, paint, fill, hinge)\n    aw = ARMS",
        "        return _draw(boxes, paint, fill, None)\n    aw = ARMS",
        _HINGE,
        "the hinge line is marked where the back meets the seat",
    ),
]
