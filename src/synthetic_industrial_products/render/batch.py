"""Drawing a whole catalog: one image per product line, at every profile.

Kept here rather than in the script that runs it, because the tests need the
same rendering the publish uses. A test that rendered a catalog its own way
would be checking a pipeline nothing ships -- and the property under test is
exactly "the published drawings differ where the published records differ", so
it has to be measured on the published bytes.

Rendered in worker processes. A thousand figures is about a minute in one
process and a few seconds across the cores this is actually run on, and every
worker returns values rather than sharing state, so the result does not depend
on how the work was split.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from hashlib import blake2b
from pathlib import Path

from . import canvas as cv
from . import generic
from .profiles import PROFILES, Profile

__all__ = ["DEFAULT_WORKERS", "Drawn", "digests", "draw_line", "render_lines"]

#: One worker per core, capped: past this the figures are smaller than the
#: cost of shipping them between processes.
DEFAULT_WORKERS = min(8, os.cpu_count() or 1)


def draw_line(line: dict, facets_by_sku: Mapping[str, Mapping], profile: Profile) -> bytes:
    """One product line's drawing at one profile, as the PNG bytes it publishes.

    ``facets_by_sku`` is ``flat.jsonl``'s ``{sku: facets}``: where the published
    spelling the drawing prints lives (see :func:`.generic.build_line`).
    """
    fig, _ = generic.build_line(line, facets_by_sku, profile)
    return cv.to_bytes(fig, profile)


class Drawn(tuple):
    """One rendered drawing: ``(image_id, profile, digest, size)``."""

    __slots__ = ()

    @property
    def image_id(self) -> str:
        return self[0]

    @property
    def profile(self) -> str:
        return self[1]

    @property
    def digest(self) -> str:
        return self[2]

    @property
    def size(self) -> int:
        return self[3]


def _job(args: tuple[dict, Mapping[str, Mapping], str, str | None]) -> Drawn:
    line, facets_by_sku, profile_name, out_root = args
    data = draw_line(line, facets_by_sku, PROFILES[profile_name])
    if out_root is not None:
        path = Path(out_root) / line["image_id"] / f"{profile_name}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        # Read the size back off the file rather than off the buffer: what is
        # published is the file, and a write that half-succeeded would
        # otherwise report the size it meant to write.
        return Drawn(
            (
                line["image_id"],
                profile_name,
                blake2b(data, digest_size=16).hexdigest(),
                path.stat().st_size,
            )
        )
    return Drawn(
        (line["image_id"], profile_name, blake2b(data, digest_size=16).hexdigest(), len(data))
    )


def render_lines(
    lines: Sequence[dict],
    facets_by_sku: Mapping[str, Mapping],
    out_root: str | Path | None,
    profiles: Sequence[str] = tuple(PROFILES),
    workers: int = DEFAULT_WORKERS,
) -> dict[str, dict[str, Drawn]]:
    """Draw every line at every profile. ``{profile: {image_id: Drawn}}``.

    ``out_root`` of ``None`` renders without writing anything, which is what a
    test comparing drawings wants: the digests are of the same bytes a publish
    would write, because both come from the same buffer.
    """
    root = None if out_root is None else str(out_root)
    # Each job carries only its own line's SKUs, so a worker is not shipped
    # the whole catalog's facets.
    own = [{v["sku"]: facets_by_sku[v["sku"]] for v in line["variants"]} for line in lines]
    jobs = [
        (line, mine, name, root) for name in profiles for line, mine in zip(lines, own, strict=True)
    ]
    out: dict[str, dict[str, Drawn]] = {name: {} for name in profiles}
    if workers > 1 and len(jobs) > workers:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for drawn in pool.map(_job, jobs, chunksize=8):
                out[drawn.profile][drawn.image_id] = drawn
    else:
        for job in jobs:
            drawn = _job(job)
            out[drawn.profile][drawn.image_id] = drawn
    return out


def digests(
    lines: Sequence[dict],
    facets_by_sku: Mapping[str, Mapping],
    profile: str,
    workers: int = DEFAULT_WORKERS,
) -> dict[str, str]:
    """``{image_id: digest}`` for one profile, rendering nothing to disk."""
    drawn = render_lines(lines, facets_by_sku, None, (profile,), workers)[profile]
    return {image_id: one.digest for image_id, one in drawn.items()}
