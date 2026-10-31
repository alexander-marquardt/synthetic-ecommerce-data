"""Mutation rows for the no-wrong-kind guard (gen#404), kept out of ``mutation_check.py``.

Each row plants one value the generator knows is wrong -- an inch length under an angle key, a cut
longer than its part, a declared system against the record's units -- and names the tests that must
go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``no wrong kind: ...`` (``--only "no wrong kind:"`` re-runs them). A row is
``(name, file, old, new, tests, property)``; the file is relative to the generator package.
"""

from __future__ import annotations

from mutation_row import Row

_GUARD = (
    'tests/test_no_wrong_kind_values_404.py -k "angle_key_holds_angles_only and measured"',
    'tests/test_no_wrong_kind_values_404.py -k "nested_angle_entry and measured"',
    'tests/test_catalog_generate.py -k "no_deliberately_wrong_value and angle"',
)

_PART_GUARD = (
    'tests/test_no_wrong_kind_values_404.py -k "no_length_of_cut and measured"',
    'tests/test_catalog_generate.py -k "no_deliberately_wrong_value and cut"',
)

_SYSTEM_GUARD = (
    'tests/test_no_wrong_kind_values_404.py -k "declared_system and measured"',
    'tests/test_catalog_generate.py -k "no_deliberately_wrong_value and declared"',
)

ROWS: list[tuple[str, str, str, str, tuple[str, ...], str]] = [
    (
        "an inch length is written under the helix angle key",
        "domains/industrial/generate.py",
        'Attribute("Helix Angle", format_angle(helix), helix)',
        """Attribute("Helix Angle", '2"', helix)""",
        _GUARD,
        "an angle key holds angles only",
    ),
    (
        "an inch length is written under the point angle key",
        "domains/industrial/generate.py",
        'Attribute("Point Angle", format_angle(point), point)',
        """Attribute("Point Angle", '1-5/8"', point)""",
        _GUARD,
        "an angle key holds angles only",
    ),
    (
        "a length of cut is published longer than its overall length",
        "domains/industrial/generate.py",
        'self._length("Length of Cut", geom.length_of_cut_in, style)',
        'self._length("Length of Cut", geom.length_of_cut_in * 9, style)',
        _PART_GUARD,
        "a part fits inside its whole",
    ),
    (
        "a declared measurement system contradicts the record's units",
        "domains/industrial/finishing.py",
        "return keyword_attribute(name, truthful)",
        'return keyword_attribute(name, "Metric" if system == "in" else "Inch")',
        _SYSTEM_GUARD,
        "a declared system agrees with the published units",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "no wrong kind"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
