"""Derive a PRISM field map from the generated catalog.

The catalog publishes 77 distinct attribute names across 12 product types, and
a PRISM field map has to declare every one it wants searchable or faceted. A
hand-maintained list of 77 declarations drifts from the generator the first
time the generator changes, and the drift is silent: a field map that names an
attribute the catalog stopped publishing does not fail, it just stops
faceting, and nothing downstream can tell that from "no product has that
value".

So the field map is DERIVED from the emitted documents -- the same
``emit.iter_flat`` output that gets indexed -- and the committed copy is
checked against a fresh derivation by a test. Changing either side alone reds
that test.

Attribute statistics are measured against the emitted flat documents rather
than the generator's configuration, because the field map describes the
INDEXED shape. An attribute the generator knows about but never emits has no
field to declare.
"""

from __future__ import annotations

import collections
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

#: An attribute is a NUMERIC range facet if this share of the documents that
#: publish it carry a parsed ``value_num``. Below it the attribute is a terms
#: facet over the published strings. The catalog deliberately emits values
#: that do not parse (a ``Helix Angle`` of ``42"`` has no angle in it), so the
#: test is a majority rather than "any" or "all".
NUMERIC_SHARE = 0.5

#: An attribute must appear on this share of the documents belonging to the
#: product types that publish it AT ALL. The denominator is per-attribute on
#: purpose: an attribute carried by one of twelve product types can never exceed
#: ~10% of the whole catalog, yet it may be the primary facet for its own
#: category. Measured against the whole catalog every category-specific
#: attribute would fail, and the sidebar for a washer would be empty.
MIN_PRESENCE = 0.5

#: Cap on the number of distinct values a TERMS facet may carry. This
#: separates a facet from an identifier: ``Thread Size`` publishes 19 distinct
#: values over 331 documents and is the first thing a shopper filters on,
#: while ``List Number`` publishes 110 over 919 and is a manufacturer's part
#: reference that no one browses. Numeric attributes are exempt -- a range
#: facet's cost does not grow with the number of distinct values.
MAX_TERMS_CARDINALITY = 25


@dataclass(frozen=True)
class AttributeStats:
    """What the emitted documents say about one attribute name."""

    key: str
    name: str
    present: int
    numeric: int
    cardinality: int
    product_types: tuple[str, ...]
    type_denominator: int

    @property
    def numeric_share(self) -> float:
        return self.numeric / self.present

    @property
    def presence(self) -> float:
        return self.present / self.type_denominator

    @property
    def is_numeric(self) -> bool:
        return self.numeric_share >= NUMERIC_SHARE


@dataclass
class Decision:
    """Whether an attribute becomes a facet, and the measured reason."""

    stats: AttributeStats
    facet: bool
    reason: str


def measure(rows: Iterable[dict[str, Any]]) -> dict[str, AttributeStats]:
    """Collect per-attribute statistics from emitted flat documents."""
    present: collections.Counter[str] = collections.Counter()
    numeric: collections.Counter[str] = collections.Counter()
    values: dict[str, set[str]] = collections.defaultdict(set)
    types: dict[str, set[str]] = collections.defaultdict(set)
    published_name: dict[str, str] = {}
    type_sizes: collections.Counter[str] = collections.Counter()

    for row in rows:
        product_type = row["product_type"]
        type_sizes[product_type] += 1
        for key, vals in row["facets"].items():
            present[key] += 1
            values[key].update(vals)
            types[key].add(product_type)
        for key in row["facets_num"]:
            numeric[key] += 1
        # The published spelling is what a shopper sees on the facet heading.
        # Take it from the attribute entries, which carry the name verbatim.
        for attribute in row["attributes"]:
            published_name.setdefault(_sanitize(attribute["name"]), attribute["name"])

    return {
        key: AttributeStats(
            key=key,
            name=published_name.get(key, key),
            present=count,
            numeric=numeric[key],
            cardinality=len(values[key]),
            product_types=tuple(sorted(types[key])),
            type_denominator=sum(type_sizes[t] for t in types[key]),
        )
        for key, count in sorted(present.items())
    }


def _sanitize(name: str) -> str:
    from ..catalog.emit import sanitize

    return sanitize(name)


def decide(stats: AttributeStats) -> Decision:
    """Apply the facet rule to one attribute, recording which gate decided it.

    The reason string is part of the committed artifact: a field map that says
    only ``facet: false`` invites someone to flip it, while one that says
    ``single-valued`` explains why flipping it would add a control that cannot
    narrow anything.
    """
    if stats.cardinality < 2:
        return Decision(stats, False, "single-valued: clicking it cannot narrow the result set")
    if stats.presence < MIN_PRESENCE:
        return Decision(
            stats,
            False,
            f"present on {stats.presence:.0%} of its product types' documents "
            f"(floor {MIN_PRESENCE:.0%})",
        )
    if not stats.is_numeric and stats.cardinality > MAX_TERMS_CARDINALITY:
        return Decision(
            stats,
            False,
            f"{stats.cardinality} distinct values reads as an identifier, not a facet "
            f"(cap {MAX_TERMS_CARDINALITY})",
        )
    if stats.is_numeric:
        return Decision(
            stats,
            True,
            f"numeric on {stats.numeric_share:.0%} of {stats.present} documents",
        )
    return Decision(stats, True, f"{stats.cardinality} distinct values")
