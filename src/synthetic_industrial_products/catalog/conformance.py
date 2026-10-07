"""Which standards a product line may claim, per type: a truth table.

The ``Standards`` attribute used to be drawn from a pool per type FAMILY, so a
flat washer could claim DIN 912 (a socket head cap screw) and a jobber drill
ISO 1641 (an end mill). A standard names what a part conforms to; claiming one
that does not apply is an invented fact. So every claim is read from the
table below, by what the line IS -- its type, its measurement system, its
dimensional standard, its material and its grade -- and a line with nothing
applicable claims nothing.

Every designation here is spelled ONE way, and the copy-noise sentences
(``Equivalent to DIN 125-A / ISO 7089``) use the same spelling.
"""

from __future__ import annotations

from collections.abc import Mapping

#: Standards with the same dimensions under a second designation.
#: Only pairs whose dimensions really are the same: ISO 4017 / DIN 933 and
#: ISO 4032 / DIN 934 are NOT (the widths across flats differ at M10 and M12,
#: which this catalog's bolts reproduce), so they are not listed.
EQUIVALENTS: dict[str, str] = {
    "ISO 4762": "DIN 912",
    "ISO 7089": "DIN 125-A",
}


def applicable(
    type_key: str,
    facts: Mapping[str, str],
    *,
    metric: bool,
    provenance: str,
    standard: str = "",
) -> tuple[str, ...]:
    """The standards a line of ``type_key`` may claim, in a fixed order.

    ``standard`` is the dimensional standard every row of the line was read
    from, for a type whose provenance does not already name one (the hex nut);
    empty when its rows are not one standard's.
    """
    material = facts.get("Material", "")
    grade = facts.get("Grade", "")
    stainless = "Stainless" in material
    out: list[str] = []
    if type_key in ("screw_socket_head", "screw_flat_head", "screw_button_head", "screw_low_head"):
        # The line's own dimensional standard (a fine-pitch metric line keeps
        # its head's standard but not its thread's, and claims neither).
        standard = "" if "fine-pitch" in provenance else provenance
        # The inch socket screws' dimensions were extracted per head style,
        # but ASME publishes them all in ONE standard, B18.3: that is what a
        # part claims.
        if standard.startswith("ASME B18.3"):
            standard = "ASME B18.3"
        if standard:
            out.append(standard)
        if standard in EQUIVALENTS:
            out.append(EQUIVALENTS[standard])
        # ASTM A574: alloy steel socket head cap screws (inch).
        if type_key == "screw_socket_head" and not metric and not stainless:
            out.append("ASTM A574")
        # ISO 898-1: the property classes of carbon and alloy steel bolts and
        # screws; ISO 3506-1 the stainless ones'; ASTM F837 stainless inch SHCS.
        if metric and "12.9" in material:
            out.append("ISO 898-1")
        if metric and stainless:
            out.append("ISO 3506-1")
        if type_key == "screw_socket_head" and not metric and stainless:
            out.append("ASTM F837")
    elif type_key == "set_screws_hex_socket":
        # The point's ISO standard (metric) or ASME B18.3 (inch), then the
        # material's: ISO 898-5 / ISO 3506-3 metric, ASTM F912 / F880 inch.
        out.append(standard if metric else "ASME B18.3")
        if metric:
            out.append("ISO 3506-3" if stainless else "ISO 898-5")
        else:
            out.append("ASTM F880" if stainless else "ASTM F912")
    elif type_key == "bolt_hex":
        out.append(provenance)
        if provenance in EQUIVALENTS:
            out.append(EQUIVALENTS[provenance])
        if grade.startswith("Grade"):
            out.append("SAE J429")
        elif grade.startswith("Class"):
            out.append("ISO 898-1")
    elif type_key == "nut_hex":
        # The dimensional standard is the one the rows were READ from, never
        # one chosen by style name: a heavy hex nut is not an ISO 4032 nut,
        # and a fine-pitch nut is not a coarse-thread standard's.
        out.append(standard)
        if metric and grade.startswith("Class"):
            out.append("ISO 898-2")
        if not metric and grade.startswith("Grade"):
            out.append("SAE J995")
    elif type_key == "lock_nuts_nylon_insert":
        # A metric line's dimensional standard is its table's; an inch line's
        # rows are no standard's, so ``standard`` is empty for it.
        out.append(standard)
        # ISO 2320: the prevailing-torque function of steel nuts; ISO 898-2
        # the steel nut's property classes, thin (04, 05) and regular (8, 10).
        if metric and not stainless:
            out.append("ISO 2320")
        if metric and grade.startswith("Class"):
            out.append("ISO 898-2")
        if metric and stainless:
            out.append("ISO 3506-2")
        if not metric and grade.startswith("Grade"):
            out.append("SAE J995")
    elif type_key == "roller_chain":
        # Every row is B29.1's standard series, whatever the material or strands.
        out.append("ASME B29.1")
    elif type_key == "washer_flat":
        out.extend(("ISO 7089", "DIN 125-A"))
    elif type_key in ("end_mill_square", "end_mill_ball"):
        if metric:
            out.append("DIN 6527" if material == "Solid Carbide" else "ISO 1641")
        else:
            out.append("ANSI B94.19")
    elif type_key == "drill_jobber":
        out.append("DIN 338" if metric else "ASME B94.11M")
    elif type_key == "tap_spiral_point":
        out.append("ISO 529" if metric else "ASME B94.9")
    elif type_key == "hex_key":
        out.append("ISO 2936" if metric else "ASME B18.3")
    elif type_key == "hammer_ball_pein":
        out.append("ASME B107.400")
    elif type_key == "abrasive_flap_disc":
        out.extend(("EN 13743", "oSa Certified"))
    elif type_key == "wheel_depressed_center":
        out.extend(("ANSI B7.1", "EN 12413", "oSa Certified"))
    elif type_key == "bearing_radial_ball":
        # ABMA 20 is "Radial Bearings of Ball, Cylindrical Roller and
        # Spherical Roller Types -- METRIC Design": it is the metric bearing's
        # ABMA standard, like ISO 15 and ISO 492. The inch R series is not in
        # it, and no inch-series standard could be confirmed from a readable
        # source, so an inch bearing claims none.
        if metric:
            out.extend(("ISO 15", "ISO 492", "ABMA 20"))
    return tuple(dict.fromkeys(s for s in out if s))
