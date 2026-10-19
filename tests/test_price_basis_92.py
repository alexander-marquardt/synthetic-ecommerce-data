"""Every price census entry says which price it measured (#92).

#57's price is the price the page shows, which on a clearance row is the
clearance price, and its parser was never committed, so its 2015 entries cannot
be shown to be on the regular price. #69's two entries are on the regular price.
The census flags the difference field by field, so part B cannot compare or pool
price levels across the two without reading the flag.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CENSUS = json.loads((ROOT / "reference-statistics" / "P2_price_census.json").read_text())
MANIFEST = json.loads((ROOT / "reference-statistics" / "MANIFEST.json").read_text())

REGULAR = "regular_price"
UNMEASURED = "shown_price_clearance_unmeasured"

SHOWN_PRICE = frozenset(
    {
        "abrasive_flap_disc",
        "bearing_radial_ball",
        "bolt_hex",
        "drill_jobber",
        "end_mill_ball",
        "end_mill_square",
        "hex_key",
        "kit_assortment",
        "nut_hex",
        "screw_flat_head",
        "screw_socket_head",
        "tap_spiral_point",
        "washer_flat",
        "wheel_depressed_center",
        "ball_valves",
        "blind_rivets",
        "c_clamps",
        "carriage_bolts",
        "cold_chisels",
        "combination_wrenches",
        "cut_resistant_gloves",
        "eye_bolts",
        "foam_ear_plugs",
        "hand_files",
        "hex_pipe_nipples",
        "hose_clamps",
        "rigid_casters",
        "roller_chain",
        "safety_glasses",
        "threaded_rod",
        "u_bolts",
        "v_belts",
        "wedge_anchors",
    }
)  # #57's 33 entries, frozen: a later re-measure moves an entry out by editing this

PRICED = [
    (section, key)
    for section in ("deep_types", "breadth_categories")
    for key, entry in CENSUS[section].items()
    if entry["n"] > 0
]


def _parser():
    path = ROOT / "scripts" / "price_census_parse.py"
    spec = importlib.util.spec_from_file_location("price_census_parse_92", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["price_census_parse_92"] = module  # a dataclass resolves its module by name
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("section", "key"), PRICED)
def test_every_priced_entry_names_the_price_it_measured(section, key):
    basis = CENSUS[section][key].get("price_basis")
    if key in SHOWN_PRICE:
        assert basis == UNMEASURED
    else:
        assert basis in {REGULAR, UNMEASURED}


def test_the_frozen_shown_price_set_is_all_present_and_priced():
    assert {key for _, key in PRICED} >= SHOWN_PRICE
    assert len(SHOWN_PRICE) == 33


def test_the_flag_covers_every_entry_the_pooled_figures_are_drawn_from():
    pooled = CENSUS["pooled_endings_all_types"]
    assert pooled.get("price_basis") == UNMEASURED


def test_the_method_block_defines_both_values():
    basis = CENSUS["method"].get("price_basis", "")
    assert REGULAR in basis
    assert UNMEASURED in basis
    assert "#92" in basis


def test_the_parser_stamps_the_regular_price_on_the_entries_it_writes():
    parse = _parser()
    row = parse.Row(
        "X", "A", "20150408043348", "page", 4.0, True, 100, "pack", 0.25, 0.375, ()
    )
    entry = parse.entry([row], {}, "Thread Size", length_held=True)
    assert entry.get("price_basis") == REGULAR


@pytest.mark.parametrize(
    "path",
    [
        ROOT / "scripts" / "price_census_parse.py",
        ROOT / "reference-statistics" / "MANIFEST.json",
    ],
)
def test_no_file_still_points_at_the_issue_placeholder(path):
    text = path.read_text()
    assert "ISSUE_PLACEHOLDER" not in text
    assert "#92" in text


def test_the_manifest_records_the_flag_and_what_clears_it():
    note = MANIFEST["P2_price_census"].get("price_basis_92", "")
    assert UNMEASURED in note
    assert "re-measure" in note
