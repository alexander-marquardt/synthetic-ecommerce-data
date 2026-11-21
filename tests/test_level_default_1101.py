"""#1101, slice 2: a drawing is level unless its shape is named as tiltable.

The maintainer, 2026-11-21, from a demo screenshot of a tilted sofa: "sofas should not be tilted.
I think most furniture should not. Neither should mountain bikes. Can you have the generator do a
sanity check on what it is tilting?" Each retail shape used to have to name a set, and a shape
nobody was sure of went to ``upright`` (+-36 degrees), so a large thing was turned unless someone
had thought to list it as ``level``. Now tilt is opt-in. A shape that no ``orientations/`` module
names is ``level`` (:func:`.orientation.of`), and only things you hold, carry or wear keep
``any``, ``slight`` or ``upright``.

:data:`NOT_HELD` is the review's list: each shape that stood in ``upright`` on main f53951d2 but
is not held or worn. It stands on the floor, is fixed to a wall, ceiling, car or plumbing, is a
mains appliance or screen used where it stands, is bedding, a rug, a mat or a curtain laid flat
or hung, or is a vehicle or something on wheels. On f53951d2, slice 1's guard applied, 485 of the
752 products drawn with them were turned.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.core.drawing import product_look
from synthetic_ecommerce_data.domains.retail import kit, orientation

#: The shapes the review moved from ``upright`` to ``level``, by what they are.
NOT_HELD: dict[str, tuple[str, ...]] = {
    "stands on the floor": (
        "bath_storage", "bbq", "camp_chair", "car_seat", "christmas_tree", "clothes_airer",
        "dishwasher", "dolls_house", "fountain", "fridge", "garden_statue", "garden_storage",
        "heater", "high_chair", "kitchen_bin", "nursery_storage", "pedestal_fan", "pet_bed",
        "planter", "play_kitchen", "potted_tree", "step_ladder", "tent", "tower_fan",
        "tumble_dryer", "vanity", "washer_dryer", "washing_machine",
    ),
    "fixed to a wall, ceiling, car or plumbing": (
        "ceiling_fan", "clock", "seat_cover", "sink_faucet", "sun_shade", "tile", "trunk_liner",
        "wallpaper",
    ),
    "a mains appliance or screen used where it stands": (
        "air_fryer", "blender", "coffee_maker", "desk_fan", "desktop", "monitor", "printer",
        "soundbar", "toaster", "tv",
    ),
    "laid flat or hung: bedding, rugs, mats, curtains": (
        "anti_vibration_mat", "bath_mat", "blind", "changing_mat", "curtains", "draped_throw",
        "duvet", "floor_mat", "mattress", "mattress_protector", "mattress_topper",
        "picnic_blanket", "roll_mat", "rug", "sheet", "sheet_set", "shower_curtain",
        "sleeping_bag", "sofa_cover", "throw", "yoga_mat",
    ),
    "a vehicle or on wheels": (
        "cabin_case", "car", "kayak", "kick_scooter", "lawn_mower", "rc_vehicle", "ride_on",
        "robot_mower", "skateboard", "stroller", "suitcase",
    ),
}  # fmt: skip

_NOT_HELD = sorted(s for shapes in NOT_HELD.values() for s in shapes)


def test_the_review_lists_78_registered_shapes_once():
    kit.register_all()
    assert len(_NOT_HELD) == len(set(_NOT_HELD)) == 78
    assert sorted(set(_NOT_HELD) - set(kit.SHAPES)) == []


def test_a_shape_no_module_names_is_drawn_level():
    """Tilt is opt-in: a shape that no ``orientations/`` module names is not turned."""
    assert "no_such_shape_1101" not in orientation.ORIENTATION
    assert orientation.of("no_such_shape_1101") == "level"
    assert product_look.ORIENTATIONS[orientation.of("no_such_shape_1101")] == (0,)


@pytest.mark.parametrize("shape", _NOT_HELD)
def test_a_shape_not_held_or_worn_is_level(shape):
    assert orientation.of(shape) == "level"


def test_upright_names_only_held_or_worn_shapes():
    """No reviewed shape is left in a tilting set, and the held ones the issue names keep theirs:
    a glove at any angle (the maintainer's ruling on #860), a garment slightly, a bottle upright."""
    tilting = {*orientation.ANY, *orientation.SLIGHT, *orientation.UPRIGHT}
    assert sorted(tilting & set(_NOT_HELD)) == []
    assert orientation.of("gloves") == "any"
    assert orientation.of("tshirt") == "slight"
    for held in ("bottle", "light_bulb", "kettle", "smartphone", "doll", "drill"):
        assert orientation.of(held) == "upright", held
