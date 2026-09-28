"""Generate a catalog from the command line.

    sip-generate build --out out/catalog --lines 400
    sip-generate report --lines 400
    sip-generate build --lines 600 --sparsity 0.6 --defects 2.0
    sip-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz

``build`` writes:

``nested.jsonl``
    parent documents with nested SKUs and nested key-value attributes
``flat.jsonl``
    one document per SKU with the line's attributes denormalised onto it
``render.jsonl``
    the same SKUs in the shape ``sip-render batch`` reads
``images.jsonl``
    one row per SKU image: its path in the bundle, its URL, and the sha256 of
    its bytes -- the drawings themselves are never written by ``build`` and
    never committed
``stats.json``
    what was generated, measured against the statistics it reproduces

``images`` rebuilds every SKU's drawing from a committed catalog, refuses
unless each matches its recorded sha256, and writes the files and a
deterministic archive -- the bundle a customization pins and fetches.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import emit, noncopy
from .config import GeneratorConfig
from .generate import generate
from .measure import measure


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
    from . import bundle  # noqa: PLC0415

    parser = argparse.ArgumentParser(prog="sip-generate images")
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
    if args.archive is not None:
        digest = bundle.write_archive(files, args.archive)
        args.archive.with_name(args.archive.name + ".sha256").write_text(
            f"{digest}  {args.archive.name}\n", encoding="utf-8"
        )
        print(f"{args.archive}  {args.archive.stat().st_size:,} bytes  sha256 {digest}")
    return 0


def _config_from(args: argparse.Namespace) -> GeneratorConfig:
    config = GeneratorConfig(seed=args.seed, lines=args.lines)
    if args.sparsity is not None:
        config = config.with_(sparsity_scale=args.sparsity)
    if args.defects is not None:
        config = config.with_(defect_scale=args.defects)
    return config


def _print_report(stats: dict) -> None:
    print(
        f"lines {stats['lines']}   skus {stats['skus']}   attribute entries "
        f"{stats['total_attribute_entries']}"
    )
    print()
    print(f"{'measured property':<52}{'target':>10}{'achieved':>10}{'n':>8}{'denom':>8}")
    print("-" * 88)
    for row in stats["comparisons"]:
        target = f"{row.target:.4f}" if row.target is not None else "-"
        print(
            f"{row.name:<52}{target:>10}{row.achieved:>10.4f}{row.numerator:>8}{row.denominator:>8}"
        )
    print()
    print("lines by type:", json.dumps(stats["lines_by_type"]))
    print("skus by type: ", json.dumps(stats["skus_by_type"]))
    print("measurement-system spellings:", json.dumps(stats["measurement_system_names"]))
    print(
        f"multi-valued attribute: {stats['standards_present']} records carry it, "
        f"{stats['standards_multivalued']} with more than one value, "
        f"{stats['standards_total_values']} values in total"
    )


def _serialisable(stats: dict) -> dict:
    out = dict(stats)
    out["comparisons"] = [asdict(row) for row in stats["comparisons"]]
    return out


def _write_field_map(catalog, config: GeneratorConfig) -> str:
    """Regenerate the committed PRISM field map from the catalog just built.

    Only for the DEFAULT generator configuration. ``sip-generate build
    --lines 900`` describes a different catalog, and letting it overwrite the
    committed field map would replace an artifact the drift test checks with
    one derived from a catalog nobody ships -- the test would then pass
    against the wrong thing, which is worse than failing.
    """
    from ..prism.field_map import render  # noqa: PLC0415

    target = (
        Path(__file__).resolve().parents[2]
        / "prism_synthetic_industrial"
        / "data"
        / "field_weights"
        / "synthetic_industrial_flat.yaml"
    )
    if config != GeneratorConfig():
        return (
            f"{target.name}  NOT rewritten -- the generator config is not the "
            "default, and the committed field map describes the default catalog"
        )
    if not target.parent.exists():
        return f"{target}  NOT rewritten -- the customization package is not present"
    target.write_text(render(emit.iter_flat(catalog)), encoding="utf-8")
    return f"{target}  field map regenerated from this catalog"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "images":
        return _images(argv[1:])
    parser = argparse.ArgumentParser(prog="sip-generate", description=__doc__)
    parser.add_argument("command", choices=("build", "report"))
    parser.add_argument("--out", type=Path, default=Path("out/catalog"))
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
        "--image-base-url",
        default=emit.DEFAULT_IMAGE_BASE_URL,
        help=(
            "where the image bundle is served; records carry "
            "<base>/<product_type>/<product_id>/<sku>.svg "
            f"(default: {emit.DEFAULT_IMAGE_BASE_URL})"
        ),
    )
    args = parser.parse_args(argv)

    config = _config_from(args)
    catalog = generate(config)
    stats = measure(catalog, config)

    if args.command == "report":
        _print_report(stats)
        return 0

    out = args.out
    base_url = args.image_base_url
    nested = emit.write_jsonl(emit.iter_nested(catalog, base_url), out / "nested.jsonl")
    flat = emit.write_jsonl(emit.iter_flat(catalog, base_url), out / "flat.jsonl")
    images = emit.write_jsonl(emit.iter_image_manifest(catalog, base_url), out / "images.jsonl")

    # Every SKU points at its own drawing and every product at one of its
    # SKUs'. Both directions are asserted before the catalog is written.
    referenced = emit.referenced_image_ids(catalog)
    problems = _check_images(catalog, referenced)
    if problems:
        for problem in problems:
            print(f"image audit FAILED: {problem}", file=sys.stderr)
        return 1
    # render.jsonl is every SKU in the shape ``sip-render batch`` reads.
    render = emit.write_jsonl(emit.render_records(catalog), out / "render.jsonl")

    audit = noncopy.audit(catalog)
    if audit["full_tuple_collisions"] or audit["sku_collisions"]:
        # Refuse to write a catalog that breaks the repository's own promise.
        print("non-copying audit FAILED:", json.dumps(audit), file=sys.stderr)
        return 1

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
    (out / "stats.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    (out / "mapping.nested.json").write_text(
        json.dumps(emit.NESTED_MAPPING, indent=1) + "\n", encoding="utf-8"
    )
    (out / "mapping.flat.json").write_text(
        json.dumps(emit.FLAT_MAPPING, indent=1) + "\n", encoding="utf-8"
    )

    field_map = _write_field_map(catalog, config)

    print(f"{out}/nested.jsonl  {nested} parent documents")
    print(f"{out}/flat.jsonl    {flat} sku documents")
    print(f"{out}/render.jsonl  {render} records for the per-record dimensioned renderer")
    print(f"{out}/images.jsonl  {images} SKU drawings, served under {base_url}")
    print(f"{out}/stats.json    measured against target")
    print(field_map)
    print()
    _print_report(stats)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
