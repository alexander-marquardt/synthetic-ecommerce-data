"""Mutation rows for the coolant outlets and the capped crest pitch (gen#9), kept out of
``mutation_check.py``.

Each row breaks one line that turns a published ``Coolant Fed`` or ``Thread Type`` into a drawn
form, and names the tests that must go red. ``mutation_check.py`` turns them into ``Mutation``
rows named ``drawn forms: ...`` (``--only "drawn forms:"`` re-runs them). A row is
``(name, file, old, new, tests, property)``; the file is relative to the generator package.
"""

from __future__ import annotations

from mutation_row import Row

_COOLANT = ("tests/test_coolant_fed_drawn_9.py",)
_THREAD = ("tests/test_thread_type_drawn_9.py",)
_FIGURES = "domains/industrial/drawing/figures.py"
_PRIMITIVES = "domains/industrial/drawing/primitives.py"
_ENDMILL = "domains/industrial/geometry/endmill.py"
_THREAD_GEOM = "domains/industrial/geometry/thread.py"
_OUTLETS = "a Coolant Through mill shows one outlet per flute, any other none"
_RATIO = "a capped fine thread stays finer than the coarse one at their true ratio"

ROWS: list[tuple[str, str, str, str, tuple[str, ...], str]] = [
    (
        "the outlets are never drawn",
        _FIGURES,
        "    if geom.coolant:\n",
        "    if False:\n",
        _COOLANT,
        _OUTLETS,
    ),
    (
        "a published coolant is never carried into the fallbacks",
        _FIGURES,
        "form[COOLANT_ATTRIBUTE] = coolant",
        "pass",
        _COOLANT,
        _OUTLETS,
    ),
    (
        "every coolant value draws outlets",
        _ENDMILL,
        'coolant=COOLANT.get(str(record.get("Coolant Fed", "")).strip().lower(), False),',
        'coolant="Coolant Fed" in record,',
        _COOLANT,
        _OUTLETS,
    ),
    (
        "one outlet whatever the flute count",
        _PRIMITIVES,
        "    for k in range(int(flutes)):\n        angle = 2 * math.pi * k / flutes + hand",
        "    for k in range(1):\n        angle = 2 * math.pi * k / flutes + hand",
        _COOLANT,
        _OUTLETS,
    ),
    (
        "the cap is a fixed pitch again",
        _THREAD_GEOM,
        "return thread.pitch_in * max(shrink, floor / coarse_pitch_in(thread))",
        "return max(thread.pitch_in * shrink, floor)",
        _THREAD,
        _RATIO,
    ),
    (
        "the metric coarse pitch is never found",
        _THREAD_GEOM,
        'return row["coarse_pitch_mm"] / MM_PER_INCH',
        "pass",
        _THREAD,
        _RATIO,
    ),
    (
        "the unified coarse pitch is never found",
        _THREAD_GEOM,
        'return 1.0 / row["unc_tpi"]',
        "pass",
        _THREAD,
        _RATIO,
    ),
]

PREFIX = "drawn forms"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
