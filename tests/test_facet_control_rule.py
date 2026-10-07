"""Which CONTROL an attribute is offered under -- range or discrete list.

The rule under test (elastic/prism#9285): an attribute is offered as a range
only when its values are CONTINUOUS, measured as saturation -- distinct values
per document publishing it -- and not merely because they happen to be
numbers. A range control over a discrete standard set implies a continuity the
domain does not have and lets a shopper select an interval containing no
manufactured size.

Two things make this worth its own module rather than a line in the drift
test:

* the assertions are on the RENDERED FIELD MAP, which is the artifact the
  sidebar is built from. A boolean on a dataclass can be right while the YAML
  says something else, and it is the YAML that is deployed.
* the rule has to serve a SECOND catalog whose answer is different. Grocery
  migrates onto this machinery and has genuinely continuous attributes, so
  half of these tests exercise a continuum this catalog does not contain --
  constructed on purpose, and labelled where it happens.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.breadth import SPEC_QUALITY
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.prism.derive import (
    MAX_TERMS_CARDINALITY,
    MEASURED_DISPERSION,
    MIN_PRESENCE,
    RANGE_DISPERSION,
    RANGE_MIN_DOCS,
    AttributeStats,
    decide,
    measure,
)
from synthetic_industrial_products.prism.field_map import render


@pytest.fixture(scope="module")
def flat_rows() -> list[dict]:
    return list(emit.iter_flat(generate(GeneratorConfig())))


@pytest.fixture(scope="module")
def rendered(flat_rows: list[dict]) -> str:
    return render(flat_rows)


def _entries(yaml_text: str) -> dict[str, dict[str, str]]:
    """Every ``- name:`` entry of the rendered map, as its own key/value block.

    Parsed off the rendered TEXT rather than re-derived from the decisions,
    because re-deriving would assert the renderer against itself.
    """
    entries: dict[str, dict[str, str]] = {}
    current: str | None = None
    for raw in yaml_text.splitlines():
        line = raw.strip()
        if line.startswith("- name:"):
            current = line.split(":", 1)[1].strip()
            entries[current] = {}
        elif current and line and not line.startswith("#") and ":" in line:
            key, _, value = line.partition(":")
            if not raw.startswith("    "):
                current = None
                continue
            entries[current][key.strip()] = value.strip()
    return entries


# --------------------------------------------------------------------------
# This catalog: every dimensional attribute is a standard set.
# --------------------------------------------------------------------------


def test_no_attribute_in_this_catalog_is_offered_as_a_range(
    flat_rows: list[dict], rendered: str
) -> None:
    """The measured outcome of the rule on the industrial catalog.

    Asserted as an exact set rather than a count. A count of zero is also what
    an empty parse produces, so the entry total is asserted first -- a
    ``_entries`` that returned nothing would otherwise read as a clean pass.
    """
    entries = _entries(rendered)
    assert len(entries) > 50, f"only {len(entries)} entries parsed; the parse is wrong"

    stats = measure(flat_rows)
    attribute_entries = {k: v for k, v in entries.items() if k in stats}
    assert attribute_entries, "no attribute entries were found in the rendered map"

    ranged = {k for k, v in attribute_entries.items() if v.get("type") == "numeric"}
    offered_as_range = {k for k in ranged if entries[k].get("facet") != "false"}
    assert offered_as_range == set(), (
        f"{sorted(offered_as_range)} are offered to a shopper as range controls. "
        f"Every dimensional attribute in this catalog is a discrete standard "
        f"set: their dispersion runs "
        f"{min(s.dispersion for s in stats.values() if s.is_numeric):.3f} to "
        f"{max(s.dispersion for s in stats.values() if s.is_numeric):.3f}, all "
        f"below the {RANGE_DISPERSION} continuity threshold."
    )


def test_drive_size_specifically_is_a_list_and_keeps_its_number(
    flat_rows: list[dict], rendered: str
) -> None:
    """The issue's own example, end to end.

    ``Drive Size`` is hex key sizes -- a standardised discrete set. A shopper
    filtering it owns a 3/8" key and wants to pick it, not bracket it. The
    second half of the assertion is the ruling's other half: the number stays
    in the data. It is declared once on the attribute set rather than per
    entry, so what this checks is that the entry did not opt out of it.
    """
    entries = _entries(rendered)
    assert entries["drive_size"]["type"] == "terms", entries["drive_size"]
    assert "interval" not in entries["drive_size"], (
        "a terms entry carrying 'interval' is REFUSED at field-map load by the "
        "Engine -- 'interval' is only valid for type='numeric'"
    )
    stats = measure(flat_rows)
    assert stats["drive_size"].is_numeric, (
        "Drive Size must stay QUANTITATIVE -- that is what puts value_canonical "
        "and unit_code on the nested child. Only the CONTROL changed."
    )


def test_every_attribute_that_is_quantitative_still_says_so(flat_rows: list[dict]) -> None:
    """Storage and control are separate, and the split is asserted, not assumed.

    The failure this guards is the tempting one: making an attribute a terms
    facet by making it stop being numeric, which would drop the canonical
    number out of the index.
    """
    stats = measure(flat_rows)
    quantitative = [s for s in stats.values() if s.is_numeric]
    assert len(quantitative) >= 25, len(quantitative)
    # Neck Length is the one real continuum on this catalog: its values never
    # repeat, and applying its census presence rate once instead of twice
    # (alexander-marquardt/synthetic-industrial-products#39) raised its
    # document count well past RANGE_MIN_DOCS, so dispersion alone now calls
    # it continuous. It still is not OFFERED as a range -- MIN_PRESENCE keeps
    # it off faceting entirely, since it is rare even among end mills (see
    # MEASURED_DISPERSION and test_the_widest_dispersion_is_a_continuum_that_
    # clears_the_document_floor) -- so this is the one exception to check
    # before the rule is trusted, not a failure of it.
    assert [s.key for s in quantitative if s.is_continuous] == ["neck_length"]


# --------------------------------------------------------------------------
# The rule itself, including the catalog this repository does not contain.
# --------------------------------------------------------------------------


def _stats(*, cardinality: int, present: int, numeric: int | None = None) -> AttributeStats:
    """A constructed measurement, for cases the industrial catalog lacks."""
    return AttributeStats(
        key="probe",
        name="Probe",
        present=present,
        numeric=present if numeric is None else numeric,
        cardinality=cardinality,
        product_types=("probe_type",),
        type_denominator=present,
    )


def test_continuity_admits_a_continuum() -> None:
    """The grocery case, constructed.

    ``Salt (g/100g)`` is published as ``0.0260417 g`` -- very nearly every
    product carries a value no other product carries. The same rule that calls
    53 drive sizes discrete must call this continuous, or the rule has
    silently become "industrial uses keyword" and breaks when OFF migrates
    (elastic/prism#9290).
    """
    salt = _stats(cardinality=6_800, present=7_173)
    assert salt.dispersion > 0.9
    assert salt.is_continuous
    assert decide(salt).facet
    assert "a range" in decide(salt).reason


def test_continuity_refuses_a_saturated_ladder() -> None:
    """The industrial case, constructed to the catalog's own figures.

    51 distinct drive sizes over 1,556 documents -- each value carried by about
    30 products, which is what makes a list of them something a shopper picks
    from. Those two numbers are asserted against the real derivation by
    ``test_drive_size_is_the_saturated_ladder_the_rule_names`` below, which is
    what makes this construction an example rather than an invention; they read
    53 / 1,309, one generation stale, until that test existed.
    """
    drive = _stats(cardinality=51, present=1_556)
    assert drive.dispersion < 0.05
    assert not drive.is_continuous
    assert drive.is_numeric, "still a quantity; only the control changed"
    assert "discrete standard set" in decide(drive).reason


def test_the_threshold_is_the_midpoint_and_both_sides_of_it_are_reachable() -> None:
    """Astride the boundary, so the comparison cannot be vacuous.

    A test that only ever probes 0.04 and 0.95 would pass against a threshold
    anywhere between them. These two differ by one document.
    """
    below = _stats(cardinality=49, present=100)
    at = _stats(cardinality=50, present=100)
    assert below.dispersion < RANGE_DISPERSION <= at.dispersion
    assert not below.is_continuous
    assert at.is_continuous


def test_a_small_sample_falls_back_to_discrete() -> None:
    """Nine distinct values over ten documents is not evidence of a continuum.

    Dispersion cannot tell a ten-rung ladder from a ten-thousand-rung one at
    that size, so the answer is the conservative control. Asserted with a pair
    that differs ONLY in the document count, so it is the floor being tested
    and not the dispersion.
    """
    tiny = _stats(cardinality=RANGE_MIN_DOCS - 1, present=RANGE_MIN_DOCS - 1)
    big = _stats(cardinality=RANGE_MIN_DOCS * 2, present=RANGE_MIN_DOCS * 2)
    assert tiny.dispersion == big.dispersion == 1.0
    assert not tiny.is_continuous, "below the floor, dispersion is not evidence"
    assert big.is_continuous


def test_values_that_are_not_numbers_are_never_a_range() -> None:
    """A keyword attribute cannot become a range by being various."""
    wordy = _stats(cardinality=900, present=1_000, numeric=0)
    assert wordy.dispersion > RANGE_DISPERSION
    assert not wordy.is_numeric
    assert not wordy.is_continuous


def test_a_quantity_is_exempt_from_the_identifier_ceiling_at_any_cardinality() -> None:
    """The ceiling separates a facet from a part number, not a list from a slider.

    The reference distributor offers ``Length of Cut (Decimal Inch)`` as a discrete list of
    819 values. A rule that dropped a quantitative attribute for exceeding 25
    would delete most of this catalog's sidebar the moment the control
    changed -- which is exactly what would have happened had the exemption
    stayed tied to the range control.
    """
    big_quantity = _stats(cardinality=819, present=10_000)
    assert big_quantity.cardinality > MAX_TERMS_CARDINALITY
    assert decide(big_quantity).facet, decide(big_quantity).reason

    part_number = _stats(cardinality=110, present=919, numeric=0)
    assert not decide(part_number).facet
    assert "identifier" in decide(part_number).reason


def test_changing_the_control_rule_changed_no_attributes_facet_status(
    flat_rows: list[dict],
) -> None:
    """The conversion moved the CONTROL and nothing else.

    Reconstructs the pre-#9285 rule -- where being numeric decided both
    questions -- and compares the set of attributes offered at all. If these
    sets ever differ, the conversion is silently adding or removing sidebar
    controls rather than changing their kind, and the before/after bucket
    counts published for the change would be comparing different sidebars.
    """
    stats = measure(flat_rows)
    new_faceted = {k for k, s in stats.items() if decide(s).facet}
    old_faceted = {
        k
        for k, s in stats.items()
        if s.cardinality >= 2
        and s.presence >= MIN_PRESENCE
        and (s.is_numeric or s.cardinality <= MAX_TERMS_CARDINALITY)
    }
    assert new_faceted == old_faceted, {
        "newly faceted": sorted(new_faceted - old_faceted),
        "no longer faceted": sorted(old_faceted - new_faceted),
    }


# ---------------------------------------------------------------------------
# The rule's PROSE, held to the catalog it describes
# ---------------------------------------------------------------------------
# ``derive.py`` argues for its thresholds from measured figures, and until this
# block nothing compared those figures to a catalog. Across one regeneration
# four of them drifted at once behind a fully green suite:
#
#     band over the dimensional attributes   0.003 - 0.144   0.0028 - 0.1401
#     Drive Size                             53 / 1,309      51 / 1,556
#     smallest faceted (Handle Length)       95              104
#
# and a fifth was wrong in a way no update would have fixed: the band was
# quoted over "every dimensional attribute" when it is a band over the FACETED
# ones. The widest quantitative dispersion in this catalog is 1.0000
# (``Neck Length``, 39 distinct values over 39 documents -- a perfect
# continuum), and what keeps THAT off a slider is ``RANGE_MIN_DOCS``, not
# ``RANGE_DISPERSION``. A single band credits the wrong threshold.
#
# So the figures moved into ``MEASURED_DISPERSION`` and these tests re-derive
# every one from the committed catalog.


@pytest.fixture(scope="module")
def decided(flat_rows: list[dict]) -> dict[str, tuple[AttributeStats, object]]:
    # The modelled types' documents only: ``MEASURED_DISPERSION`` describes
    # them, so a breadth type that publishes a shared attribute (Drive Size,
    # say) moves no pin here and two breadth PRs do not conflict on one. What
    # a breadth row does to a facet decision still reaches the committed
    # field map, which the drift test rebuilds.
    stats = measure([row for row in flat_rows if row.get("spec_quality") != SPEC_QUALITY])
    return {key: (value, decide(value)) for key, value in stats.items()}


def test_the_measured_figures_describe_a_catalog_that_exists(decided) -> None:
    """Non-vacuity control for the four tests below.

    Every one of them looks a name up in the derivation, and an EMPTY
    derivation would make the band tests raise rather than assert. Pinned
    explicitly so a broken catalog reads as broken rather than as agreement.
    """
    quantitative = [s for s, _ in decided.values() if s.is_numeric]
    faceted = [s for s, d in decided.values() if s.is_numeric and d.facet]
    # 39 since the retaining rings (#53); 38 since the set screws' Point Dia., which is not faceted.
    assert len(quantitative) == 39
    assert len(faceted) == 35


def test_the_faceted_dispersion_band_is_what_the_rule_states(decided) -> None:
    """The band, over the attributes it is actually a band over."""
    faceted = [s for s, d in decided.values() if s.is_numeric and d.facet]
    low = min(s.dispersion for s in faceted)
    high = max(s.dispersion for s in faceted)
    assert round(low, 4) == MEASURED_DISPERSION["faceted_low"]
    assert round(high, 4) == MEASURED_DISPERSION["faceted_high"]
    densest = max(faceted, key=lambda s: s.dispersion)
    assert densest.name == MEASURED_DISPERSION["densest_faceted"]
    assert high < RANGE_DISPERSION, "the band must sit below the threshold"


def test_the_widest_dispersion_is_a_continuum_kept_off_by_min_presence(decided) -> None:
    """The arm the band does NOT cover, and which threshold decides it now.

    ``Neck Length`` is a real continuum and clears ``RANGE_DISPERSION`` with
    room to spare. It used to be the catalog's real example of
    ``RANGE_MIN_DOCS`` -- too few documents to trust the dispersion statistic
    -- but applying its census presence rate once instead of twice
    (alexander-marquardt/synthetic-industrial-products#39) raised its
    document count from 48 to 388, clearing that floor too. It is still not
    offered as a range: it is rare even among end mills, the only product
    types that carry it, so ``MIN_PRESENCE`` is the floor that decides it
    now. If a regeneration drops either count back below its floor, this
    reds rather than quietly changing the control.
    """
    quantitative = [s for s, _ in decided.values() if s.is_numeric]
    widest = max(quantitative, key=lambda s: s.dispersion)
    assert widest.name == MEASURED_DISPERSION["min_presence_arm"]
    assert round(widest.dispersion, 4) == MEASURED_DISPERSION["min_presence_arm_dispersion"]
    assert widest.present == MEASURED_DISPERSION["min_presence_arm_present"]
    assert widest.type_denominator == MEASURED_DISPERSION["min_presence_arm_type_denominator"]
    assert widest.dispersion > RANGE_DISPERSION, (
        "dispersion alone would offer this as a RANGE -- the reason "
        "MIN_PRESENCE, not dispersion, has to be the one that keeps it off a "
        "slider"
    )
    assert widest.present >= RANGE_MIN_DOCS, (
        "RANGE_MIN_DOCS no longer decides this attribute -- if it reds, "
        "restate this test against whichever attribute IS below it, or "
        "against the constructed case in test_a_small_sample_falls_back_to_discrete"
    )
    assert widest.is_continuous
    presence_share = widest.present / widest.type_denominator
    assert round(presence_share, 2) == MEASURED_DISPERSION["min_presence_arm_share"]
    assert presence_share < MIN_PRESENCE, (
        "MIN_PRESENCE is the floor this test is about; it has to actually apply"
    )
    _, decision = decided["neck_length"]
    assert not decision.facet
    assert "floor 50%" in decision.reason, decision.reason


def test_drive_size_is_the_saturated_ladder_the_rule_names(decided) -> None:
    """The example the rule argues from, read off the catalog.

    ``test_continuity_refuses_a_saturated_ladder`` above CONSTRUCTS these
    numbers to probe the threshold. This one asserts the catalog really
    publishes them, which is what makes that construction an example rather
    than an invention.
    """
    stats, decision = decided["drive_size"]
    assert stats.cardinality == MEASURED_DISPERSION["drive_size_cardinality"]
    assert stats.present == MEASURED_DISPERSION["drive_size_present"]
    assert not stats.is_continuous
    assert stats.is_numeric, "still a quantity; only the control changed"
    assert decision.facet


def test_the_smallest_faceted_attribute_clears_the_document_floor(decided) -> None:
    """``RANGE_MIN_DOCS`` never decides a FACETED attribute here, and this is
    the figure that says so."""
    faceted = [s for s, d in decided.values() if s.is_numeric and d.facet]
    smallest = min(faceted, key=lambda s: s.present)
    assert smallest.name == MEASURED_DISPERSION["smallest_faceted"]
    assert smallest.present == MEASURED_DISPERSION["smallest_faceted_present"]
    assert smallest.present > RANGE_MIN_DOCS
