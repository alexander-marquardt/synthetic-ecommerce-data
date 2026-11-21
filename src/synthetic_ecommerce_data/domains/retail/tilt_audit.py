"""The build report's tilt audit: what the retail build draws turned, and a turn it refuses (#1101).

The maintainer, 2026-11-21, from a demo screenshot of a tilted sofa: "Can you have the generator
do a sanity check on what it is tilting?" Each wrong tilt had been found by a person looking at
served images, one class at a time (#1049, #1095). :func:`audit` reads every product's drawn
angle, :func:`.orientation.drawn_angle`, the one the image is rendered at, and reports:

* ``per_category``: for each category path, how many products it holds and how many are turned;
* ``largest_turned``: the :data:`LARGEST` turned products with the largest stated height or
  length (:func:`.orientation.stated_cm`), largest first, then those that state none;
* ``refused``: each turned product in a :data:`.orientation.NEVER_TILT` category or stating a
  size over :data:`.orientation.MAX_TILT_CM`. The build fails when it is not empty
  (:func:`.scale.main`).

The check reads the category and the size itself rather than :func:`.orientation.level_because`,
so a change that weakens that guard turns a sofa and fails the build, instead of passing its own
test.
"""

from __future__ import annotations

import collections
from collections.abc import Iterable
from typing import Any

from synthetic_ecommerce_data.domains.retail import orientation

#: How many of the largest turned products the report lists.
LARGEST = 20


def _row(rec: dict[str, Any], angle: int, cm: float | None) -> dict[str, Any]:
    return {
        "product_id": rec["product_id"],
        "title": rec["title"],
        "category": " > ".join(rec["category_path"]),
        "shape": rec["drawing"]["shape"],
        "angle": angle,
        "stated_cm": cm,
    }


def _never_tilt(rec: dict[str, Any]) -> bool:
    path = tuple(rec["category_path"])
    return any(path[: len(prefix)] == prefix for prefix in orientation.NEVER_TILT)


def audit(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """The tilt section of the build report over product ``records`` (see the module docstring)."""
    counts: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    turned: list[dict[str, Any]] = []
    refused: list[dict[str, Any]] = []
    for rec in records:
        angle = orientation.drawn_angle(rec)
        count = counts[" > ".join(rec["category_path"])]
        count[0] += 1
        if not angle:
            continue
        count[1] += 1
        cm = orientation.stated_cm(rec)
        row = _row(rec, angle, cm)
        turned.append(row)
        oversize = cm is not None and cm > orientation.MAX_TILT_CM
        why = [w for w, hit in (("category", _never_tilt(rec)), ("size", oversize)) if hit]
        if why:
            refused.append(row | {"because": why})
    largest = sorted(
        turned, key=lambda r: (r["stated_cm"] is None, -(r["stated_cm"] or 0), r["product_id"])
    )[:LARGEST]
    return {
        "products": sum(c[0] for c in counts.values()),
        "turned": len(turned),
        "per_category": {k: {"products": c[0], "turned": c[1]} for k, c in sorted(counts.items())},
        "largest_turned": largest,
        "refused": refused,
    }


def refusals(section: dict[str, Any]) -> list[str]:
    """One line per product the audit ``section`` refuses, for the build's stderr."""
    return [
        f"tilt refused ({', '.join(r['because'])}): {r['product_id']} {r['title']!r} "
        f"[{r['category']}] shape {r['shape']} turned {r['angle']} degrees, "
        f"stated {r['stated_cm']} cm (#1101)"
        for r in section["refused"]
    ]
