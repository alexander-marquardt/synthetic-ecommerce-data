"""Mutation rows for the tableware drawn features and the stainless steel material (gen#230).

Each row plants one defect and names the test that must go red. ``mutation_check.py`` turns them
into ``Mutation`` rows named ``tableware features: ...`` (``--only "tableware features:"``
re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_ROOT = "prototypes/retail_drawings"
_TEST = "tests/test_retail_tableware_drawn_features_230.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the bamboo board names a juice groove and its row stops asking for it",
        "tableware_rows.py",
        '        drawn=(("groove", "juice"),)),',
        "        ),",
        f'{_TEST} -k "names_a_feature_draws_it and groove"',
        "a title that names a juice groove draws one",
        _ROOT,
    ),
    (
        "the board draws its groove only on plastic",
        "kit_tableware.py",
        '    if groove:\n        out.append(',
        '    if groove == "plastic":\n        out.append(',
        f'{_TEST} -k "names_a_feature_draws_it and groove"',
        "a bamboo board with a groove in its title draws the groove",
        _ROOT,
    ),
    (
        "the ribbed highball row stops asking for ribs",
        "tableware_rows.py",
        '(("kind", "highball"), ("ribbed", "1"))',
        '(("kind", "highball"),)',
        f'{_TEST} -k "names_a_feature_draws_it and ribbed"',
        "a title that names ribs draws them",
        _ROOT,
    ),
    (
        "every tumbler draws ribs",
        "kit_tableware.py",
        "    if ribbed:\n        ribs = [",
        "    if True:\n        ribs = [",
        f'{_TEST} -k "does_not_name_the_feature and ribbed"',
        "the ribs are drawn for the title that names them, not for every tumbler",
        _ROOT,
    ),
    (
        "the utensil set darkens its heads again",
        "kit_tableware.py",
        "head, start = _utensil_head(kind, 0, top, paint)",
        "head, start = _utensil_head(kind, 0, top, _shade(fill.base, 0.3))",
        f'{_TEST} -k "utensil_set_paints_its_heads"',
        "a Cream utensil set draws cream heads",
        _ROOT,
    ),
    (
        "the single cutlery states the 18/10 grade in its material",
        "tableware_rows.py",
        '_a("material", "Material", "Stainless Steel"), _a("handle", "Handle", handle))',
        '_a("material", "Material", "Stainless Steel 18/10"), _a("handle", "Handle", handle))',
        f'{_TEST} -k "one_material_is_one_value"',
        "one metal is one material value in the facet",
        _ROOT,
    ),
    (
        "the steak knives state the 18/10 grade in their material",
        "distractor_rows.py",
        '("material", "Material", "Stainless Steel"),',
        '("material", "Material", "Stainless Steel 18/10"),',
        f'{_TEST} -k "one_material_is_one_value"',
        "one metal is one material value in the facet",
        _ROOT,
    ),
    (
        "the steak serving board names a juice groove and its row stops asking for it",
        "distractor_rows.py",
        '          params=(("material", "wood"), ("groove", "juice"))),',
        '          params=(("material", "wood"),)),',
        f'{_TEST} -k "every_template_that_names_a_juice_groove"',
        "a template of any file whose title names a juice groove draws one",
        _ROOT,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "tableware features"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
