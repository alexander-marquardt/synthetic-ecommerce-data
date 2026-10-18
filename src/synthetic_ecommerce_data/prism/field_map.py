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

# The namespacing rule lives in the catalog layer, because a nested entry's ``key``
# applies it too: one rule for both, so the key and the field map cannot drift.
from synthetic_ecommerce_data.core.entry import STRUCTURAL_NAMES, canonical_name
from synthetic_ecommerce_data.prism.derive import (
    IDENTIFIER_ATTRIBUTES,
    IDENTIFIER_DISPERSION,
    MIN_PRESENCE,
    NUMERIC_SHARE,
    RANGE_DISPERSION,
    RANGE_MIN_DOCS,
    Decision,
    decide,
    measure,
)

# The rename (#125) keeps every build artifact byte-identical, this generated
# YAML included, so its text still names the pre-rename ``sip-generate``
# (a deprecated alias that still runs) and repository. They change with the
# first intended output change (#125 step 4), not before.
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
#     is per-attribute: an attribute carried by one of twelve product types can
#     never exceed ~10% of the catalog, yet may be the primary facet for its
#     own category.
#   * an attribute the generator declares an identifier ({identifiers}) is NOT
#     a facet, whatever its values measure: it is a part code.
#   * any other attribute over free-text values whose values do not repeat
#     across products is NOT a facet -- that is an identifier, not something a
#     shopper browses. Measured as {identifier_dispersion:.2f} or more distinct values per
#     distinct (product, value) pair, on at least {range_min_docs} distinct products: a
#     ratio, so a standards ladder stays a facet however large the catalog grows.
#     QUANTITATIVE attributes are exempt at any cardinality: a measured
#     quantity is not a part number.
#
# WHICH CONTROL AN ATTRIBUTE GETS
# -----------------------------------------------------------------------------
# Two questions, answered separately (elastic/prism#9285):
#
#   * an attribute is QUANTITATIVE when {numeric_share:.0%} or more of the documents
#     publishing it carry a parsed ``value_num``. The catalog deliberately
#     emits values that do not parse, so the test is a majority rather than
#     "all". This decides what is STORED -- the canonical number and its unit
#     code -- and nothing else.
#   * an attribute is offered as a RANGE (``facets_num.*``) only when its
#     values are CONTINUOUS: published on at least {range_min_docs} distinct products,
#     and at least {range_dispersion:.2f} distinct values per (product, value) pair. A
#     value repeated on a product's variants counts once, so the variant count
#     cannot move the answer. Below that the values
#     REPEAT, which means they are a standard set -- hex key sizes, thread
#     pitches -- and the honest control is a list of them (``facets.*``), not
#     an interval a shopper can set to a size nobody manufactures.
#
# The threshold is a midpoint between two limits, not a tuned constant:
# dispersion tends to 0 for a saturated ladder and to 1 when every measurement
# is unique. Deriving it this way is what lets ONE rule serve two catalogs --
# every dimensional attribute here is discrete, while a grocery catalog's
# ``Salt (g/100g)`` is a genuine continuum and would be offered as a range by
# the same code.
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
  # The name a shopper reads for that family (gen#331): ``product_type`` is a snake_case id on
  # an industrial product ("hammer_ball_pein"), which the catalogue repo keys its weights on.
  # Declared, not offered: which of the two a facet shows is the catalogue repo's decision.
  - name: product_type_label
    type: terms
    source: product_type_label
    facet: false

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
  # The SKU's own copy, which names what separates it from its siblings. This
  # is what renders under the title on a card, so it carries ``studio:
  # description``; ``parent_title`` used to, and a line title is the same
  # string on every SKU of the line -- six cards, six identical descriptions.
  - name: description
    type: text
    source: description
    searchable: true
    boost: 55
    studio: description
  - name: parent_title
    type: text
    source: parent_title
    searchable: true
    boost: 40
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
  # "realistic" for the census-modelled types, "fast_and_cheap" for the
  # breadth categories (alexander-marquardt/synthetic-industrial-products#34).
  # Excluded from BOTH search text and facets: it is a maintainer removal
  # handle, not something a shopper should be able to filter or match on --
  # ``tests/test_breadth.py`` checks it appears in neither.
  - name: spec_quality
    type: terms
    source: spec_quality
    facet: false

  # --- commerce -------------------------------------------------------------
  - name: price
    type: numeric
    source: price_usd
    facet: false
  - name: stock
    type: numeric
    source: stock
    facet: false
  # How the shown price is quoted ("Each", "Per Pack") and the multiple a SKU is
  # ordered in (gen#14): plain published fields on every SKU, not variants.
  - name: pricing_unit
    type: terms
    source: pricing_unit
    facet: false
  - name: order_multiple
    type: numeric
    source: order_multiple
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
    # The CONTROL follows continuity, not numeracy. A quantitative attribute
    # whose values are a discrete standard set is a terms facet over the
    # published strings -- which is why it reads ``facets.*`` and not
    # ``facets_num.*``: the shopper picks a published size, not an interval.
    kind = "numeric" if stats.is_continuous else "terms"
    source = f"facets_num.{stats.key}" if stats.is_continuous else f"facets.{stats.key}"
    lines = [
        f"  # {stats.name} -- {decision.reason}",
        f"  #   present on {stats.present} documents across "
        f"{len(stats.product_types)} product type(s); {stats.cardinality} distinct values",
        f"  - name: {canonical_name(stats.key)}",
        f"    type: {kind}",
        f"    source: {source}",
    ]
    if not decision.facet:
        lines.append("    facet: false")
    return "\n".join(lines)


def render(rows: Iterable[dict[str, Any]]) -> str:
    """Render the complete field map YAML for a catalog's flat documents."""
    measured = measure(rows)
    # Namespacing must not itself collide: two attributes may not land on one
    # canonical name, nor on a structural one.
    names = [canonical_name(key) for key in measured]
    clashes = sorted({n for n in names if names.count(n) > 1} | (set(names) & STRUCTURAL_NAMES))
    if clashes:
        raise ValueError(f"attribute canonical name(s) collide after namespacing: {clashes}")

    decided = [decide(stats) for stats in measured.values()]
    facets = [d for d in decided if d.facet]
    header = HEADER.format(
        attribute_count=len(decided),
        facet_count=len(facets),
        numeric_count=sum(1 for d in facets if d.stats.is_continuous),
        terms_count=sum(1 for d in facets if not d.stats.is_continuous),
        excluded_count=len(decided) - len(facets),
        min_presence=MIN_PRESENCE,
        identifier_dispersion=IDENTIFIER_DISPERSION,
        identifiers=", ".join(sorted(IDENTIFIER_ATTRIBUTES)),
        numeric_share=NUMERIC_SHARE,
        range_dispersion=RANGE_DISPERSION,
        range_min_docs=RANGE_MIN_DOCS,
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
