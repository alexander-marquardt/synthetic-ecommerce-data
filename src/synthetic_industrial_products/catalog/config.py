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


@dataclass(frozen=True)
class GeneratorConfig:
    """How much catalog to make, and how ragged to make it."""

    #: Deterministic: the same seed produces the same catalog, byte for byte.
    seed: int = 20260917

    #: Roughly how many parent product lines to emit in total. The actual
    #: count lands within a line or two of this; lines are apportioned across
    #: product types by ``type_weights``.
    #:
    #: 500 lines yields about 4,500 SKUs. A line cannot offer more SKUs than
    #: its series has members -- there are nine imperial shank sizes and eight
    #: ball pein head weights -- so the SKU count is driven by the line count
    #: far more than by ``skus_per_line``.
    lines: int = 500

    #: SKUs per line, sampled uniformly from this inclusive range. 400 lines
    #: at a mean of 12 gives about 4,800 children.
    skus_per_line: tuple[int, int] = (4, 20)

    #: Relative share of lines per product type. Cutting tools dominate the
    #: reference corpus and dominate here.
    #:
    #: The shares sum to 1.0, and adding a product type means taking the room
    #: for it from the others rather than appending to the list: ``lines`` is
    #: apportioned by multiplying this through, so a table summing to 1.09
    #: would quietly emit 545 lines where 500 were asked for.
    type_weights: dict[str, float] = field(
        default_factory=lambda: {
            "end_mill_square": 0.19,
            "end_mill_ball": 0.11,
            "drill_jobber": 0.11,
            "tap_spiral_point": 0.07,
            "screw_socket_head": 0.12,
            "screw_flat_head": 0.07,
            "screw_button_head": 0.05,
            "screw_low_head": 0.04,
            "bolt_hex": 0.09,
            "washer_flat": 0.06,
            "hammer_ball_pein": 0.04,
            "abrasive_flap_disc": 0.05,
        }
    )

    # ---- measured rates -------------------------------------------------

    #: 04_shank_dia_vs_milling_dia.json: 85 of 131 records carrying both a
    #: milling diameter and a shank diameter have them EQUAL. This is the
    #: attribute-role ambiguity rate and the reason the catalog exists.
    shank_equals_cutting_dia: float = 0.6489

    #: 09_defect_rate.json, each against its own denominator -- the records
    #: that actually carry the attribute pair the class tests.
    defect_loc_exceeds_oal: float = 0.0829
    defect_angle_carries_length_unit: float = 0.0469
    defect_system_contradicts_units: float = 0.0323

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

    #: P1, label_truncation: 16 of 496 titles are cut at a length cap mid-label.
    title_label_truncation: float = 0.0323
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
    #: product's own (0.7353). Not reproduced *as a rate*, because the catalog
    #: now goes further than the rate does: there is one generic drawing per
    #: product type and style, so EVERY product points at an image that is not
    #: its own and the reference is derivable from the product type. That is
    #: what the measurement is evidence of -- a category listing of four end
    #: mills from one series at four diameters shows the same photograph four
    #: times -- rather than something the rate captures better than the
    #: mechanism does.
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

    def scaled_presence(self, presence: float) -> float:
        if presence >= 1.0:
            return 1.0
        return max(0.0, min(1.0, presence * self.sparsity_scale))

    def scaled_defect(self, rate: float) -> float:
        return max(0.0, min(1.0, rate * self.defect_scale))

    def with_(self, **changes: object) -> GeneratorConfig:
        """A copy with some fields replaced -- the dialling entry point."""
        return replace(self, **changes)  # type: ignore[arg-type]


#: A small configuration for tests and for a quick look at the output shape.
SMALL = GeneratorConfig(lines=40, skus_per_line=(3, 8))
