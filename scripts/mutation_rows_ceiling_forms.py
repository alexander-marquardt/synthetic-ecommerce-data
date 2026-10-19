"""Mutation rows for the derived ceiling-light forms (gen#237, gen#401).

Each row plants one defect in ``lighting_rows.fit_ceiling_form`` or its call in ``scale.derive``
and names the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``ceiling forms: ...`` (``--only "ceiling forms:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_ceiling_forms_237.py"
_ROOT = "prototypes/retail_drawings"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a form that does not hang keeps its drop_length",
        "lighting_rows.py",
        "    if form not in HANGING_FORMS:\n",
        "    if False:\n",
        f'{_T} -k "drop_length"',
        "only a pendant or a chandelier has a drop_length",
        _ROOT,
    ),
    (
        "a flush light counts as hanging",
        "lighting_rows.py",
        'HANGING_FORMS = frozenset({"Pendant", "Chandelier"})',
        'HANGING_FORMS = frozenset({"Pendant", "Chandelier", "Flush"})',
        f'{_T} -k "drop_length"',
        "only a pendant or a chandelier has a drop_length",
        _ROOT,
    ),
    (
        "a chandelier loses its drop_length",
        "lighting_rows.py",
        'HANGING_FORMS = frozenset({"Pendant", "Chandelier"})',
        'HANGING_FORMS = frozenset({"Pendant"})',
        f'{_T} -k "keeps_the_drop"',
        "a chandelier hangs by a drop",
        _ROOT,
    ),
    (
        "a derived form keeps the pendant's title words",
        "lighting_rows.py",
        '    if form != "Pendant":\n',
        "    if False:\n",
        f'{_T} -k "title"',
        "a ceiling light's title names one form",
        _ROOT,
    ),
    (
        "a derived pendant loses its own title words",
        "lighting_rows.py",
        '    if form != "Pendant":\n',
        "    if True:\n",
        f'{_T} -k "own_qualifier"',
        "a pendant keeps its own dome or cluster word",
        _ROOT,
    ),
    (
        "the derivation does not fit the form",
        "scale.py",
        "    lighting_rows.fit_ceiling_form(rec)  # a flush light has no drop (gen#237)\n",
        "",
        f'{_T} -k "drop_length"',
        "a derived ceiling light is fitted to its form",
        _ROOT,
    ),
    (
        "a hanging form derived from a flush template gets no drop_length",
        "lighting_rows.py",
        "    elif not any(a[\"key\"] == \"drop_length\" for a in rec[\"attributes\"]):\n",
        "    elif False:\n",
        f'{_T} -k "carries_a_drop_length"',
        "a pendant or chandelier carries a drop_length whatever template it derives from",
        _ROOT,
    ),
    (
        "a derived chandelier is given a drop of zero",
        "lighting_rows.py",
        '_DEFAULT_DROP_CM = {"Pendant": 100, "Chandelier": 80}',
        '_DEFAULT_DROP_CM = {"Pendant": 100, "Chandelier": 0}',
        f'{_T} -k "carries_a_drop_length"',
        "a drop is a positive length",
        _ROOT,
    ),
    (
        "the authored chandelier drops its drop_length",
        "lighting_rows.py",
        '_cm("diameter", "Diameter", 60), _cm("drop_length", "Drop length", 80),',
        '_cm("diameter", "Diameter", 60),',
        f'{_T} -k "authored_hanging"',
        "every authored hanging ceiling light has a drop_length",
        _ROOT,
    ),
    (
        "a derived drop is appended after the shade",
        "lighting_rows.py",
        "    attributes.insert(after + 1, entry)\n",
        "    attributes.append(entry)\n",
        f'{_T} -k "among_the_templates_own_keys"',
        "the added drop follows the fixture's size, ahead of its shade",
        _ROOT,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "ceiling forms"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
