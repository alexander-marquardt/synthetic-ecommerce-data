"""The extracted fastener dimensions must be the published ones.

The gate that matters is the one the brief names: ASME B18.3.2 fixes the head
of a ``#10`` flat countersunk socket head cap screw at 0.411" across and
0.127" high. If the extraction does not reproduce those two numbers exactly
then every fastener in the catalog is subtly wrong, and nothing downstream
would notice.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.core.dimensions import parse_thread
from synthetic_ecommerce_data.domains.industrial import standards
from synthetic_ecommerce_data.domains.industrial.records import FIXTURES


def test_the_published_number_ten_flat_head_is_reproduced_exactly():
    head = standards.flat_head("ASME B18.3.2", "#10")
    assert head.head_dia_in == pytest.approx(0.411, abs=5e-4)
    assert head.head_height_in == pytest.approx(0.127, abs=5e-4)


def test_that_agreement_is_with_the_reference_record_too():
    """The reference cap screw carries the same two numbers, and must.

    26LD37 is a real archived record and publishes Head Dia. 0.411 in and
    Head Height 0.127 in. A generated #10 flat head cap screw publishing
    anything else would not be a #10 flat head cap screw. This is the exact
    case the non-copying guarantee has to tolerate, which is why that
    guarantee is stated over the full attribute tuple.
    """
    reference = FIXTURES["26LD37"]
    head = standards.flat_head("ASME B18.3.2", "#10")
    assert reference["Head Dia."] == "0.411 in"
    assert reference["Head Height"] == "0.127 in"
    assert head.head_dia_in == pytest.approx(0.411, abs=5e-4)
    assert head.head_height_in == pytest.approx(0.127, abs=5e-4)


def test_the_coarse_inch_series_lands_on_the_published_thread_counts():
    """25.4 / pitch must come out as the Unified coarse series, exactly."""
    expected = {
        "#6": 32,
        "#8": 32,
        "#10": 24,
        "1/4": 20,
        "5/16": 18,
        "3/8": 16,
        "1/2": 13,
        "5/8": 11,
    }
    for size, tpi in expected.items():
        head = standards.socket_head("ASME B18.3", size)
        assert head.threads_per_inch == pytest.approx(tpi, abs=1e-6), size


def test_metric_socket_head_dimensions_are_the_iso_4762_ones():
    # ISO 4762 M6: 10.0 mm head across, 6.0 mm high, 5 mm socket.
    head = standards.socket_head("ISO 4762", "M6")
    assert head.head_dia_in * 25.4 == pytest.approx(10.0, abs=1e-6)
    assert head.head_height_in * 25.4 == pytest.approx(6.0, abs=1e-6)
    assert head.pitch_mm == pytest.approx(1.0, abs=1e-9)


def test_every_thread_designation_parses():
    """A designation the repository's own parser cannot read is unusable."""
    for size in standards.available_sizes("ISO 4762"):
        head = standards.socket_head("ISO 4762", size)
        assert parse_thread(head.thread_designation).designation
    for size in standards.available_sizes("ASME B18.3"):
        head = standards.socket_head("ASME B18.3", size)
        assert parse_thread(head.thread_designation).designation


def test_two_standards_for_one_product_really_do_disagree():
    """ISO 4017 and DIN 933 differ on width across flats at M10 and M12.

    Both upstream sources reproduce the split identically, so it is a real
    difference between the standards rather than a transcription slip. The
    catalog uses it: which standard a line is built to changes a published
    dimension at the same nominal size.
    """
    for size, iso_mm, din_mm in (("M10", 16.0, 17.0), ("M12", 18.0, 19.0)):
        iso = standards.hex_bolt("ISO 4017", size)
        din = standards.hex_bolt("DIN 933", size)
        assert iso.width_across_flats_in * 25.4 == pytest.approx(iso_mm, abs=1e-6)
        assert din.width_across_flats_in * 25.4 == pytest.approx(din_mm, abs=1e-6)
        assert iso.width_across_flats_in != din.width_across_flats_in


def test_a_size_the_standard_does_not_define_is_refused_not_invented():
    """ASME B18.2.1 hex head screws start at 1/4"; there is no #10."""
    assert "#10" not in standards.available_sizes("ASME B18.2.1")
    with pytest.raises(standards.StandardsDataError):
        standards.hex_bolt("ASME B18.2.1", "#10")


def test_the_washer_standard_with_no_extracted_rows_yields_nothing():
    """DIN 125 A is absent upstream and is not back-filled from a bad source."""
    assert standards.available_sizes("DIN 125 A") == ()
    with pytest.raises(standards.StandardsDataError):
        standards.washer("DIN 125 A", "M6")


def test_washer_dimensions_come_from_iso_7089():
    # ISO 7089 M6: 12.0 mm outside, 6.4 mm inside, 1.6 mm thick.
    plain = standards.washer("ISO 7089", "M6")
    assert plain.outside_dia_in * 25.4 == pytest.approx(12.0, abs=1e-6)
    assert plain.inside_dia_in * 25.4 == pytest.approx(6.4, abs=1e-6)
    assert plain.thickness_in * 25.4 == pytest.approx(1.6, abs=1e-6)


def test_offered_lengths_are_the_sources_own_lists():
    lengths = standards.offered_lengths_in("ISO 4762", "M6")
    assert lengths, "ISO 4762 M6 must offer some lengths"
    in_mm = sorted(round(v * 25.4, 3) for v in lengths)
    # The source's list for M6 runs 8 mm to 60 mm on the standard nominals.
    assert in_mm[0] == pytest.approx(8.0, abs=1e-6)
    assert in_mm[-1] == pytest.approx(60.0, abs=1e-6)
    assert 25.0 in in_mm


def test_a_washer_has_no_offered_lengths():
    assert standards.offered_lengths_in("ISO 7089", "M6") == ()


def test_provenance_names_every_upstream_repository_and_licence():
    prov = standards.provenance()
    repos = prov["repositories"]
    by_name = {r["name"]: r for r in repos}
    assert "FreeCAD_FastenersWB" in by_name
    assert by_name["FreeCAD_FastenersWB"]["license"].startswith("GPL-2.0")
    assert "boltsparts" in by_name
    assert "LGPL-2.1" in by_name["boltsparts"]["license"]
    for repo in repos:
        assert repo["commit_sha"], f"{repo['name']} must name the commit it was read at"


def test_the_excluded_source_material_is_recorded_as_excluded():
    prov = standards.provenance()
    bolts = next(r for r in prov["repositories"] if r["name"] == "boltsparts")
    exclusions = " ".join(bolts["exclusions_honoured"]).lower()
    assert "profile_hollow" in exclusions
    assert "10642" in exclusions
    assert "washer" in exclusions


def test_the_fine_thread_transcription_covers_the_sizes_offered():
    for size in ("#10", "1/4", "3/8", "1/2"):
        designation = standards.thread_designation_inch(size, fine=True, coarse_tpi=None)
        assert parse_thread(designation).designation == designation
    assert standards.thread_designation_inch("#10", fine=True, coarse_tpi=None) == "#10-32"
