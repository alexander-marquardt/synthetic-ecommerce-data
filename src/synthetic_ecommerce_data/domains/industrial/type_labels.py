"""The shopper-readable name of each industrial product type (#331).

An industrial ``product_type`` is a snake_case id (``hammer_ball_pein``): the catalogue repo keys
its field weights, facet decisions and field map on it, so it never changes. Shown as a facet
value it reads as a field name, so every product also carries ``product_type_label``, the name
below. A retail product's ``product_type`` is already a display name, and its label is that
name (``export.standard_document``).

This is the one table, filled from two places: the entries below, and the ``label`` of each
type module's ``TypeSpec`` (``typespec.register`` calls this module's hook, which writes it
in; a key in both is refused). A new type declares its label on its own spec, so two PRs
that each add a type edit no line in common here (#103).
``tests/test_product_type_label_331.py`` holds the table to the types the generator emits:
none missing, none extra, no ``_`` in a label, no two types sharing one.
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import (
    RegistryTable,
    TypeCollisionError,
    TypeSpec,
    on_register,
)

_LABELS: dict[str, str] = {
    "abrasive_flap_disc": "Flap Disc",
    "ball_stock_precision": "Precision Ball",
    "ball_stock_rubber": "Rubber Ball",
    "ball_valves": "Ball Valve",
    "bar_stock_hex": "Hex Bar",
    "bar_stock_round": "Round Bar",
    "bar_stock_square": "Square Bar",
    "bearing_radial_ball": "Radial Ball Bearing",
    "bench_vises": "Bench Vise",
    "blind_rivets": "Blind Rivet",
    "bolt_hex": "Hex Head Bolt",
    "bronze_sleeve_bushings": "Bronze Sleeve Bushing",
    "c_clamps": "C-Clamp",
    "cap_nuts_acorn": "Acorn Cap Nut",
    "carriage_bolts": "Carriage Bolt",
    "center_punches": "Center Punch",
    "cold_chisels": "Cold Chisel",
    "combination_wrenches": "Combination Wrench",
    "compression_springs": "Compression Spring",
    "cotter_pins": "Cotter Pin",
    "coupling_nuts": "Coupling Nut",
    "cut_resistant_gloves": "Cut-Resistant Glove",
    "dowel_pins": "Dowel Pin",
    "drill_bushings": "Drill Bushing",
    "drill_jobber": "Jobber Length Drill Bit",
    "end_mill_ball": "Ball End Mill",
    "end_mill_square": "Square End Mill",
    "er_collets": "ER Collet",
    "eye_bolts": "Eye Bolt",
    "flange_nuts": "Flange Nut",
    "flat_gaskets": "Flat Gasket",
    "foam_ear_plugs": "Foam Ear Plug",
    "hammer_ball_pein": "Ball Pein Hammer",
    "hammer_claw": "Claw Hammer",
    "hammer_club": "Club Hammer",
    "hammer_dead_blow": "Dead Blow Hammer",
    "hammer_framing": "Framing Hammer",
    "hammer_rubber_mallet": "Rubber Mallet",
    "hammer_sledge": "Sledge Hammer",
    "hand_files": "Hand File",
    "hex_bit_sockets": "Hex Bit Socket",
    "hex_key": "Hex Key",
    "hex_pipe_nipples": "Hex Pipe Nipple",
    "hose_clamps": "Hose Clamp",
    "key_stock": "Key Stock Bar",
    "kit_assortment": "Assortment Kit",
    "lag_screws": "Lag Screw",
    "lock_nuts_nylon_insert": "Nylon Insert Lock Nut",
    "nut_hex": "Hex Nut",
    "o_rings": "O-Ring",
    "pillow_block_bearings": "Pillow Block Bearing",
    "retaining_rings_external": "External Retaining Ring",
    "rigid_casters": "Rigid Caster",
    "rigid_shaft_couplings": "Rigid Shaft Coupling",
    "roll_pins": "Roll Pin",
    "roller_chain": "Roller Chain",
    "roller_chain_links": "Roller Chain Link",
    "roller_chain_sprockets": "Roller Chain Sprocket",
    "safety_glasses": "Safety Glasses",
    "screw_button_head": "Button Head Socket Cap Screw",
    "screw_flat_head": "Flat Head Socket Cap Screw",
    "screw_low_head": "Low Head Socket Cap Screw",
    "screw_socket_head": "Socket Head Cap Screw",
    "set_screws_hex_socket": "Hex Socket Set Screw",
    "shackles": "Rigging Shackle",
    "shaft_collars": "Set Screw Shaft Collar",
    "studs_double_end": "Double-End Stud",
    "t_slot_nuts": "T-Slot Nut",
    "tap_spiral_point": "Spiral Point Tap",
    "thread_pitch_gages": "Thread Pitch Gage",
    "threaded_rod": "Threaded Rod",
    "timing_pulleys": "Timing Pulley",
    "turnbuckles": "Turnbuckle",
    "u_bolts": "U-Bolt",
    "v_belts": "V-Belt",
    "washer_flat": "Flat Washer",
    "wedge_anchors": "Wedge Anchor",
    "wheel_depressed_center": "Depressed-Center Wheel",
    "zerk_grease_fittings": "Zerk Grease Fitting",
}
PRODUCT_TYPE_LABELS: RegistryTable[str, str] = RegistryTable(_LABELS)


def label_for(type_key: str) -> str:
    """The label of industrial product type ``type_key``; an unknown type is a KeyError, never
    a guess, so a type added without a label stops the build."""
    return PRODUCT_TYPE_LABELS[type_key]


def _declare_label(spec: TypeSpec) -> None:
    """Write ``spec.label`` into the table; a key labelled here and on its spec is refused."""
    if not spec.label:
        return
    if dict.__contains__(PRODUCT_TYPE_LABELS, spec.key):
        raise TypeCollisionError(
            f"{spec.key!r} is labelled both in type_labels.PRODUCT_TYPE_LABELS and by type "
            f"module {spec.module}; keep the label on its TypeSpec"
        )
    PRODUCT_TYPE_LABELS[spec.key] = spec.label


# Core's register() reaches this table through the hook, never an import (#103).
on_register(_declare_label)
