"""The checks every per-type gate file shares (#53), kept in one place.

A deepened type's gate file (``test_type_<key>.py``) states its key and its
floor and calls these. Each comparison here compares sha256 digests first, and
only on a mismatch walks the records to name the first differing SKU. Pytest's
own diff of two megabyte strings does not finish in practical time, so a gate
built on a bare ``assert a == b`` reports a red after many minutes or not at all.
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

from published import published_attributes
from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.model import Catalog
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from synthetic_ecommerce_data.domains.industrial.newtypes import NO_STANDARD

TESTS = Path(__file__).resolve().parent
GOLDEN_FLAT = TESTS.parent / "golden-catalog" / "flat.jsonl"

#: Two hash seeds a set or a str-keyed dict iterates differently under.
HASH_SEEDS = ("0", "1")


def records(lines) -> list[str]:
    """Flat records, one string each, serialised as ``golden-catalog/flat.jsonl`` is."""
    catalog = Catalog(lines=tuple(lines))
    return [
        json.dumps(doc, ensure_ascii=False)
        for doc in emit.iter_flat(catalog, emit.DEFAULT_IMAGE_BASE_URL)
    ]


def default_records(key: str) -> list[str]:
    """The type's flat records at the default build, from a config of its own."""
    return records(generate_type(GeneratorConfig(), key))


def _digest(lines: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _sku(line: str) -> str:
    try:
        return f" (SKU {json.loads(line)['sku']})"
    except (ValueError, TypeError, KeyError):
        return ""


def difference(committed: Sequence[str], rebuilt: Sequence[str]) -> str | None:
    """``None`` when the two are byte-identical; else where they first differ.

    The report names the first differing line, its SKU when the line is a
    record, and the first differing character, with a window around it. A
    record is one long line, so quoting it from the start would show two
    identical prefixes and hide the change.
    """
    if _digest(committed) == _digest(rebuilt):
        return None
    pairs = list(zip(committed, rebuilt, strict=False))
    differing = sum(1 for a, b in pairs if a != b) + abs(len(committed) - len(rebuilt))
    first = next((i for i, (a, b) in enumerate(pairs) if a != b), len(pairs))
    a = committed[first] if first < len(committed) else ""
    b = rebuilt[first] if first < len(rebuilt) else ""
    column = next(
        (i for i, (x, y) in enumerate(zip(a, b, strict=False)) if x != y), min(len(a), len(b))
    )
    start = max(0, column - 60)

    def excerpt(lines: Sequence[str]) -> str:
        if first >= len(lines):
            return "<EOF>"
        line = lines[first]
        window = line[start : column + 120]
        return ("…" if start else "") + window + ("…" if column + 120 < len(line) else "")

    return (
        f"committed {len(committed)} lines, rebuilt {len(rebuilt)} lines; "
        f"{differing} line(s) differ, first at line {first + 1}{_sku(a or b)} "
        f"character {column + 1}:\n"
        f"    committed: {excerpt(committed)}\n"
        f"    rebuilt  : {excerpt(rebuilt)}"
    )


_BUILD_ONE_TYPE = """
import sys
sys.path.insert(0, sys.argv[1])
from type_gates import default_records
sys.stdout.write("".join(line + "\\n" for line in default_records(sys.argv[2])))
"""


def builds_under_two_hash_seeds(key: str) -> tuple[list[str], list[str]]:
    """The type's default records, built in two fresh processes, one per hash seed.

    Two builds in ONE process share a hash seed, so a draw from a set's order
    (``rng.choice(list(set(...)))``) agrees with itself there and moves only
    in the next process. The global ``random`` is also seeded afresh in each.
    """
    runs = [
        subprocess.Popen(
            [sys.executable, "-c", _BUILD_ONE_TYPE, str(TESTS), key],
            env={**os.environ, "PYTHONHASHSEED": seed},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        for seed in HASH_SEEDS
    ]
    outputs = []
    for seed, run in zip(HASH_SEEDS, runs, strict=True):
        out, err = run.communicate(timeout=600)
        assert run.returncode == 0, f"the build under PYTHONHASHSEED={seed} failed:\n{err[-2000:]}"
        outputs.append(out.splitlines())
    return outputs[0], outputs[1]


def _by_type(lines: Iterable[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in lines:
        out.setdefault(json.loads(line)["product_type"], []).append(line)
    return out


@functools.cache
def _golden_by_type() -> dict[str, list[str]]:
    return _by_type(GOLDEN_FLAT.read_text(encoding="utf-8").splitlines())


@functools.cache
def _fresh_by_type() -> dict[str, list[str]]:
    # ``generate()`` makes a new default config, so no earlier build's write reaches it.
    return _by_type(records(generate().lines))


def others_moved_from_the_golden(key: str) -> str | None:
    """``None`` when every type but ``key`` builds today as ``golden-catalog/`` has it.

    This sees what leaving ``key`` out cannot: a shared helper edited for
    ``key`` moves the other types on both sides of that comparison alike. It
    compares against the committed golden, so a PR that also regenerates the
    golden shows the moved types in its diff rather than here.
    """
    golden, fresh = _golden_by_type(), _fresh_by_type()
    moved = sorted(
        k
        for k in golden.keys() | fresh.keys()
        if k != key and _digest(golden.get(k, [])) != _digest(fresh.get(k, []))
    )
    if not moved:
        return None
    first = moved[0]
    return (
        f"{len(moved)} other type(s) differ from {GOLDEN_FLAT.parent.name}/{GOLDEN_FLAT.name}: "
        f"{moved[:8]}\n{first}: {difference(golden.get(first, []), fresh.get(first, []))}"
    )


def provenance_problems(
    docs: Iterable[dict], dimensional: Iterable[str], dimensions: Iterable[str]
) -> tuple[list[tuple[str, str]], int]:
    """Records whose ``dimension_provenance`` disagrees with what they publish,
    and how many dimensional claims were checked.

    A record that claims a dimensional standard (one of ``dimensional``) must
    name it in its provenance and must not say that no standard fixes its
    values. Every published dimension (of ``dimensions``) must be named, so a
    reader can tell where each value came from.
    """
    dimensional, dimensions = set(dimensional), tuple(dimensions)
    problems: list[tuple[str, str]] = []
    checked = 0
    for doc in docs:
        provenance = doc["dimension_provenance"]
        published = published_attributes(doc)
        for standard in {a["value"] for a in published if a["name"] == "Standards"} & dimensional:
            checked += 1
            if standard not in provenance or NO_STANDARD in provenance:
                problems.append((doc["sku"], f"claims {standard}; provenance {provenance!r}"))
        for name in {a["name"] for a in published} & set(dimensions):
            if name not in provenance:
                problems.append((doc["sku"], f"publishes {name}; provenance {provenance!r}"))
    return problems, checked
