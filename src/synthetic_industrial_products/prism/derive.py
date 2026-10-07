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

1. **Is it a facet at all?** :func:`decide`, from presence and, for a terms
   attribute, whether its values repeat (:data:`IDENTIFIER_DISPERSION`).
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

from ..catalog.entry import flat_key
from ..catalog.generate import Generator

#: Attributes the generator itself mints as part codes (``List Number``), and
#: so withheld from the sidebar whatever their values measure. Read from the
#: generator rather than restated here: it is the one place that knows a value
#: was drawn as a reference, and a measured ratio cannot see that once a
#: finite code pool saturates (see :data:`IDENTIFIER_DISPERSION`).
IDENTIFIER_ATTRIBUTES = Generator.IDENTIFIER_ATTRIBUTES

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
#: * the attribute is exempt from :data:`IDENTIFIER_DISPERSION`, because that
#:   test separates a facet from an IDENTIFIER and a measured quantity is
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

#: THE IDENTIFIER RULE. An attribute the generator declares an identifier
#: (:data:`IDENTIFIER_ATTRIBUTES`) is withheld from the sidebar at any ratio.
#: Any other terms attribute is an IDENTIFIER, and is withheld, when its
#: values do not repeat across products: its
#: :attr:`AttributeStats.dispersion` (distinct values per distinct
#: ``(product, value)`` pair) is at or above this, on at least
#: :data:`RANGE_MIN_DOCS` distinct products. A facet is a few values that
#: many products share; an identifier is roughly one value per product.
#:
#: It is the same midpoint as :data:`RANGE_DISPERSION`, for the same reason:
#: below it the average value is carried by more than one product, so a list
#: of the values is something a shopper can pick from. On a terms attribute
#: the far side of that line means a part reference; on a quantity it means a
#: continuum. One statistic answers both questions, so the two thresholds are
#: equal.
#:
#: The rule is a RATIO on purpose. It replaced an absolute cap of 25 distinct
#: values (alexander-marquardt/synthetic-industrial-products#31), which
#: does not grow with the catalog: ``Thread Size`` passed it at 19 values and
#: failed it at 55 while staying a standards body's ladder, and ``Standards``
#: failed it at 26. A ladder keeps its rungs as products accumulate, so its
#: dispersion FALLS with catalog size; an identifier gains a value with nearly
#: every product, so its dispersion stays near 1. The default build's figures
#: (the one identifier, and the densest terms attribute that is still a
#: facet) live in :data:`MEASURED_DISPERSION`.
#:
#: What the ratio cannot see, and why the declaration comes first: an
#: identifier drawn from a FINITE pool saturates like a ladder once the
#: catalog outgrows the pool. ``List Number`` draws from 9,000 codes; its
#: dispersion is 0.98 at the default size, 0.62 at ``--lines 39000`` and
#: 0.508 at ``--lines 60000``, so the ratio alone would offer it as a facet
#: from about 62,000 lines, 1.6 times the published 39,000-line build
#: (measured for #31). The ratio stays for identifiers nothing declares.
#:
#: QUANTITATIVE attributes are exempt, and the reason is worth stating
#: precisely because it used to be stated wrongly. The old reason was "a range
#: control's cost does not grow with its distinct-value count", which tied the
#: exemption to the CONTROL. It belongs to the attribute: a measured quantity
#: is not an identifier at any cardinality. The reference distributor's own captured facet
#: payload settles it -- ``Length of Cut (Decimal Inch)`` is offered as a
#: discrete list of **819** values (``square-end-mill-unfiltered.json``, all
#: 23 facets ``NAVIGATION``).
IDENTIFIER_DISPERSION = 0.5

