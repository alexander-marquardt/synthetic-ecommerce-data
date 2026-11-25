"""Breadth types drawn as their own product fill at least half of the product area (#1216).

Each type of ``BREADTH_PRODUCTS`` is drawn at every angle its orientation allows, at every size it
sells, and measured with #1129's sweep (``picture_fill_1129.sheet_measures``)."""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.core import brands, domain, drawing  # noqa: E402
from synthetic_ecommerce_data.core.drawing import product_look  # noqa: E402
from synthetic_ecommerce_data.domains.industrial import breadth  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.drawing import breadth_rungs  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_products import (  # noqa: E402
    BREADTH_PRODUCTS,
)
from test_sku_drawings import MAX_DRAWING_BYTES  # noqa: E402

FLOOR = 0.50
#: The named exceptions: a true outline that cannot reach the floor, at its own measured one.
FLOORS: dict[str, float] = {
    "blind_rivets": 0.43,  # a mandrel and a body narrower than the flange
    "c_clamps": 0.42,  # its throat is open
    "chain_lubricants": 0.41,  # an aerosol is a narrow can
    "compound_cutters": 0.39,  # its handles stand apart
    "eye_bolts": 0.43,  # an open eye over a narrower shank
    "grub_screw_keys": 0.23,  # an L of hex bar, open between its arms
    "replacement_pins": 0.36,  # an eye, a collar and a narrower shank
    "spanner_wrenches": 0.31,  # an open hook over its handle
    # Rods, laid corner to corner.
    "cold_chisels": 0.33,
    "magnetic_bit_holders": 0.23,
    "nut_drivers_hex": 0.24,
    "pin_pullers": 0.20,
    "sds_drill_bits": 0.18,
    "tap_extractors": 0.24,
    "thread_plug_gages": 0.26,
    "thread_restoring_files": 0.26,
}

#: Slice 2: the types drawn by their row's shared shape at 5 to 15% of the area before it.
SLICE_2 = (
    "backing_pads",
    "band_saw_blades",
    "bench_tool_racks",
    "bit_index_cases",
    "bit_socket_sets",
    "blind_rivets",
    "cantilever_racks",
    "cold_chisels",
    "cutter_sharpening_fixtures",
    "cutter_storage_cases",
    "diamond_wheels",
    "drawer_slides",
    "driver_bit_sets",
    "foam_ear_plugs",
    "grub_screw_keys",
    "handle_wedges",
    "hex_bit_socket_sets",
    "micro_collets",
    "nut_drivers_hex",
    "nylon_wall_anchors",
    "piloted_counterbores",
    "pin_punch_sets",
    "pneumatic_cut_off_tools",
    "quick_disconnect_couplings",
    "rigging_pulleys",
    "rigid_shaft_couplings",
    "snap_ring_pliers",
    "spanner_wrenches",
    "spill_socks",
    "thread_restoring_files",
    "tool_holsters",
    "v_belts",
    "wrench_organizers",
)


#: Slice 3: the last 32 types under half the area before it.
SLICE_3 = (
    "ball_stock_precision",
    "ball_stock_rubber",
    "ball_valves",
    "bench_vises",
    "bit_sharpeners",
    "center_punches",
    "circle_cutters",
    "compression_springs",
    "cutter_storage_racks",
    "fastener_extractors",
    "flat_gaskets",
    "fluted_dowels",
    "grooving_cutters",
    "hose_clamps",
    "induction_heaters",
    "keyed_padlocks",
    "milling_collets",
    "milling_tool_holders",
    "nut_splitters",
    "seal_pick_sets",
    "sems_bolts",
    "serrated_flange_nuts",
    "shaft_collars",
    "side_lock_holders",
    "swivel_casters",
    "t_slot_nuts",
    "tap_wrenches",
    "thread_pitch_gages",
    "timing_pulleys",
    "u_bolts",
    "wedge_anchors",
    "wheel_mandrels",
)


@pytest.mark.parametrize("key", SLICE_2)
def test_a_slice_2_type_is_drawn_as_its_own_product(key):
    """Every fill test below runs over ``BREADTH_PRODUCTS``, so a type that leaves it is
    unmeasured."""
    assert key in BREADTH_PRODUCTS


@pytest.mark.parametrize("key", SLICE_3)
def test_a_slice_3_type_is_drawn_as_its_own_product(key):
    """As for slice 2."""
    assert key in BREADTH_PRODUCTS


def test_every_named_exception_is_under_the_floor():
    """An exception that reaches the floor is an exception no longer."""
    for key, floor in FLOORS.items():
        assert floor <= min(area.cover for _, _, area in _measured(key)) < FLOOR, key


def _measured(key):
    row = breadth.row_for(key)
    common = {name: values[0] for name, values in row.attributes.items()}
    records = [{**common, row.size_attr: value} for value in row.size_values]
    ratios = breadth_rungs.ratios(key, records)
    for angle in product_look.ORIENTATIONS[domain.orientation(key)]:
        scale = drawing.product_scale_for(key, records, angle)
        for record, ratio in zip(records, ratios, strict=True):
            svg, _ = drawing._draw(key, brands.BRANDS[0], record, scale * ratio, angle)
            assert drawing.svg_problems(svg) == [], (key, record)
            _, area = pf.sheet_measures(svg)
            yield angle, record, area


@pytest.mark.parametrize("key", sorted(BREADTH_PRODUCTS))
def test_every_size_and_angle_fills_the_floor_with_a_highlight_and_a_shadow(key):
    for angle, record, area in _measured(key):
        assert area.cover >= FLOORS.get(key, FLOOR), (angle, record, area)
        assert area.highlight and area.shadow and not area.flat, (angle, record, area)


@pytest.mark.parametrize("key", sorted(BREADTH_PRODUCTS))
def test_every_drawing_stays_under_the_byte_cap(key):
    """The worst case of each type, over every brand, material, size and angle: one seed's
    catalog stocks a few of them."""
    row = breadth.row_for(key)
    largest = 0
    for values in itertools.product(*row.attributes.values()):
        common = dict(zip(row.attributes, values, strict=True))
        records = [{**common, row.size_attr: value} for value in row.size_values]
        ratios = breadth_rungs.ratios(key, records)
        for angle in product_look.ORIENTATIONS[domain.orientation(key)]:
            scale = drawing.product_scale_for(key, records, angle)
            for record, ratio in zip(records, ratios, strict=True):
                for brand in brands.BRANDS:
                    svg, _ = drawing._draw(key, brand, record, scale * ratio, angle)
                    largest = max(largest, len(svg))
    assert largest < MAX_DRAWING_BYTES, largest
