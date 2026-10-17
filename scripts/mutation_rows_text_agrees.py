"""Mutation rows for the title and description coherence check on industrial (gen#139), kept out of
``mutation_check.py``.

Each row loosens or breaks one rule of ``standard.text_contradictions`` or the hammer decoy
predicate, and names the tests that must go red. ``mutation_check.py`` turns them into
``Mutation`` rows named ``text agrees: ...`` (``--only "text agrees:"`` re-runs them). A row is
``(name, file, old, new, tests, property)``; every file is under ``src/synthetic_ecommerce_data``.
"""

# ruff: noqa: E501  (a row's old and new text are source lines, as written)
from __future__ import annotations

_T = "tests/test_text_agrees_139.py"
_SILENT = f"{_T}::test_the_false_positive_is_silent"
_PLANTED = f"{_T}::test_a_true_incoherence_planted_on_the_same_doc_is_still_reported"
_STANDARD = "core/standard.py"
_HAMMERS = "domains/industrial/hammers.py"

ROWS: list[tuple[str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "a comparison is a claim again",
        _STANDARD,
        'padded = words(_REFERENCE.sub(" | ", text))',
        "padded = words(text)",
        (f"{_SILENT} -k comparison", f"{_SILENT} -k equivalence", f"{_SILENT} -k tolerance"),
        "a comparison, an equivalence and a tolerance class name a value without claiming it",
    ),
    (
        "every sentence is a reference",
        _STANDARD,
        'padded = words(_REFERENCE.sub(" | ", text))',
        'padded = words(" | ")',
        f"{_PLANTED} -k comparison",
        "a true incoherence beside a comparison is still reported",
    ),
    (
        "a value inside the doc's own value is a claim again",
        _STANDARD,
        "if not any(_names(own_value, v) for own_value in padded_own)",
        "if True",
        (f"{_SILENT} -k inside-own-value", f"{_SILENT} -k words-of-own-value"),
        "a pool value whose words sit inside the doc's own value contradicts nothing",
    ),
    (
        "every pool value is exempt",
        _STANDARD,
        "if not any(_names(own_value, v) for own_value in padded_own)",
        "if False",
        f"{_PLANTED} -k inside-own-value",
        "a pool value outside the doc's own values is still a contradiction",
    ),
    (
        "'than' is no longer a comparison cue",
        _STANDARD,
        r'r"\b(?:than|equivalent to)\b(?:[^.;]|\.(?=\d))*',
        r'r"\b(?:equivalent to)\b(?:[^.;]|\.(?=\d))*',
        (f"{_SILENT} -k comparison",),
        "'Higher strength than Grade 5' on a Grade 8 nut names no contradiction",
    ),
    (
        "'equivalent to' is no longer a cue",
        _STANDARD,
        r'r"\b(?:than|equivalent to)\b(?:[^.;]|\.(?=\d))*',
        r'r"\b(?:than)\b(?:[^.;]|\.(?=\d))*',
        (f"{_SILENT} -k equivalence",),
        "'Equivalent to DIN 912 / ISO 4762' names no contradiction",
    ),
    (
        "a tolerance class in parentheses is a claim again",
        _STANDARD,
        r"|\([^()]*\bclass\)",
        r"|\(\)",
        (f"{_SILENT} -k tolerance-class",),
        "'(ISO 492 Normal class)' names no contradiction",
    ),
    (
        "a decimal point ends a comparison",
        _STANDARD,
        r"(?:[^.;]|\.(?=\d))*",
        r"[^.;]*",
        (f"{_SILENT} -k comparison-decimal-grade",),
        "'Class 8.8' inside a comparison does not end it at the point",
    ),
    (
        "a comparison runs past its sentence",
        _STANDARD,
        r"(?:[^.;]|\.(?=\d))*",
        r"(?:[^;]|\.(?=\d))*",
        (f"{_PLANTED} -k comparison",),
        "a true incoherence in the sentence after a comparison is still reported",
    ),
    (
        "the material-look decoy is no decoy",
        _HAMMERS,
        "(_CATEGORY_WORD, _MATERIAL_LOOK, INCIDENTAL_PHRASE)",
        "(_CATEGORY_WORD, INCIDENTAL_PHRASE)",
        (
            f"{_T}::test_the_decoy_title_predicate -k look",
            f"{_T}::test_the_industrial_golden_has_no_contradicting_text",
        ),
        "a 'Hickory-Look' title is a decoy, exempt by id",
    ),
    (
        "the category-word decoy is no decoy",
        _HAMMERS,
        "(_CATEGORY_WORD, _MATERIAL_LOOK, INCIDENTAL_PHRASE)",
        "(_MATERIAL_LOOK, INCIDENTAL_PHRASE)",
        (
            f"{_T}::test_the_decoy_title_predicate -k series",
            f"{_T}::test_the_industrial_golden_has_no_contradicting_text",
        ),
        "a 'Sledge Series' title is a decoy, exempt by id",
    ),
    (
        "the incidental-word decoy is no decoy",
        _HAMMERS,
        "(_CATEGORY_WORD, _MATERIAL_LOOK, INCIDENTAL_PHRASE)",
        "(_CATEGORY_WORD, _MATERIAL_LOOK)",
        (
            f"{_T}::test_the_decoy_title_predicate -k creek",
            f"{_T}::test_the_industrial_golden_has_no_contradicting_text",
        ),
        "a 'Hickory Creek' title is a decoy, exempt by id",
    ),
    (
        "every hammer is a decoy",
        _HAMMERS,
        'is_decoy_title(str(d.get("title") or ""))',
        "True",
        f"{_T}::test_a_hammer_that_is_no_decoy_is_still_checked",
        "an ordinary hammer is still checked: the exemption is the decoys', not the leaf's",
    ),
    (
        "the framing use line says a milled face of every framing hammer again",
        _HAMMERS,
        '"The face grips the nail head; the straight claw pries and pulls.",',
        '"The milled face grips the nail head; the straight claw pries and pulls.",',
        f"{_T}::test_a_use_line_says_milled_only_of_a_kind_whose_every_face_is_milled",
        "a smooth-faced framing hammer is not described as milled",
    ),
]
