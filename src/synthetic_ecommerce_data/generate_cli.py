"""Generate a catalog from the command line.

    ecom-generate build --out out/catalog --lines 400
    ecom-generate report --lines 400
    ecom-generate build --lines 600 --sparsity 0.6 --defects 2.0
    ecom-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz
    ecom-generate block shim_stock_precision
    ecom-generate compose --domain industrial=out/catalog --domain retail=out/retail --out out/all

``build`` builds one product type at a time: it builds a type, audits it, writes its lines and
drops it before it builds the next, so its peak grows with the largest type and not with the
catalog (gen#952). It writes into a temporary directory beside ``--out`` and moves the files into
``--out`` only once the image, product and non-copying audits have all passed: a refused build
writes nothing to ``--out`` (exit 1, ``--out`` untouched: gen#253). When all pass it writes:

``nested.jsonl``
    parent documents with nested SKUs and nested key-value attributes
``flat.jsonl``
    one document per SKU with the line's attributes denormalised onto it
``images.jsonl``
    one row per SKU image: its path in the bundle, its URL, and the sha256 of
    its bytes -- the drawings themselves are never written by ``build`` and
    never committed
``stats.json``
    what was generated, measured against the statistics it reproduces, and
    under ``figures`` the counts and the facet rule's figures that docs and
    tests point at rather than restate (#103)

``compose`` writes the named domains' builds as ONE catalog and its provenance, refusing a
union the output standard refuses (:mod:`synthetic_ecommerce_data.compose`, gen#125).

``block`` prints the part-number block a new type's key derives and, when
another type already uses it, the first free block to declare instead.

``images`` rebuilds every SKU's drawing from a committed catalog, refuses
unless each matches its recorded sha256, and writes the files and a
deterministic archive -- the bundle a customization pins and fetches.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from collections.abc import Iterable, Iterator
from contextlib import ExitStack
from dataclasses import asdict
from pathlib import Path
from typing import Any

from synthetic_ecommerce_data import stress
from synthetic_ecommerce_data.core import emit, letter_case, noncopy, typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.model import Catalog
from synthetic_ecommerce_data.domains.industrial.breadth import SPEC_QUALITY
from synthetic_ecommerce_data.domains.industrial.generate import all_type_keys, iter_types
from synthetic_ecommerce_data.domains.industrial.measure import Measurement
from synthetic_ecommerce_data.domains.industrial.product_split import distribution_problems


def _check_images(catalog, referenced: set[str]) -> list[str]:
    """Every SKU has its OWN image, and every product points at one of its SKUs'.

    Both directions, because each fails differently and silently: a product
    with no reference is a blank card, and two SKUs sharing an id would show
    one variant's drawing for another's dimensions.
    """
    problems: list[str] = []
    skus = [child for _, child in catalog.all_skus()]
    own = {child.image_id for child in skus}
    if len(own) != len(skus):
        problems.append(f"{len(skus)} SKUs share {len(own)} image ids; one SKU, one drawing")
    childless = [child.sku for child in skus if not child.image_id]
    if childless:
        problems.append(f"{len(childless)} variants carry no image: {childless[:5]}")
    unknown = sorted(referenced - own)
    if unknown:
        problems.append(f"{len(unknown)} referenced image ids name no SKU: {unknown[:5]}")
    return problems


def _images(argv: list[str]) -> int:
    from synthetic_ecommerce_data.core import bundle  # noqa: PLC0415

    parser = argparse.ArgumentParser(prog="ecom-generate images")
    parser.add_argument("--catalog", type=Path, default=Path("golden-catalog"))
    parser.add_argument("--out", type=Path, default=Path("out/images"))
    parser.add_argument("--archive", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        files = bundle.rebuild(args.catalog)
    except bundle.BundleMismatchError as exc:
        print(f"image bundle REFUSED: {exc}", file=sys.stderr)
        return 1
    bundle.write_files(files, args.out)
    total = sum(len(data) for _, data in files)
    print(f"{args.out}  {len(files)} drawings, {total:,} bytes, every digest matches the catalog")
    content = bundle.files_digest(files)
    print(f"content digest (pin this) {content}  over {len(files)} files")
    if args.archive is not None:
        digest = bundle.write_archive(files, args.archive)
        args.archive.with_name(args.archive.name + ".sha256").write_text(
            f"{digest}  {args.archive.name}\n", encoding="utf-8"
        )
        args.archive.with_name(args.archive.name + ".content-sha256").write_text(
            f"{content}  {len(files)}\n", encoding="utf-8"
        )
        print(f"{args.archive}  {args.archive.stat().st_size:,} bytes  archive sha256 {digest}")
    return 0


def _config_from(args: argparse.Namespace) -> GeneratorConfig:
    config = GeneratorConfig(seed=args.seed, lines=args.lines)
    if args.sparsity is not None:
        config = config.with_(sparsity_scale=args.sparsity)
    if args.defects is not None:
        config = config.with_(defect_scale=args.defects)
    if args.noise is not None:
        config = config.with_(noise=args.noise)
    return config


def _print_report(stats: dict) -> None:
    print(
        f"lines {stats['lines']}   skus {stats['skus']}   attribute entries "
        f"{stats['total_attribute_entries']}"
    )
    print()
    print(
        f"{'measured property':<52}{'target':>10}{'achieved':>10}{'n':>8}{'denom':>8}{'band':>20}"
    )
    print("-" * 108)
    for row in stats["comparisons"]:
        target = f"{row.target:.4f}" if row.target is not None else "-"
        band = (
            f"{row.band[0]:.3f}-{row.band[1]:.3f} {'ok' if row.within else 'OUT'}"
            if row.band is not None
            else ""
        )
        print(
            f"{row.name:<52}{target:>10}{row.achieved:>10.4f}{row.numerator:>8}{row.denominator:>8}"
            f"{band:>20}"
        )
    print()
    print("lines by type:", json.dumps(stats["lines_by_type"]))
    print("skus by type: ", json.dumps(stats["skus_by_type"]))
    print("skus per product by type:")
    for key, row in stats["skus_per_product_by_type"].items():
        print(
            f"  {key:<34}{row['products']:>6} products  median {row['median']:>3}  max {row['max']}"
        )
    print(
        "products whose SKUs disagree on a product-constant attribute:",
        stats["products_disagreeing_on_a_product_constant"],
    )
    print("measurement-system spellings:", json.dumps(stats["measurement_system_names"]))
    print(
        f"multi-valued attribute: {stats['standards_present']} records carry it, "
        f"{stats['standards_multivalued']} with more than one value, "
        f"{stats['standards_total_values']} values in total"
    )


def round_floats(value: Any) -> Any:
    """Return ``value`` with every float rounded to 6 significant digits.

    The last digits of a float differ between platforms, so a build written on
    one machine would not match a fresh build on another. Six digits keep a
    ratio or spread meaningful and are identical everywhere.
    """
    if isinstance(value, float):
        return float(f"{value:.6g}")
    if isinstance(value, dict):
        return {key: round_floats(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [round_floats(item) for item in value]
    return value


def _serialisable(stats: dict) -> dict:
    out = dict(stats)
    out["comparisons"] = [asdict(row) for row in stats["comparisons"]]
    return out


def field_map_target() -> Path:
    """Where the default-config build writes the PRISM field map (the source tree).

    The climb is relative to this file (``src/synthetic_ecommerce_data/``), so
    it changes whenever the module moves; ``parents[1]`` is ``src/``.
    """
    return (
        Path(__file__).resolve().parents[1]
        / "prism_synthetic_industrial"
        / "data"
        / "field_weights"
        / "synthetic_industrial_flat.yaml"
    )


def _write_field_map(flat_rows: Iterable[dict[str, Any]], config: GeneratorConfig) -> str:
    """Regenerate the committed PRISM field map from the flat documents just written.

    Only for the DEFAULT generator configuration. ``ecom-generate build
    --lines 900`` describes a different catalog, and letting it overwrite the
    committed field map would replace an artifact the drift test checks with
    one derived from a catalog nobody ships -- the test would then pass
    against the wrong thing, which is worse than failing.
    """
    from synthetic_ecommerce_data.prism.field_map import render  # noqa: PLC0415

    target = field_map_target()
    if config != GeneratorConfig():
        return (
            f"{target.name}  NOT rewritten -- the generator config is not the "
            "default, and the committed field map describes the default catalog"
        )
    if not target.parent.exists():
        return f"{target}  NOT rewritten -- the customization package is not present"
    # Replaced, not truncated and rewritten: a reader that has the file open (a test of
    # another xdist worker, an editor) sees the old file whole or the new one whole (#440).
    staged = target.with_name(f"{target.name}.{os.getpid()}.tmp")
    try:
        staged.write_text(render(flat_rows), encoding="utf-8")
        os.replace(staged, target)
    finally:
        staged.unlink(missing_ok=True)
    return f"{target}  field map regenerated from this catalog"


def _measured_figures(out: Path) -> dict[str, Any]:
    """The figures a type moves, measured on the files just written (#103).

    Docs and source point here rather than quote them, so a pull request that
    adds a type changes them only in the ``stats.json`` it regenerates, which
    ``scripts/merge_pr.sh`` rebuilds on a conflict.
    """
    from synthetic_ecommerce_data.prism.derive import (  # noqa: PLC0415
        OvermatchTally,
        dispersion_figures,
    )

    # Each file is read one line at a time and each figure keeps only its own small state:
    # the files as one list of rows were 3.3 GiB of the 39,000-line build's peak (gen#952).
    types: set[str] = set()
    breadth: set[str] = set()
    brands: set[str] = set()
    overmatch = OvermatchTally()

    def tallied() -> Iterator[dict[str, Any]]:
        for doc in _jsonl(out / "flat.jsonl"):
            types.add(doc["product_type"])
            brands.add(doc["brand"])
            if doc.get("spec_quality") == SPEC_QUALITY:
                breadth.add(doc["product_type"])
            overmatch.add(doc)
            yield doc

    dispersion = dispersion_figures(tallied())
    count = total_bytes = 0
    geometry: Counter[str] = Counter()
    largest: dict[str, Any] | None = None
    for image in _jsonl(out / "images.jsonl"):
        count += 1
        total_bytes += image["bytes"]
        geometry[image["geometry"]] += 1
        # Strictly larger: the first of equal keys stays, as ``max`` keeps it.
        if largest is None or (image["bytes"], image["image_id"]) > (
            largest["bytes"],
            largest["image_id"],
        ):
            largest = image
    figures: dict[str, Any] = {
        "catalog": {
            "modelled_types": len(types - breadth),
            "breadth_categories": len(breadth),
            "brands": len(brands),
        },
        "drawings": {
            "count": count,
            "bytes": total_bytes,
            # How many drawings fell down the provenance ladder, by rung.
            "geometry": dict(sorted(geometry.items())),
        },
        "dispersion": dispersion,
        "flat_overmatch": overmatch.figures(),
    }
    if largest is not None:
        figures["drawings"] |= {
            "largest_bytes": largest["bytes"],
            "largest_product_type": largest["product_type"],
        }
    return figures


def _jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """``path``'s rows, parsed one line at a time."""
    with path.open(encoding="utf-8") as lines:
        for line in lines:
            yield json.loads(line)


def _block(argv: list[str]) -> int:
    """Print the part-number block a type should declare, if any (#54)."""
    parser = argparse.ArgumentParser(
        prog="ecom-generate block",
        description="The part-number block a new type's key derives, and whether it is free.",
    )
    parser.add_argument("type_key")
    key = parser.parse_args(argv).type_key
    known = all_type_keys()
    used = {other: typespec.block_of(other) for other in known if other != key}
    derived = typespec.part_number_block(key)
    owners = sorted(other for other, block in used.items() if block == derived)
    if key in known and typespec.block_of(key) != derived:
        print(f"{key}: already declares part_number_block={typespec.block_of(key):04d}")
        return 0
    if not owners:
        print(f"{key}: derived block {derived:04d} is free; leave part_number_block unset")
        return 0
    free = typespec.first_free_block(derived, used.values())
    print(
        f"{key}: derived block {derived:04d} is taken by {', '.join(owners)}; "
        f"declare part_number_block={free:04d}, the first free block after it"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "images":
        return _images(argv[1:])
    if argv and argv[0] == "block":
        return _block(argv[1:])
    if argv and argv[0] == "compose":
        from synthetic_ecommerce_data import compose  # noqa: PLC0415

        return compose.main(argv[1:])
    parser = argparse.ArgumentParser(prog="ecom-generate", description=__doc__)
    parser.add_argument("command", choices=("build", "report"))
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="default out/catalog, or out/stress with --stress-keys",
    )
    parser.add_argument("--seed", type=int, default=GeneratorConfig.seed)
    parser.add_argument("--lines", type=int, default=GeneratorConfig.lines)
    parser.add_argument(
        "--sparsity",
        type=float,
        help="multiplier on every optional attribute's presence rate (1.0 = measured)",
    )
    parser.add_argument(
        "--defects",
        type=float,
        help="multiplier on every defect rate (1.0 = measured, 0.0 = a clean catalog)",
    )
    parser.add_argument(
        "--noise",
        type=float,
        help=(
            "multiplier on every copy-noise rate (1.0 = the realistic default, "
            "0.0 = clean copy; attributes are identical either way)"
        ),
    )
    parser.add_argument(
        "--image-base-url",
        default=emit.DEFAULT_IMAGE_BASE_URL,
        help=(
            "where the image bundle is served; records carry "
            "<base>/<product_type>/<product_id>/<sku>.svg "
            f"(default: {emit.DEFAULT_IMAGE_BASE_URL})"
        ),
    )
    parser.add_argument(
        "--stress-keys",
        type=int,
        default=0,
        help=(
            "build the stress catalog instead (gen#948, docs/stress-catalog.md): about this many "
            "attribute keys, as numbered copies of each product's attributes; 0 (default) = off"
        ),
    )
    parser.add_argument(
        "--stress-copies",
        type=int,
        default=3,
        help="with --stress-keys: at most this many copies of each attribute per product",
    )
    args = parser.parse_args(argv)
    if args.stress_keys < 0 or args.stress_copies < 1:
        parser.error("--stress-keys must be 0 (off) or more, --stress-copies 1 or more")
    if args.stress_keys and args.command != "build":
        parser.error("--stress-keys applies to build only")
    if args.out is None:
        args.out = Path("out/stress" if args.stress_keys else "out/catalog")
    if args.stress_keys and (args.out / "stats.json").exists():
        # The standard catalog's own file: a stress build is never written over one (gen#948).
        parser.error(f"{args.out} holds a standard build; give the stress catalog its own --out")

    config = _config_from(args)
    if args.command == "report":
        counters: dict[str, int] = {}
        measurement = Measurement(config)
        for part in iter_types(config, counters=counters):
            measurement.add(part)
        _print_report(measurement.result(counters))
        return 0
    return _build(args, config)


#: The files the build streams, one type at a time, and the writer each line comes from.
STREAMED = {
    "nested.jsonl": emit.iter_nested,
    "flat.jsonl": emit.iter_flat,
    "images.jsonl": emit.iter_image_manifest,
}


def _image_problems(part: Catalog) -> list[str]:
    """One type's image audit: every SKU points at its own drawing and every product at one of
    its SKUs', and each id has the form ``<type>/<product>/<sku>`` with the product pointing at
    its first variant's (gen#387). An id names its type, so a type audited alone is audited
    against every other: two types cannot share one."""
    problems = _check_images(part, emit.referenced_image_ids(part))
    if problems:
        return problems
    try:
        emit.check_image_ids(part)
    except emit.UnresolvedImageError as error:
        return [str(error)]
    return []


def _merged_audit(total: dict | None, part: dict) -> dict:
    """Two parts' non-copying audits as one: the SKUs checked summed, the collisions joined."""
    if total is None:
        return part
    return {
        key: total[key] + value if key == "n_skus_checked" or isinstance(value, list) else value
        for key, value in part.items()
    }


def _build(args: argparse.Namespace, config: GeneratorConfig) -> int:
    """Build, audit and write one type at a time into a staging directory; move the files into
    ``--out`` once every audit has passed (gen#952, gen#253)."""
    out: Path = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}.", suffix=".building", dir=out.parent))
    try:
        return _build_into(args, config, staging)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _publish(staging: Path, out: Path) -> None:
    """Every audit has passed: only now does anything reach ``--out`` (gen#253). A refused build
    leaves ``--out`` as it was, so ``--out golden-catalog`` never replaces the tracked files with
    a catalog an audit just refused. Each file is renamed into place, beside whatever else
    ``--out`` holds."""
    out.mkdir(parents=True, exist_ok=True)
    for path in sorted(staging.iterdir()):
        os.replace(path, out / path.name)


