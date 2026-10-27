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

from collections.abc import Callable, Iterable, Mapping
from fractions import Fraction

from synthetic_ecommerce_data.core.typespec import RegistryTable

#: Standards with the same dimensions under a second designation.
#: Only pairs whose dimensions really are the same: ISO 4017 / DIN 933 and
#: ISO 4032 / DIN 934 are NOT (the widths across flats differ at M10 and M12,
#: which this catalog's bolts reproduce), so they are not listed.
EQUIVALENTS: dict[str, str] = {
    "ISO 4762": "DIN 912",
    "ISO 7089": "DIN 125-A",
}

#: The claims of each type declared in its own module (``TypeSpec.claims``):
#: ``claims(facts, metric=..., provenance=..., standard=...)``.
CLAIMS: RegistryTable[str, Callable[..., Iterable[str]]] = RegistryTable()


def socket_screw(
    facts: Mapping[str, str], *, metric: bool, provenance: str, cap_screw: bool = False
) -> list[str]:
    """The socket-screw family's claims; ``cap_screw`` adds the inch SHCS standards."""
    material = facts.get("Material", "")
    stainless = "Stainless" in material
    out: list[str] = []
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
    if cap_screw and not metric and not stainless:
        out.append("ASTM A574")
    # ISO 898-1: the property classes of carbon and alloy steel bolts and
    # screws; ISO 3506-1 the stainless ones'; ASTM F837 stainless inch SHCS.
    if metric and "12.9" in material:
        out.append("ISO 898-1")
    if metric and stainless:
        out.append("ISO 3506-1")
    if cap_screw and not metric and stainless:
        out.append("ASTM F837")
    return out


def applicable(
    type_key: str,
    facts: Mapping[str, str],
    *,
    metric: bool,
    provenance: str,
    standard: str = "",
    sizes: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """The standards a line of ``type_key`` may claim, in a fixed order.

    ``standard`` is the dimensional standard every row of the line was read
    from, for a type whose provenance does not already name one (the hex nut);
    empty when its rows are not one standard's. ``sizes`` is the thread size of
    each child, for a type whose claim has a size scope (the hex nut).

    A type declared in its own module states its claims there
    (``TypeSpec.claims``, registered into :data:`CLAIMS`); a type still
    declared in the shared tables has a branch in :func:`_shared_claims`.
    """
    rule = CLAIMS.get(type_key)
    if rule is None:
        claimed: Iterable[str] = _shared_claims(
            type_key, facts, metric=metric, provenance=provenance, standard=standard, sizes=sizes
        )
    else:
        claimed = rule(facts, metric=metric, provenance=provenance, standard=standard)
    return tuple(dict.fromkeys(s for s in claimed if s))


#: The nominal diameters a nut standard covers, where it does not cover every
#: size a nut is made in (#33). SAE J995 is 1/4" to 1-1/2"; ISO 898-2 (2022) is
#: 5 mm to 39 mm. A nut line claims one only when EVERY size it offers is
#: inside, as a standard that does not cover a size is not claimed for it.
J995_INCHES = (Fraction(1, 4), Fraction(3, 2))
ISO_898_2_MM = (Fraction(5), Fraction(39))


def nominal_diameter(thread: str) -> tuple[bool, Fraction]:
    """``(metric, nominal diameter)`` of a thread size, in mm for a metric one and
    in inches otherwise: ``M12x1.75`` -> (True, 12); ``1/4-20`` -> (False, 1/4);
    ``#10-24`` -> (False, 0.190), a number size being 0.060 + 0.013 N inch."""
    if thread.startswith("M"):
        return True, Fraction(thread[1:].split("x")[0])
    size = thread.split("-")[0]
    if size.startswith("#"):
        return False, Fraction(60 + 13 * int(size[1:]), 1000)
    return False, Fraction(size)


def within(scope: tuple[Fraction, Fraction], threads: Iterable[str], *, metric: bool) -> bool:
    """Whether the line offers at least one size, every one in ``scope``."""
    diameters = [nominal_diameter(t) for t in threads]
    low, high = scope
    return bool(diameters) and all(m is metric and low <= d <= high for m, d in diameters)


def _shared_claims(
    type_key: str,
    facts: Mapping[str, str],
    *,
    metric: bool,
    provenance: str,
    standard: str,
    sizes: tuple[str, ...] = (),
) -> list[str]:
    """The claims of the types still declared in the shared tables, one branch
    per type that claims a standard; a type with no branch claims nothing."""
    material = facts.get("Material", "")
    grade = facts.get("Grade", "")
    out: list[str] = []
    if type_key in ("screw_flat_head", "screw_button_head", "screw_low_head"):
        out.extend(socket_screw(facts, metric=metric, provenance=provenance))
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
        # A grade standard has a size scope: ISO 898-2 stops at M5, SAE J995
        # starts at 1/4" (#33). A line spanning the scope's edge claims neither.
        if grade.startswith("Class") and within(ISO_898_2_MM, sizes, metric=True):
            out.append("ISO 898-2")
        if grade.startswith("Grade") and within(J995_INCHES, sizes, metric=False):
            out.append("SAE J995")
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
    elif type_key == "bearing_radial_ball":  # noqa: SIM102 - mutation_check.py patches the inner if
        # ABMA 20 is "Radial Bearings of Ball, Cylindrical Roller and
        # Spherical Roller Types -- METRIC Design": it is the metric bearing's
        # ABMA standard, like ISO 15 and ISO 492. The inch R series is not in
        # it, and no inch-series standard could be confirmed from a readable
        # source, so an inch bearing claims none.
        if metric:
            out.extend(("ISO 15", "ISO 492", "ABMA 20"))
    return out
