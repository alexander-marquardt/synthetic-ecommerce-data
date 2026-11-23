"""One ``unbranded`` drawing per row of a picture manifest: step 1 of gen#1022, run (gen#1220).

:func:`draw` reads a picture manifest (:mod:`.picture_manifest`) and writes
``OUT_DIR/images/<image id>.svg`` for each row: a :class:`~.picture_manifest.Picture` as its own
type, a :class:`~.picture_manifest.Fallback` as its department's picture. It reads nothing but the
manifest, and imports no product writer. Run it::

    uv run python -m synthetic_ecommerce_data.picture_drawings MANIFEST OUT_DIR

Each file's bytes come from its own row alone, so the same manifest gives the same files. A file
is moved into place whole, so a stopped run leaves no half-written picture, and the next run draws
only the rows that have none. ``OUT_DIR/run.json`` holds what the run was started on (the manifest's
digest, and the renderer's); a directory started on another manifest or renderer is refused, as its
files would be a mix of two sets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data.picture_manifest import (
    COLORS,
    DEPARTMENTS,
    TYPES,
    Fallback,
    Picture,
    load_file,
)

FINISH = "unbranded"
IMAGES = "images"
STAMP = "run.json"
#: The fill a department's picture is drawn in: no product's own color.
FALLBACK_COLOR = COLORS["Grey"]


@dataclass(frozen=True)
class Report:
    """What a run over a manifest left in its directory."""

    rows: int
    #: The pictures in the directory, counted there.
    files: int
    #: Type -> rows drawn as that type.
    own_type: Counter[str]
    #: Department -> rows drawn as that department's picture.
    fallbacks: Counter[str]
    #: Rows this run drew; the rest had a picture from an earlier run.
    drawn: int

    def lines(self) -> list[str]:
        out = [
            f"rows: {self.rows}",
            f"files: {self.files}",
            f"own-type drawings: {self.own_type.total()}",
            f"fallbacks: {self.fallbacks.total()}",
            f"drawn by this run: {self.drawn} (kept from earlier runs: {self.rows - self.drawn})",
        ]
        out += [f"  {t}: {n}" for t, n in sorted(self.own_type.items())]
        out += [f"  fallback {d}: {n}" for d, n in sorted(self.fallbacks.items())]
        return out


def picture(row: Picture | Fallback) -> str:
    """The SVG of one manifest row; its image id is the id the finish is picked by."""
    if isinstance(row, Fallback):
        shape, attributes = DEPARTMENTS[row.department], {"color": FALLBACK_COLOR}
    else:
        shape, attributes = row.type, row.attributes()
    return drawings.render(shape, attributes, FINISH, product_id=row.image_id)


def _renderer() -> str:
    """A digest of how the renderer draws each type and each department now."""
    h = hashlib.sha256()
    shapes = (*TYPES, *DEPARTMENTS.values())
    for shape in shapes:
        h.update(
            drawings.render(shape, {"color": FALLBACK_COLOR}, FINISH, product_id=shape).encode()
        )
    return h.hexdigest()


def _stamp(manifest: Path, out: Path) -> None:
    """Record what ``out`` is drawn from, or refuse a directory started on something else."""
    stamp = {
        "manifest": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "renderer": _renderer(),
    }
    path = out / STAMP
    if path.exists():
        held = json.loads(path.read_text(encoding="utf-8"))
        changed = [k for k in stamp if held.get(k) != stamp[k]]
        if changed:
            raise ValueError(
                f"{out} was started on another {' and '.join(changed)}: draw into a new directory"
            )
        return
    out.mkdir(parents=True, exist_ok=True)
    if any((out / IMAGES).glob("*.svg")):
        raise ValueError(f"{out / IMAGES} holds pictures of no run: draw into a new directory")
    path.write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")


def draw(manifest: Path, out: Path) -> Report:
    """Draw each row of ``manifest`` that has no picture in ``out`` yet, and count what is there."""
    rows = load_file(manifest)
    _stamp(manifest, out)
    images = out / IMAGES
    images.mkdir(exist_ok=True)
    drawn = 0
    for row in rows:
        path = images / f"{row.image_id}.svg"
        if path.exists():
            continue
        part = path.with_suffix(".part")
        part.write_text(picture(row), encoding="utf-8")
        os.replace(part, path)
        drawn += 1
    return Report(
        rows=len(rows),
        files=sum(1 for _ in images.glob("*.svg")),
        own_type=Counter(r.type for r in rows if isinstance(r, Picture)),
        fallbacks=Counter(r.department for r in rows if isinstance(r, Fallback)),
        drawn=drawn,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One unbranded drawing per picture manifest row.")
    parser.add_argument("manifest", type=Path, help="a picture manifest: a JSON list or JSON Lines")
    parser.add_argument("out", type=Path, help="the directory the pictures go in")
    args = parser.parse_args(argv)
    report = draw(args.manifest, args.out)
    print("\n".join(report.lines()))
    return 0 if report.files == report.rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
