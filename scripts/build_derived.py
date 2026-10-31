#!/usr/bin/env python3
"""Build the files the repository no longer commits (gen#536).

    uv run python scripts/build_derived.py --out build/derived    # the CI artifact, locally
    python3 scripts/build_derived.py --list                       # the paths it writes

Each path is the one the file used to have in git, under ``--out``: ``golden-retail/stats.json``
(the retail build's measured totals), ``docs/figures.md`` (the same totals as a page),
``docs/retail-apparel-decoys.md`` (the apparel decoy table), the sneak-peek samples and previews
under ``domains/retail/``, ``docs/retail-product-word-decoys-table.md`` and
``docs/retail-text-match-decoys-table.md`` (the decoy tables, cut out of their pages in gen#513),
and ``docs/feature-pages.md`` (the index of the features' own pages, gen#513). The ``derived`` CI
job runs this once per run and uploads ``--out`` as a workflow artifact;
``scripts/check_no_derived_files.py`` keeps them out of git, and a test reads a figure with
``retail_figures.figures()``, never from a file.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Every path this script writes, relative to ``--out``. ``tests/test_no_derived_files_536.py``
#: holds this list and ``check_no_derived_files.DERIVED`` to each other.
OUTPUTS: tuple[str, ...] = (
    "golden-retail/stats.json",
    "docs/figures.md",
    "docs/retail-apparel-decoys.md",
    "docs/retail-product-word-decoys-table.md",
    "docs/retail-text-match-decoys-table.md",
    "docs/feature-pages.md",
    "src/synthetic_ecommerce_data/domains/retail/samples.ndjson",
    "src/synthetic_ecommerce_data/domains/retail/preview.html",
    "src/synthetic_ecommerce_data/domains/retail/samples4.ndjson",
    "src/synthetic_ecommerce_data/domains/retail/preview4.html",
)

#: The built index of the features' own pages.
FEATURE_PAGES = "docs/feature-pages.md"
#: The folders under ``docs/`` a feature writes its page in, one file per feature.
FEATURE_PAGE_DIRS: tuple[str, ...] = (
    "retail-prototype",
    "retail-product-word-decoys",
    "industrial-types",
)


def feature_pages(root: Path) -> str:
    """The index page: each feature page under its folder, named by its first heading."""
    lines = ["# Feature pages (built)", "", "Built by `scripts/build_derived.py`."]
    for folder in FEATURE_PAGE_DIRS:
        lines += ["", f"## {folder}", ""]
        for page in sorted((root / "docs" / folder).glob("*.md")):
            text = page.read_text(encoding="utf-8").splitlines()
            title = next((ln.lstrip("# ") for ln in text if ln.startswith("#")), None)
            if title is None:
                raise SystemExit(f"build_derived: docs/{folder}/{page.name} has no heading")
            lines.append(f"- [{title}]({folder}/{page.name})")
    return "\n".join(lines) + "\n"


def build(out: Path) -> list[str]:
    """Write every output under ``out``; return the paths written."""
    from synthetic_ecommerce_data.domains.retail import (
        build_preview,  # noqa: PLC0415
        build_preview4,  # noqa: PLC0415
        decoy_apparel,  # noqa: PLC0415
        decoy_product_words,  # noqa: PLC0415
        decoy_rows,  # noqa: PLC0415
        retail_figures,  # noqa: PLC0415
    )

    figures = retail_figures.figures()
    html, ndjson = build_preview.outputs()
    html4, ndjson4 = build_preview4.outputs()
    texts = {
        "golden-retail/stats.json": retail_figures.render(figures),
        "docs/figures.md": retail_figures.markdown(figures),
        "docs/retail-apparel-decoys.md": decoy_apparel.doc_text(),
        decoy_product_words.TABLE_DOC: decoy_product_words.table_doc(),
        decoy_rows.TABLE_DOC: decoy_rows.table_doc(),
        FEATURE_PAGES: feature_pages(ROOT),
        "src/synthetic_ecommerce_data/domains/retail/samples.ndjson": ndjson,
        "src/synthetic_ecommerce_data/domains/retail/preview.html": html,
        "src/synthetic_ecommerce_data/domains/retail/samples4.ndjson": ndjson4,
        "src/synthetic_ecommerce_data/domains/retail/preview4.html": html4,
    }
    if set(texts) != set(OUTPUTS):
        raise SystemExit("build_derived: OUTPUTS and the built files disagree")
    for name, text in texts.items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return list(OUTPUTS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, default=ROOT / "build" / "derived")
    parser.add_argument("--list", action="store_true", help="print the paths it writes and stop")
    args = parser.parse_args(argv)
    if args.list:
        print("\n".join(OUTPUTS))
        return 0
    for name in build(args.out):
        print(f"wrote {args.out / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
