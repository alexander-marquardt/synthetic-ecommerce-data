"""Mutation rows for the closure and pattern check (gen#250), kept out of ``mutation_check.py``.

Each row plants one defect in ``attribute_text.py`` and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``attribute text: ...``
(``--only "attribute text:"`` re-runs them). A row is ``(name, old, new, test, property)``.
"""

from __future__ import annotations

ROWS: list[tuple[str, str, str, str, str]] = [
    (
        "a closure the text does not name goes unreported",
        "            if family not in named:",
        "            if False:",
        "magnetic_fastening_over_a_zip",
        "the text names the closure the attribute says",
    ),
    (
        "a zipped pocket counts as the closure",
        "text = NOT_A_CLOSURE.sub(\" \", f\"{rec['title']} {rec['description']}\")",
        "text = f\"{rec['title']} {rec['description']}\"",
        "zipped_pocket_is_not_the_closure",
        "a pocket is not a closure",
    ),
    (
        "a pocket phrase is only recognised right next to the word",
        "(?:\\w+\\s+){0,2}",
        "(?:\\w+\\s+){0,0}",
        "zipped_pocket_is_not_the_closure",
        "a pocket phrase may hold a word or two",
    ),
    (
        "an unlisted closure may name any closure word",
        "        extra = named - set(ALSO.get(value.lower(), {}))\n        if extra:",
        "        extra = set()\n        if extra:",
        "closure_word_over_an_unlisted_closure",
        "another closure names no closure word",
    ),
    (
        "a listed closure may name any closure word",
        "        extra = named - set(ALSO.get(value.lower(), {}))",
        "        extra = named",
        "listed_allowance_agrees",
        "a listed allowance agrees",
    ),
    (
        "a text with no closure word is read as naming none of its own",
        "        if not named:\n            continue\n",
        "",
        "text_without_a_closure_word",
        "a text that names no closure agrees",
    ),
    (
        "the magnetic words stop naming magnetic",
        '"magnetic": r"magnet|magnets|magnetic",',
        '"magnetic": r"magnet|magnets",',
        "magnetic_fastening_over_a_zip",
        "magnetic is a closure word",
    ),
    (
        "a color option of another pattern goes unreported",
        "        if sold - {kind}:",
        "        if False:",
        "polka_dot_style_that_sells_a_gingham",
        "every color sells the style's pattern",
    ),
    (
        "the drawing's pattern goes unchecked",
        "        if drawn is not None and drawn != kind:",
        "        if False:",
        "draws_another_pattern",
        "the drawing carries the style's pattern",
    ),
    (
        "the text's other pattern goes unreported",
        "        said = _named(",
        "        said = set() and _named(",
        "text_names_another_pattern",
        "the text names no other pattern",
    ),
    (
        "a gingham check may no longer say check",
        "        said -= PATTERN_ALSO.get(kind, set())\n",
        "",
        "gingham_check_agrees",
        "gingham is a check",
    ),
    (
        "an unmapped pattern is skipped, not reported",
        '            out.append(f"pattern {value} is not in PATTERN_KIND")\n            continue',
        "            continue",
        "unmapped_pattern_value",
        "an unmapped pattern is reported",
    ),
    (
        "polka dot maps to the gingham kind",
        '"polka dot": "polka",',
        '"polka dot": "gingham",',
        "polka_dot_style_that_sells_a_gingham",
        "polka dot is polka",
    ),
    (
        "the rows lose their pattern lines",
        "for line in closure_lines(rec) + pattern_lines(rec)",
        "for line in closure_lines(rec)",
        "disagreements_names_the_row",
        "both checks feed the metric",
    ),
    (
        "the rows lose their closure lines",
        "for line in closure_lines(rec) + pattern_lines(rec)",
        "for line in pattern_lines(rec)",
        "disagreements_names_the_row",
        "both checks feed the metric",
    ),
]
