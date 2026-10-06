"""The industrial deployment's unit declaration, read from the pinned copy.

Each unit code's KIND and EXACT size come from ``tests/data/
industrial_canonical_units.yaml``, a verbatim copy of the deployment's
``canonical_units:`` block. A test that needs a unit's size reads it here
rather than writing it down, so a unit the deployment rules on cannot be
redeclared in this repository unseen. The copy records its own digest, which
``tests/test_industrial_unit_pin.py`` checks, and
``scripts/check_industrial_unit_pin.py`` compares it with its source.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

PIN = Path(__file__).resolve().parent / "data" / "industrial_canonical_units.yaml"


@dataclass(frozen=True)
class Unit:
    #: The quantity kind the deployment declares the code under (``length``).
    kind: str
    #: The code's exact size against the kind's storage ``code``.
    size: Fraction
    #: A count PER that size (``TPI``): the canonical is ``size / magnitude``.
    reciprocal: bool = False

    def canonical(self, magnitude: Fraction) -> Fraction:
        return self.size / magnitude if self.reciprocal else magnitude * self.size


def parse(canonical_units: Mapping[str, Any]) -> dict[str, Unit]:
    """``{code: Unit}`` from a ``canonical_units:`` mapping.

    Refuses a code under two kinds, and a kind whose storage ``code`` is not
    declared at size 1: every other size is measured against that code, so
    ``value_canonical`` is in it.
    """
    units: dict[str, Unit] = {}
    for kind, declaration in canonical_units.items():
        for code, size in declaration["units"].items():
            assert code not in units, f"{code} is declared under {units[code].kind} and {kind}"
            if isinstance(size, Mapping):
                units[code] = Unit(kind, Fraction(size["reciprocal"]), reciprocal=True)
            else:
                units[code] = Unit(kind, Fraction(size))
        storage = units.get(declaration["code"])
        assert storage == Unit(kind, Fraction(1)), f"{kind}: storage code {declaration['code']}"
    return units


def load_block(text: str) -> dict[str, Any]:
    """The ``canonical_units:`` mapping out of a customization's YAML text."""
    return yaml.safe_load(text)["canonical_units"]


def pinned() -> dict[str, Unit]:
    return parse(load_block(PIN.read_text(encoding="utf-8")))