#: THE RANGE RULE. An attribute is offered as a range control only if its
#: values are CONTINUOUS, and continuity is measured rather than assumed.
#:
#: The measurable difference between a standard set and a continuum is
#: SATURATION. A standard set is a finite ladder that products land on, so as
#: documents accumulate the distinct-value count stops growing and each value
#: is shared by many products. A continuous quantity does not saturate: very
#: nearly every document contributes a value no other document has.
#:
#: The statistic is therefore ``cardinality / product_values`` -- distinct
#: values per distinct ``(product, value)`` pair publishing the attribute,
#: called DISPERSION below. Its limits are the two cases: dispersion -> 0 for
#: a saturated ladder, dispersion -> 1 when every measurement is unique.
#: **0.5 is the midpoint, and it means something rather than being tuned:
#: below it the average value is carried by more than one product -- values
#: REPEAT, which is what makes a list of them something a shopper can pick
#: from.** Above it most products carry a value nobody else does, and listing
#: them offers one row per product.
#:
#: The denominator counts PRODUCTS, not SKU documents
#: (alexander-marquardt/synthetic-industrial-products#28). A value set at
#: product scope is repeated on every variant of the product, and counting
#: each copy made the ratio fall with the variant count rather than with the
#: values: a rating jittered per product read as a ladder because each
#: product had several sizes. A value that differs between a product's SKUs is
#: still one observation per SKU, because each SKU contributes its own pair.
#:
#: MEASURED ON THE INDUSTRIAL CATALOG (elastic/prism#9285), and the figures
#: live in :data:`MEASURED_DISPERSION` beside this rather than in this
#: sentence, because a sentence went stale across one regeneration while every
#: test stayed green. Every attribute this catalog FACETS lands inside the
#: band that dict records -- ``Drive Size``, a ladder of nominal hex keys, sits
#: low in it, and the densest is named there too. Before the catalog grew
#: (elastic/prism-industrial-products#103) the band was 0.0028-0.1401 with no
#: continuum at all, agreeing with the reference distributor, whose facet
#: list for the end-mill category has no range control.
#:
#: THE BAND IS OVER THE FACETED ONES, and saying so is the correction rather
#: than the update. Two quantitative attributes are NOT faceted, and one of
#: them, ``Neck Length``, has a dispersion of 0.9928 -- nearly every value
#: distinct, a real continuum. Dispersion does not make THAT one a list;
#: :data:`MIN_PRESENCE` does (it is present on 28% of end-mill documents,
#: below the 50% floor -- see :data:`MEASURED_DISPERSION`). A band quoted over
#: all quantitative attributes runs to 0.99 and credits the wrong threshold
#: with an outcome :data:`MIN_PRESENCE` produced. Applying Neck Length's
#: census presence rate once instead of twice
#: (alexander-marquardt/synthetic-industrial-products#39) is what moved it
#: from below :data:`RANGE_MIN_DOCS` to below :data:`MIN_PRESENCE` instead --
#: still off a slider, now for the floor that actually fits a category-scoped
#: attribute this rare.
#:
#: **This rule is derived on purpose, and must not be reimplemented as
#: "industrial uses keyword".** Grocery migrates onto the same machinery
#: (elastic/prism#9290) and is genuinely mixed: ``Salt (g/100g)`` at
#: ``0.0260417 g`` is a continuum whose dispersion is near 1 and which a
#: shopper really does ask to bracket, while ``Case size`` is a pack count
#: that lands on the discrete side. One rule, two answers, because the two
#: catalogs differ in the property the rule measures.
RANGE_DISPERSION = 0.5

