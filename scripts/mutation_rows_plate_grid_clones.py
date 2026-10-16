"""Mutation rows for the plate material price weights (gen#229), kept out of ``mutation_check.py``.

Each row plants one defect in the tableware weights of ``scale.PREMIUM`` and names the test that
must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``plate grid clones: ...`` (``--only "plate grid clones:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

_OLD = '"bone": 1.6, "porcelain": 1.2, "enamel": 0.8, "melamine": 0.6,'
_PLATES = "tests/test_retail_scale.py -k test_plates_mostly_draw_a_tile_of_their_own"
_ORDER = "tests/test_retail_scale.py -k test_a_plate_material_has_its_own_price"
_PROP = "plates of one finish and color draw apart through their material's price"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the plate material weights are dropped",
        "scale.py",
        "    " + _OLD + "\n",
        "",
        _PLATES,
        _PROP,
        "prototypes/retail_drawings",
    ),
    (
        "every plate material weighs the same",
        "scale.py",
        _OLD,
        '"bone": 1.0, "porcelain": 1.0, "enamel": 1.0, "melamine": 1.0,',
        _ORDER,
        _PROP,
        "prototypes/retail_drawings",
    ),
    (
        "melamine costs more than stoneware",
        "scale.py",
        '"melamine": 0.6,',
        '"melamine": 1.4,',
        _ORDER,
        _PROP,
        "prototypes/retail_drawings",
    ),
    (
        "bone china costs less than stoneware",
        "scale.py",
        '"bone": 1.6,',
        '"bone": 0.9,',
        _ORDER,
        _PROP,
        "prototypes/retail_drawings",
    ),
]
