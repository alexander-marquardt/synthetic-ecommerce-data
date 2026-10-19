#!/usr/bin/env python3
"""Build the files the repository no longer commits (gen#536).

    uv run python scripts/build_derived.py --out build/derived    # the CI artifact, locally
    python3 scripts/build_derived.py --list                       # the paths it writes

Each path is the one the file used to have in git, under ``--out``: ``golden-retail/stats.json``
(the retail build's measured totals), ``docs/figures.md`` (the same totals as a page),
``docs/retail-apparel-decoys.md`` (the apparel decoy table) and the sneak-peek samples and
previews under ``prototypes/retail_drawings/``. The ``derived`` CI job runs this once per run and
uploads ``--out`` as a workflow artifact; ``scripts/check_no_derived_files.py`` keeps them out of
git, and a test reads a figure with ``retail_figures.figures()``, never from a file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"

#: Every path this script writes, relative to ``--out``. ``tests/test_no_derived_files_536.py``
#: holds this list and ``check_no_derived_files.DERIVED`` to each other.
OUTPUTS: tuple[str, ...] = (
    "golden-retail/stats.json",
    "docs/figures.md",
    "docs/retail-apparel-decoys.md",
    "prototypes/retail_drawings/samples.ndjson",
    "prototypes/retail_drawings/preview.html",
    "prototypes/retail_drawings/samples4.ndjson",
    "prototypes/retail_drawings/preview4.html",
)


def build(out: Path) -> list[str]:
    """Write every output under ``out``; return the paths written."""
    if str(RETAIL) not in sys.path:
        sys.path.insert(0, str(RETAIL))
    import build_preview  # noqa: PLC0415 -- the prototype's own directory is its import root
    import build_preview4  # noqa: PLC0415
    import decoy_apparel  # noqa: PLC0415
    import retail_figures  # noqa: PLC0415

    figures = retail_figures.figures()
    html, ndjson = build_preview.outputs()
    html4, ndjson4 = build_preview4.outputs()
    texts = {
        "golden-retail/stats.json": retail_figures.render(figures),
        "docs/figures.md": retail_figures.markdown(figures),
        "docs/retail-apparel-decoys.md": decoy_apparel.doc_text(),
        "prototypes/retail_drawings/samples.ndjson": ndjson,
        "prototypes/retail_drawings/preview.html": html,
        "prototypes/retail_drawings/samples4.ndjson": ndjson4,
        "prototypes/retail_drawings/preview4.html": html4,
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
