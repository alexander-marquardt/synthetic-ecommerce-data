"""Generate a catalog from the command line.

    sip-generate build --out out/catalog --lines 400
    sip-generate report --lines 400
    sip-generate build --lines 600 --skus 6 24 --sparsity 0.6 --defects 2.0

``build`` writes five files:

``nested.jsonl``
    parent documents with nested SKUs and nested key-value attributes
``flat.jsonl``
    one document per SKU with the line's attributes denormalised onto it
``render.jsonl``
    the same SKUs in the shape ``sip-render batch`` already reads
``images.jsonl``
    one row per distinct image reference: its product type, its path under the
    image base URL, and how many SKUs point at it
``stats.json``
    what was generated, measured against the statistics it reproduces

Records carry ``image_urls`` alongside ``image_skus``. The URL is built from
the image REFERENCE and never from the product's own SKU: the two differ for
roughly three records in four, so building it from the SKU produces a dead
link at that rate. ``--image-base-url`` moves the host.
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


def _config_from(args: argparse.Namespace) -> GeneratorConfig:
    config = GeneratorConfig(seed=args.seed, lines=args.lines)
    if args.skus:
        config = config.with_(skus_per_line=(args.skus[0], args.skus[1]))
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
    parser = argparse.ArgumentParser(prog="sip-generate", description=__doc__)
    parser.add_argument("command", choices=("build", "report"))
    parser.add_argument("--out", type=Path, default=Path("out/catalog"))
    parser.add_argument("--seed", type=int, default=GeneratorConfig.seed)
    parser.add_argument("--lines", type=int, default=GeneratorConfig.lines)
    parser.add_argument("--skus", type=int, nargs=2, metavar=("MIN", "MAX"), help="SKUs per line")
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
            "where the card drawings are published; records carry "
            "<base>/<product_type>/<image_ref>.png "
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
    # Only the records the renderer can dispatch on. It picks a renderer from
    # the attribute NAMES a record carries, and a hammer carries none it knows
    # -- writing those into the batch file would make `sip-render batch` fail
    # on the whole file rather than skip them.
    from ..render import UnknownProductError, renderer_for  # noqa: PLC0415

    def drawable():
        for record in emit.render_records(catalog):
            try:
                renderer_for(record)
            except UnknownProductError:
                continue
            yield record

    render = emit.write_jsonl(drawable(), out / "render.jsonl")

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
        "skus_per_line": list(config.skus_per_line),
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
    print(
        f"{out}/render.jsonl  {render} of {flat} records the renderer can dispatch on "
        f"({flat - render} carry no attribute it recognises)"
    )
    print(f"{out}/images.jsonl  {images} distinct images, published under {base_url}")
    print(f"{out}/stats.json    measured against target")
    print(field_map)
    print()
    _print_report(stats)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
