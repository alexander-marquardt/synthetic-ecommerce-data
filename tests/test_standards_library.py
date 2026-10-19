"""One shared standards library: each size table is sourced once, cited and reused (#73).

A table is one JSON file under ``core/standards_library/tables/``. Adding one is a new
file, never an edit to a shared list, so parallel family PRs do not collide: the planted
proof below adds a file and reads it through the library without touching an existing one.
Each table also has a test of its own rule (ascending sizes, a pitch that matches its
series), and each consumer is held to the library's figures, so a copy cannot drift.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import noise
from synthetic_ecommerce_data.core import standards_library as lib
from synthetic_ecommerce_data.domains.industrial import compat, newtypes, standards
from synthetic_ecommerce_data.domains.industrial.product_types.fasteners import (
    lock_nuts_nylon_insert as lock_nuts,
)

#: Every table the library ships, by file name.
EXPECTED = (
    "iso_2936_hex_key_mm",
    "asme_b18_3_hex_key_in",
    "iso_492_normal_bore_tolerance",
    "asme_b1_1_unified_threads",
    "iso_262_metric_threads",
    "asme_b18_2_2_hex_nuts_in",
    "metric_tap_drills",
    "inch_tap_drills",
    "property_class_strength",
    "fastener_standards",
    "fastener_offered_lengths",
    "set_screw_standards",
    "as568_sizes",
)

PACKAGE = Path(lib.__file__).resolve().parent


def _write(root: Path, name: str, body: dict) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{name}.json").write_text(json.dumps(body), encoding="utf-8")


def _header(**over: object) -> dict:
    return {
        "standards": ["ISO 9999"],
        "edition": "ISO 9999:2001 Table 1",
        "source": "a planted table",
        "kind": "series",
    } | over


def test_the_library_lists_every_table():
    assert set(EXPECTED) <= set(lib.names())


@pytest.mark.parametrize("name", EXPECTED)
def test_every_table_cites_the_standard_and_edition_it_was_read_from(name):
    table = lib.table(name)
    assert table.name == name
    assert table.standards, name
    assert all(isinstance(s, str) and s for s in table.standards), name
    assert table.edition.strip(), name
    assert table.source.strip(), name


def test_a_new_table_file_is_read_without_editing_an_existing_one(tmp_path):
    """The planted proof: a new file is all it takes."""
    before = {p.name: p.read_bytes() for p in (PACKAGE / "tables").glob("*.json")}
    _write(tmp_path, "iso_9999_planted", {"_library": _header(), "values": [1, 2, 4]})
    library = lib.Library(tmp_path)
    assert "iso_9999_planted" in library.names()
    assert set(EXPECTED) <= set(library.names())
    planted = library.table("iso_9999_planted")
    assert planted.values == [1, 2, 4]
    assert planted.standards == ("ISO 9999",)
    assert before == {p.name: p.read_bytes() for p in (PACKAGE / "tables").glob("*.json")}


@pytest.mark.parametrize("missing", ["standards", "edition", "source", "kind"])
def test_a_table_that_does_not_cite_its_source_is_refused(tmp_path, missing):
    header = _header()
    del header[missing]
    _write(tmp_path, "uncited", {"_library": header, "values": [1]})
    with pytest.raises(lib.StandardsTableError, match=missing):
        lib.Library(tmp_path).table("uncited")


def test_a_table_with_no_library_block_is_refused(tmp_path):
    _write(tmp_path, "bare", {"values": [1]})
    with pytest.raises(lib.StandardsTableError, match="_library"):
        lib.Library(tmp_path).table("bare")


def test_two_files_of_one_name_are_refused(tmp_path):
    _write(tmp_path, "iso_2936_hex_key_mm", {"_library": _header(), "values": [1]})
    with pytest.raises(lib.StandardsTableError, match="iso_2936_hex_key_mm"):
        lib.Library(tmp_path).names()


def test_an_unknown_table_names_the_ones_there_are():
    with pytest.raises(lib.StandardsTableError, match="iso_2936_hex_key_mm"):
        lib.table("no_such_table")


def test_select_keeps_the_callers_order_and_refuses_a_row_the_table_lacks():
    chosen = lib.table("asme_b1_1_unified_threads").select(["1/4", "#10"])
    assert [r["size"] for r in chosen] == ["1/4", "#10"]
    with pytest.raises(lib.StandardsTableError, match="2 1/2"):
        lib.table("asme_b1_1_unified_threads").select(["#10", "2 1/2"])


def test_the_moved_extractions_left_the_industrial_data_directory():
    data = Path(standards.__file__).parent / "data"
    for name in (
        "fastener_standards",
        "fastener_offered_lengths",
        "set_screw_standards",
        "as568_sizes",
    ):
        assert (PACKAGE / "tables" / f"{name}.json").is_file(), name
        assert not (data / f"{name}.json").exists(), name


# --- each table's own rule ---------------------------------------------------------


def _ascending(values) -> bool:
    return len(values) > 3 and all(a < b for a, b in zip(values, values[1:], strict=False))


def test_the_hex_key_series_are_ascending_and_cited_to_their_standards():
    mm = lib.table("iso_2936_hex_key_mm")
    inch = lib.table("asme_b18_3_hex_key_in")
    assert mm.standards == ("ISO 2936",) and inch.standards == ("ASME B18.3",)
    assert _ascending(mm.values)
    assert _ascending([Fraction(v) for v in inch.values])


def test_the_bore_tolerance_ranges_are_contiguous_and_never_tighten_with_size():
    rows = lib.table("iso_492_normal_bore_tolerance").rows
    assert len(rows) >= 4
    for (_, high, tol), (low, _, nxt) in zip(rows, rows[1:], strict=False):
        assert high == low
        assert nxt >= tol
    assert all(low < high for low, high, _ in rows)


def test_a_unified_thread_pitch_matches_its_series():
    rows = lib.table("asme_b1_1_unified_threads").rows
    assert len(rows) >= 13
    coarse = [r["unc_tpi"] for r in rows if r.get("unc_tpi")]
    # Coarser threads per inch fall as the diameter grows, down the ladder.
    assert all(a >= b for a, b in zip(coarse, coarse[1:], strict=False))
    for row in rows:
        if row.get("unc_tpi") and row.get("unf_tpi"):
            assert row["unf_tpi"] > row["unc_tpi"], row["size"]
    majors = [r["major_dia_in"] for r in rows]
    assert _ascending(majors)
    for row in rows:
        if row["size"].startswith("#"):
            number = int(row["size"][1:])
            assert row["major_dia_in"] == pytest.approx(0.060 + 0.013 * number, abs=5e-4), row[
                "size"
            ]
        else:
            assert row["major_dia_in"] == pytest.approx(float(Fraction(row["size"])))


def test_a_metric_fine_pitch_is_finer_than_its_coarse_pitch():
    rows = {r["size"]: r for r in lib.table("iso_262_metric_threads").rows}
    assert len(rows) >= 10
    assert _ascending([r["diameter_mm"] for r in rows.values()])
    for size, row in rows.items():
        assert size == f"M{row['diameter_mm']:g}"
        assert all(fine < row["coarse_pitch_mm"] for fine in row.get("fine_pitches_mm", ())), size


def test_every_metric_nut_designation_carries_its_standards_pitch():
    rows = {r["size"]: r["coarse_pitch_mm"] for r in lib.table("iso_262_metric_threads").rows}
    assert len(rows) >= 10
    fine = {
        (r["size"], p)
        for r in lib.table("iso_262_metric_threads").rows
        for p in r.get("fine_pitches_mm", ())
    }
    tables = [newtypes._NUT_METRIC, lock_nuts._ISO_7040, lock_nuts._ISO_10511, lock_nuts._DIN_985]
    checked = 0
    for table in tables:
        for thread, *_ in table:
            size, pitch = thread.split("x")
            assert rows[size] == float(pitch), thread
            checked += 1
    fine_rows = [row for rng in (*newtypes._NUT_METRIC_FINE, *lock_nuts._ISO_10512) for row in rng]
    for thread, *_ in fine_rows:
        size, pitch = thread.split("x")
        assert (size, float(pitch)) in fine, thread
        checked += 1
    assert checked > 30


def test_the_hex_nut_widths_are_the_b18_2_2_rows_and_a_jam_nut_is_thinner():
    table = lib.table("asme_b18_2_2_hex_nuts_in")
    rows = table.rows
    assert len(rows) >= 11
    flats = [Fraction(r["flats_in"]) for r in rows]
    assert flats == sorted(flats)
    for row in rows:
        if row.get("jam_height_in"):
            assert Fraction(row["jam_height_in"]) < Fraction(row["height_in"]), row["size"]


def test_a_tap_drill_is_smaller_than_the_thread_it_makes_a_hole_for():
    metric = lib.table("metric_tap_drills").rows
    assert len(metric) >= 10
    for row in metric:
        diameter = float(re.match(r"M([\d.]+)x", row["thread"]).group(1))
        assert row["drill_mm"] < diameter, row["thread"]
    inch = lib.table("inch_tap_drills").rows
    assert len(inch) >= 10
    majors = {r["size"]: r["major_dia_in"] for r in lib.table("asme_b1_1_unified_threads").rows}
    for row in inch:
        size = row["thread"].split("-")[0]
        assert row["dia_in"] < majors[size], row["thread"]


def test_a_stronger_class_has_the_higher_number():
    rows = lib.table("property_class_strength").rows
    assert len(rows) >= 3
    for row in rows:
        number = lambda s: float(s.split()[-1])  # noqa: E731
        assert number(row["class"]) > number(row["stronger_than"]), row


# --- each consumer reads the library, not a copy -----------------------------------


def test_the_key_series_the_catalog_uses_are_the_library_tables():
    assert tuple(lib.table("iso_2936_hex_key_mm").values) == compat.KEY_SERIES_MM
    assert (
        tuple(float(Fraction(v)) for v in lib.table("asme_b18_3_hex_key_in").values)
        == compat.KEY_SERIES_IN
    )
    assert set(newtypes._KEY_MM) <= set(compat.KEY_SERIES_MM)
    assert set(newtypes._KEY_INCH) <= set(compat.KEY_SERIES_IN)


def test_the_bore_tolerance_the_noise_reads_is_the_library_table():
    rows = lib.table("iso_492_normal_bore_tolerance").rows
    assert tuple(tuple(r) for r in rows) == noise.BORE_TOLERANCE_MM


def test_the_thread_series_every_family_reads_are_one_table():
    rows = {r["size"]: r for r in lib.table("asme_b1_1_unified_threads").rows}
    assert len(rows) >= 13
    for size, tpi in standards.UNF_THREADS_PER_INCH.items():
        assert rows[size]["unf_tpi"] == tpi
    for size, dia in standards.INCH_MAJOR_DIA.items():
        assert rows[size]["major_dia_in"] == dia
    for thread, *_ in (*newtypes._NUT_UNC, *newtypes._NUT_UNF):
        size, tpi = thread.rsplit("-", 1)
        assert int(tpi) in (rows[size].get("unc_tpi"), rows[size].get("unf_tpi")), thread
    for thread in (*lock_nuts._UNC, *lock_nuts._UNF):
        size, tpi = thread.rsplit("-", 1)
        assert int(tpi) in (rows[size].get("unc_tpi"), rows[size].get("unf_tpi")), thread
    fine = {
        r["size"]: tuple(r.get("fine_pitches_mm", ()))
        for r in lib.table("iso_262_metric_threads").rows
    }
    assert {
        s: p for s, p in fine.items() if s in compat.METRIC_FINE_PITCHES and p
    } == compat.METRIC_FINE_PITCHES
    assert set(compat.METRIC_FINE_PITCHES) <= {s for s, p in fine.items() if p}


def test_the_nut_tables_the_catalog_uses_are_the_b18_2_2_rows():
    rows = {r["size"]: r for r in lib.table("asme_b18_2_2_hex_nuts_in").rows}
    assert len(rows) >= 11
    for thread, flats, height in newtypes._NUT_UNC:
        row = rows[thread.rsplit("-", 1)[0]]
        assert (flats, height) == (
            float(Fraction(row["flats_in"])),
            float(Fraction(row["height_in"])),
        )
    for size, jam in newtypes._JAM_HEIGHT_IN.items():
        assert jam == float(Fraction(rows[size]["jam_height_in"]))
    for size, flats in lock_nuts._FLATS_IN.items():
        assert flats == float(Fraction(rows[size]["flats_in"]))


def test_the_tap_drills_the_sentences_cite_are_the_library_tables():
    metric = {r["thread"]: r["drill_mm"] for r in lib.table("metric_tap_drills").rows}
    assert metric == compat.TAP_DRILLS_METRIC
    inch = {r["thread"]: (r["drill"], r["dia_in"]) for r in lib.table("inch_tap_drills").rows}
    assert inch == compat.TAP_DRILLS_INCH


def test_the_stronger_than_pairs_are_the_library_table():
    rows = lib.table("property_class_strength").rows
    assert {r["class"]: r["stronger_than"] for r in rows} == noise.STRONGER_THAN
