"""Which attributes an industrial title names, per product type, and how it abbreviates each
(#937).

The reference catalogue's titles read ``<Product Type>: <value> <Abbrev>, <value> <Abbrev>``,
for example ``Square End Mill: 3/4" Dia, 1-1/2" LOC``. The title writes an attribute's
abbreviated name (``Dia``) after its value, while the attribute block keeps the full name
(``Milling Dia.``). This table declares, for each product type, the attributes its title may
name. Each attribute's full name sits beside its abbreviation. ``None`` means the title writes
the value alone, because a value such as ``Alloy Steel`` or ``Grade 8`` already says what it is.

Which attributes a family names, and how many, is chosen per family. The one family the
reference sample holds was measured on elastic/prism-retail-and-industrial#1694. All 24 square
end mill titles name the mill diameter, then the length of cut. The two end mill types declare
exactly that pair, in that order, and each of their titles names every declared attribute the
record publishes (:data:`MEASURED`), before the #657 pass drops the axis from some SKU titles.
Every other type keeps the attributes its titles named before #937, following #9284's rule of
"the most identifying attributes for that family". Those types are listed most-named first. The
title composer (:mod:`.titles`) names no attribute its type leaves out, and writes each with the
abbreviation declared here.
"""

from __future__ import annotations

#: A product type's title attributes: the attribute's full name beside the abbreviation the
#: title writes after its value (``None``: the value alone).
TITLE_ATTRIBUTES: dict[str, tuple[tuple[str, str | None], ...]] = {
    "abrasive_flap_disc": (
        ("Diameter", "Dia"),
        ("Abrasive Material", None),
        ("Grit", "Grit"),
    ),
    "anaerobic_threadlockers": (("Container Size", "Size"),),
    "anti_seize_compounds": (("Container Size", "Size"),),
    "backing_pads": (("Diameter", "Dia"),),
    "ball_stock_precision": (("Diameter", "Dia"),),
    "ball_stock_rubber": (("Diameter", "Dia"),),
    "ball_valves": (("Size", "Size"),),
    "band_saw_blades": (("Length", "L"),),
    "bar_stock_hex": (("Size", "Size"),),
    "bar_stock_round": (("Diameter", "Dia"),),
    "bar_stock_square": (("Size", "Size"),),
    "bearing_greases": (("Container Size", "Size"),),
    "bearing_pullers": (("Maximum Size", "Max"),),
    "bearing_radial_ball": (
        ("Bearing Number", None),
        ("Bore Dia.", "Bore"),
        ("Material", None),
        ("Closure Type", None),
    ),
    "bench_tool_racks": (("Capacity", None),),
    "bench_vises": (("Size", "Size"),),
    "bit_index_cases": (("Capacity", None),),
    "bit_sharpeners": (("Maximum Size", "Max"),),
    "bit_socket_sets": (("Drive Size", "Drive"),),
    "blind_rivets": (("Diameter", "Dia"),),
    "bolt_hex": (
        ("Dia./Thread Size", "Thread"),
        ("Grade", None),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
        ("Thread Length", "Thread L"),
    ),
    "bronze_sleeve_bushings": (
        ("Material", None),
        ("Type", None),
        ("Bore Dia.", "Bore"),
        ("Length", "L"),
    ),
    "c_clamps": (("Size", "Size"),),
    "cantilever_racks": (("Rated Load", "Load"),),
    "cap_nuts_acorn": (("Thread Size", "Thread"),),
    "carriage_bolts": (
        ("Material", None),
        ("Thread Size", "Thread"),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "center_punches": (("Length", "L"),),
    "chain_breakers": (("Size", "Size"),),
    "chain_lubricants": (("Container Size", "Size"),),
    "chain_tensioners": (("Size", "Size"),),
    "circle_cutters": (("Maximum Size", "Max"),),
    "cold_chisels": (("Length", "L"),),
    "combination_wrenches": (
        ("Number of Points", None),
        ("Type", None),
        ("Size", "Size"),
    ),
    "compound_cutters": (("Overall Length", "OAL"),),
    "compression_springs": (("Outside Dia.", "OD"),),
    "conduit_pliers": (("Overall Length", "OAL"),),
    "cord_splicing_kits": (("Diameter", "Dia"),),
    "cotter_pins": (
        ("Pin Dia.", "Pin Dia"),
        ("Units per Pack", "Pk"),
    ),
    "coupling_nuts": (("Thread Size", "Thread"),),
    "cut_resistant_gloves": (
        ("ANSI Cut Level", "Cut Level"),
        ("Size", "Size"),
    ),
    "cutter_sharpening_fixtures": (("Size", "Size"),),
    "cutter_storage_cases": (("Size", "Size"),),
    "cutter_storage_racks": (("Size", "Size"),),
    "diamond_wheels": (("Diameter", "Dia"),),
    "dowel_pins": (
        ("Dowel Dia.", "Dia"),
        ("Length", "L"),
    ),
    "drawer_slides": (("Length", "L"),),
    "drill_bushings": (
        ("Head Type", "Head"),
        ("Type", None),
        ("Size", "Size"),
    ),
    "drill_jobber": (
        ("Material", None),
        ("Size", "Size"),
        ("Overall Length", "OAL"),
        ("Flute Length", "Flute L"),
    ),
    "drill_stop_collars": (("Size", "Size"),),
    "drive_guards": (("Width", "W"),),
    "driver_bit_sets": (("Piece Count", "Pc"),),
    "end_mill_ball": (
        ("Milling Dia.", "Dia"),
        ("Length of Cut", "LOC"),
    ),
    "end_mill_square": (
        ("Milling Dia.", "Dia"),
        ("Length of Cut", "LOC"),
    ),
    "er_collets": (
        ("Class", None),
        ("Type", None),
        ("Size", "Size"),
    ),
    "eye_bolts": (("Thread Size", "Thread"),),
    "fastener_dispensers": (("Diameter", "Dia"),),
    "fastener_extractors": (("Piece Count", "Pc"),),
    "flange_nuts": (("Thread Size", "Thread"),),
    "flat_gaskets": (("Size", "Size"),),
    "fluted_dowels": (("Diameter", "Dia"),),
    "foam_ear_plugs": (("Type", None),),
    "gear_pullers": (("Maximum Size", "Max"),),
    "grinder_guards": (("Diameter", "Dia"),),
    "grooving_cutters": (("Width", "W"),),
    "grub_screw_keys": (("Size", "Size"),),
    "hammer_ball_pein": (
        ("Handle Material", None),
        ("Head Weight", "Wt"),
        ("Overall Length", "OAL"),
    ),
    "hammer_claw": (
        ("Handle Material", None),
        ("Head Weight", "Wt"),
        ("Overall Length", "OAL"),
    ),
    "hammer_club": (
        ("Handle Material", None),
        ("Head Weight", "Wt"),
        ("Overall Length", "OAL"),
    ),
    "hammer_dead_blow": (
        ("Handle Material", None),
        ("Head Weight", "Wt"),
        ("Overall Length", "OAL"),
    ),
    "hammer_framing": (
        ("Handle Material", None),
        ("Head Weight", "Wt"),
        ("Overall Length", "OAL"),
    ),
    "hammer_rubber_mallet": (
        ("Handle Material", None),
        ("Head Weight", "Wt"),
        ("Overall Length", "OAL"),
    ),
    "hammer_sledge": (
        ("Handle Material", None),
        ("Head Weight", "Wt"),
        ("Overall Length", "OAL"),
    ),
    "hand_files": (
        ("Cut Type", None),
        ("Length", "L"),
    ),
    "handle_wedges": (("Width", "W"),),
    "hex_bit_socket_sets": (("Drive Size", "Drive"),),
    "hex_bit_sockets": (
        ("Tip Style", None),
        ("Type", None),
        ("Size", "Size"),
    ),
    "hex_key": (
        ("Tip Style", None),
        ("Size", "Size"),
        ("Overall Length", "OAL"),
    ),
    "hex_pipe_nipples": (
        ("Material", None),
        ("Type", None),
        ("Pipe Size", "Pipe"),
        ("Length", "L"),
    ),
    "hose_clamps": (("Size", "Size"),),
    "induction_heaters": (("Maximum Workpiece Weight", "Max Wt"),),
    "key_stock": (
        ("Material", None),
        ("Stock Fit", None),
        ("Width", "W"),
        ("Height", "H"),
    ),
    "keyed_padlocks": (("Width", "W"),),
    "kit_assortment": (
        ("Piece Count", "Pc"),
        ("Container Type", None),
    ),
    "lag_screws": (
        ("Diameter", "Dia"),
        ("Material", None),
        ("Length", "L"),
    ),
    "lock_nuts_nylon_insert": (
        ("Material", None),
        ("Thread Size", "Thread"),
    ),
    "magnetic_bit_holders": (("Length", "L"),),
    "micro_collets": (("Size", "Size"),),
    "milling_collets": (("Size", "Size"),),
    "milling_tool_holders": (("Size", "Size"),),
    "nail_finishing": (
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "nail_framing": (
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "nail_masonry": (
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "nut_drivers_hex": (("Drive Size", "Drive"),),
    "nut_hex": (
        ("Material", None),
        ("Thread Size", "Thread"),
        ("Units per Pack", "Pk"),
    ),
    "nut_splitters": (("Maximum Size", "Max"),),
    "nylon_wall_anchors": (("Diameter", "Dia"),),
    "o_rings": (
        ("Material", None),
        ("Size", "Size"),
        ("Inside Dia.", "ID"),
    ),
    "orb_hydraulic_fittings": (("Thread Size", "Thread"),),
    "pillow_block_bearings": (
        ("Bore Dia.", "Bore"),
        ("Units per Pack", "Pk"),
    ),
    "piloted_counterbores": (("Diameter", "Dia"),),
    "picture_hangers": (
        ("Style", None),
        ("Load Capacity", "Load"),
        ("Color", None),
    ),
    "pin_pullers": (("Maximum Size", "Max"),),
    "pin_punch_sets": (("Piece Count", "Pc"),),
    "pneumatic_cut_off_tools": (("Diameter", "Dia"),),
    "quick_disconnect_couplings": (("Size", "Size"),),
    "replacement_pins": (("Diameter", "Dia"),),
    "retaining_rings_external": (
        ("For Shaft Diameter", "Shaft"),
        ("Units per Pack", "Pk"),
    ),
    "rigging_pulleys": (("Size", "Size"),),
    "rigid_casters": (
        ("Material", None),
        ("Wheel Diameter", "Dia"),
        ("Overall Height", "OAH"),
    ),
    "rigid_shaft_couplings": (("Bore Dia.", "Bore"),),
    "roll_pins": (
        ("Material", None),
        ("Pin Dia.", "Pin Dia"),
        ("Length", "L"),
    ),
    "roller_chain": (
        ("Material", None),
        ("Style", None),
        ("Pitch", "Pitch"),
    ),
    "roller_chain_links": (
        ("Material", None),
        ("Style", None),
        ("Pitch", "Pitch"),
        ("Units per Pack", "Pk"),
    ),
    "roller_chain_sprockets": (
        ("Outside Dia.", "OD"),
        ("Units per Pack", "Pk"),
        ("Pitch", "Pitch"),
    ),
    "safety_glasses": (
        ("Style", None),
        ("Lens Color", None),
    ),
    "screw_button_head": (
        ("Dia./Thread Size", "Thread"),
        ("Material", None),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
        ("Thread Length", "Thread L"),
    ),
    "screw_deck": (
        ("Gauge", "Ga"),
        ("Head Type", "Head"),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "screw_drywall": (
        ("Gauge", "Ga"),
        ("Head Type", "Head"),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "screw_flat_head": (
        ("Dia./Thread Size", "Thread"),
        ("Material", None),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
        ("Thread Length", "Thread L"),
    ),
    "screw_hex_head": (
        ("Dia./Thread Size", "Thread"),
        ("Material", None),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "screw_low_head": (
        ("Dia./Thread Size", "Thread"),
        ("Material", None),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
        ("Thread Length", "Thread L"),
    ),
    "screw_machine": (
        ("Head Type", "Head"),
        ("Thread Size", "Thread"),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "screw_sheet_metal": (
        ("Gauge", "Ga"),
        ("Head Type", "Head"),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "screw_socket_head": (
        ("Dia./Thread Size", "Thread"),
        ("Material", None),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "screw_wood": (
        ("Gauge", "Ga"),
        ("Head Type", "Head"),
        ("Length", "L"),
        ("Units per Pack", "Pk"),
    ),
    "sds_drill_bits": (("Diameter", "Dia"),),
    "seal_pick_sets": (("Piece Count", "Pc"),),
    "sems_bolts": (("Thread Size", "Thread"),),
    "serrated_flange_nuts": (("Thread Size", "Thread"),),
    "set_screws_hex_socket": (
        ("Dia./Thread Size", "Thread"),
        ("Point Type", None),
        ("Length", "L"),
    ),
    "shackles": (
        ("Size", "Size"),
        ("Units per Pack", "Pk"),
    ),
    "shaft_alignment_lasers": (("Overall Length", "OAL"),),
    "shaft_collars": (("Bore Dia.", "Bore"),),
    "side_lock_holders": (("Size", "Size"),),
    "silicone_greases": (("Container Size", "Size"),),
    "sleeve_anchors": (("Diameter", "Dia"),),
    "sleeve_installation_kits": (("Piece Count", "Pc"),),
    "snap_ring_pliers": (("Overall Length", "OAL"),),
    "spanner_wrenches": (("Size", "Size"),),
    "spill_socks": (("Length", "L"),),
    "studs_double_end": (
        ("Length", "L"),
        ("Material", None),
        ("Thread Size", "Thread"),
    ),
    "swivel_casters": (("Diameter", "Dia"),),
    "t_slot_nuts": (("Thread Size", "Thread"),),
    "tap_extractors": (("Size", "Size"),),
    "tape_measures": (
        ("Length", "L"),
        ("Width", "W"),
        ("Color", None),
    ),
    "tap_spiral_point": (
        ("Thread Size", "Thread"),
        ("Number of Flutes", "FL"),
        ("Thread Type", None),
        ("Overall Length", "OAL"),
        ("Thread Length", "Thread L"),
    ),
    "tap_wrenches": (("Size", "Size"),),
    "tapping_fluids": (("Container Size", "Size"),),
    "thread_chasers": (("Thread Size", "Thread"),),
    "thread_pitch_gages": (("Type", None),),
    "thread_plug_gages": (("Thread Size", "Thread"),),
    "thread_repair_kits": (("Thread Size", "Thread"),),
    "thread_restoring_files": (("Thread Size", "Thread"),),
    "threaded_rod": (
        ("Length", "L"),
        ("Material", None),
        ("Thread Size", "Thread"),
    ),
    "timing_pulleys": (("Bore Dia.", "Bore"),),
    "tool_holsters": (("Width", "W"),),
    "turnbuckles": (
        ("End Style", None),
        ("Thread Size", "Thread"),
        ("Units per Pack", "Pk"),
        ("Load Capacity", "Load"),
    ),
    "u_bolts": (("Size", "Size"),),
    "v_belts": (("Length", "L"),),
    "washer_flat": (
        ("Material", None),
        ("Size", "Size"),
        ("Outside Dia.", "OD"),
    ),
    "wedge_anchors": (("Diameter", "Dia"),),
    "wheel_depressed_center": (
        ("Abrasive Material", None),
        ("Diameter", "Dia"),
        ("Grit", "Grit"),
    ),
    "wheel_mandrels": (("Shank Diameter", "Shank"),),
    "wrench_organizers": (("Capacity", None),),
    "zerk_grease_fittings": (("Thread Size", "Thread"),),
}

#: The types whose title shape was measured on the reference (elastic/prism-retail-and-
#: industrial#1694): a title names EVERY declared attribute the record publishes, in the declared
#: order, as all 24 measured titles do.
MEASURED: frozenset[str] = frozenset({"end_mill_square", "end_mill_ball"})


def declared(type_key: str) -> dict[str, str | None]:
    """The type's title attributes, full name to abbreviation (empty for an undeclared type)."""
    return dict(TITLE_ATTRIBUTES.get(type_key, ()))
