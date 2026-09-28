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

Two separate questions
----------------------
This module answers three questions about each attribute and keeps them
apart, because collapsing two of them is the defect elastic/prism#9285
records:

1. **Is it a facet at all?** :func:`decide`, from cardinality and presence.
2. **Are its values numbers?** :attr:`AttributeStats.is_numeric`. This governs
   what is STORED -- the canonical number and its unit code stay in the nested
   child whatever else happens.
3. **Is it offered as a RANGE?** :attr:`AttributeStats.is_continuous`. This
   governs what is PUBLISHED to a shopper.

(2) used to answer (3) as well, and that is wrong in both directions: it
offered a slider over 53 standard hex-key sizes, inviting a shopper to select
an interval containing no manufactured size, and it would have withheld the
number from anything that stopped being a range. Storage and control are now
decided separately, by different statistics, on the same measurement pass.
"""

from __future__ import annotations

import collections
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

#: An attribute is QUANTITATIVE if this share of the documents that publish it
#: carry a parsed ``value_num``. The catalog deliberately emits values that do
#: not parse (a ``Helix Angle`` of ``42"`` has no angle in it), so the test is
#: a majority rather than "any" or "all".
#:
#: Being quantitative decides two things and, since elastic/prism#9285, does
#: NOT decide a third:
#:
#: * the nested child carries ``value_canonical`` and ``unit_code`` -- the
#:   number stays in the data whatever control is published over it;
#: * the attribute is exempt from :data:`MAX_TERMS_CARDINALITY`, because that
#:   ceiling separates a facet from an IDENTIFIER and a measured quantity is
#:   not an identifier however many values it has;
#: * it does **not** decide whether the shopper is offered a RANGE. That is
#:   :data:`RANGE_DISPERSION` below.
NUMERIC_SHARE = 0.5

#: An attribute must appear on this share of the documents belonging to the
#: product types that publish it AT ALL. The denominator is per-attribute on
#: purpose: an attribute carried by one of twelve product types can never exceed
#: ~10% of the whole catalog, yet it may be the primary facet for its own
#: category. Measured against the whole catalog every category-specific
#: attribute would fail, and the sidebar for a washer would be empty.
MIN_PRESENCE = 0.5

#: Cap on the number of distinct values a facet over free-text values may
#: carry. This separates a facet from an identifier: ``Thread Size`` publishes
#: 19 distinct values over 331 documents and is the first thing a shopper
#: filters on, while ``List Number`` publishes 110 over 919 and is a
#: manufacturer's part reference that no one browses.
#:
#: QUANTITATIVE attributes are exempt, and the reason is worth stating
#: precisely because it used to be stated wrongly. The old reason was "a range
#: control's cost does not grow with its distinct-value count", which tied the
#: exemption to the CONTROL. It belongs to the attribute: a measured quantity
#: is not an identifier at any cardinality. The reference distributor's own captured facet
#: payload settles it -- ``Length of Cut (Decimal Inch)`` is offered as a
#: discrete list of **819** values (``square-end-mill-unfiltered.json``, all
#: 23 facets ``NAVIGATION``). A 53-value ``Drive Size`` is a facet; a 110-value
#: ``List Number`` is a part number. Cardinality does not tell those apart and
#: was never what did.
MAX_TERMS_CARDINALITY = 25

#: THE RANGE RULE. An attribute is offered as a range control only if its
#: values are CONTINUOUS, and continuity is measured rather than assumed.
#:
#: The measurable difference between a standard set and a continuum is
#: SATURATION. A standard set is a finite ladder that products land on, so as
#: documents accumulate the distinct-value count stops growing and each value
#: is shared by many products. A continuous quantity does not saturate: very
#: nearly every document contributes a value no other document has.
#:
#: The statistic is therefore ``cardinality / present`` -- distinct values per
#: document publishing the attribute, called DISPERSION below. Its limits are
#: the two cases: dispersion -> 0 for a saturated ladder, dispersion -> 1 when
#: every measurement is unique. **0.5 is the midpoint, and it means something
#: rather than being tuned: below it the average value is carried by more than
#: one document -- values REPEAT, which is what makes a list of them something
#: a shopper can pick from.** Above it most documents carry a value nobody
#: else does, and listing them offers one row per product.
#:
#: MEASURED ON THE INDUSTRIAL CATALOG (elastic/prism#9285), and the figures
#: live in :data:`MEASURED_DISPERSION` beside this rather than in this
#: sentence, because a sentence went stale across one regeneration while every
#: test stayed green. Every attribute this catalog FACETS lands between 0.0018
#: and 0.4357 -- ``Drive Size``'s 52 values over 1,389 documents is 0.037, and
#: the densest, ``Dynamic Load Capacity``, is 0.4357: a generated bearing
#: rating, nearly one value per bearing number, and still just on the discrete
#: side. The one continuum is ``Neck Length`` (see ``RANGE_MIN_DOCS``). Before
#: the catalog grew (elastic/prism-industrial-products#103) the band was
#: 0.0028-0.1401 with no continuum at all, agreeing with the reference
#: distributor, whose facet list for the end-mill category has no range control.
#:
#: THE BAND IS OVER THE FACETED ONES, and saying so is the correction rather
#: than the update. Two quantitative attributes are NOT faceted and one of
#: them, ``Neck Length``, has a dispersion of exactly 1.0000 -- 39 distinct
#: values over 39 documents, a perfect continuum. Dispersion does not make
#: THAT one a list; :data:`RANGE_MIN_DOCS` does. A band quoted over all
#: quantitative attributes runs to 1.0 and credits this threshold with an
#: outcome the other one produced.
#:
#: **This rule is derived on purpose, and must not be reimplemented as
#: "industrial uses keyword".** Grocery migrates onto the same machinery
#: (elastic/prism#9290) and is genuinely mixed: ``Salt (g/100g)`` at
#: ``0.0260417 g`` is a continuum whose dispersion is near 1 and which a
#: shopper really does ask to bracket, while ``Case size`` is a pack count
#: that lands on the discrete side. One rule, two answers, because the two
#: catalogs differ in the property the rule measures.
RANGE_DISPERSION = 0.5

#: Dispersion cannot tell saturation from growth on a handful of documents:
#: nine distinct values over ten documents reads as 0.9 whether the ladder has
#: ten rungs or ten thousand. Below this many documents the statistic is not
#: evidence, so the answer is the conservative one -- a discrete control, which
#: is always serviceable, where a range over an unknown distribution is not.
#: Every attribute this catalog FACETS clears it -- the smallest, ``Handle
#: Length``, has 129 documents. It used to decide the other side as well:
#: ``Neck Length`` published 39 distinct values over 39 documents and this
#: floor alone kept it off a slider. Since the catalog grew
#: (elastic/prism-industrial-products#103) it publishes 51 over 51, clears the
#: floor, and is offered as the range it always was. See
#: :data:`MEASURED_DISPERSION`.
RANGE_MIN_DOCS = 50

#: What the rule above MEASURES on the catalog this package generates, as
#: numbers rather than as a sentence.
#:
#: The prose here used to carry them inline and it drifted in four figures at
#: once across one regeneration -- a band of "0.003 to 0.144" for one of
#: 0.0028 to 0.1401, ``Drive Size`` at "53 values over 1,309 documents" for
#: 51 over 1,556, and ``Handle Length`` at "95" for 104 -- while the whole
#: suite stayed green, because nothing compared a docstring to a catalog.
#:
#: ``tests/test_facet_control_rule.py`` re-derives every entry here from the
#: committed golden catalog, so the next regeneration has to restate them.
#: Restated from the default catalog after the 100K brand book regenerated it
#: (elastic/prism-industrial-products, 100K catalog, 2026-09-28), each by a
#: direct ``measure()`` over golden-catalog/flat.jsonl.
MEASURED_DISPERSION: dict[str, Any] = {
    # The band over the attributes that are actually FACETED.
    "faceted_low": 0.0019,
    "faceted_high": 0.4488,
    "densest_faceted": "Dynamic Load Capacity",
    # The saturated ladder the rule exists to keep off a slider.
    "drive_size_cardinality": 52,
    "drive_size_present": 1378,
    # The smallest faceted attribute, which is what clears RANGE_MIN_DOCS.
    "smallest_faceted": "Handle Length",
    "smallest_faceted_present": 136,
    # The continuum RANGE_MIN_DOCS -- not dispersion -- keeps off a slider.
    "min_docs_arm": "Neck Length",
    "min_docs_arm_dispersion": 1.0,
    "min_docs_arm_present": 51,
}


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
        """The values ARE numbers: the attribute is quantitative.

        Decides storage (``value_canonical`` / ``unit_code``) and the
        identifier-ceiling exemption. It does NOT decide the control -- see
        :attr:`is_continuous`.
        """
        return self.numeric_share >= NUMERIC_SHARE

    @property
    def dispersion(self) -> float:
        """Distinct values per document publishing this attribute.

        The saturation statistic :data:`RANGE_DISPERSION` documents. Measured
        over the distinct values as PUBLISHED, which is the same set the facet
        would offer.
        """
        return self.cardinality / self.present if self.present else 0.0

    @property
    def is_continuous(self) -> bool:
        """Whether the values are a continuum, so a RANGE control is honest.

        Three conditions, each of which can independently refuse a range:
        the values must be numbers at all, there must be enough documents for
        dispersion to mean anything, and the values must not saturate.
        """
        return (
            self.is_numeric
            and self.present >= RANGE_MIN_DOCS
            and self.dispersion >= RANGE_DISPERSION
        )


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
    if stats.is_continuous:
        return Decision(
            stats,
            True,
            f"a range: {stats.cardinality} distinct values over {stats.present} "
            f"documents is {stats.dispersion:.2f} per document, at or above the "
            f"{RANGE_DISPERSION:.2f} continuity threshold",
        )
    if stats.is_numeric:
        return Decision(
            stats,
            True,
            f"a discrete standard set: {stats.cardinality} distinct values over "
            f"{stats.present} documents is {stats.dispersion:.2f} per document, "
            f"below the {RANGE_DISPERSION:.2f} continuity threshold, so the values "
            f"repeat and are offered as a list rather than an interval",
        )
    return Decision(stats, True, f"{stats.cardinality} distinct values")