def _build_into(args: argparse.Namespace, config: GeneratorConfig, staging: Path) -> int:
    out: Path = args.out
    base_url = args.image_base_url
    counters: dict[str, int] = {}
    measurement = Measurement(config)
    audit: dict | None = None
    authored: dict[str, dict[str, str]] = {}
    written: Counter[str] = Counter()
    # The stress catalog spools each type's nested documents and keeps only their keys; it is
    # expanded from the spool once every audit has passed (gen#952).
    stress_keys: set[str] = set()
    names = [stress.SPOOL] if args.stress_keys else list(STREAMED)
    with ExitStack() as files:
        handles = {
            name: files.enter_context((staging / name).open("w", encoding="utf-8"))
            for name in names
        }
        for part in iter_types(config, counters=counters):
            # Every SKU points at its own drawing and every product at one of its SKUs'. Both
            # directions are asserted before the type's lines are written: the writers run the
            # id-form check too, but only on their first ``next()`` (gen#387).
            problems = _image_problems(part)
            if problems:
                for problem in problems:
                    print(f"image audit FAILED: {problem}", file=sys.stderr)
                return 1
            measurement.add(part)
            audit = _merged_audit(audit, noncopy.audit(part))
            authored.update(emit.authored_name_map(part))
            if args.stress_keys:
                stress.spool(emit.iter_nested(part, base_url), handles[stress.SPOOL], stress_keys)
            else:
                for name, rows in STREAMED.items():
                    written[name] += emit.append_jsonl(rows(part, base_url), handles[name])
            # Dropped before the next type is built: the loop name would hold it until then.
            del part
    if audit is None:
        audit = noncopy.audit(Catalog(lines=()))
    stats = measurement.result(counters)

    # A product's SKUs agree on its product-constant attributes, and the SKUs per product
    # follow ``variants_per_product`` (gen#63); a catalog that breaks either is not written.
    split_problems = distribution_problems(stats["skus_per_product_by_type"], config)
    if stats["products_disagreeing_on_a_product_constant"]:
        split_problems.append(
            f"{stats['products_disagreeing_on_a_product_constant']} product(s) have SKUs "
            "that disagree on a product-constant attribute"
        )
    if split_problems:
        for problem in split_problems:
            print(f"product audit FAILED: {problem}", file=sys.stderr)
        return 1
    if audit["full_tuple_collisions"] or audit["sku_collisions"]:
        # Refuse to write a catalog that breaks the repository's own promise.
        print("non-copying audit FAILED:", json.dumps(audit), file=sys.stderr)
        return 1

    if args.stress_keys:
        mappings = {
            "mapping.nested.json": emit.NESTED_MAPPING,
            "mapping.flat.json": emit.FLAT_MAPPING,
        }
        lines = stress.write(staging, stress_keys, args.stress_keys, args.stress_copies, mappings)
        _publish(staging, out)
        print(f"{out}  {lines[0]}")
        for line in lines[1:]:
            print(line)
        return 0

    payload = _serialisable(stats)
    payload["noncopy_audit"] = audit
    payload["config"] = {
        "seed": config.seed,
        "lines": config.lines,
        "variants_per_product": [list(pair) for pair in config.variants_per_product],
        "new_type_products": dict(config.new_type_products),
        "sparsity_scale": config.sparsity_scale,
        "defect_scale": config.defect_scale,
    }
    payload["figures"] = _measured_figures(staging)
    (staging / "stats.json").write_text(
        json.dumps(round_floats(payload), indent=1) + "\n", encoding="utf-8"
    )
    (staging / letter_case.AUTHORED_NAMES_FILE).write_text(
        json.dumps(dict(sorted(authored.items())), indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (staging / "mapping.nested.json").write_text(
        json.dumps(emit.NESTED_MAPPING, indent=1) + "\n", encoding="utf-8"
    )
    (staging / "mapping.flat.json").write_text(
        json.dumps(emit.FLAT_MAPPING, indent=1) + "\n", encoding="utf-8"
    )

    _publish(staging, out)

    # The field map reads the flat documents back one line at a time; it reads no image URL,
    # so the file's base URL is the default's to it.
    field_map = _write_field_map(_jsonl(out / "flat.jsonl"), config)

    print(f"{out}/nested.jsonl  {written['nested.jsonl']} parent documents")
    print(f"{out}/flat.jsonl    {written['flat.jsonl']} sku documents")
    print(f"{out}/images.jsonl  {written['images.jsonl']} SKU drawings, served under {base_url}")
    print(f"{out}/stats.json    measured against target")
    print(field_map)
    print()
    _print_report(stats)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
