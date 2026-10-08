"""Build the reference fingerprint file that the non-copying test checks against.

The repository promises that no generated record matches a reference record on
its full attribute tuple. Checking that needs the reference tuples -- but the
reference corpus is someone else's compilation and never ships (see
:file:`.gitignore`), so the tuples themselves cannot live in the repository
either.

What ships instead is a set of **hashes**. A hash is not the compilation: it
cannot be read back into a product record, it redistributes no attribute
value, and it is still sufficient to prove the property the README claims. The
SKU list is different -- those are bare identifiers, carry no catalog content,
and are published so the generator can refuse to mint a code that collides
with a real archived one.

Run against a local copy of the derived statistics::

    python scripts/build_reference_fingerprints.py \\
        /tmp/industrial-reference-2026-09-16/stats
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = (
    REPO_ROOT / "src" / "synthetic_ecommerce_data" / "data" / "reference_fingerprints.json"
)


def tuple_fingerprint(attributes: dict[str, Any]) -> str:
    """A stable hash of a full attribute tuple.

    Sorted (name, value) pairs, so the fingerprint does not depend on the
    order a source happened to serialise them in. ``sku`` is excluded: two
    records with identical attributes under different SKUs are the same
    compilation entry, and it is the tuple the guarantee is about.
    """
    pairs = sorted(
        (str(name), str(value)) for name, value in attributes.items() if name not in ("sku", "SKU")
    )
    canonical = json.dumps(pairs, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _walk(node: Any, found: list[dict], skus: set[str]) -> None:
    if isinstance(node, dict):
        attributes = node.get("attributes_verbatim")
        if isinstance(attributes, dict) and attributes:
            found.append(attributes)
        for key in ("sku", "product_sku"):
            value = node.get(key)
            if isinstance(value, str) and value:
                skus.add(value)
        for key in ("example_skus", "image_skus"):
            value = node.get(key)
            if isinstance(value, list):
                skus.update(str(v) for v in value if isinstance(v, str))
        for value in node.values():
            _walk(value, found, skus)
    elif isinstance(node, list):
        for value in node:
            _walk(value, found, skus)


def build(stats_dir: Path) -> dict:
    found: list[dict] = []
    skus: set[str] = set()
    files = sorted(stats_dir.glob("*.json"))
    if not files:
        raise SystemExit(f"no statistics files under {stats_dir}")
    for path in files:
        _walk(json.loads(path.read_text(encoding="utf-8")), found, skus)

    # The bundled fixtures in records.py are reference records too, and the
    # live test compares against them directly; their hashes go in as well so
    # the two checks cannot drift apart.
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from synthetic_ecommerce_data.domains.industrial.records import FIXTURES  # noqa: PLC0415

    for record in FIXTURES.values():
        found.append(record)
        skus.add(str(record["sku"]))

    fingerprints = sorted({tuple_fingerprint(attributes) for attributes in found})

    # The joint dimension tuples are a second, narrower compilation: the
    # observed (milling dia, length of cut, overall length, shank) combinations.
    dimension_hashes: set[str] = set()
    joint = stats_dir / "02_joint_combinations.json"
    if joint.exists():
        data = json.loads(joint.read_text(encoding="utf-8"))
        for row in data.get("complete_tuples", []):
            values = [
                str(row.get("milling_dia", "")),
                str(row.get("length_of_cut", "")),
                str(row.get("overall_length", "")),
                str(row.get("shank_dia", "")),
            ]
            canonical = json.dumps(values, separators=(",", ":"), ensure_ascii=False)
            dimension_hashes.add(hashlib.sha256(canonical.encode("utf-8")).hexdigest())

    return {
        "_what_this_is": (
            "Hashes of reference-record attribute tuples, and the bare SKU codes those "
            "records were published under. The reference corpus itself never ships; a "
            "hash cannot be read back into a record, so this file enforces the "
            "non-copying guarantee without redistributing anything."
        ),
        "_method": (
            "sha256 over a canonical JSON of the sorted (name, value) pairs of a "
            "record's full attribute set, excluding the sku field."
        ),
        "_source": "derived statistics of archived catalog pages, plus records.FIXTURES",
        "n_reference_records": len(found),
        "n_distinct_tuple_hashes": len(fingerprints),
        "n_reference_skus": len(skus),
        "n_dimension_tuple_hashes": len(dimension_hashes),
        "tuple_hashes": fingerprints,
        "dimension_tuple_hashes": sorted(dimension_hashes),
        "skus": sorted(skus),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    payload = build(Path(argv[1]))
    OUT_PATH.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"{OUT_PATH}: {payload['n_distinct_tuple_hashes']} tuple hashes from "
        f"{payload['n_reference_records']} reference records, "
        f"{payload['n_reference_skus']} skus, "
        f"{payload['n_dimension_tuple_hashes']} dimension tuples"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
