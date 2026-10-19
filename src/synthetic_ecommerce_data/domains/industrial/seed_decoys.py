"""Which text-match decoys serve which industrial seed query (#462).

A seed query is one the Combined demo runs on its industrial half (the Fasteners, Motion Control,
Fluid Power and Fittings, and Tools and Raw Materials sections, plus the item nouns). A decoy for
it is a real product whose TITLE holds the seed's words but whose category path does not name the
seed's own category, so a category policy has something visible to remove. Each decoy is one type
module under ``product_types/decoys/``; ``tests/test_industrial_seed_decoys_462.py`` holds the
rule.

* :data:`SEED_TERMS` maps a query to ``(terms, forbidden)``. ``terms`` are the words a decoy's
  title must hold, all in one SKU's title; a term matches as a whole word with an optional plural
  ending, so ``screw`` never matches ``Screwdriver``. ``forbidden`` are the phrases the decoy's
  category path must not hold: the seed's own category, a plural leaf by the catalogue's leaf rule.
* :data:`SEED_DECOYS` maps a query to the type keys that serve it.
* :data:`SECTIONS` groups the queries the way the issue's four tables do.
"""

from __future__ import annotations

#: query -> (terms the title holds, phrases the category path must not hold)
SEED_TERMS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    # Fasteners
    "hex nuts": (("hex nut",), ("hex nuts",)),
    "lock nuts": (("lock nut",), ("lock nuts",)),
    "m10 washers": (("m10", "washer"), ("washers",)),
    "stainless steel hex bolts": (("stainless steel", "hex bolt"), ("hex bolts",)),
    "7/16-14 hex head bolts": (("7/16-14", "hex head bolt"), ("hex head bolts",)),
    "m12x1.75 socket cap screws": (("m12x1.75", "socket cap screw"), ("socket cap screws",)),
    "m6x1 set screws": (("m6x1", "set screw"), ("set screws",)),
    "1/4-20 screws": (("1/4-20", "screw"), ("screws",)),
    "dowel pins": (("dowel pin",), ("dowel pins",)),
    "retaining rings": (("retaining ring",), ("retaining rings",)),
    # Motion Control, Fluid Power and Fittings
    "ball bearings": (("ball bearing",), ("ball bearings",)),
    "6203 bearing": (("6203", "bearing"), ("bearings",)),
    "roller chain": (("roller chain",), ("roller chain",)),
    "sprockets": (("sprocket",), ("sprockets",)),
    "shackles": (("shackle",), ("shackles",)),
    # Tools and Raw Materials
    "1/2 endmill": (("1/2", "end mill"), ("end mills",)),
    "3/8 square endmill": (("3/8", "square end mill"), ("square end mills",)),
    "2.5mm end mill": (("2.5 mm", "end mill"), ("end mills",)),
    "25mm end mill": (("25 mm", "end mill"), ("end mills",)),
    "3/8 inch drill bit": (("3/8", "drill bit"), ("drill bits",)),
    "carbide drill bit": (("carbide", "drill bit"), ("drill bits",)),
    "spiral flute tap": (("spiral flute tap",), ("spiral flute taps",)),
    "flap discs": (("flap disc",), ("flap discs",)),
    "cut-off wheels": (("cut-off wheel",), ("cut-off wheels",)),
    "hammers": (("hammer",), ("hammers",)),
    "screwdrivers": (("screwdriver",), ("screwdrivers",)),
    "hex keys": (("hex key",), ("hex keys",)),
    "bar stock": (("bar stock",), ("bar stock",)),
    # Item nouns
    "o-rings": (("o-ring",), ("o-rings",)),
    "screws": (("screw",), ("screws",)),
    "bolts": (("bolt",), ("bolts",)),
    "washers": (("washer",), ("washers",)),
    "nuts": (("nut",), ("nuts",)),
}

