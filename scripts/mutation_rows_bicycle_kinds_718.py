"""Mutation rows for the bike kinds, the ten brands and the bicycle sizes (gen#718).

Each row plants one defect in the bicycle drawing, the size ladder or the brand tables and names
the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``bikekinds: ...`` (``--only "bikekinds:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501 -- a row's old and new text are source lines, quoted whole.

from __future__ import annotations

from mutation_row import Row

_R = "src/synthetic_ecommerce_data/domains/retail"
_K = "kit_sports.py"
_B = "bicycle_model_numbers.py"
_T = "tests/test_retail_bicycle_kinds_718.py"
_N = "tests/test_retail_bicycle_model_numbers_625.py"
_G = "tests/test_retail_bicycle_range_685.py"
_MOUNTAIN = '"mountain": (78, 18, 100, 300, 268, 200, 160)'

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a mountain tire as thin as a road tire",
        _K,
        _MOUNTAIN,
        '"mountain": (78, 4, 100, 300, 268, 200, 160)',
        f'{_T} -k "mountain_tire_and_the_electric_down_tube"',
        "a mountain tire is wider than a road tire",
        _R,
    ),
    (
        "the mountain wheels overlap",
        _K,
        _MOUNTAIN,
        '"mountain": (78, 18, 120, 280, 268, 200, 160)',
        f'{_T} -k "larger_fatter_and_clear"',
        "the mountain wheels clear each other",
        _R,
    ),
    (
        "a mountain top tube as level as a road one",
        _K,
        _MOUNTAIN,
        '"mountain": (78, 18, 100, 300, 268, 200, 200)',
        f'{_T} -k "top_tube_slopes"',
        "a mountain bike's top tube slopes",
        _R,
    ),
    (
        "an electric down tube no thicker than the rest",
        _K,
        'TUBE * 2.5 if kind == "electric" else TUBE',
        "TUBE",
        f'{_T} -k "two_and_a_half_times"',
        "the electric down tube is about 2.5 times the other tubes",
        _R,
    ),
    (
        "every bike gets a knobbly tread",
        _K,
        'if kind == "mountain":  # the tread',
        "if True:  # the tread",
        f'{_T} -k "knobbly_tread"',
        "only a mountain bike has a tread",
        _R,
    ),
    (
        "the battery is dark on every frame",
        _K,
        "BATTERY_DARK if _luminance(frame) >= BATTERY_TURN else BATTERY_LIGHT",
        "BATTERY_DARK",
        f'{_T} -k "stands_out_from_every_electric_frame_color"',
        "the battery is at least 3:1 against every electric frame color",
        _R,
    ),
    (
        "the battery sits at the head of the frame",
        _K,
        "mx, my = (hx + bx) / 2, (hy + by) / 2",
        "mx, my = hx, hy",
        f'{_T} -k "sits_on_the_down_tube"',
        "the battery sits on the down tube",
        _R,
    ),
    (
        "the bolt is ink, not the frame's color",
        _K,
        """_path(f"M{' L'.join(bolt)} Z", frame, 1.2""",
        """_path(f"M{' L'.join(bolt)} Z", INK, 1.2""",
        f'{_T} -k "carries_a_bolt"',
        "the battery's bolt is in the frame's color",
        _R,
    ),
    (
        "the hub motor stays the size it was",
        _K,
        """_ell(rx, cy, 24, 24, dark, 2.4, ' class="hub-motor"')""",
        """_ell(rx, cy, 15, 15, dark, 2.4, ' class="hub-motor"')""",
        f'{_T} -k "hub_motor_is_larger"',
        "the hub motor is larger than it was",
        _R,
    ),
    (
        "the stabilizer stands in front of the rear axle",
        _K,
        "x, y = rx - 36, cy + r - small",
        "x, y = rx + 36, cy + r - small",
        f'{_T} -k "one_stabilizer_behind"',
        "the stabilizer is behind the rear axle",
        _R,
    ),
    (
        "the stabilizer hangs off the axle's height",
        _K,
        "x, y = rx - 36, cy + r - small",
        "x, y = rx - 36, cy + small",
        f'{_T} -k "one_stabilizer_behind"',
        "the stabilizer stands on the main wheels' ground",
        _R,
    ),
    (
        "a road bike gets a stabilizer too",
        _K,
        'out = [_stabilizer(rx, cy, r, tire, dark)] if kind == "kids" else []',
        "out = [_stabilizer(rx, cy, r, tire, dark)]",
        f'{_T} -k "road_bike_has_no_stabilizer"',
        "only a kids' bike has a stabilizer",
        _R,
    ),
    (
        "a bicycle is off the size ladder",
        "size_axes.py",
        '"Bicycle": ("frame_cm", "wheel_size_in"),',
        '"Bicycle": (),',
        f'{_T} -k "step_up_the_shared_ladder"',
        "a bike's sizes step up the shared ladder",
        _R,
    ),
    (
        "a kids' bike has no rung",
        "size_axes.py",
        '"Bicycle": ("frame_cm", "wheel_size_in"),',
        '"Bicycle": ("frame_cm",),',
        f'{_T} -k "step_up_the_shared_ladder"',
        "a kids' bike's wheel sizes step up the ladder",
        _R,
    ),
    (
        "encode builds a kind the brand does not sell",
        _B,
        "if kind not in SERIES[brand]:\n        raise ValueError",
        "if False:\n        raise ValueError",
        f'{_N} -k "refuses_a_kind_it_does_not_sell"',
        "a brand refuses a kind it does not sell",
        _R,
    ),
    (
        "decode reads a kind the brand does not sell",
        _B,
        'if (wheel is None) != (kind == "Kids") or kind not in SERIES[brand]:',
        'if (wheel is None) != (kind == "Kids"):',
        f'{_N} -k "refuses_a_kind_it_does_not_sell"',
        "a code for a kind its brand does not sell decodes to nothing",
        _R,
    ),
    (
        "a new brand moves the house brands' model years",
        "type_specs/bicycle.py",
        "LAST_YEAR_EVERY = 3",
        "LAST_YEAR_EVERY = 4",
        f'{_G} -k "keeps_the_bikes_it_had"',
        "each house brand keeps the bikes it had",
        _R,
    ),
    (
        "a new brand owned by the house",
        "breadth_row.py",
        '"Hessenby": "third_party"',
        '"Hessenby": "own"',
        f'{_N} -k "another_houses_make"',
        "a bicycle-only brand is another house's make",
        _R,
    ),
]

PREFIX = "bikekinds"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
