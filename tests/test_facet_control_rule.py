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
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.prism.derive import (
    MAX_TERMS_CARDINALITY,
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
    assert [s.key for s in quantitative if s.is_continuous] == [], (
        "this catalog contains no continuum; any attribute reported as one "
        "should be checked before the rule is trusted"
    )


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
    """The industrial case, constructed to the issue's own figures.

    53 distinct drive sizes over 1,309 documents. Each value is carried by
    about 25 products, which is what makes a list of them something a shopper
    picks from.
    """
    drive = _stats(cardinality=53, present=1_309)
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

    The customer offers ``Length of Cut (Decimal Inch)`` as a discrete list of
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
