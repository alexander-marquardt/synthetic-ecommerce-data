"""Which CONTROL an attribute is offered under -- range or discrete list.

The rule under test (elastic/prism#9285): an attribute is offered as a range
only when its values are CONTINUOUS, measured as saturation -- distinct values
per distinct (product, value) pair publishing it (#28) -- and not merely because they happen to be
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
    IDENTIFIER_DISPERSION,
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


def _stats(
    *,
    cardinality: int,
    present: int,
    numeric: int | None = None,
    product_values: int | None = None,
    products: int | None = None,
    name: str = "Probe",
) -> AttributeStats:
    """A constructed measurement, for cases the industrial catalog lacks.

    ``product_values`` and ``products`` default to ``present``: one SKU per
    product and one value per SKU, so the per-document, per-pair and
    per-product counts agree unless a test separates them.
    """
    return AttributeStats(
        key="probe",
        name=name,
        present=present,
        numeric=present if numeric is None else numeric,
        cardinality=cardinality,
        product_types=("probe_type",),
        type_denominator=present,
        product_values=present if product_values is None else product_values,
        products=present if products is None else products,
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


def test_a_quantity_is_exempt_from_the_identifier_rule_at_any_dispersion() -> None:
    """The identifier rule separates a facet from a part number, not a list from a slider.

    The reference distributor offers ``Length of Cut (Decimal Inch)`` as a discrete list of
    819 values. A quantity whose values never repeat is a continuum, not a
    part number, so it is offered (as a range) where a terms attribute with
    the same figures is withheld.
    """
    big_quantity = _stats(cardinality=819, present=10_000)
    assert decide(big_quantity).facet, decide(big_quantity).reason

    unrepeated = _stats(cardinality=819, present=820)
    assert unrepeated.dispersion >= IDENTIFIER_DISPERSION
    assert not unrepeated.is_identifier
    assert decide(unrepeated).facet, decide(unrepeated).reason

    # List Number's shape: a series code, about one value per product.
    part_number = _stats(cardinality=110, present=919, numeric=0, product_values=113)
    assert part_number.is_identifier
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
        and (s.is_numeric or not s.is_identifier)
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
    # 38 since the set screws' Point Dia. (#53), which is not faceted.
    assert len(quantitative) == 38
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


# ---------------------------------------------------------------------------
# A facet or an identifier: a property of the values, not of the catalog's size
# (alexander-marquardt/synthetic-industrial-products#31, #28)
# ---------------------------------------------------------------------------
# The retired rule withheld a terms attribute with more than 25 distinct values.
# 25 is a count, and a count does not grow with the catalog: Thread Size, a
# standards body's ladder, passed it at 19 values and failed it at 55, while
# nothing about it had become an identifier.

#: The retired absolute cap, kept here only to reconstruct the old rule.
RETIRED_TERMS_CAP = 25

#: What the default build gains under the relative rule: every one is a terms
#: attribute the retired cap withheld for its count alone. Measured on the
#: default build and on ``--lines 39000`` (111,499 SKUs); the same seven at both.
NEWLY_OFFERED = frozenset(
    {
        "bearing_number",
        "dia_thread_size",
        "item",
        "sizes_included",
        "standards",
        "thread_size",
        "type",
    }
)


def test_the_identifier_figures_are_what_the_rule_states(decided) -> None:
    """The terms side of the band, read off the catalog like the quantitative one.

    Exactly one terms attribute is withheld as an identifier, and the densest
    terms facet sits well under the line, so the threshold is not deciding
    anything by a hair.
    """
    identifiers = [s for s, _ in decided.values() if s.is_identifier]
    assert [s.name for s in identifiers] == [MEASURED_DISPERSION["identifier"]]
    assert round(identifiers[0].dispersion, 4) == MEASURED_DISPERSION["identifier_dispersion"]
    _, decision = decided[identifiers[0].key]
    assert not decision.facet

    terms_facets = [
        s
        for s, d in decided.values()
        if not s.is_numeric and d.facet and s.product_values >= RANGE_MIN_DOCS
    ]
    densest = max(terms_facets, key=lambda s: s.dispersion)
    assert densest.name == MEASURED_DISPERSION["densest_terms_facet"]
    assert round(densest.dispersion, 4) == MEASURED_DISPERSION["densest_terms_facet_dispersion"]
    assert densest.dispersion < IDENTIFIER_DISPERSION


@pytest.mark.parametrize("scale", [1, 10, 100])
def test_a_ladder_stays_a_facet_and_an_identifier_stays_withheld_at_any_size(
    scale: int,
) -> None:
    """The same two attributes, measured on catalogs 1x, 10x and 100x as large.

    A ladder keeps its rungs while products accumulate, so its cardinality is
    fixed (55, Thread Size's count on the default build). An identifier gains
    a value with nearly every product. The decision for each must not move
    with the scale.
    """
    products = 200 * scale
    ladder = _stats(cardinality=55, present=products, numeric=0)
    assert decide(ladder).facet, decide(ladder).reason

    identifier = _stats(cardinality=products * 97 // 100, present=products, numeric=0)
    assert not decide(identifier).facet
    assert "identifier" in decide(identifier).reason


def test_the_identifier_threshold_is_the_midpoint_and_both_sides_are_reachable() -> None:
    """Astride the boundary: one value apart, so the comparison is not vacuous.

    Both sides carry far more than 25 values, so the retired cap would have
    withheld both.
    """
    below = _stats(cardinality=99, present=200, numeric=0)
    at = _stats(cardinality=100, present=200, numeric=0)
    assert decide(below).facet, decide(below).reason
    assert not decide(at).facet
    assert "identifier" in decide(at).reason


def test_a_small_terms_attribute_is_not_called_an_identifier() -> None:
    """Below ``RANGE_MIN_DOCS`` observations dispersion is not evidence.

    ``Style`` publishes 11 values over 13 products on the default build, a
    dispersion of 0.85, and it is a facet there today. A list under the floor
    holds fewer than ``RANGE_MIN_DOCS`` values, so offering it costs little;
    withholding it would drop a facet the default build offers.
    """
    style = _stats(cardinality=11, present=13, numeric=0)
    assert decide(style).facet, decide(style).reason
    floor = _stats(cardinality=RANGE_MIN_DOCS, present=RANGE_MIN_DOCS, numeric=0)
    assert not decide(floor).facet


def test_standards_and_thread_size_are_offered_and_list_number_is_not(rendered: str) -> None:
    """The issue's acceptance, on the rendered field map."""
    entries = _entries(rendered)
    for name in ("standards", "thread_size"):
        assert entries[name].get("facet") != "false", (name, entries[name])
    assert entries["list_number"].get("facet") == "false", entries["list_number"]


def test_no_facet_the_default_build_offers_is_lost(flat_rows: list[dict]) -> None:
    """The relative rule only ADDS facets, and exactly the named ones.

    Reconstructs the retired rule beside the current one over the default
    build. Every attribute it offered is still offered; what is new is the
    set of terms attributes it withheld for their count alone.
    """
    stats = measure(flat_rows)
    new_faceted = {k for k, s in stats.items() if decide(s).facet}
    old_faceted = {
        k
        for k, s in stats.items()
        if s.cardinality >= 2
        and s.presence >= MIN_PRESENCE
        and (s.is_numeric or s.cardinality <= RETIRED_TERMS_CAP)
    }
    assert old_faceted - new_faceted == set()
    assert new_faceted - old_faceted == NEWLY_OFFERED


def _rows_of(products: int, variants: int, value_of) -> list[dict]:
    """Constructed flat rows: ``products`` products of ``variants`` SKUs each."""
    rows = []
    for p in range(products):
        for v in range(variants):
            value = value_of(p, v)
            rows.append(
                {
                    "product_id": f"P{p}",
                    "product_type": "probe_type",
                    "facets": {"load": [str(value)]},
                    "facets_num": {"load": float(value)},
                    "attributes": [{"name": "Load", "value": str(value)}],
                }
            )
    return rows


def test_dispersion_counts_products_not_sku_variants() -> None:
    """A product-scope value repeated on its siblings is one observation.

    60 products, each with its own rating, published on all 4 of its SKUs.
    Per document that reads as 60 values over 240 documents (0.25), a ladder;
    per product it is 60 over 60, a continuum. The answer must not depend on
    how many variants a product happens to have (#28).
    """
    for variants in (1, 4, 9):
        stats = measure(_rows_of(60, variants, lambda p, v: 1000 + 7 * p))["load"]
        assert stats.present == 60 * variants
        assert stats.product_values == 60
        assert stats.dispersion == 1.0
        assert stats.is_continuous, variants


def test_a_sku_scope_ladder_is_still_a_ladder() -> None:
    """Values that vary across a product's SKUs are each an observation.

    60 products, 4 SKUs each, every SKU on one of 8 rungs: 240 distinct
    (product, value) pairs and 8 values, so the ladder stays a list.
    """
    stats = measure(_rows_of(60, 4, lambda p, v: (p + v) % 8))["load"]
    assert stats.product_values == 240
    assert stats.cardinality == 8
    assert not stats.is_continuous


# ---------------------------------------------------------------------------
# Both rules ask whether values repeat ACROSS PRODUCTS, so the evidence floor
# has to count products. A kit lists a dozen sizes, so five kits made 52
# (product, value) pairs at ``--lines 200`` and cleared a floor counted in
# pairs: Sizes Included was withheld at 200, 400 and 600 lines and offered
# from 900 up (#31 review).

#: The sizes the decisions are compared across. 260 is where Overall Length,
#: a ladder at every larger size, reads exactly 0.5 on 202 products: the
#: largest product count at which any ladder in this catalog still looks like
#: a continuum. ``--lines 39000`` makes the same decisions as the default
#: build (measured by hand for #31; too slow to build here).
STABILITY_SIZES = (200, 260, 400, 600, 900)


def _controls(rows: list[dict]) -> dict[str, str]:
    """The control each attribute gets, for those past the presence gates.

    Presence (``MIN_PRESENCE``) and cardinality are left out on purpose: a
    category-scoped attribute sampled on a few products can fall either side
    of 50% presence, and that is not what the dispersion rules decide.
    """
    out = {}
    for key, stats in measure(rows).items():
        if stats.cardinality < 2 or stats.presence < MIN_PRESENCE:
            continue
        decision = decide(stats)
        if not decision.facet:
            out[key] = "withheld"
        else:
            out[key] = "range" if stats.is_continuous else "list"
    return out


@pytest.fixture(scope="module")
def controls_by_size(flat_rows: list[dict]) -> dict[int, dict[str, str]]:
    by_size = {
        lines: _controls(list(emit.iter_flat(generate(GeneratorConfig(lines=lines)))))
        for lines in STABILITY_SIZES
    }
    by_size[GeneratorConfig().lines] = _controls(flat_rows)
    return by_size


def test_every_decision_is_the_same_at_every_catalog_size(controls_by_size) -> None:
    """No attribute changes between withheld, range and list with ``--lines``.

    The rules are ratios so that the answer does not move with catalog size;
    this is the test that varies the size. The three the review measured
    moving are named, so a regression on them reads by name.
    """
    seen: dict[str, dict[int, str]] = {}
    for lines, controls in controls_by_size.items():
        for key, control in controls.items():
            seen.setdefault(key, {})[lines] = control
    moved = {key: by for key, by in seen.items() if len(set(by.values())) > 1}
    assert moved == {}
    sizes = sorted(controls_by_size)
    for key in ("sizes_included", "bore", "overall_length"):
        assert [controls_by_size[lines][key] for lines in sizes] == ["list"] * len(sizes), key
    assert [controls_by_size[lines]["list_number"] for lines in sizes] == ["withheld"] * len(sizes)


def _terms_rows(name: str, values_of: dict[str, list[str]]) -> list[dict]:
    """One SKU per product, publishing a terms attribute with the given values."""
    return [
        {
            "product_id": product,
            "product_type": "probe_type",
            "facets": {emit.sanitize(name): list(values)},
            "facets_num": {},
            "attributes": [{"name": name, "value": value} for value in values],
        }
        for product, values in values_of.items()
    ]


def test_a_multi_valued_attribute_on_few_products_is_not_an_identifier() -> None:
    """Twenty kits of thirteen sizes each: 260 pairs, but twenty products.

    Dispersion over twenty products is not evidence that values never repeat
    across products, however many pairs the kits list, so the attribute is
    offered, as Sizes Included is at every size. The pairs clear the floor
    and the products do not, so it is the floor's unit under test.
    """
    kits = {f"K{k}": [f"{13 * k + i}/64 in." for i in range(13)] for k in range(20)}
    stats = measure(_terms_rows("Sizes Included", kits))["sizes_included"]
    assert (stats.cardinality, stats.product_values, stats.products) == (260, 260, 20)
    assert stats.products < RANGE_MIN_DOCS <= stats.product_values
    decision = decide(stats)
    assert decision.facet, decision.reason


def test_a_declared_identifier_is_withheld_whatever_its_dispersion() -> None:
    """The generator says List Number is a part code; derive reads that.

    600 products sharing ten codes is a dispersion of 0.017, a ladder by the
    ratio, which is what a finite code pool becomes once the catalog outgrows
    it (List Number reads 0.62 at ``--lines 39000`` and crosses 0.5 near 62K
    lines). The same rows under an undeclared name are a facet, so it is the
    declaration that withholds it.
    """
    codes = {f"P{p}": [f"L{p % 10:03d}"] for p in range(600)}
    declared = measure(_terms_rows("List Number", codes))["list_number"]
    assert declared.dispersion < IDENTIFIER_DISPERSION
    decision = decide(declared)
    assert not decision.facet
    assert "declares" in decision.reason, decision.reason

    undeclared = measure(_terms_rows("Series Code", codes))["series_code"]
    assert decide(undeclared).facet, decide(undeclared).reason


def test_derive_reads_the_generators_identifier_declaration() -> None:
    """One source for which attributes are identifiers: the generator's own set."""
    from synthetic_industrial_products.catalog.generate import Generator
    from synthetic_industrial_products.prism import derive

    assert derive.IDENTIFIER_ATTRIBUTES is Generator.IDENTIFIER_ATTRIBUTES
