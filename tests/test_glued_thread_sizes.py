"""A glued metric thread size is also written in its parts.

The standard analyzer indexes ``M12x1.75`` as ONE token, so a search for
``m12`` misses a record whose text only carries the glued form -- measured on
catalog-2026-09-29f, the six jobber drills saying "Tap drill for M12x1.75
threads" were not returned for ``m12``. The maintainer ruled this is fixed in
the data (alexander-marquardt/synthetic-ecommerce-data#33): wherever the
text carries a glued size, the description also writes the diameter and the
pitch as tokens of their own.

The tokens are read here the way the standard tokenizer splits them, from
this file's own pattern, never from the generator's.
"""

from __future__ import annotations

import collections
import json
import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.naming import thread_parts
from synthetic_ecommerce_data.domains.industrial.generate import generate

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"

#: A metric designation the analyzer keeps whole: no space, an ASCII ``x``.
GLUED = re.compile(r"(?<![\w.])M(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)(?!\.?\d)")
#: Word tokens as the standard tokenizer cuts them: letters and digits, with a
#: ``.`` kept only BETWEEN two of them (``1.75``, ``m12x1.75``).
TOKEN = re.compile(r"\w+(?:\.\w+)*")
#: A size written in its parts.
PART = re.compile(r"\bM(\d+(?:\.\d+)?) thread, (\d+(?:\.\d+)?) mm pitch\b")


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in TOKEN.findall(text)}


@pytest.fixture(scope="module")
def golden() -> list[dict]:
    return [json.loads(line) for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()]


@pytest.fixture(scope="module")
def fresh() -> list[dict]:
    return list(emit.iter_flat(generate(GeneratorConfig())))


@pytest.fixture(scope="module", params=["golden", "fresh"])
def docs(request) -> list[dict]:
    return request.getfixturevalue(request.param)


def unsplit(docs: list[dict]) -> tuple[list[tuple[str, str]], collections.Counter[str]]:
    """Records whose title or description glues a size the description never
    writes in parts, and the count of glued records checked, by type."""
    missing, checked = [], collections.Counter()
    for doc in docs:
        hits = GLUED.findall(f"{doc['title']} {doc['description']}")
        if not hits:
            continue
        checked[doc["product_type"]] += 1
        tokens = _tokens(doc["description"])
        for dia, pitch in hits:
            if f"m{dia}" not in tokens or pitch not in tokens:
                missing.append((doc["sku"], f"M{dia}x{pitch}"))
    return missing, checked


def test_every_glued_thread_size_is_also_written_in_parts(docs):
    missing, checked = unsplit(docs)
    assert missing == [], f"{len(missing)} glued sizes never written in parts: {missing[:10]}"
    # Every family that carries a metric thread is checked, the drills whose
    # only mention is the tap-drill sentence included.
    for type_key in ("drill_jobber", "tap_spiral_point", "nut_hex", "screw_socket_head"):
        assert checked[type_key] > 20, (type_key, checked)


def test_every_written_part_is_a_glued_size_the_record_names(docs):
    """The parts are read from the record's own designations, never invented:
    each "M8 thread, 1.25 mm pitch" stands beside an ``M8x1.25`` the same
    title or description glues."""
    invented, written = [], 0
    for doc in docs:
        glued = set(GLUED.findall(f"{doc['title']} {doc['description']}"))
        for dia, pitch in PART.findall(doc["description"]):
            written += 1
            if (dia, pitch) not in glued:
                invented.append((doc["sku"], dia, pitch))
    assert invented == [], invented[:10]
    assert written > 1000


def test_a_tap_drill_for_m12_is_found_by_m12(docs):
    """The case the maintainer measured: a drill whose only M12 is the glued
    size in its tap-drill sentence."""
    drills = [
        doc
        for doc in docs
        if doc["product_type"] == "drill_jobber" and "for M12x1.75 threads" in doc["description"]
    ]
    assert drills, "no drill names the M12x1.75 tap drill"
    assert [d["sku"] for d in drills if "m12" not in _tokens(d["description"])] == []


@pytest.mark.parametrize(
    ("text", "parts"),
    [
        ("Hex Nut, M12x1.75, Class 8", ["M12 thread, 1.75 mm pitch"]),
        ("Tap drill for M6x1 threads.", ["M6 thread, 1 mm pitch"]),
        ("M3x0.5, M4x0.7, M3x0.5", ["M3 thread, 0.5 mm pitch", "M4 thread, 0.7 mm pitch"]),
        ("M1.6x0.35 Dia./Thread Size", ["M1.6 thread, 0.35 mm pitch"]),
        # Already split by the analyzer: nothing to add.
        ("M12 x 1.75, 1/4\"-20, #10-32", []),
    ],
)
def test_thread_parts_names_each_glued_size_once(text, parts):
    assert thread_parts(text) == parts
