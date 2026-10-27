"""Mutation rows for the hex nut size scopes (#33).

They are kept out of ``mutation_check.py``. Each row plants one defect in the nut's claims or its
size table, and names the test that must go red. ``mutation_row.discover`` finds this file by glob
and the harness names the rows ``nut size scope: ...`` (``--only "nut size scope:"`` re-runs
them). Every row reds on the old golden's behaviour: it puts back what #33 took out.
"""

from __future__ import annotations

from mutation_row import Row

_C = "domains/industrial/conformance.py"
_H = "domains/industrial/product_types/fasteners/nut_hex.py"
_N = "domains/industrial/newtypes.py"
_T = "tests/test_nut_size_scope_33.py"
_SCOPE = f"{_T}::test_a_nut_claims_a_grade_standard_only_inside_its_size_scope"
_HEAVY = f"{_T}::test_a_heavy_hex_nut_is_not_offered_below_the_heavy_series"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "a #6-#10 nut claims SAE J995 again",
        _H,
        'if grade.startswith("Grade") and conformance.within(\n'
        "        conformance.J995_INCHES, sizes, metric=False\n"
        "    ):",
        'if not metric and grade.startswith("Grade"):',
        _SCOPE,
        "SAE J995 is claimed only for a nut line whose every size is 1/4 in to 1-1/2 in",
    ),
    (
        "an M3 or M4 nut claims ISO 898-2 again",
        _H,
        'if grade.startswith("Class") and conformance.within(\n'
        "        conformance.ISO_898_2_MM, sizes, metric=True\n"
        "    ):",
        'if metric and grade.startswith("Class"):',
        _SCOPE,
        "ISO 898-2 is claimed only for a nut line whose every size is M5 to M39",
    ),
    (
        "a line spanning the edge of a scope claims the standard for its in-scope sizes",
        _C,
        "return bool(diameters) and all(m is metric",
        "return bool(diameters) and any(m is metric",
        _SCOPE,
        "a nut line claims a grade standard only when every size it offers is in scope",
    ),
    (
        "a heavy hex nut is offered at every size of the finished table again",
        _N,
        "_HEAVY_HEX_FROM = {False: Fraction(1, 4), True: Fraction(12)}",
        "_HEAVY_HEX_FROM = {False: Fraction(0), True: Fraction(0)}",
        _HEAVY,
        "no heavy hex nut below 1/4 in or M12",
    ),
    (
        "the metric heavy hex floor drops to M8",
        _N,
        "True: Fraction(12)}",
        "True: Fraction(8)}",
        _HEAVY,
        "the structural heavy hex series starts at M12",
    ),
]

PREFIX = "nut size scope"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
