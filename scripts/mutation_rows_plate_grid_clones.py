"""Mutation rows for the plate material price weights (gen#229), kept out of ``mutation_check.py``.

Each row plants one defect in the tableware weights of ``scale_measures.PREMIUM`` and names the
test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``plate grid clones: ...`` (``--only "plate grid clones:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_OLD = '"bone": 2.0, "porcelain": 1.4, "enamel": 0.75, "melamine": 0.5,'
_PLATES = "tests/test_retail_scale.py -k test_plates_mostly_draw_a_tile_of_their_own"
_ORDER = "tests/test_retail_scale.py -k test_a_plate_material_has_its_own_price"
_PROP = "plates of one finish and color draw apart through their material's price"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the plate material weights are dropped",
        "scale_measures.py",
        "    " + _OLD + "\n",
        "",
        _PLATES,
        _PROP,
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "every plate material weighs the same",
        "scale_measures.py",
        _OLD,
        '"bone": 1.0, "porcelain": 1.0, "enamel": 1.0, "melamine": 1.0,',
        _ORDER,
        _PROP,
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "melamine costs more than stoneware",
        "scale_measures.py",
        '"melamine": 0.5,',
        '"melamine": 1.4,',
        _ORDER,
        _PROP,
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "bone china costs less than stoneware",
        "scale_measures.py",
        '"bone": 2.0,',
        '"bone": 0.9,',
        _ORDER,
        _PROP,
        "src/synthetic_ecommerce_data/domains/retail",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "plate grid clones"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
