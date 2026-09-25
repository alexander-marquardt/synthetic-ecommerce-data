"""The attribute vocabularies must really be disjoint, and the tree really a tree.

Disjointness is not decoration. The facet-discovery case under test is "scope a
terms aggregation to one product type and get back exactly that type's
attribute names". If two unrelated types quietly shared a name, that query
would still look correct while proving nothing, so the property is asserted
here rather than assumed.
"""

from __future__ import annotations

import math

from synthetic_industrial_products.catalog import taxonomy
from synthetic_industrial_products.catalog.vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    MEASUREMENT_SYSTEM_VALUES,
    SHARED_NAMES,
    STANDARDS_FAMILY,
    STANDARDS_POOL,
    VOCAB,
    names_for,
)


def test_every_type_has_a_category_leaf_and_every_leaf_a_type():
    assert set(VOCAB) == set(taxonomy.LEAVES)
    assert set(VOCAB) == set(STANDARDS_FAMILY)


def test_the_tree_is_three_or_four_levels_deep():
    assert taxonomy.tree_depths() == {3, 4}


def test_no_category_path_is_duplicated():
    paths = taxonomy.all_paths()
    assert len(paths) == len(set(paths))


def test_ancestors_are_the_prefixes():
    path = (
        "Holemaking",
        "Drilling & Drill Bits",
        "Metalworking & Multipurpose Drill Bits",
        "Jobber Length Drill Bits",
    )
    assert taxonomy.ancestors(path) == (
        ("Holemaking",),
        ("Holemaking", "Drilling & Drill Bits"),
        ("Holemaking", "Drilling & Drill Bits", "Metalworking & Multipurpose Drill Bits"),
        path,
    )


def test_a_screw_and_a_hammer_share_almost_nothing():
    screw = names_for("screw_socket_head")
    hammer = names_for("hammer_ball_pein")
    overlap = screw & hammer
    # "Item" is the only name both publish. Everything else about a threaded
    # fastener and a striking tool is described in different words.
    assert overlap == {"Item"}, overlap


def test_an_end_mill_and_a_flap_disc_share_almost_nothing():
    overlap = names_for("end_mill_square") & names_for("abrasive_flap_disc")
    assert overlap == {"Item"}, overlap


def test_no_unshared_name_appears_in_two_different_type_families():
    """A name outside SHARED_NAMES belongs to exactly one product type.

    ``end_mill_square`` and ``end_mill_ball`` are the same family under two
    category leaves and legitimately share a whole vocabulary, so they are
    compared as one.
    """
    families = {
        "end_mill": ("end_mill_square", "end_mill_ball"),
        "drill": ("drill_jobber",),
        "tap": ("tap_spiral_point",),
        "socket_screw": ("screw_socket_head", "screw_flat_head"),
        "hex_bolt": ("bolt_hex",),
        "washer": ("washer_flat",),
        "hammer": ("hammer_ball_pein",),
        "flap_disc": ("abrasive_flap_disc",),
    }
    seen: dict[str, str] = {}
    for family, keys in families.items():
        names: set[str] = set()
        for key in keys:
            names |= names_for(key)
        for name in names - SHARED_NAMES:
            assert name not in seen, f"{name!r} is in both {seen.get(name)} and {family}"
            seen[name] = family


def test_the_measurement_system_attribute_has_three_spellings():
    names = [name for name, _ in MEASUREMENT_SYSTEM_NAMES]
    assert names == ["Dimension Type", "Measurement System", "System of Measurement"]
    assert len(set(names)) == 3


def test_measurement_system_weights_are_distributions():
    for table in (MEASUREMENT_SYSTEM_NAMES, MEASUREMENT_SYSTEM_VALUES):
        assert math.isclose(sum(weight for _, weight in table), 1.0, abs_tol=5e-3)


def test_every_standards_family_has_a_pool_with_room_for_three_values():
    for key, family in STANDARDS_FAMILY.items():
        pool = STANDARDS_POOL[family]
        assert len(pool) >= 3, f"{key} -> {family} cannot supply 1-3 distinct values"


def test_each_type_declares_both_line_and_sku_scoped_attributes():
    for key, specs in VOCAB.items():
        scopes = {spec.scope for spec in specs}
        assert scopes == {"line", "sku"}, f"{key}: {scopes}"


def test_presence_rates_are_probabilities():
    for key, specs in VOCAB.items():
        for spec in specs:
            assert 0.0 < spec.presence <= 1.0, f"{key}.{spec.name} = {spec.presence}"
