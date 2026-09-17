"""Render the derived field map as the YAML PRISM loads.

The rendering is deterministic -- same catalog in, byte-identical YAML out --
because a drift test compares the committed file against a fresh render and a
test that reports a diff in key ORDER teaches everyone to ignore it.

The file is written by hand rather than through ``yaml.dump`` so that the
generated artifact can carry the measured reason for every decision as a
comment beside the entry it explains. A reviewer asking "why is Rockwell
Hardness not a facet?" gets the answer in the file, with the number that
decided it.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .derive import (
    MAX_TERMS_CARDINALITY,
    MIN_PRESENCE,
    NUMERIC_SHARE,
    Decision,
    decide,
    measure,
)

#: PRISM canonical names taken by the document's first-class columns. An
#: attribute that sanitises onto one of these would silently redefine a
#: structural field, so the renderer refuses rather than emitting it.
STRUCTURAL_NAMES = frozenset(
    {
        "id",
        "sku",
        "product_id",
        "product_type",
        "title",
        "parent_title",
        "brand",
        "brand_search",
        "series",
        "series_search",
        "categories",
        "category_path_joined",
        "category_leaf",
        "dimension_provenance",
        "price",
        "stock",
        "attribute_names",
        "fulltext",
    }
)

HEADER = """\
# =============================================================================
# Field map -- synthetic industrial catalog, FLAT shape
# =============================================================================
#
# GENERATED FILE -- do not edit by hand.
#
#     uv run sip-generate build --out out/catalog
#
# rewrites it from the catalog it just emitted, and
# ``tests/test_prism_field_map_drift.py`` fails if this file and a fresh
# derivation disagree. Editing this file alone reds that test; changing the
# generator without rebuilding reds it too, which is the point -- the catalog
# publishes {attribute_count} distinct attribute names and a hand-maintained list
# of {attribute_count} declarations drifts from the data the first time either side moves.
#
# WHICH ATTRIBUTES BECOME FACETS
# -----------------------------------------------------------------------------
# Three measured gates, applied to the emitted documents -- not chosen by eye:
#
#   * an attribute with fewer than 2 distinct values is NOT a facet. Clicking
#     it cannot narrow the result set, so it is a control that does nothing.
#   * an attribute present on fewer than {min_presence:.0%} of the documents belonging to
#     the product types that publish it AT ALL is NOT a facet. The denominator
#     is per-attribute: an attribute carried by one of ten product types can
#     never exceed ~10% of the catalog, yet may be the primary facet for its
#     own category.
#   * a TERMS attribute with more than {max_cardinality} distinct values is NOT a facet --
#     that is an identifier, not something a shopper browses. Numeric
#     attributes are exempt; a range control's cost does not grow with the
#     number of distinct values.
#
# An attribute is NUMERIC (a range facet over ``facets_num.*``) when {numeric_share:.0%} or
# more of the documents publishing it carry a parsed ``value_num``, and TERMS
# (over the published strings in ``facets.*``) otherwise. The catalog
# deliberately emits values that do not parse, so the test is a majority
# rather than "all".
#
# Attributes that fail a gate are still DECLARED, with ``facet: false``. They
# stay searchable and stay available as filter and rule targets -- they are
# simply not offered as sidebar controls. Dropping them from the map entirely
# would make them unreachable, which is a bigger loss than an unhelpful facet.
#
# MEASURED OUTCOME
# -----------------------------------------------------------------------------
#   attributes declared      {attribute_count}
#   offered as facets        {facet_count}  ({numeric_count} numeric ranges, {terms_count} terms)
#   declared, not faceted    {excluded_count}
# =============================================================================

