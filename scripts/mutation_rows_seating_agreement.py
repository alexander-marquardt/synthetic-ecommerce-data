"""Mutation rows for the seating kit's words, seat counts and depths (gen#225), kept out of
``mutation_check.py``.

Each row plants one defect in the chaise docs, the corner sofa's seat count or a mattress depth
entry and names the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows
named ``seating agreement: ...`` (``--only "seating agreement:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

_T = "tests/test_retail_seating_225.py"
_ROOT = "prototypes/retail_drawings"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a corner sofa draws a run of three whatever its seat count",
        "kit_seating.py",
        "n = max(0, int(float(seats)) - 3 * returns)",
        "n = 3",
        f'{_T} -k "seat_cushions_its_record_states and corner_sofa"',
        "a corner sofa is drawn with the seat cushions its record states",
        _ROOT,
    ),
    (
        "a u-shaped corner sofa counts one return",
        "kit_seating.py",
        'returns = 2 if side == "u" else 1',
        "returns = 1",
        f'{_T} -k "seat_cushions_its_record_states and corner_sofa"',
        "a u-shaped corner sofa takes the seats of both returns from its seat count",
        _ROOT,
    ),
    (
        "a handed corner style passes three seats to the drawing",
        "sofa_rows.py",
        'params=(("seats", str(seats)), ("side", side), ("arms", arms), ("legs", legs)))',
        'params=(("seats", "3"), ("side", side), ("arms", arms), ("legs", legs)))',
        "tests/test_retail_seating_196.py -k draws_the_seats_its_record_states",
        "a corner style's seats param is its record's seat count",
        _ROOT,
    ),
    (
        "the chaise table says it has no back again",
        "kit_seating.py",
        "its back along the whole rear, chaise included   arms, legs",
        "no back over the chaise                          arms, legs",
        f'{_T} -k "chaise_docs"',
        "the chaise docs describe the back the drawing gives it",
        _ROOT,
    ),
    (
        "the chaise docstring says it has no back again",
        "kit_seating.py",
        "chaise end too (the chaise is the front of that last seat, not a seat without a back).",
        "chaise end too (the chaise has no back over it).",
        f'{_T} -k "chaise_docs"',
        "the chaise docs describe the back the drawing gives it",
        _ROOT,
    ),
    (
        "the chaise loses its back",
        "kit_seating.py",
        """        Box(0.0, width, BASE, BACK - 6, DEPTH - 14, DEPTH, "fill"),
        *_cushions(0.0, width, n, CUSHION - 2, BACK, DEPTH - 32, DEPTH - 14),
        Box(SEAT, width, LEG, BASE, 0.0, DEPTH, "fill", front=0.14),""",
        """        Box(SEAT, width, LEG, BASE, 0.0, DEPTH, "fill", front=0.14),""",
        f'{_T} -k "chaise_has_its_back"',
        "the chaise has its back along the whole rear",
        _ROOT,
    ),
    (
        "the corner sofa decoy is a bare corner again",
        "decoy_rows.py",
        'params=(("seats", "5"), ("side", "left"), ("arms", "track"),',
        'params=(("seats", "3"), ("side", "left"), ("arms", "track"),',
        f'{_T} -k "corner_sofa_decoy"',
        "a corner sofa decoy draws a run beside its corner and return",
        _ROOT,
    ),
    (
        "a sofa bed's depth is free text again",
        "sofa_rows.py",
        '_cm("depth", "Depth", depth)),',
        '("depth", "Depth", f"{depth} cm")),',
        f'{_T} -k "sofa_beds_mattress_depth"',
        "a sofa bed's mattress depth is a measured centimeter entry",
        _ROOT,
    ),
    (
        "a topper's depth loses its unit code",
        "variants.py",
        '"attributes": [attr(*e) for e in self.extra],',
        '"attributes": [attr(e[0], e[1], e[2]) for e in self.extra],',
        f'{_T} -k "toppers_depth"',
        "a topper's depth is a measured centimeter entry",
        _ROOT,
    ),
    (
        "a topper's canonical depth is in centimeters",
        "variants.py",
        '(("depth", "Depth", "5", "CMT", 50.0),)',
        '(("depth", "Depth", "5", "CMT", 5.0),)',
        f'{_T} -k "toppers_depth"',
        "a topper's depth has a millimeter canonical value",
        _ROOT,
    ),
    (
        "the round-two topper's canonical depth is in centimeters",
        "samples_round2.py",
        'attr("depth", "Depth", 5, "CMT", 50.0)',
        'attr("depth", "Depth", 5, "CMT")',
        f'{_T} -k "toppers_depth"',
        "the round-two topper's depth has a millimeter canonical value",
        _ROOT,
    ),
]
