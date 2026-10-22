"""Mutation rows for the rules module and the decoy contract (gen#538), one per rule and clause.

Each row weakens one rule of ``prototypes/retail_drawings/rules.py`` (or one clause of
``decoy_contract.py``) so that it no longer finds the breach it exists for, and names the planted
breach that must then go unfound: the test that plants a breach of that rule fails. A row is
``(name, root, file, old, new, tests, property)``; ``root`` is relative to the repository.
"""

# ruff: noqa: E501  -- an anchor is the exact source line, so it cannot be wrapped
from __future__ import annotations

from mutation_row import Row

_RETAIL = "prototypes/retail_drawings"
_RULE = 'tests/test_rules_538.py -k "test_a_planted_breach_of_a_rule_is_found and {}"'
_CLAUSE = 'tests/test_feature_decoys_513.py -k "test_a_planted_decoy_file and {}"'
_RANGE = 'tests/test_feature_decoys_513.py -k "test_a_planted_toy_range_decoy and {}"'

ROWS: list[tuple[str, str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "the range-name rule ignores a color word in a range title",
        _RETAIL,
        "rules.py",
        '    if words(doc["title"]) & TITLE_COLORS:',
        "    if False:",
        _RULE.format("color_in_range_name"),
        "a range decoy whose name holds a color word is found (#444)",
    ),
    (
        "the two-color rule stops refusing an ampersand",
        _RETAIL,
        "rules.py",
        'for v in values if "/" in v or "&" in v',
        'for v in values if "/" in v',
        _RULE.format("blue_and_white"),
        "a color written 'Blue & White' is found (#514)",
    ),
    (
        "the dress rule stops asking the style table",
        _RETAIL,
        "rules.py",
        "    return list(style_table.violations(doc))",
        "    return []",
        _RULE.format("dress_neckline_by_length"),
        "a coat with a boat neck is found (#511)",
    ),
    (
        "the sentence-case rule stops comparing the form",
        _RETAIL,
        "rules.py",
        "if s and cased(s) != s]",
        "if False]",
        _RULE.format("sentence_case"),
        "a node or a name that is not its own sentence case is found (#499)",
    ),
    (
        "the one-key rule forgets the merged-away keys",
        _RETAIL,
        "rules.py",
        '            if e["key"] in REMOVED_KEYS | set(MERGED_AWAY):',
        '            if e["key"] in REMOVED_KEYS:',
        _RULE.format("one_key_per_concept"),
        "a key that was merged into another is found (#497)",
    ),
    (
        "the orange-shoes rule wants no style in an audience",
        _RETAIL,
        "rules.py",
        "            if n < 3:",
        "            if n < 0:",
        _RULE.format("orange_shoes"),
        "an audience with fewer than three orange trainer styles is found (#420)",
    ),
    (
        "the seed rule stops asking for the seed's words",
        _RETAIL,
        "rules.py",
        "    if not want <= (title if row.seed == seed else text):",
        "    if False:",
        _RULE.format("two_word_seeds"),
        "a seed decoy that lacks a word of the seed is found (#460, #461)",
    ),
    (
        "the contract stops comparing the title to the query",
        _RETAIL,
        "decoy_contract.py",
        "        elif not set(tokens(query)) & set(tokens(title)):",
        "        elif False:",
        _CLAUSE.format("title"),
        "a decoy file whose title lacks the query word fails the contract (#538)",
    ),
    (
        "the contract stops asking that a field contradicts the query",
        _RETAIL,
        "decoy_contract.py",
        "        if not exempt and matches(query, doc):",
        "        if False:",
        _CLAUSE.format("field"),
        "a decoy whose fields say it is the query fails the contract (#538)",
    ),
    (
        "the contract accepts any policy name",
        _RETAIL,
        "decoy_contract.py",
        "            if head not in POLICIES:",
        "            if False:",
        _CLAUSE.format("policy"),
        "a policy name no proof knows fails the contract (#538)",
    ),
    (
        "the contract lets a special policy name no sibling",
        _RETAIL,
        "decoy_contract.py",
        '            if head == "special" and not (name.strip() and row.sibling):',
        "            if False:",
        _CLAUSE.format("special"),
        "a special policy without a sibling query fails the contract (#538)",
    ),
    (
        "the contract stops drawing the product",
        _RETAIL,
        "decoy_contract.py",
        '            image_release.render(doc, doc["skus"][0])',
        "            pass",
        _CLAUSE.format("drawing"),
        "a decoy whose drawing does not render fails the contract (#538)",
    ),
    (
        "the range clause lets a toy title drop a query word",
        _RETAIL,
        "decoy_contract.py",
        "            if not query <= set(tokens(d.row.title)):",
        "            if False:",
        _RANGE.format("range_title"),
        "a toy range decoy whose title lacks a query word fails the contract (#446)",
    ),
    (
        "the range clause lets a toy query name its category leaf",
        _RETAIL,
        "decoy_contract.py",
        "            if query & set(tokens(d.row.path[-1])):",
        "            if False:",
        _RANGE.format("range_leaf"),
        "a toy range decoy whose query names its leaf fails the contract (#446)",
    ),
    (
        "the range clause lets two toy decoys share a query",
        _RETAIL,
        "decoy_contract.py",
        "            if d.query in seen:",
        "            if False:",
        _RANGE.format("range_unique"),
        "two toy range decoys with one query fail the contract (#446)",
    ),
    (
        "the range clause accepts a toy with one range decoy",
        _RETAIL,
        "decoy_contract.py",
        "        if len(sixes) < 2:",
        "        if False:",
        _RANGE.format("range_count"),
        "a toy with fewer than 2 range decoys fails the contract (#446)",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "rules 538"


def rows() -> list[Row]:
    return [Row(n, f, o, w, t, p, root) for n, root, f, o, w, t, p in ROWS]
