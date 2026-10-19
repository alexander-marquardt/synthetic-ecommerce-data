"""Mutation rows for the one-letter-case rule (gen#499), kept out of ``mutation_check.py``.

Each row plants one defect in the normaliser or in a place that must call it, and names the
tests that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``letter case: ...`` (``--only "letter case:"`` re-runs them). A row is
``(name, root, file, old, new, tests, property)``; ``root`` is relative to the repository.
"""

# ruff: noqa: E501  -- an anchor is the exact source line, so it cannot be wrapped
from __future__ import annotations

from mutation_row import Row

_SRC = "src/synthetic_ecommerce_data"
_RETAIL = "prototypes/retail_drawings"
_T = "tests/test_letter_case_499.py"
_LC = "core/letter_case.py"

ROWS: list[tuple[str, str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "the industrial nested export stops applying the rule",
        _SRC,
        "core/emit.py",
        "    return letter_case.apply(_nested_document(catalog, line, base_url))",
        "    return _nested_document(catalog, line, base_url)",
        f"{_T} -k test_no_industrial",
        "the nested export is in sentence case",
    ),
    (
        "the industrial flat export stops applying the rule",
        _SRC,
        "core/emit.py",
        "        yield letter_case.apply({\n            \"sku\": child.sku,",
        "        yield ({\n            \"sku\": child.sku,",
        f"{_T} -k test_no_industrial",
        "the flat export is in sentence case",
    ),
    (
        "the retail export stops applying the rule",
        _RETAIL,
        "export.py",
        "    return letter_case.apply(doc | {",
        "    return (doc | {",
        f"{_T} -k test_no_retail",
        "the retail export is in sentence case",
    ),
    (
        "the searchable text carries the authored category case",
        _SRC,
        "core/emit.py",
        "        *(letter_case.sentence_case(node) for node in line.category),",
        "        *line.category,",
        f"{_T} -k searchable_text",
        "the searchable text agrees with the published category",
    ),
    (
        "a variant's attribute names keep their authored case",
        _SRC,
        _LC,
        '            variant | {"attributes": _renamed(variant["attributes"])} if "attributes" in variant',
        '            variant if "attributes" in variant',
        f"{_T} -k test_apply_renames",
        "variant attributes are renamed with the product's",
    ),
    (
        "the leaf stays on its authored case",
        _SRC,
        _LC,
        '        out["category_leaf"] = out["category_path"][-1]',
        '        out["category_leaf"] = doc["category_leaf"]',
        f"{_T} -k test_apply_takes_the_leaf",
        "the leaf is the last cased node",
    ),
    (
        "the published attribute_names stay in the authored case",
        _SRC,
        _LC,
        '        out["attribute_names"] = sorted({sentence_case(name) for name in doc["attribute_names"]})',
        '        out["attribute_names"] = doc["attribute_names"]',
        f"{_T} -k test_apply_renames",
        "the attribute_names list is renamed too",
    ),
    (
        "a code with a digit is lower-cased",
        _SRC,
        _LC,
        "    if any(ch.isdigit() for ch in part):\n        return True\n",
        "",
        f"{_T} -k M12x1",
        "a code keeps its capitals",
    ),
    (
        "a lone capital letter after the first word is lower-cased",
        _SRC,
        _LC,
        "    if part.isupper():",
        "    if False:",
        f"{_T} -k Steel",
        "a lone capital letter that names a shape keeps its capital",
    ),
    (
        "a capital inside a word is lower-cased",
        _SRC,
        _LC,
        "    return any(ch.isupper() for ch in part[1:])  # ``iPhone``",
        "    return False",
        f"{_T} -k iPhone",
        "a mixed-case word keeps its capitals",
    ),
    (
        "the trade name Torx loses its capital",
        _SRC,
        _LC,
        '    "torx": "Torx",  # a trade name: "Hex & Torx keys"\n',
        "",
        f"{_T} -k Torx",
        "the exception list keeps a trade name",
    ),
    (
        "a later word keeps its authored capitals",
        _SRC,
        _LC,
        "        return text.capitalize() if first else text.lower()",
        "        return text.capitalize() if first else text",
        f"{_T} -k test_sentence_case_of_a_string",
        "every later word is lower case",
    ),
    (
        "the bundle hands the drawing code the published names",
        _SRC,
        "core/bundle.py",
        "        name = (authored or {}).get(name, name)\n",
        "",
        "tests/test_sku_drawings.py -k a_drawing_that_moved",
        "the bundle looks attributes up by the name a type authored",
    ),
    (
        "the identifier declaration is read in its authored case",
        _SRC,
        "prism/derive.py",
        "IDENTIFIER_ATTRIBUTES = frozenset(sentence_case(n) for n in Generator.IDENTIFIER_ATTRIBUTES)",
        "IDENTIFIER_ATTRIBUTES = Generator.IDENTIFIER_ATTRIBUTES",
        "tests/test_facet_control_rule.py -k reads_the_generators",
        "the sidebar reads the published identifier names",
    ),
    (
        "the grocery coverage report matches the authored food root",
        _RETAIL,
        "grocery.py",
        '    food = sentence_case("Food & Drink")  # the published (sentence case) root, gen#499',
        '    food = "Food & Drink"',
        "tests/test_grocery_steak_grapes_296.py -k coverage_report",
        "the coverage report counts the food rows",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "letter case"


def rows() -> list[Row]:
    return [Row(n, f, o, w, t, p, root) for n, root, f, o, w, t, p in ROWS]
