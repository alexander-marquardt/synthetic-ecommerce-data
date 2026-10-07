"""The facts each modelled type's records are held to, by type key.

The facts tests (``test_catalog_facts``) and the size pins (``catalog_size``)
read these.
"""

from __future__ import annotations


class TypeFactsError(Exception):
    """A type's facts are missing, or declared in two places."""


#: The standards a record of each type may claim.
LEGACY_MAY_CLAIM: dict[str, frozenset[str]] = {
    "screw_socket_head": frozenset({"ISO 4762", "DIN 912", "ASME B18.3", "ASTM A574", "ASTM F837",
                                    "ISO 898-1", "ISO 3506-1"}),
    "screw_flat_head": frozenset({"ISO 10642", "ASME B18.3", "ISO 898-1", "ISO 3506-1"}),
    "screw_button_head": frozenset({"ISO 7380-1", "ASME B18.3", "ISO 898-1", "ISO 3506-1"}),
    "screw_low_head": frozenset({"DIN 7984", "ASME B18.3", "ISO 898-1", "ISO 3506-1"}),
    "bolt_hex": frozenset({"ASME B18.2.1", "ISO 4014", "ISO 4017", "DIN 933", "ISO 8765",
                           "ISO 8676", "DIN 961", "SAE J429", "ISO 898-1"}),
    "nut_hex": frozenset({"ISO 4032", "ISO 4035", "ISO 8673", "ISO 8675", "ASME B18.2.2",
                          "SAE J995", "ISO 898-2"}),
    "set_screws_hex_socket": frozenset({"ISO 4026", "ISO 4027", "ISO 4028", "ISO 4029",
                                        "ASME B18.3", "ISO 898-5", "ISO 3506-3", "ASTM F912",
                                        "ASTM F880"}),
    "lock_nuts_nylon_insert": frozenset({"ISO 7040", "ISO 10511", "ISO 10512", "DIN 985",
                                         "ISO 2320", "ISO 898-2", "ISO 3506-2", "SAE J995"}),
    "washer_flat": frozenset({"ISO 7089", "DIN 125-A"}),
    "end_mill_square": frozenset({"ISO 1641", "DIN 6527", "ANSI B94.19"}),
    "end_mill_ball": frozenset({"ISO 1641", "DIN 6527", "ANSI B94.19"}),
    "drill_jobber": frozenset({"DIN 338", "ASME B94.11M"}),
    "tap_spiral_point": frozenset({"ISO 529", "ASME B94.9"}),
    "hex_key": frozenset({"ISO 2936", "ASME B18.3"}),
    "hammer_ball_pein": frozenset({"ASME B107.400"}),
    "abrasive_flap_disc": frozenset({"EN 13743", "oSa Certified"}),
    "wheel_depressed_center": frozenset({"ANSI B7.1", "EN 12413", "oSa Certified"}),
    "bearing_radial_ball": frozenset({"ISO 15", "ISO 492", "ABMA 20"}),
    "kit_assortment": frozenset(),
}  # fmt: skip

#: The key dimension every title names, per type.
LEGACY_TITLE_KEY: dict[str, tuple[str, ...]] = {
    "end_mill_square": ("Milling Dia.",), "end_mill_ball": ("Milling Dia.",),
    "drill_jobber": ("Size",), "tap_spiral_point": ("Thread Size",),
    "screw_socket_head": ("Dia./Thread Size",), "screw_flat_head": ("Dia./Thread Size",),
    "screw_button_head": ("Dia./Thread Size",), "screw_low_head": ("Dia./Thread Size",),
    "bolt_hex": ("Dia./Thread Size",), "washer_flat": ("Size",), "nut_hex": ("Thread Size",),
    "set_screws_hex_socket": ("Dia./Thread Size",),
    "lock_nuts_nylon_insert": ("Thread Size",),
    "hex_key": ("Size",), "bearing_radial_ball": ("Bearing Number", "Bore"),
    "wheel_depressed_center": ("Diameter",), "abrasive_flap_disc": ("Diameter",),
    "hammer_ball_pein": ("Head Weight",), "kit_assortment": ("Number of Pieces",),
}  # fmt: skip


def may_claim() -> dict[str, frozenset[str]]:
    """Every modelled type's claimable standards."""
    return dict(LEGACY_MAY_CLAIM)


def title_key() -> dict[str, tuple[str, ...]]:
    """Every modelled type's title key."""
    return dict(LEGACY_TITLE_KEY)


def default_size() -> dict[str, tuple[int, int]]:
    """Every modelled type's default-build (lines, SKUs): not yet per type."""
    return {}
