"""A machine key shared by unrelated types carries one unit system.

The Engine classes a bare number by its key. When the key ``diameter`` held 4
in as a wheel's diameter (INH) and 4 as a cotter pin's (MMT), a bare ``4``
could not be classed and the Engine refused to boot (AmbiguousClassKeyError).
Diameters are named by what they measure (``Wheel Dia.``, ``Pin Dia.``), so
types that publish a key in different unit systems do not share it.

A type that itself is sold in both systems (a hex bolt, an end mill) publishes
its own keys in both: that is one type's catalog, not two types sharing a key,
and it is exempt. The defect-injection knob that contradicts a unit is off here,
because it plants a unit on purpose.
"""

from __future__ import annotations

import dataclasses
from collections import defaultdict

from synthetic_industrial_products.catalog.config import SMALL
from synthetic_industrial_products.catalog.generate import generate

#: Keys measured on 2026-10-07 to be shared by single-system types of different
#: systems, fixed in a follow-up. The set only shrinks: a key not listed here
#: must be clean, and a listed key that has become clean must be removed.
KNOWN_UNFIXED = frozenset({"height", "inside_dia", "length", "outside_dia", "thickness"})


def _single_system_units() -> dict[str, dict[str, set[str]]]:
    """Per key, per unit code, the single-system types that publish it."""
    config = dataclasses.replace(SMALL, defect_system_contradicts_units=0.0)
    codes: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for line in generate(config).lines:
        for owner in (line, *line.children):
            for attribute in owner.attributes:
                for entry in attribute.as_entries():
                    if entry.get("unit_code"):
                        codes[entry["key"]][line.type_key].add(entry["unit_code"])
    shared: dict[str, dict[str, set[str]]] = {}
    for key, by_type in codes.items():
        single = {t: next(iter(c)) for t, c in by_type.items() if len(c) == 1}
        by_unit: dict[str, set[str]] = defaultdict(set)
        for type_key, code in single.items():
            by_unit[code].add(type_key)
        if len(by_unit) > 1:
            shared[key] = by_unit
    return shared


SHARED = _single_system_units()


def test_no_key_is_shared_across_unit_systems():
    clashing = {k: {c: sorted(t) for c, t in v.items()} for k, v in SHARED.items()}
    assert {k: v for k, v in clashing.items() if k not in KNOWN_UNFIXED} == {}


def test_the_known_unfixed_list_has_no_clean_key():
    assert sorted(KNOWN_UNFIXED - set(SHARED)) == []
