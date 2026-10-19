"""Mutation rows for the product-type label every product carries, and the labels on a type's own spec.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- every product carries a readable product_type_label (gen#331) ----
    Mutation(
        "label: the hammer kind loses its label",
        "domains/industrial/type_labels.py",
        '    "hammer_claw": "Claw Hammer",\n',
        "",
        "tests/test_product_type_label_331.py -k every_emitted_type_has_a_label",
        "",
        "every emitted type has a label",
    ),
    Mutation(
        "label: a label keeps its id's underscore",
        "domains/industrial/type_labels.py",
        '"nut_hex": "Hex Nut"',
        '"nut_hex": "Hex_Nut"',
        "tests/test_product_type_label_331.py -k no_label_is_an_id",
        "",
        "no label reads as a field name",
    ),
    Mutation(
        "label: a label starts in lower case",
        "domains/industrial/type_labels.py",
        '"nut_hex": "Hex Nut"',
        '"nut_hex": "hex Nut"',
        "tests/test_product_type_label_331.py -k starts_with_a_capital",
        "",
        "every label starts with a capital letter",
    ),
    Mutation(
        "label: two types share one label",
        "domains/industrial/type_labels.py",
        '"hammer_club": "Club Hammer"',
        '"hammer_club": "Claw Hammer"',
        "tests/test_product_type_label_331.py -k a_label_names_one_type",
        "",
        "a label names one type",
    ),
    Mutation(
        "label: the industrial generator builds a line with no label",
        "domains/industrial/finishing.py",
        "            type_label=label_for(type_key),\n",
        "",
        "tests/test_product_type_label_331.py -k documents_carry_the_label",
        "",
        "an industrial document carries its label",
    ),
    Mutation(
        "label: the flat document drops the label",
        "core/emit.py",
        '            "product_type_label": line.type_label,\n            "title": child.title,',
        '            "title": child.title,',
        "tests/test_product_type_label_331.py -k documents_carry_the_label",
        "",
        "an industrial document carries its label",
    ),
    Mutation(
        "label: a retail label drifts from its type",
        "prototypes/retail_drawings/export.py",
        '        "product_type_label": product_type,',
        '        "product_type_label": product_type.lower(),',
        "tests/test_product_type_label_331.py -k retail_product_is_labelled",
        "",
        "a retail label is its type",
        root=".",
    ),
    Mutation(
        "label: the standard stops requiring the label",
        "core/standard.py",
        '    "product_type_label": (_STR, True),',
        '    "product_type_label": (_STR, False),',
        "tests/test_product_type_label_331.py -k standard_requires_the_label",
        "",
        "a product without a label is refused",
    ),
    # ---- labels on the type's own spec: two type PRs share no line (#103) ----
    Mutation(
        "labels: a label in the table and on the spec is accepted",
        "domains/industrial/type_labels.py",
        "    if dict.__contains__(PRODUCT_TYPE_LABELS, spec.key):",
        "    if False:",
        "tests/test_type_registration.py::test_a_label_in_the_table_and_on_the_spec_is_refused",
        "",
        "a label is declared once",
    ),
    Mutation(
        "labels: register drops the label a spec declares",
        "domains/industrial/type_labels.py",
        "    PRODUCT_TYPE_LABELS[spec.key] = spec.label",
        "    pass",
        "tests/test_type_registration.py::test_a_label_on_the_spec_joins_the_label_table",
        "",
        "a type's label on its spec reaches every product",
    ),
    Mutation(
        "labels: the steps of a new type are a numbered list again",
        "docs/adding-a-type.md",
        "- **Module.** Write the module.",
        "1. Write the module.",
        "tests/test_adding_a_type_doc_103.py::test_the_steps_of_a_new_type_are_named_items",
        "",
        "an inserted step renumbers no neighbour",
        root=".",
    ),
]

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: labels"


def rows() -> list[Mutation]:
    return MUTATIONS
