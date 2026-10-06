"""Two builds of one seed and commit must be byte-identical.

    uv run python scripts/check_determinism.py                  # the default ~10K catalog
    uv run python scripts/check_determinism.py --lines 39000    # the ~100K catalog
    uv run python scripts/check_determinism.py --images         # the drawings bundle too

elastic/prism-industrial-products#129 requires that the 100K build is
deterministic, verified by two builds with identical digests. This script is
that check. It runs ``sip-generate build`` twice, each in a FRESH interpreter
with a different ``PYTHONHASHSEED``, so a set or dict iteration order that leaks
into the output shows up as a differing file. Then it compares the sha256 of
every file either build wrote. With ``--images`` it also builds the drawings
archive from each build and compares the archives' content digests.

Exit 0 and ``DETERMINISTIC`` when every file matches; exit 1 and the differing
files otherwise. ``tests/test_determinism_check.py`` runs it at a small size.

At the DEFAULT config ``build`` also writes the PRISM field map into the source
tree, outside ``--out`` (``_write_field_map``). Each build's copy is taken right
after it runs and compared like any other file. A build that leaves an expected
file missing, in either build, is refused: an empty comparison proves nothing.

What this proves: the output does not depend on the seed-independent sources of
order (hash seed, set iteration) on one machine. It cannot see a date-only
timestamp, filesystem listing order, locale or timezone, or the zlib build.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path

from synthetic_industrial_products.catalog.cli import field_map_target
from synthetic_industrial_products.catalog.generate import GeneratorConfig

#: Two different hash seeds: the point is that the output must not depend on it.
HASH_SEEDS = ("1", "987")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def digests(directory: Path) -> dict[str, str]:
    """sha256 of every file under ``directory``, keyed by its relative path."""
    return {
        str(path.relative_to(directory)): _sha256(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def compare(left: Path, right: Path) -> list[str]:
    """The files that differ between two build directories, or that only one holds."""
    a, b = digests(left), digests(right)
    return sorted(name for name in a.keys() | b.keys() if a.get(name) != b.get(name))


#: What ``sip-generate build`` writes into ``--out``, and what ``images --archive`` adds.
CATALOG_FILES = (
    "nested.jsonl",
    "flat.jsonl",
    "images.jsonl",
    "render.jsonl",
    "stats.json",
    "mapping.nested.json",
    "mapping.flat.json",
)
ARCHIVE_FILES = ("images.tar.gz", "images.tar.gz.sha256", "images.tar.gz.content-sha256")
FIELD_MAP_COPY = "field_map.yaml"


def expected_files(*, default_config: bool, images: bool, field_map: bool) -> set[str]:
    """Every file the configured build must leave under its label directory."""
    names = {f"catalog/{name}" for name in CATALOG_FILES}
    if default_config and field_map:
        names.add(FIELD_MAP_COPY)
    if images:
        names |= {f"images/{name}" for name in ARCHIVE_FILES}
    return names


def missing(found: dict[str, str], expected: set[str]) -> list[str]:
    return sorted(expected - found.keys())


def _sip_generate(args: list[str], hash_seed: str) -> None:
    env = {**os.environ, "PYTHONHASHSEED": hash_seed}
    code = (
        "import sys; from synthetic_industrial_products.catalog.cli import main; "
        "sys.exit(main(sys.argv[1:]))"
    )
    done = subprocess.run(
        [sys.executable, "-c", code, *args], env=env, capture_output=True, text=True
    )
    if done.returncode != 0:
        raise SystemExit(
            f"sip-generate {' '.join(args)} failed ({done.returncode}):\n"
            f"{done.stdout}{done.stderr}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lines", type=int, help="the size knob (default: the generator's)")
    parser.add_argument("--seed", type=int, help="the seed (default: the generator's)")
    parser.add_argument("--images", action="store_true", help="also compare the drawings bundle")
    args = parser.parse_args(argv)

    build_args = []
    if args.lines is not None:
        build_args += ["--lines", str(args.lines)]
    if args.seed is not None:
        build_args += ["--seed", str(args.seed)]

    # The generator writes the field map only for its default config, and only
    # where the customization package is present.
    default_config = (
        args.lines in (None, GeneratorConfig.lines) and args.seed in (None, GeneratorConfig.seed)
    )
    target = field_map_target()
    want_field_map = default_config and target.parent.exists()
    expected = expected_files(
        default_config=default_config, images=args.images, field_map=want_field_map
    )

    with tempfile.TemporaryDirectory(prefix="sip-determinism-") as tmp:
        root = Path(tmp)
        builds = []
        for label, hash_seed in zip("ab", HASH_SEEDS, strict=True):
            out = root / label / "catalog"
            _sip_generate(["build", "--out", str(out), *build_args], hash_seed)
            # The next build overwrites this file, so copy it out now.
            if want_field_map and target.is_file():
                shutil.copyfile(target, root / label / FIELD_MAP_COPY)
            if args.images:
                images = root / label / "images"
                _sip_generate(
                    [
                        "images",
                        "--catalog",
                        str(out),
                        "--out",
                        str(root / label / "images-files"),
                        "--archive",
                        str(images / "images.tar.gz"),
                    ],
                    hash_seed,
                )
            builds.append(root / label)
        # The unpacked drawings are compared through the archive's content
        # digest file; comparing ~100K SVGs one by one says nothing more.
        left, right = builds
        for side in builds:
            files = side / "images-files"
            if files.exists():
                for path in sorted(files.rglob("*"), reverse=True):
                    path.unlink() if path.is_file() else path.rmdir()
                files.rmdir()
        a, b = digests(left), digests(right)
        differing = compare(left, right)
        absent = {side.name: missing(digests(side), expected) for side in builds}
        for name in sorted(a.keys() | b.keys()):
            verdict = "DIFFERS" if name in differing else "same"
            print(f"{name:<40} {verdict} {a.get(name, '-')[:16]} {b.get(name, '-')[:16]}")
    size = f"--lines {args.lines}" if args.lines is not None else "default --lines"
    if any(absent.values()):
        print(f"NOT DETERMINISTIC ({size}): expected files missing: {absent}")
        return 1
    if differing:
        print(f"NOT DETERMINISTIC ({size}): {len(differing)} file(s) differ: {differing}")
        return 1
    print(f"DETERMINISTIC ({size}): {len(a)} files byte-identical across two builds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
