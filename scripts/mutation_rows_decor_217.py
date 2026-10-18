"""Mutation rows for the home accessories and decor types of gen#217, in their own file.

Each row plants one defect in a spec, a drawing parameter, a decoy or the wiring of gen#217 and
names the test that must go red. ``mutation_check.py`` turns them into rows named ``decor 217: ...``
(``--only "decor 217:"`` re-runs them). A row is ``(name, file, old, new, test, property)`` and
``file`` is under ``prototypes/retail_drawings``.
"""

# ruff: noqa: E501  (a removal row quotes the whole decoy call it takes out)
from __future__ import annotations

_T = "tests/test_retail_decor_217.py"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the wedge door stop draws as a weighted one",
        "type_specs/door_stop.py",
        'params=(("kind", "wedge"),)),',
        'params=(("kind", "weighted"),)),',
        f"{_T} -k a_style_names_the_reading",
        "two door stops that differ on the kind carry different drawing params",
    ),
    (
        "the wallpaper roll length is not a structured entry",
        "export.py",
        '"roll_length_m": ("roll_length", "Roll length", "MTR"),',
        '"roll_length_m": ("roll_len", "Roll length", "MTR"),',
        f"{_T} -k key_attribute_is_a_structured_entry",
        "a wallpaper's roll length is a structured attribute of its SKUs",
    ),
    (
        "the stems lose their second decoy",
        "decor_rows.py",
        '"Long Stem Wine Glass"',
        '"Wine Glass"',
        f"{_T} -k text_match_decoys_that_tell_the_truth",
        "every decor type carries at least two text-match decoys whose title holds its word",
    ),
    (
        "the clock loses a decoy",
        "decor_rows.py",
        '_decoy("DCYCLW", "Clockwork Robot"',
        '_decoy("DCYCLW", "Wind Up Robot"',
        f"{_T} -k text_match_decoys_that_tell_the_truth",
        "a clock search meets a toy robot and a cushion on the word alone",
    ),
    (
        "the decoys are no longer exempt from the text check",
        "scale.py",
        "| garden_rows.decoy_ids()\n             | decor_rows.decoy_ids() | neckline_rows.decoy_ids())",
        "| garden_rows.decoy_ids() | neckline_rows.decoy_ids())",
        f"{_T} -k decoys_are_templates",
        "a decor decoy is exempt from the output standard's text check",
    ),
    (
        "the decor decoys are derived",
        "scale.py",
        "| GARDEN_IDS | DECOR_IDS | NIKE_IDS",
        "| GARDEN_IDS | NIKE_IDS",
        f"{_T} -k decoys_are_templates",
        "the derivation leaves the decor decoys alone",
    ),
    (
        "the watch loses its alarm clock decoy",
        "type_specs/digital_watch.py",
        '"Digital Watch with Alarm Clock"',
        '"Digital Watch with Alarm"',
        f"{_T} -k a_watch_carries_the_word_clock",
        "a clock search can meet a watch whose text names a clock",
    ),
]
