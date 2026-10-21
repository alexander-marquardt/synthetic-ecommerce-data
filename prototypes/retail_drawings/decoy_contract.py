"""What every authored decoy row must be, checked in one place (gen#538).

A decoy is data: a row that declares its ``query``, its class and its policy, in a file of
``feature_decoys/`` (:mod:`feature_decoys`) or in one of the two tables those files feed
(:mod:`decoy_rows`, :mod:`decoy_product_words`). This module reads every such row and returns one
note per breach of the contract; ``tests/test_feature_decoys_513.py`` asserts the list is empty
and plants a breach of each clause to show the test fails. A new decoy set therefore needs its
file and nothing else: no per-issue test restates what is checked here.

The clauses, for each row:

``id``
    The product id of a row is unique across both tables.
``title``
    The title carries a word of the query (class 7, whose word is only in the text and the
    ingredients, holds it there instead).
``field``
    A structured field contradicts the query: the product's type and its category leaf are not
    the query's noun in the query's color, so a filter on the true fields drops it. A row marked
    ``true_hit`` is the one that is meant to match, and is exempt.
``policy``
    A word-table row names a policy the proofs know (``category``, ``department``, ``color`` or
    ``special: <name>``), and a special one names the sibling query it is proved on.
``drawing``
    The product draws: its first SKU renders.

Decoys of :mod:`decoy_apparel` come from generated specs and carry their own contract.
"""

from __future__ import annotations

from typing import Any

import colorwords
from distractors import tokens

#: The policies a class-8 row may declare, before the ``:`` of a special one.
POLICIES = ("category", "department", "color", "special")

_COLOR_TOKENS = frozenset(w for c in colorwords.COLOR_WORDS for w in tokens(c))


def matches(query: str, doc: dict[str, Any]) -> bool:
    """Whether the document's own fields say it is what ``query`` asks for: the query's noun is
    its product type or its category leaf, and every color of the query is one of its SKUs'."""
    words = set(tokens(query))
    noun = words - _COLOR_TOKENS
    colors = words & _COLOR_TOKENS
    kinds = {frozenset(tokens(doc["product_type"])), frozenset(tokens(doc["category_leaf"]))}
    have = set(tokens(" ".join(s.get("color") or "" for s in doc["skus"])))
    return frozenset(noun) in kinds and colors <= have


def _rows() -> list[tuple[str, str, Any, bool]]:
    """``(product id, kind of table, row, exempt)`` for every authored row."""
    import decoy_product_words as dpw
    import decoy_rows

    out: list[tuple[str, str, Any, bool]] = [
        (f"PLT-D{r.code}", "decoy_rows", r, r.true_hit) for r in decoy_rows.TABLE
    ]
    out += [(f"PLT-{r.code}", "word", r, False) for r in dpw.ROWS if r.query]
    return out


def violations(templates: list[dict[str, Any]] | None = None) -> list[str]:
    """Red commit: the contract finds nothing (the implementation is the next commit)."""
    return []
