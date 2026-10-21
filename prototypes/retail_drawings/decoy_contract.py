"""What every authored decoy row must be, checked in one place (gen#538).

A decoy is data: a row that declares its ``query``, its class and its policy, in a file of
``feature_decoys/`` (:mod:`feature_decoys`) or in one of the two tables those files feed
(:mod:`decoy_rows`, :mod:`decoy_product_words`). This module reads every such row and returns one
note per breach of the contract; ``tests/test_feature_decoys_513.py`` asserts the list is empty
and plants a breach of each clause to show the test fails. A new decoy set therefore needs its
file and nothing else: no per-issue test restates what is checked here.

The clauses, for each row:

``id``
    The product id of a row is unique across both tables. The build refuses a second row with an
    id (``type_registry.SpecError``) before a document is made, so this module holds no clause for
    it; ``tests/test_feature_decoys_513.py`` plants the clash to show the file is refused.
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


def range_violations(specs: dict[str, Any] | None = None) -> list[str]:
    """One note per breach of the ``range`` clause by a class-6 toy decoy (stub, gen#538)."""
    return []


def violations(templates: list[dict[str, Any]] | None = None) -> list[str]:
    """One note per breach of the contract, over every row of both decoy tables."""
    import image_release
    import scale

    docs = {d["product_id"]: d for d in templates or scale.templates(baseline=False)}
    found: list[str] = []
    for pid, table, row, exempt in _rows():
        doc = docs.get(pid)
        if doc is None:
            found.append(f"{pid}: no document is built for the row")
            continue
        title = row.title
        query = row.query
        if table == "decoy_rows" and row.cls == 7:
            text = f"{row.description} {' '.join(row.ingredients)}"
            if not set(tokens(query)) & set(tokens(text)):
                found.append(f"{pid}: the query word {query!r} is in no description or ingredient")
        elif not set(tokens(query)) & set(tokens(title)):
            found.append(f"{pid}: the title {title!r} lacks a word of the query {query!r}")
        if not exempt and matches(query, doc):
            found.append(f"{pid}: its fields say it is {query!r}, so it is no decoy of it")
        if table == "word":
            head, _, name = row.policy.partition(":")
            if head not in POLICIES:
                found.append(f"{pid}: the policy {row.policy!r} is not one of {POLICIES}")
            if head == "special" and not (name.strip() and row.sibling):
                found.append(f"{pid}: a special policy names itself and a sibling query")
        try:
            image_release.render(doc, doc["skus"][0])
        except Exception as error:  # noqa: BLE001 -- any failure to draw is the finding
            found.append(f"{pid}: the drawing does not render ({type(error).__name__}: {error})")
    return found