#: Dispersion cannot tell saturation from growth on too few products: a
#: ladder of K rungs reads below 0.5 only once roughly 1.6K products have
#: landed on it, so an undersampled ladder looks like a continuum or an
#: identifier. Below this many DISTINCT PRODUCTS the ratio is not evidence,
#: and each rule that reads it takes its conservative answer: a discrete
#: control rather than a range, and a facet rather than an identifier. (The
#: name predates both #28 and the switch to products; the deployment reads it.)
#:
#: It counts products, not ``(product, value)`` pairs, because both rules ask
#: whether values repeat ACROSS products. A kit lists a dozen sizes, so five
#: kits made 52 pairs at ``--lines 200`` and cleared a floor of 50 pairs:
#: ``Sizes Included`` was withheld at 200, 400 and 600 lines and offered from
#: 900 up (the #31 review).
#:
#: The value is MEASURED, not derived: it is the floor at which no decision
#: moves with ``--lines``. The largest product count at which a ladder of
#: this catalog still reads 0.5 is 202 (``Overall Length`` at ``--lines
#: 260``, a list at every larger size); below that, at ``--lines 200``,
#: ``Bore`` (38 values on 58 products) and ``Overall Length`` (149 on 157)
#: read as ranges and ``Bearing Number`` (27 on 54) as an identifier. 250
#: clears 202. ``test_every_decision_is_the_same_at_every_catalog_size`` is
#: the gate, at 200, 260, 400, 600 and 900 lines and the default; ``--lines
#: 39000`` makes the default's decisions (measured for #31).
#:
#: What it costs: an identifier nothing declares, published on fewer than
#: this many products, is offered as a list of at most this many values.
#: :data:`IDENTIFIER_ATTRIBUTES` covers the one this catalog mints. On the
#: default build's modelled types the floor decides nothing: every attribute
#: under it has a ratio under 0.5, so the ratio and the floor agree
#: (``held_by_floor`` in :data:`MEASURED_DISPERSION`). Across the whole build
#: it keeps two breadth-category terms facets offered that the ratio alone
#: would withhold, ``Style`` (11 values on 13 products) and ``Color`` (2 on
#: 2). ``Neck Length`` clears it and is kept off a slider by
#: :data:`MIN_PRESENCE`.
RANGE_MIN_DOCS = 250

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
#: Restated for alexander-marquardt/synthetic-industrial-products#39 (Corner
#: Radius/Neck Length applied once instead of twice), each by a direct
#: ``measure()`` over golden-catalog/flat.jsonl. That fix does not touch any
#: of the FACETED figures below by name or reason -- they move by the same
#: small RNG-order margin any generator change causes -- except
#: ``min_presence_arm``, which did not exist under this name before: Neck
#: Length crossed RANGE_MIN_DOCS and is now kept off a slider by
#: MIN_PRESENCE instead, the first real (not constructed) example of that
#: floor this catalog has published.
#:
#: Restated again for alexander-marquardt/synthetic-industrial-products#48
#: (every product type draws from its own random stream), the same way. Every
#: figure that moved did so by that RNG margin; no attribute changed its
#: control, its densest/smallest/widest name, or the floor that decides it.
#:
#: Restated again for alexander-marquardt/synthetic-industrial-products#28,
#: when dispersion moved from SKU documents to ``(product, value)`` pairs:
#: the band's ends move (a product-scope value on several variants now
#: counts once) and no quantitative attribute changes its control. The two
#: ``identifier`` / ``densest_terms_facet`` rows are new with #31. When the
#: floor moved to 250 distinct products (the #31 review), the smallest-facet
#: row moved from documents to products and ``held_by_floor`` is new.
MEASURED_DISPERSION: dict[str, Any] = {
    # The band over the QUANTITATIVE attributes that are actually FACETED.
    "faceted_low": 0.0037,
    # Width since the bearing table widened to 75 numbers (#64); Flute Length before it,
    # and Dynamic Load Capacity at 0.44 while a formula manufactured a value per SKU.
    "faceted_high": 0.2209,
    "densest_faceted": "Width",
    # The saturated ladder the rule exists to keep off a slider.
    # Low since the drive size is published as the nominal key (10mm), not
    # the extracted socket's toleranced across-flats (10.07mm). The hex socket
    # set screws (#53) add their small keys (0.7-1.3mm, 0.028-0.035") and 485 documents.
    "drive_size_cardinality": 41,
    "drive_size_present": 1842,
    # The faceted quantity on the fewest products: a roller chain's Roller
    # Dia. (30 of its 40 lines; the rollerless 25 and 35 chains publish none).
    # Under RANGE_MIN_DOCS, like many faceted quantities, but with a ratio
    # under the continuity threshold, so the floor decides none of them.
    "smallest_faceted": "Roller Dia.",
    "smallest_faceted_products": 30,
    # The terms facets of the modelled types that the ratio alone would
    # withhold and RANGE_MIN_DOCS keeps offered: none. (Two breadth-category
    # facets are, Style and Color; the committed field map's reasons say so.)
    "held_by_floor": [],
    # The real continuum this catalog does not offer as a range. It clears
    # BOTH RANGE_DISPERSION and RANGE_MIN_DOCS now (#39) -- MIN_PRESENCE is
    # what still keeps it off a slider, because it is rare even among its
    # own product types.
    "min_presence_arm": "Neck Length",
    "min_presence_arm_dispersion": 0.9928,
    "min_presence_arm_present": 417,
    # Its OWN denominator -- end-mill documents, not the whole catalog -- and
    # the share MIN_PRESENCE measures against 50%.
    "min_presence_arm_type_denominator": 1486,
    "min_presence_arm_share": 0.28,
    # The one terms attribute IDENTIFIER_DISPERSION withholds: a series code,
    # about one value per product. IDENTIFIER_ATTRIBUTES withholds it first;
    # at this size the ratio agrees.
    "identifier": "List Number",
    "identifier_dispersion": 0.9764,
    # The densest terms facet over RANGE_MIN_DOCS: 75 bearing designations.
    # The terms side's margin under 0.5. (Sizes Included, 0.2783, is denser
    # but on 59 kits, under the floor.)
    "densest_terms_facet": "Bearing Number",
    "densest_terms_facet_dispersion": 0.1105,
}


