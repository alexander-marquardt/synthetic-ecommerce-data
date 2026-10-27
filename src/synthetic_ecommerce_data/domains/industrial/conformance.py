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
from inspect import signature

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

    A type states its claims in its own module (``TypeSpec.claims``,
    registered into :data:`CLAIMS`); a type with no rule claims nothing.
    """
    rule = CLAIMS.get(type_key)
    # A rule that scopes its claims by size declares ``sizes`` (the hex nut);
    # the others keep the narrower signature.
    extra = {"sizes": sizes} if rule is not None and "sizes" in signature(rule).parameters else {}
    claimed: Iterable[str] = (
        ()
        if rule is None
        else rule(facts, metric=metric, provenance=provenance, standard=standard, **extra)
    )
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
