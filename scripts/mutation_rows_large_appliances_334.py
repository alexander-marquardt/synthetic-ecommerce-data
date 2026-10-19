"""Mutation rows for the large appliances (gen#334), kept out of ``mutation_check.py``.

Each row plants one defect in a spec and names the test that must go red. ``mutation_check.py``
turns them into ``Mutation`` rows named ``large appliances: ...`` (``--only "large appliances:"``
re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501 -- a row's old and new text are spec lines, quoted whole.

from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"
_T = "tests/test_retail_large_appliances_334.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "large appliances: the Black Edition fridge is sold in black",
        "type_specs/fridge_freezer.py",
        '"freezer with frost free cooling.", (rows.SILVER,),',
        '"freezer with frost free cooling.", (rows.BLACK,),',
        f'{_T} -k "black_edition"',
        "the structured finish of the Black Edition fridge stays stainless steel",
        _R,
    ),
    (
        "large appliances: the thermometer decoy sits in the appliance leaf",
        "type_specs/fridge_thermometer.py",
        '("Home", "Kitchen & Dining", "Fridge Thermometers"),\n            "Fridge Thermometer", "fridge_thermometer", 7.0',
        '("Home", "Large Appliances", "Fridges & Freezers"),\n            "Fridge Thermometer", "fridge_thermometer", 7.0',
        f'{_T} -k "magnet_a_thermometer"',
        "a class-8 decoy of the fridge is not in the appliance node",
        _R,
    ),
    (
        "large appliances: the mat's ordinary product names the machine",
        "type_specs/anti_vibration_mat.py",
        '"Rubber Floor Pads for Laundry Machines, Set of 4"',
        '"Washing Machine Rubber Floor Pads, Set of 4"',
        f'{_T} -k "magnet_a_thermometer"',
        "a type's ordinary product is titled without the appliance word",
        _R,
    ),
    (
        "large appliances: the magnets decoy is the only fridge magnet",
        "type_specs/fridge_magnets.py",
        '"Photo and Note Magnets, Set of 8"',
        '"Fridge Magnets, Set of 8"',
        f'{_T} -k "magnet_a_thermometer"',
        "a type's ordinary product is titled without the appliance word",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "large appliances"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
