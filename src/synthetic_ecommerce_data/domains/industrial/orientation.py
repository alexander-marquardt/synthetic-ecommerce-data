"""The orientation of every industrial type: the set of angles its products' figures turn by (#849).

Every type the domain draws names one, here, and ``tests/test_one_paper_one_angle_849.py`` refuses a
drawn type missing from this table, so a new type cannot forget it. The sets are
:data:`...core.drawing.product_look.ORIENTATIONS`:

* ``any`` (the 24 clock positions): a part with no natural up. Screws, bolts, nuts, washers,
  nails, pins, rivets, bar and ball stock, discs and wheels, collets and cutters, chain, belts,
  springs, small fittings, and gloves, which read at any angle (the maintainer's ruling on #860).
* ``upright`` (+-36 degrees): a product with a natural up, or one nobody was sure of. Tools with
  a working end and a handle (hammers, pliers, wrenches, files, punches), vises and clamps,
  racks, cases and kits, containers of grease or fluid, casters, pulleys and bearings on a
  base, guards, padlocks and glasses.
* ``slight`` (+-15 degrees): clothing. No industrial type wears it; gloves are ``any``.

To move a type, move its line to the other tuple.
"""

from __future__ import annotations

#: Parts with no natural up, drawn at any of the 24 clock positions.
ANY: tuple[str, ...] = (
    "abrasive_flap_disc", "backing_pads", "ball_stock_precision", "ball_stock_rubber",
    "bar_stock_hex", "bar_stock_round", "bar_stock_square", "bearing_radial_ball", "blind_rivets",
    "bolt_hex", "bronze_sleeve_bushings", "cap_nuts_acorn", "carriage_bolts",
    "compression_springs", "cotter_pins", "coupling_nuts", "cut_resistant_gloves",
    "diamond_wheels", "dowel_pins", "drill_bushings", "drill_jobber", "drill_stop_collars",
    "end_mill_ball", "end_mill_square", "er_collets", "eye_bolts", "fastener_extractors",
    "flange_nuts", "flat_gaskets", "fluted_dowels", "foam_ear_plugs", "grub_screw_keys",
    "handle_wedges", "hex_bit_sockets", "hex_key", "hex_pipe_nipples", "hose_clamps", "key_stock",
    "lag_screws", "lock_nuts_nylon_insert", "magnetic_bit_holders", "micro_collets",
    "milling_collets", "nail_finishing", "nail_framing", "nail_masonry", "nut_hex",
    "nylon_wall_anchors", "o_rings", "orb_hydraulic_fittings", "piloted_counterbores",
    "quick_disconnect_couplings", "replacement_pins", "retaining_rings_external",
    "rigid_shaft_couplings", "roll_pins", "roller_chain", "roller_chain_links",
    "roller_chain_sprockets", "screw_button_head", "screw_deck", "screw_drywall",
    "screw_flat_head", "screw_hex_head", "screw_low_head", "screw_machine", "screw_sheet_metal",
    "screw_socket_head", "screw_wood", "sds_drill_bits", "sems_bolts", "serrated_flange_nuts",
    "set_screws_hex_socket", "shackles", "shaft_collars", "sleeve_anchors", "spill_socks",
    "studs_double_end", "t_slot_nuts", "tap_extractors", "tap_spiral_point", "threaded_rod",
    "timing_pulleys", "turnbuckles", "u_bolts", "v_belts", "washer_flat", "wedge_anchors",
    "wheel_depressed_center", "wheel_mandrels", "zerk_grease_fittings",
)

#: Products with a natural up, and every type nobody was sure of: within +-36 degrees.
UPRIGHT: tuple[str, ...] = (
    "anaerobic_threadlockers", "anti_seize_compounds", "ball_valves", "band_saw_blades",
    "bearing_greases", "bearing_pullers", "bench_tool_racks", "bench_vises", "bit_index_cases",
    "bit_sharpeners", "bit_socket_sets", "c_clamps", "cantilever_racks", "center_punches",
    "chain_breakers", "chain_lubricants", "chain_tensioners", "circle_cutters", "cold_chisels",
    "combination_wrenches", "compound_cutters", "conduit_pliers", "cord_splicing_kits",
    "cutter_sharpening_fixtures", "cutter_storage_cases", "cutter_storage_racks", "drawer_slides",
    "drive_guards", "driver_bit_sets", "fastener_dispensers", "gear_pullers", "grinder_guards",
    "grooving_cutters", "hammer_ball_pein", "hammer_claw", "hammer_club", "hammer_dead_blow",
    "hammer_framing", "hammer_rubber_mallet", "hammer_sledge", "hand_files", "hex_bit_socket_sets",
    "induction_heaters", "keyed_padlocks", "kit_assortment", "milling_tool_holders",
    "nut_drivers_hex", "nut_splitters", "pillow_block_bearings", "pin_pullers", "pin_punch_sets",
    "pneumatic_cut_off_tools", "rigging_pulleys", "rigid_casters", "safety_glasses",
    "seal_pick_sets", "shaft_alignment_lasers", "side_lock_holders", "silicone_greases",
    "sleeve_installation_kits", "snap_ring_pliers", "spanner_wrenches", "swivel_casters",
    "tap_wrenches", "tapping_fluids", "thread_chasers", "thread_pitch_gages", "thread_plug_gages",
    "thread_repair_kits", "thread_restoring_files", "tool_holsters", "wrench_organizers",
)

#: Clothing: within +-15 degrees. No industrial type is clothing.
SLIGHT: tuple[str, ...] = ()

#: Type key -> orientation.
ORIENTATION: dict[str, str] = {
    **dict.fromkeys(ANY, "any"),
    **dict.fromkeys(UPRIGHT, "upright"),
    **dict.fromkeys(SLIGHT, "slight"),
}
