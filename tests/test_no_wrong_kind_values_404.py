"""No generator step writes a value of the wrong kind for its key (#404).

The maintainer's ruling (2026-10-16): the generator adds no deliberately WRONG
data. A decoy (a real product whose text shares a word with another type) stays;
a value a real retailer would fix does not. The case that prompted it was
``_corrupt_angle``, which wrote inch lengths (``2"``, ``1-5/8"``) under the angle
keys ``point_angle`` and ``helix_angle``, where a facet offered them beside
``118`` and ``135``.

The guard reads the PUBLISHED spelling in the flat ``facets`` and the nested
entries, each judged by its own table here (not by :func:`entry.split`), over a
sample that holds every product type, built twice: at the measured defect rates
and with every defect rate forced to its ceiling, so a step that only fires
sometimes cannot hide in the quiet build.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

import pytest

from industrial_units import pinned
from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.vocab import VOCAB

#: The quantity kind a published unit mark means, written down here.
KIND_OF_MARK = {
    '"': "length",
    "in": "length",
    "in.": "length",
    "mm": "length",
    "ft": "length",
    "Degrees": "plane_angle",
    "oz": "mass",
    "lb": "mass",
    "lbf": "force",
}
PUBLISHED = re.compile(
    r"^\s*(?:[0-9]+(?:[ -][0-9]+)?/[0-9]+|[0-9][0-9,]*(?:\.[0-9]+)?|\.[0-9]+)\s*"
    r"(?P<mark>lbf|lb|in\.|in|mm|ft|oz|Degrees|\")\s*$"
)

#: Keys that measure a plane angle, found by what they are called, not listed.
ANGLE_KEY = re.compile(r"(?:^|_)angle$")

SAMPLES = {
    "measured defect rates": SMALL,
    "every defect rate at its ceiling": SMALL.with_(defect_scale=1000.0),
}


@pytest.fixture(scope="module", params=sorted(SAMPLES))
def docs(request: pytest.FixtureRequest) -> list[dict[str, Any]]:
    catalog = generate(SAMPLES[request.param])
    return list(emit.iter_flat(catalog)) + list(emit.iter_nested(catalog))


def _entries(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return [*doc["attributes"], *(a for v in doc.get("variants", ()) for a in v["attributes"])]


def test_the_sample_holds_every_product_type(docs):
    assert {d["product_type"] for d in docs if "facets" in d} == set(VOCAB)


def test_each_flat_facet_key_holds_one_quantity_kind(docs):
    kinds: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for doc in docs:
        for key, values in doc.get("facets", {}).items():
            for value in values:
                match = PUBLISHED.match(value)
                if match:
                    kinds[key][KIND_OF_MARK[match["mark"]]].add(value)
    mixed = {k: {q: sorted(v)[:4] for q, v in qs.items()} for k, qs in kinds.items() if len(qs) > 1}
    assert not mixed, f"keys that hold more than one quantity kind: {mixed}"


def test_an_angle_key_holds_angles_only(docs):
    seen: set[str] = set()
    wrong: list[tuple[str, str]] = []
    for doc in docs:
        for key, values in doc.get("facets", {}).items():
            if ANGLE_KEY.search(key):
                seen.add(key)
                wrong += [
                    (key, v)
                    for v in values
                    if not (m := PUBLISHED.match(v)) or m["mark"] != "Degrees"
                ]
    assert seen >= {"helix_angle", "point_angle"}, f"the sample offers no angle keys: {seen}"
    assert not wrong, (
        f"{len(wrong)} non-angle values under an angle key, e.g. {sorted(set(wrong))[:6]}"
    )


def test_a_nested_angle_entry_is_an_angle_measurement(docs):
    units = pinned()
    wrong = []
    measured = 0
    for doc in docs:
        if "facets" in doc:
            continue
        for entry in _entries(doc):
            if ANGLE_KEY.search(entry["key"]):
                measured += 1
                if "unit_code" not in entry or units[entry["unit_code"]].kind != "plane_angle":
                    wrong.append((entry["key"], entry["value"], entry.get("unit_code")))
    assert measured, "the sample holds no nested angle entry"
    assert not wrong, (
        f"{len(wrong)} angle entries that measure no angle, e.g. {sorted(set(wrong))[:6]}"
    )