#: query -> the type keys (modules under ``product_types/decoys/``) that serve it
SEED_DECOYS: dict[str, tuple[str, ...]] = {
    # Fasteners
    "hex nuts": ("nut_drivers_hex", "nut_splitters", "thread_plug_gages"),
    "lock nuts": ("conduit_pliers", "spanner_wrenches"),
    "m10 washers": ("sems_bolts", "serrated_flange_nuts"),
    "stainless steel hex bolts": ("sleeve_anchors", "anti_seize_compounds"),
    "7/16-14 hex head bolts": ("thread_chasers", "thread_restoring_files"),
    "m12x1.75 socket cap screws": ("piloted_counterbores", "hex_bit_socket_sets"),
    "m6x1 set screws": ("anaerobic_threadlockers", "grub_screw_keys"),
    "1/4-20 screws": ("fastener_extractors", "thread_repair_kits"),
    "dowel pins": ("pin_pullers", "pin_punch_sets", "fluted_dowels"),
    "retaining rings": ("snap_ring_pliers", "grooving_cutters", "fastener_dispensers"),
    # Motion Control, Fluid Power and Fittings
    "ball bearings": ("bearing_greases", "bearing_pullers", "drawer_slides", "swivel_casters"),
    "6203 bearing": ("induction_heaters", "sleeve_installation_kits"),
    "roller chain": ("chain_breakers", "chain_lubricants", "chain_tensioners"),
    "sprockets": ("gear_pullers", "shaft_alignment_lasers", "drive_guards"),
    "shackles": ("replacement_pins", "rigging_pulleys", "keyed_padlocks"),
    # Tools and Raw Materials
    "1/2 endmill": (
        "milling_tool_holders",
        "milling_collets",
        "cutter_sharpening_fixtures",
        "cutter_storage_cases",
    ),
    "3/8 square endmill": ("cutter_sharpening_fixtures", "cutter_storage_cases"),
    "2.5mm end mill": ("micro_collets", "cutter_storage_racks"),
    "25mm end mill": ("side_lock_holders", "cutter_storage_racks"),
    "3/8 inch drill bit": ("bit_sharpeners", "drill_stop_collars"),
    "carbide drill bit": ("bit_index_cases", "diamond_wheels"),
    "spiral flute tap": ("tap_extractors", "tap_wrenches", "tapping_fluids"),
    "flap discs": ("backing_pads", "grinder_guards"),
    "cut-off wheels": ("wheel_mandrels", "pneumatic_cut_off_tools"),
    "hammers": ("handle_wedges", "tool_holsters", "sds_drill_bits"),
    "screwdrivers": ("bench_tool_racks", "driver_bit_sets", "magnetic_bit_holders"),
    "hex keys": ("wrench_organizers", "bit_socket_sets", "grub_screw_keys"),
    "bar stock": ("band_saw_blades", "cantilever_racks"),
    # Item nouns
    "o-rings": (
        "seal_pick_sets",
        "silicone_greases",
        "orb_hydraulic_fittings",
        "cord_splicing_kits",
        "quick_disconnect_couplings",
    ),
    "screws": ("fastener_extractors", "nylon_wall_anchors", "thread_repair_kits"),
    "bolts": (
        "compound_cutters",
        "sleeve_anchors",
        "anti_seize_compounds",
        "thread_chasers",
        "thread_restoring_files",
    ),
    "washers": ("sems_bolts", "serrated_flange_nuts", "circle_cutters"),
    "nuts": (
        "nut_drivers_hex",
        "nut_splitters",
        "thread_plug_gages",
        "conduit_pliers",
        "spanner_wrenches",
    ),
}

#: section -> its queries, the four tables of the issue
SECTIONS: dict[str, tuple[str, ...]] = {
    "Fasteners": (
        "hex nuts",
        "lock nuts",
        "m10 washers",
        "stainless steel hex bolts",
        "7/16-14 hex head bolts",
        "m12x1.75 socket cap screws",
        "m6x1 set screws",
        "1/4-20 screws",
        "dowel pins",
        "retaining rings",
    ),
    "Motion Control, Fluid Power and Fittings": (
        "ball bearings",
        "6203 bearing",
        "roller chain",
        "sprockets",
        "shackles",
    ),
    "Tools and Raw Materials": (
        "1/2 endmill",
        "3/8 square endmill",
        "2.5mm end mill",
        "25mm end mill",
        "3/8 inch drill bit",
        "carbide drill bit",
        "spiral flute tap",
        "flap discs",
        "cut-off wheels",
        "hammers",
        "screwdrivers",
        "hex keys",
        "bar stock",
    ),
    "Item nouns": ("o-rings", "screws", "bolts", "washers", "nuts"),
}