@dataclass(frozen=True)
class AttributeStats:
    """What the emitted documents say about one attribute key."""

    key: str
    name: str
    present: int
    numeric: int
    cardinality: int
    product_types: tuple[str, ...]
    type_denominator: int
    #: Distinct ``(product_id, value)`` pairs: how many independent
    #: observations the values rest on. A product-scope value repeated on a
    #: product's variants is one; a value that differs per SKU is one per SKU.
    product_values: int
    #: Distinct ``product_id`` values publishing the attribute: what the
    #: evidence floor :data:`RANGE_MIN_DOCS` counts, because both rules ask
    #: whether values repeat ACROSS products.
    products: int

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
        identifier exemption. It does NOT decide the control -- see
        :attr:`is_continuous`.
        """
        return self.numeric_share >= NUMERIC_SHARE

    @property
    def dispersion(self) -> float:
        """Distinct values per distinct ``(product, value)`` pair.

        The saturation statistic :data:`RANGE_DISPERSION` documents. Measured
        over the distinct values as PUBLISHED, which is the same set the facet
        would offer, and per product rather than per SKU document (#28).
        """
        return self.cardinality / self.product_values if self.product_values else 0.0

    @property
    def is_continuous(self) -> bool:
        """Whether the values are a continuum, so a RANGE control is honest.

        Three conditions, each of which can independently refuse a range:
        the values must be numbers at all, there must be enough observations
        for dispersion to mean anything, and the values must not saturate.
        """
        return (
            self.is_numeric
            and self.products >= RANGE_MIN_DOCS
            and self.dispersion >= RANGE_DISPERSION
        )

    @property
    def is_identifier(self) -> bool:
        """Whether a terms attribute's values do not repeat across products.

        The test :data:`IDENTIFIER_DISPERSION` documents: a ratio, so the
        answer does not move with the size of the catalog (#31).
        """
        return (
            not self.is_numeric
            and self.products >= RANGE_MIN_DOCS
            and self.dispersion >= IDENTIFIER_DISPERSION
        )


@dataclass
class Decision:
    """Whether an attribute becomes a facet, and the measured reason."""

    stats: AttributeStats
    facet: bool
    reason: str


def measure(rows: Iterable[dict[str, Any]]) -> dict[str, AttributeStats]:
    """Collect per-attribute statistics from emitted flat documents.

    One statistic per machine KEY, never per display name: a roller chain's
    ``Pitch`` (``chain_pitch``) and a metric tap's ``Pitch`` (``pitch``) are two
    concepts that real catalogs label alike, and merging them would put a
    chain's inch spacing in one bucket list with thread pitches (#36).
    """
    present: collections.Counter[str] = collections.Counter()
    numeric: collections.Counter[str] = collections.Counter()
    values: dict[str, set[str]] = collections.defaultdict(set)
    product_values: dict[str, set[tuple[str, str]]] = collections.defaultdict(set)
    products: dict[str, set[str]] = collections.defaultdict(set)
    types: dict[str, set[str]] = collections.defaultdict(set)
    published_name: dict[str, str] = {}
    type_sizes: collections.Counter[str] = collections.Counter()

    for row in rows:
        product_type = row["product_type"]
        type_sizes[product_type] += 1
        for key, vals in row["facets"].items():
            present[key] += 1
            values[key].update(vals)
            product_values[key].update((row["product_id"], value) for value in vals)
            products[key].add(row["product_id"])
            types[key].add(product_type)
        for key in row["facets_num"]:
            numeric[key] += 1
        # The published spelling is what a shopper sees on the facet heading.
        # Take it from the attribute entries, which carry the name verbatim,
        # filed under the facets key each entry's value sits under.
        for attribute in row["attributes"]:
            published_name.setdefault(flat_key(attribute), attribute["name"])

    return {
        key: AttributeStats(
            key=key,
            name=published_name.get(key, key),
            present=count,
            numeric=numeric[key],
            cardinality=len(values[key]),
            product_types=tuple(sorted(types[key])),
            type_denominator=sum(type_sizes[t] for t in types[key]),
            product_values=len(product_values[key]),
            products=len(products[key]),
        )
        for key, count in sorted(present.items())
    }


def decide(stats: AttributeStats) -> Decision:
    """Apply the facet rule to one attribute, recording which gate decided it.

    The reason string is part of the committed artifact: a field map that says
    only ``facet: false`` invites someone to flip it, while one that says
    ``single-valued`` explains why flipping it would add a control that cannot
    narrow anything.
    """
    if stats.name in IDENTIFIER_ATTRIBUTES:
        return Decision(
            stats,
            False,
            "an identifier, not a facet: the generator declares it a part code, "
            "so it is withheld whatever its values measure",
        )
    if stats.cardinality < 2:
        return Decision(stats, False, "single-valued: clicking it cannot narrow the result set")
    if stats.presence < MIN_PRESENCE:
        return Decision(
            stats,
            False,
            f"present on {stats.presence:.0%} of its product types' documents "
            f"(floor {MIN_PRESENCE:.0%})",
        )
    over = (
        f"{stats.cardinality} distinct values over {stats.product_values} "
        f"product-value pairs is {stats.dispersion:.2f} per product"
    )
    if stats.is_identifier:
        return Decision(
            stats,
            False,
            f"reads as an identifier, not a facet: {over}, at or above the "
            f"{IDENTIFIER_DISPERSION:.2f} identifier threshold, so the values do not repeat",
        )
    if stats.is_continuous:
        return Decision(
            stats,
            True,
            f"a range: {over}, at or above the {RANGE_DISPERSION:.2f} continuity threshold",
        )
    # Only reached under the floor: the ratio says continuum or identifier,
    # and too few products carry the attribute for that to be evidence.
    few = f"but on {stats.products} products, fewer than the {RANGE_MIN_DOCS} the"
    if stats.is_numeric and stats.dispersion >= RANGE_DISPERSION:
        return Decision(
            stats,
            True,
            f"a discrete list: {over}, at or above the {RANGE_DISPERSION:.2f} "
            f"continuity threshold {few} continuity test needs as evidence",
        )
    if stats.is_numeric:
        return Decision(
            stats,
            True,
            f"a discrete standard set: {over}, below the {RANGE_DISPERSION:.2f} "
            f"continuity threshold, so the values repeat and are offered as a list "
            f"rather than an interval",
        )
    if stats.dispersion >= IDENTIFIER_DISPERSION:
        return Decision(
            stats,
            True,
            f"{over}, at or above the {IDENTIFIER_DISPERSION:.2f} identifier threshold "
            f"{few} identifier test needs as evidence",
        )
    return Decision(
        stats,
        True,
        f"{over}, below the {IDENTIFIER_DISPERSION:.2f} identifier threshold, so the values repeat",
    )
