"""Generator parameters.

Every rate here is either a number measured off the reference corpus or a
knob the consumer is expected to turn. The two are kept apart on purpose: a
measured rate carries the file and figure it came from in its comment, so a
later reader can tell which numbers are evidence and which are choices.

The knobs exist because the implementation work this catalog feeds needs to
find where limits bite -- how many nested children before a query plan
degrades, how sparse an attribute can get before a facet stops being useful.
Those answers come from dialling the catalog, not from regenerating it by
hand.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace


def _newer_shares() -> dict[str, float]:
    """Every newer type's default share of ``lines``, from its type module.

    Read when a config is made, not when this module is imported: the type
    modules import the code that imports this one.
    """
    from synthetic_ecommerce_data.core import typespec  # noqa: PLC0415

    return {key: spec.share for key, spec in typespec.modelled().items() if spec.newer}


@dataclass(frozen=True)
class GeneratorConfig:
    """How much catalog to make, and how ragged to make it."""

    #: Deterministic: the same seed produces the same catalog, byte for byte.
    seed: int = 20260917

    #: Roughly how many parent PRODUCTS of the original twelve types to emit.
    #: The actual count lands within a product or two of this; products are
    #: apportioned across those types by ``type_weights``. The newer types are
    #: sized from this same number, through ``new_type_share``.
    #:
    #: 2,600 products at a mean of ~1.9 variants gives about 4,700 SKUs -- the
    #: size of the catalog before variants were trimmed, spread over five times
    #: as many products (elastic/prism-industrial-products#103, D1/D2).
    lines: int = 2600

    #: How many variants (SKUs) a product has: ``((count, weight), ...)``.
    #: THE one knob for the variant distribution (maintainer, 2026-09-27):
    #: about half of products are single-SKU, the rest 2-5, skewed small, as on
    #: a marketplace. A product never offers more variants than its series has
    #: members, so a draw is capped by the pool it is taken from.
    variants_per_product: tuple[tuple[int, float], ...] = (
        (1, 0.50),
        (2, 0.25),
        (3, 0.15),
        (4, 0.06),
        (5, 0.04),
    )

    #: Share of the newer types' single-variant products whose one variant
    #: carries NO variant-scope attribute -- a deliberately awkward case, so a
    #: grouped view is proven on a selector with zero axes, not only on the
    #: well-formed shapes (maintainer guardrail, 2026-09-27).
    zero_axis_share: float = 0.02

    #: THE noise knob (:mod:`.noise`): scales every rate at which the copy
    #: carries a true-but-distracting sentence -- a size it does not fit, a
    #: sibling it is also sold in, a unit equivalent, what it pairs with or
    #: cuts. 1.0 is the realistic default; 0 is a clean catalog with IDENTICAL
    #: attributes, so the two can be compared record for record.
    noise: float = 1.0

    #: Stock a SKU for every requirement example (:mod:`.muststock`), after
    #: the main generation, whatever the random streams drew.
    must_stock: bool = True

    #: Products per NEWER product type, as a SHARE of ``lines``: a type with
    #: share ``s`` gets ``round(lines * s)`` products (:attr:`new_type_products`).
    #: A share, not a count, so ``lines`` stays the ONE size knob -- a catalog
    #: built at ten times the lines carries ten times the nuts, bearings, wheels
    #: and hex keys, instead of the four newer types staying fixed while
    #: everything else grows (elastic/prism-industrial-products, 100K catalog,
    #: 2026-09-28). 700/2600 is the ratio the default catalog was built with,
    #: so the default still carries exactly 700 of each. The default is each
    #: newer type's ``TypeSpec.share`` (``newer=True``), declared in its own
    #: module.
    #:
    #: Every type draws from its own random stream (:mod:`.typespec`), so
    #: adding, removing or resizing one moves no other type's products.
    new_type_share: dict[str, float] = field(default_factory=lambda: _newer_shares())

    #: Share of ``lines`` per original product type: a type with share ``s``
    #: drafts ``max(1, round(lines * s))`` lines. Cutting tools dominate the
    #: reference corpus and dominate here.
    #:
    #: Each share is that type's own and the others do not move with it, so
    #: resizing one type leaves every other type's products unchanged. A type
    #: declared in its own module carries its default share there
    #: (``TypeSpec.share``), and an entry here overrides it; the default is
    #: empty, so a build uses the shares the modules declare. The original
    #: types' shares sum to 1.0. A deepened type adds its own share on top and
    #: takes no room from the others (taking it would move their output), so
    #: the catalog is that much larger (#53).
    type_weights: dict[str, float] = field(default_factory=dict)

    # ---- measured rates -------------------------------------------------

    #: 04_shank_dia_vs_milling_dia.json: 85 of 131 records carrying both a
    #: milling diameter and a shank diameter have them EQUAL. This is the
    #: attribute-role ambiguity rate and the reason the catalog exists.
    shank_equals_cutting_dia: float = 0.6489

    #: 09_defect_rate.json, each against its own denominator -- the records
    #: that actually carry the attribute pair the class tests.
    defect_loc_exceeds_oal: float = 0.0829
    #: 09_defect_rate.json measures 0.0469 of angle-carrying records with a
    #: length keyed into the angle field (``Point Angle = 2"``). **Measured and
    #: deliberately not reproduced**: the generator writes no value of the wrong
    #: kind for its key, and a real retailer would fix that row (#404). The
    #: reproduction is declined, the measurement stands.
    measured_angle_carries_length_unit: float = 0.0469
    defect_system_contradicts_units: float = 0.0323

    #: The share of parents carrying ``Standards`` that publish one of its
    #: values twice (``Standards = [ISO, ISO]``): a repeated (name, value) PAIR
    #: on one parent, the shape that makes a nested count over-report without
    #: ``reverse_nested`` (#1). Measured on a live retail catalog: 87 of 20,000
    #: sampled documents (0.00435) repeat a pair. Over parents carrying
    #: ``Standards`` (about 51% of this catalog's parents) 0.0085 lands at the
    #: same share of ALL parents, about 0.43%. Scaled by ``defect_scale``.
    defect_repeated_pair: float = 0.0085

    #: 07_value_format_variation.json: 11 of 496 records mix imperial and
    #: metric units across their own dimension fields.
    unit_mixing_within_record: float = 0.0222

    #: P1_title_grammar.json, title_style_counts: 339 descriptive, 157 terse.
    title_descriptive_share: float = 0.6835

    #: P1, title_token_vs_assumed_attribute: 49 of 105 title dimension tokens
    #: carry no label at all.
    title_token_unlabelled: float = 0.4667

    #: P1, same block: 18 of 105 title dimension tokens are NOT the milling
    #: diameter. Every one of those 18 carries a label -- the corpus has zero
    #: cases that are both unlabelled and not the milling diameter -- so the
    #: two hazards are reproduced as disjoint.
    title_token_not_primary: float = 0.1714

    #: Which secondary dimension the misleading token turns out to be, from
    #: the same block: other_length 7, length_of_cut 5, neck 4, flute 2.
    title_secondary_mix: dict[str, float] = field(
        default_factory=lambda: {
            "other_length": 0.3889,
            "length_of_cut": 0.2778,
            "neck": 0.2222,
            "flute": 0.1111,
        }
    )

    #: P1, label_truncation: 16 of 496 titles in the REFERENCE corpus are cut
    #: at a length cap mid-label. **Measured and deliberately not reproduced**,
    #: which is why it is 0.0 rather than absent -- the measurement stands, the
    #: reproduction is declined. The reference distributor's own titles carry no truncation
    #: (24 of 24 clean on the scraped sample), so generating it invented a
    #: defect class their catalog does not have; and a title reading
    #: "Dia./Thread Siz" reads as OUR bug rather than as realism about supplier
    #: data. Same call, same reason, as the missing product images below.
    #: Ruling: elastic/prism#9284.
    measured_title_label_truncation: float = 0.0323
    title_label_truncation: float = 0.0
    #: The cap the longest observed truncations land on.
    title_length_cap: int = 100

    #: 10_image_sku_divergence.json measures two things about image
    #: references, and **neither is reproduced**. Both deviations are recorded
    #: here rather than hidden.
    #:
    #: 54 of 496 records carry no parseable image reference at all (0.1089).
    #: Not reproduced: the catalog is used as a demo, and a product with no
    #: image reads there as a broken page rather than as realism about supplier
    #: data. Every product and every variant carries one.
    #:
    #: Of the 442 that do carry one, 325 point at an image whose id is not the
    #: product's own (0.7353). Not reproduced, in the OTHER direction now: every
    #: SKU carries a drawing of its own, drawn from its own values, so selecting
    #: a variant can switch the picture (maintainer ruling on
    #: elastic/prism-industrial-products#103, 2026-09-26: "we should do like
    #: amazon"). A distributor photographs one size of a line; a generated
    #: drawing costs nothing per size, so there is no reason to share one.
    measured_image_missing: float = 0.1089
    measured_image_sku_diverges: float = 0.7353

    #: 06_attribute_sparsity.json: the whole-corpus mean is 13.12 attributes
    #: per record, but it is a mean over families that differ a lot
    #: (end_mill 16.98, fastener 9.87). Per-type presence rates in vocab.py
    #: carry the shape; this is the figure the result is checked against.
    target_attrs_per_record: float = 13.12

    #: Multiplier on every optional attribute's presence rate. 1.0 reproduces
    #: the measured sparsity; lower makes the catalog raggeder.
    sparsity_scale: float = 1.0

    #: Multiplier on every defect rate. 0.0 produces a catalog with no
    #: internal contradictions at all -- useful as a control, and not what a
    #: real catalog looks like.
    defect_scale: float = 1.0

    @property
    def new_type_products(self) -> dict[str, int]:
        """Products per newer type at this size: ``new_type_share`` times ``lines``."""
        return {key: round(self.lines * share) for key, share in self.new_type_share.items()}

    def scaled_presence(self, presence: float) -> float:
        if presence >= 1.0:
            return 1.0
        return max(0.0, min(1.0, presence * self.sparsity_scale))

    def scaled_defect(self, rate: float) -> float:
        return max(0.0, min(1.0, rate * self.defect_scale))

    def with_(self, **changes: object) -> GeneratorConfig:
        """A copy with some fields replaced -- the dialling entry point."""
        return replace(self, **changes)  # type: ignore[arg-type]


#: The ``--lines`` that lands the catalog at about 100,000 SKUs: measured,
#: ``ecom-generate build --lines 39000`` gives 99,929 SKUs over 57,985
#: products (README, "The 100K catalog"); 111,499 over 64,483 since the
#: deepened ``lock_nuts_nylon_insert`` and ``set_screws_hex_socket`` each added
#: their own share (#53); 119,363 over 68,979 since ``o_rings`` added its
#: own, on a build the bearings' wider table and four more types had grown;
#: 122,324 over 70,776 since five more table types (#101) and key stock
#: (#108) added theirs.
#: A named value of the one knob, not a second knob; built on demand, not
#: published while the spec is iterated at the default size. (28,300 until
#: uniqueness stopped counting metadata -- the standards claimed, the
#: measurement-system spelling -- as a difference, which rejects more drafts
#: per line.)
HUNDRED_K_LINES = 39000


def small() -> GeneratorConfig:
    """A new small configuration, sharing no dict with any other.

    The config is frozen but its dicts are not, so a builder that writes into
    ``type_weights`` changes every later build made from the same object. A
    test that compares two builds makes each from its own ``small()``.
    """
    return GeneratorConfig(
        lines=160,
        # 30 products of each newer type: 160 * 0.1875.
        new_type_share={
            "nut_hex": 0.1875,
            "bearing_radial_ball": 0.1875,
            "wheel_depressed_center": 0.1875,
            "hex_key": 0.1875,
            "kit_assortment": 0.1,
        },
    )


#: A small configuration for tests and for a quick look at the output shape.
SMALL = small()