field_map_version: 1
"""


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _structural_fields() -> list[str]:
    """The document's first-class columns, hand-written because they are not
    attributes -- they are the shape ``emit.flat_documents`` always writes.
    """
    return [
        """\
  # --- identity -------------------------------------------------------------
  - name: id
    type: id
    source: sku
    studio: id_ui
  - name: sku
    type: terms
    source: sku
    facet: false
  - name: product_id
    type: terms
    source: product_id
    facet: false
  # The product family. Ten values over the whole catalog, on every document:
  # the one facet that is always worth offering.
  - name: product_type
    type: terms
    source: product_type

  # --- searchable text ------------------------------------------------------
  # ``text`` concatenates the title, brand, series, category and EVERY
  # attribute value. The demo case depends on it: a query for a bare dimension
  # token has to reach a product whose SHANK -- not whose cutting diameter --
  # carries that value, and that can only happen if the shank's published
  # value is searchable as text.
  - name: title
    type: text
    source: title
    searchable: true
    boost: 100
    studio: title
  - name: parent_title
    type: text
    source: parent_title
    searchable: true
    boost: 40
    studio: description
  - name: fulltext
    type: text
    source: text
    searchable: true
    boost: 8
    fulltext_filter: true

  # --- line attributes ------------------------------------------------------
  # ``brand`` and ``series`` are keywords, so the facet entry points at the
  # keyword and a separate searchable entry points at the analysed ``.text``
  # sub-field. A multi_match against the keyword alone would only match a
  # brand typed in full, verbatim.
  - name: brand
    type: terms
    source: brand
  - name: brand_search
    type: text
    source: brand.text
    searchable: true
    boost: 60
  - name: series
    type: terms
    source: series
  - name: series_search
    type: text
    source: series.text
    searchable: true
    boost: 40
  # Category is a ``/``-joined root-to-leaf path, built at load time from the
  # ``category_path`` array (see ``prism/index.py``). Every product line sits
  # on exactly one chain -- the generator builds the path from a single
  # taxonomy node -- so ``paths_form_tree`` is true, and the engine re-checks
  # that against the live catalog at every boot.
  - name: categories
    type: hierarchy
    source: category_path_joined
    path_separator: "/"
    display_separator: " > "
    paths_form_tree: true
  - name: dimension_provenance
    type: terms
    source: dimension_provenance

  # --- commerce -------------------------------------------------------------
  - name: price
    type: numeric
    source: price_usd
    facet: false
  - name: stock
    type: numeric
    source: stock
    facet: false

  # --- attribute inventory --------------------------------------------------
  # Which attribute NAMES a document publishes, as a facet-free keyword list.
  # This is what makes "which attributes does this category use?" answerable
  # without walking every document.
  - name: attribute_names
    type: terms
    source: attribute_names
    facet: false
"""
    ]


def _attribute_entry(decision: Decision) -> str:
    stats = decision.stats
    kind = "numeric" if stats.is_numeric else "terms"
    source = f"facets_num.{stats.key}" if stats.is_numeric else f"facets.{stats.key}"
    lines = [
        f"  # {stats.name} -- {decision.reason}",
        f"  #   present on {stats.present} documents across "
        f"{len(stats.product_types)} product type(s); {stats.cardinality} distinct values",
        f"  - name: {stats.key}",
        f"    type: {kind}",
        f"    source: {source}",
    ]
    if not decision.facet:
        lines.append("    facet: false")
    return "\n".join(lines)


def render(rows: Iterable[dict[str, Any]]) -> str:
    """Render the complete field map YAML for a catalog's flat documents."""
    measured = measure(rows)
    collisions = sorted(set(measured) & STRUCTURAL_NAMES)
    if collisions:
        raise ValueError(
            "attribute name(s) collide with a structural field and would "
            f"silently redefine it: {collisions}. Rename the structural field "
            "in field_map.STRUCTURAL_NAMES and in _structural_fields()."
        )

    decided = [decide(stats) for stats in measured.values()]
    facets = [d for d in decided if d.facet]
    header = HEADER.format(
        attribute_count=len(decided),
        facet_count=len(facets),
        numeric_count=sum(1 for d in facets if d.stats.is_numeric),
        terms_count=sum(1 for d in facets if not d.stats.is_numeric),
        excluded_count=len(decided) - len(facets),
        min_presence=MIN_PRESENCE,
        max_cardinality=MAX_TERMS_CARDINALITY,
        numeric_share=NUMERIC_SHARE,
    )

    parts = [header, "fields:\n"]
    parts.extend(_structural_fields())
    parts.append(
        "\n  # --- catalog attributes "
        "---------------------------------------------------\n"
        "  # Derived from the emitted documents, in sanitised-key order. Every\n"
        "  # entry's comment carries the measurement that placed it.\n"
    )
    parts.append("\n".join(_attribute_entry(d) for d in decided))
    parts.append(
        "\n\n"
        "# The phrase boost goes on the title: an exact phrase in a product\n"
        "# title is a much stronger signal than the same phrase somewhere in\n"
        "# the concatenated attribute text.\n"
        "phrase_boost_field: title\n"
    )
    return "".join(parts)
