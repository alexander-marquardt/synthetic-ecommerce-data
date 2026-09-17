"""``golden-catalog/`` must be exactly what ``sip-generate build`` writes today.

The build output is committed so that a change to the generator shows up as a
readable diff in review, and so that the catalog can be read without running
anything. That is also why these files are plain NDJSON rather than a gzip or
an LFS pointer, both of which would hide exactly the diff that is the point.
16.7 MiB in the tree occupies 741 KiB in the pack.

Committed output rots the moment nobody checks it, so this is the gate. The
generator is deterministic -- one seed, one catalog, byte for byte -- so the
test is a straight regeneration into a temporary directory and a sha256 per
file. The comparison is per FILE, and the failure names the file and the line
counts, because a whole-file diff of an 11 MB NDJSON tells a reader nothing.

Two very different things make this test red, and the failure message says so:
an intentional generator change (regenerate and commit; expected, for instance,
when issue #5 gives each product line its own drawing and every ``image_id``
moves) versus genuine nondeterminism (a real bug: the same seed is supposed to
produce the same bytes twice).

The headline invariants are asserted separately, against the COMMITTED files
rather than the fresh build, so that regenerating from a broken generator and
committing the result is still red instead of quietly agreeing with itself.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from prism_synthetic_industrial import FIELD_MAP_PATH
from synthetic_industrial_products.catalog import cli
from synthetic_industrial_products.catalog.config import GeneratorConfig

#: Where the committed build output lives, relative to the repository root.
GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden-catalog"

#: The exact command a contributor runs to update it.
REBUILD = "uv run sip-generate build --out golden-catalog"

#: Everything ``build`` writes. Asserted as a set against the directory, so a
#: new output file that nobody committed is red rather than invisible.
GOLDEN_FILES = (
    "flat.jsonl",
    "nested.jsonl",
    "render.jsonl",
    "images.jsonl",
    "mapping.flat.json",
    "mapping.nested.json",
    "stats.json",
)

LINES = 500
SKUS = 4624


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


@pytest.fixture(scope="module")
def fresh_build(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """One full ``sip-generate build`` at the default configuration.

    Module-scoped: the build is a couple of seconds, and running it once per
    parametrised file would multiply that by seven for no extra signal. Not
    marked slow and not skipped by default -- a golden test that does not run
    reads as coverage while asserting nothing.

    ``build`` also rewrites the committed PRISM field map in the SOURCE tree
    (see ``catalog.cli._write_field_map``), which a test has no business
    leaving behind. The bytes are snapshotted and put back unconditionally,
    and then asserted unchanged: the build is supposed to be idempotent
    against a checkout that is already up to date, and if it is not, that is
    the same drift ``tests/test_prism_field_map_drift.py`` exists to catch.
    """
    out = tmp_path_factory.mktemp("golden")
    before = FIELD_MAP_PATH.read_bytes()
    try:
        code = cli.main(["build", "--out", str(out)])
    finally:
        after = FIELD_MAP_PATH.read_bytes()
        FIELD_MAP_PATH.write_bytes(before)
    assert code == 0, "sip-generate build failed; its own audits print to stderr"
    assert after == before, (
        f"{FIELD_MAP_PATH} is not up to date with the generator -- a build "
        f"rewrote it. Run `{REBUILD}` and commit the field map too."
    )
    return out


def test_golden_directory_holds_exactly_the_build_output(fresh_build: Path) -> None:
    """Neither side may carry a file the other does not.

    A file the generator started writing and nobody committed would otherwise
    never be compared by the hash test below, because that test iterates the
    names this module knows about.
    """
    written = {path.name for path in fresh_build.iterdir()}
    committed = {path.name for path in GOLDEN_DIR.iterdir()}
    assert written == set(GOLDEN_FILES), (
        f"sip-generate build writes {sorted(written)}, but this test checks "
        f"{sorted(GOLDEN_FILES)}. Add the new file to GOLDEN_FILES, commit it "
        f"under {GOLDEN_DIR.name}/, and describe it in the README."
    )
    assert committed == set(GOLDEN_FILES), (
        f"{GOLDEN_DIR} holds {sorted(committed)}, expected {sorted(GOLDEN_FILES)}. "
        f"Regenerate with `{REBUILD}`."
    )


@pytest.mark.parametrize("name", GOLDEN_FILES)
def test_committed_file_matches_a_fresh_build(name: str, fresh_build: Path) -> None:
    committed = GOLDEN_DIR / name
    rebuilt = fresh_build / name
    assert committed.exists(), f"{committed} is missing. Regenerate with `{REBUILD}`."

    if _sha256(committed) == _sha256(rebuilt):
        return

    committed_lines = committed.read_text(encoding="utf-8").splitlines()
    rebuilt_lines = rebuilt.read_text(encoding="utf-8").splitlines()
    differing = sum(
        1 for a, b in zip(committed_lines, rebuilt_lines, strict=False) if a != b
    ) + abs(len(committed_lines) - len(rebuilt_lines))
    first = next(
        (
            i
            for i, (a, b) in enumerate(zip(committed_lines, rebuilt_lines, strict=False))
            if a != b
        ),
        min(len(committed_lines), len(rebuilt_lines)),
    )

    # A record is a single 2.5 KB line, so quoting it from the start shows two
    # identical prefixes and hides the change. Window on the first differing
    # CHARACTER instead -- that is the byte the reader came here to see.
    a = committed_lines[first] if first < len(committed_lines) else ""
    b = rebuilt_lines[first] if first < len(rebuilt_lines) else ""
    column = next(
        (i for i, (x, y) in enumerate(zip(a, b, strict=False)) if x != y), min(len(a), len(b))
    )
    start = max(0, column - 60)

    def excerpt(lines: list[str]) -> str:
        if first >= len(lines):
            return "<EOF>"
        window = lines[first][start : column + 120]
        return ("…" if start else "") + window + ("…" if column + 120 < len(lines[first]) else "")

    pytest.fail(
        f"{GOLDEN_DIR.name}/{name} differs from a fresh `sip-generate build`.\n"
        f"  committed {len(committed_lines)} lines, rebuilt {len(rebuilt_lines)} lines; "
        f"{differing} line(s) differ, first at line {first + 1} character {column + 1}:\n"
        f"    committed: {excerpt(committed_lines)}\n"
        f"    rebuilt  : {excerpt(rebuilt_lines)}\n"
        f"\n"
        f"Two things cause this, and they are not the same problem:\n"
        f"\n"
        f"  1. YOU CHANGED THE GENERATOR. Expected, and the fix is one command:\n"
        f"         {REBUILD}\n"
        f"     then commit the changed files. The diff is the review artifact --\n"
        f"     that is why these are plain NDJSON. Issue #5 (a distinct drawing\n"
        f"     per product line) will move every image_id and is exactly this\n"
        f"     case: regenerate, commit, and the diff shows what moved.\n"
        f"\n"
        f"  2. THE GENERATOR IS NONDETERMINISTIC. A bug. One seed is supposed to\n"
        f"     produce one catalog byte for byte.\n"
        f"\n"
        f"Tell them apart by building twice into two fresh directories and\n"
        f"diffing THOSE against each other, with no edits in between:\n"
        f"    uv run sip-generate build --out /tmp/a && uv run sip-generate build --out /tmp/b\n"
        f"    diff -rq /tmp/a /tmp/b\n"
        f"Clean means case 1 -- regenerate and commit. Any difference means case\n"
        f"2, and the golden files must NOT be updated: find the unseeded source\n"
        f"of randomness (an unsorted set or dict iteration, a timestamp, a\n"
        f"hash-ordered key, a float formatted from an unstable accumulation) "
        f"first."
    )


# --------------------------------------------------------------------------
# Headline invariants, asserted against the COMMITTED files.
#
# Deliberately not derived from the fresh build: if these read the same bytes
# the hash test just compared, they would agree with whatever was committed,
# and a careless `sip-generate build && git commit -a` from a broken generator
# would sail through. These are the numbers a reader of the README is entitled
# to rely on, stated independently of the generator that produced them.
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def flat_docs() -> list[dict]:
    return _read_jsonl(GOLDEN_DIR / "flat.jsonl")


@pytest.fixture(scope="module")
def nested_docs() -> list[dict]:
    return _read_jsonl(GOLDEN_DIR / "nested.jsonl")


def test_flat_holds_one_document_per_sku(flat_docs: list[dict]) -> None:
    assert len(flat_docs) == SKUS, (
        f"golden-catalog/flat.jsonl carries {len(flat_docs)} documents, expected {SKUS}"
    )
    skus = {doc["sku"] for doc in flat_docs}
    assert len(skus) == SKUS, (
        f"{SKUS} documents but only {len(skus)} distinct sku values -- the flat "
        f"shape is one document per SKU, so a duplicate is a collision the "
        f"non-copying audit should have refused to write"
    )


def test_flat_covers_exactly_the_product_lines(flat_docs: list[dict]) -> None:
    product_ids = {doc["product_id"] for doc in flat_docs}
    assert len(product_ids) == LINES, (
        f"golden-catalog/flat.jsonl spans {len(product_ids)} distinct product_id "
        f"values, expected {LINES}"
    )


@pytest.mark.parametrize("field", ["image_url", "image_detail_url"])
def test_every_flat_document_carries_an_image_url(flat_docs: list[dict], field: str) -> None:
    """Non-EMPTY, not merely present.

    A card whose ``image_url`` is ``""`` renders the same blank tile as one
    with no key at all, and ``"image_url" in doc`` passes for both. The two
    profiles are asserted separately because a detail view reads only the
    second one, and a demo can look fine on the grid and break on click.
    """
    missing = [doc["sku"] for doc in flat_docs if not doc.get(field)]
    assert not missing, (
        f"{len(missing)} flat document(s) carry no {field}: {missing[:5]}. "
        f"Every product and variant points at one of the generic drawings."
    )


@pytest.mark.parametrize("field", ["image_url", "image_detail_url"])
def test_every_nested_line_and_variant_carries_an_image_url(
    nested_docs: list[dict], field: str
) -> None:
    lines = [doc["product_id"] for doc in nested_docs if not doc.get(field)]
    variants = [
        variant["sku"]
        for doc in nested_docs
        for variant in doc["variants"]
        if not variant.get(field)
    ]
    assert not lines, f"{len(lines)} nested product line(s) carry no {field}: {lines[:5]}"
    assert not variants, f"{len(variants)} nested variant(s) carry no {field}: {variants[:5]}"


def test_nested_lines_account_for_every_sku(nested_docs: list[dict]) -> None:
    """The two shapes are two serialisations of ONE catalog.

    ``variant_count`` is asserted against the array it counts as well as
    against the total, because a stale count field is a number the consumer
    displays without ever opening the array.
    """
    assert len(nested_docs) == LINES, (
        f"golden-catalog/nested.jsonl carries {len(nested_docs)} product lines, expected {LINES}"
    )
    total = sum(len(doc["variants"]) for doc in nested_docs)
    assert total == SKUS, (
        f"nested variant counts sum to {total}, expected {SKUS} -- the nested and "
        f"flat shapes are the same catalog and must describe the same SKUs"
    )
    disagreeing = [
        doc["product_id"] for doc in nested_docs if doc["variant_count"] != len(doc["variants"])
    ]
    assert not disagreeing, (
        f"{len(disagreeing)} product line(s) publish a variant_count that "
        f"disagrees with their own variants array: {disagreeing[:5]}"
    )


def test_the_two_shapes_describe_the_same_skus(
    flat_docs: list[dict], nested_docs: list[dict]
) -> None:
    flat_skus = {doc["sku"] for doc in flat_docs}
    nested_skus = {variant["sku"] for doc in nested_docs for variant in doc["variants"]}
    assert flat_skus == nested_skus, (
        f"{len(flat_skus - nested_skus)} SKU(s) appear only in flat.jsonl and "
        f"{len(nested_skus - flat_skus)} only in nested.jsonl"
    )


def test_stats_reports_the_catalog_that_was_committed() -> None:
    """``stats.json`` is what a reader trusts without opening 11 MB of NDJSON."""
    stats = json.loads((GOLDEN_DIR / "stats.json").read_text(encoding="utf-8"))
    assert stats["lines"] == LINES
    assert stats["skus"] == SKUS
    assert stats["config"] == {
        "seed": GeneratorConfig.seed,
        "lines": GeneratorConfig.lines,
        "skus_per_line": list(GeneratorConfig.skus_per_line),
        "sparsity_scale": GeneratorConfig.sparsity_scale,
        "defect_scale": GeneratorConfig.defect_scale,
    }, (
        "the golden catalog is the DEFAULT configuration -- a catalog built with "
        f"--lines/--seed/--sparsity/--defects is a different catalog. Rebuild with `{REBUILD}`."
    )
    audit = stats["noncopy_audit"]
    assert not audit["full_tuple_collisions"], (
        f"{len(audit['full_tuple_collisions'])} generated records reproduce a "
        f"reference tuple in full; this repository's promise is that none do"
    )
    assert not audit["sku_collisions"], (
        f"{len(audit['sku_collisions'])} generated SKUs collide with a reference SKU"
    )
