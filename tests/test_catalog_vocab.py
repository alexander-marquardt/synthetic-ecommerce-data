"""The attribute vocabularies are shaped the way the census shapes them, and the tree is a tree.

Which NAMES are allowed is ``tests/test_attribute_names.py``. What is asserted
here is the shape: unrelated product types still share almost nothing, so a
facet discovery scoped to one type returns that type's names -- but a concept
both types carry is ONE name on both (``Material``), never one per type.
"""

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.industrial import taxonomy
from synthetic_ecommerce_data.domains.industrial.vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    MEASUREMENT_SYSTEM_VALUES,
    STANDARDS_FAMILY,
    VOCAB,
    names_for,
)


def test_every_type_has_a_category_leaf_and_every_leaf_a_type():
    assert set(VOCAB) == set(taxonomy.LEAVES)
    assert set(VOCAB) == set(STANDARDS_FAMILY)


def test_the_tree_is_three_to_five_levels_deep():
    """As the reference distributor's is: hex keys sit five levels down."""
    # The one shared leaf, Hand Tools > Hammers (#305), is two levels: the combined tree puts
    # the catalog's own root above it, so a shopper reads Tools > Hand Tools > Hammers.
    own = {len(p) for p in taxonomy.all_paths() if p not in taxonomy.SHARED_LEAVES}
    assert own == {3, 4, 5}
    assert taxonomy.tree_depths() == {2, 3, 4, 5}


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


def test_a_screw_and_a_hammer_share_only_generic_concepts():
    screw = names_for("screw_socket_head")
    hammer = names_for("hammer_ball_pein")
    # What a threaded fastener and a striking tool have in common is what they
    # are made of -- and they say "Material" alike. The item name is gone (#497):
    # it repeated the product type.
    assert screw & hammer == {"Material"}, screw & hammer


def test_an_end_mill_and_a_flap_disc_share_almost_nothing():
    overlap = names_for("end_mill_square") & names_for("abrasive_flap_disc")
    assert overlap == set(), overlap


def test_one_concept_is_one_name_across_types():
    """The rule the disjointness gate used to forbid.

    Every type that publishes what it is made of calls it ``Material``, and
    every type with a coating or plating calls it ``Finish``. A filter on the
    concept is one field on a nested index, whatever the type count.
    """
    carrying_material = {key for key in VOCAB if "Material" in names_for(key)}
    # An abrasive is described by its grain, ``Abrasive Material``, a component
    # the reference spec table names separately; it publishes no ``Material``.
    abrasives = {"abrasive_flap_disc", "wheel_depressed_center"}
    assert carrying_material == set(VOCAB) - abrasives, carrying_material
    carrying_finish = {key for key in VOCAB if "Finish" in names_for(key)}
    assert {"end_mill_square", "drill_jobber", "tap_spiral_point", "bolt_hex"} <= carrying_finish


def test_the_measurement_system_attribute_has_one_name():
    """Dimension Type and System of Measurement were two more names for it (#497)."""
    names = [name for name, _ in MEASUREMENT_SYSTEM_NAMES]
    assert names == ["Measurement System"]


def test_measurement_system_weights_are_distributions():
    for table in (MEASUREMENT_SYSTEM_NAMES, MEASUREMENT_SYSTEM_VALUES):
        assert math.isclose(sum(weight for _, weight in table), 1.0, abs_tol=5e-3)


def test_each_type_declares_both_line_and_sku_scoped_attributes():
    for key, specs in VOCAB.items():
        scopes = {spec.scope for spec in specs}
        assert scopes == {"line", "sku"}, f"{key}: {scopes}"


def test_presence_rates_are_probabilities():
    for key, specs in VOCAB.items():
        for spec in specs:
            assert 0.0 < spec.presence <= 1.0, f"{key}.{spec.name} = {spec.presence}"
