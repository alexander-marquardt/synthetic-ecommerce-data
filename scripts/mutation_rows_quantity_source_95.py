"""Mutation rows for the generator's tabled-or-drawn declaration (gen#95).

Each row plants one defect in the reader of ``AttrSpec.source`` or in the declaration, and names
the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``quantity source: ...`` (``--only "quantity source:"`` re-runs them). A row is
``(name, root, file, old, new, tests, property)``; ``root`` is relative to the repository.
"""

# ruff: noqa: E501  -- an anchor is the exact source line, so it cannot be wrapped
from __future__ import annotations

from mutation_row import Row

_SRC = "src/synthetic_ecommerce_data"
_T = "tests/test_facet_control_rule.py"

ROWS: list[tuple[str, str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "the control ignores the declaration and reads the ratio and the floor",
        _SRC,
        "prism/derive.py",
        "        if self.declared_source is not None:\n            return self.declared_source == \"drawn\"\n",
        "",
        (
            f"{_T} -k declared_drawn_quantity_is_a_range",
            f"{_T} -k declared_tabled_quantity_is_a_list",
        ),
        "a declared quantity is a range or a list by the generator's word",
    ),
    (
        "a tabled quantity is called a range",
        _SRC,
        "prism/derive.py",
        "            return self.declared_source == \"drawn\"\n",
        "            return self.declared_source != \"drawn\"\n",
        (
            f"{_T} -k declared_drawn_quantity_is_a_range",
            f"{_T} -k declared_tabled_quantity_is_a_list",
        ),
        "drawn is a range and tabled is a list",
    ),
    (
        "a keyword attribute declares a source",
        _SRC,
        "prism/derive.py",
        "            if spec.kind != \"keyword\":\n",
        "            if True:\n",
        f"{_T} -k two_types_declare_differently",
        "only a quantity declares how it is made",
    ),
    (
        "a name two types declare differently still declares",
        _SRC,
        "prism/derive.py",
        "if len(sources) == 1}",
        "if len(sources) >= 1}",
        f"{_T} -k two_types_declare_differently",
        "a mixed name is left to the ratio",
    ),
    (
        "the declaration is read in its authored case",
        _SRC,
        "prism/derive.py",
        "            if spec.kind != \"keyword\":\n                seen[sentence_case(spec.name)].add(spec.source)",
        "            if spec.kind != \"keyword\":\n                seen[spec.name].add(spec.source)",
        (
            f"{_T} -k two_types_declare_differently",
            f"{_T} -k every_quantity_this_catalog_publishes_is_declared",
        ),
        "the sidebar reads the published quantity names",
    ),
    (
        "the end mill's drawn neck length is declared tabled",
        _SRC,
        "domains/industrial/vocab.py",
        "    _spec(\"Neck Length\", \"sku\", 0.27, kind=\"length\", source=\"drawn\"),",
        "    _spec(\"Neck Length\", \"sku\", 0.27, kind=\"length\"),",
        (
            f"{_T} -k reads_the_generators_quantity_declaration",
            f"{_T} -k every_declaration_agrees_with_the_data",
        ),
        "the declaration says what the builder does",
    ),
    (
        "a spec may name any source",
        _SRC,
        "domains/industrial/vocab.py",
        "        if self.source not in SOURCES:\n",
        "        if False:\n",
        f"{_T} -k source_other_than_tabled_or_drawn",
        "a source is tabled or drawn",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "quantity source"


def rows() -> list[Row]:
    return [Row(n, f, o, w, t, p, root) for n, root, f, o, w, t, p in ROWS]
