"""The figures two builds measure, written to one committed file (#85, #103).

A type PR moves what the default build and the 100K build measure: the sizes
the 100K build reaches per type, and the figures the pinned price rows
(:data:`.price.PINNED_SHORTFALLS`) land on. Typed into ``core/price.py`` or the
README, they put every type PR on the same lines, so each conflicted with the
last to merge. The file is build output instead:

* ``default.price_pins`` and ``hundred_k.price_pins``: each pinned row's figure
  on the build, to :func:`.price_report.recorded_digits` places. ``core/price.py``
  reads them as :data:`.price.PINNED_FIGURES`.
* ``hundred_k.lines``, ``skus`` and ``skus_by_type``: the 100K build's size.

``tests/test_price.py`` rebuilds the file from the two builds the suite already
holds and compares it with the committed one, so a figure that moves is red
until the rebuild is committed. ``scripts/merge_pr.sh`` reruns it on the merged
tree and lists the file as generated, so a conflict in it is resolved by the
rebuild, never by hand::

    uv run python -m synthetic_ecommerce_data.domains.industrial.measured_builds
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any

from synthetic_ecommerce_data.core import price
from synthetic_ecommerce_data.core.config import HUNDRED_K_LINES, GeneratorConfig
from synthetic_ecommerce_data.core.model import Catalog
from synthetic_ecommerce_data.domains.industrial import price_report
from synthetic_ecommerce_data.domains.industrial.generate import generate

#: The command that rewrites :data:`.price.BUILDS_FILE` (``scripts/merge_pr.sh`` runs it).
REBUILD = "uv run python -m synthetic_ecommerce_data.domains.industrial.measured_builds"


def _pins(catalog: Catalog) -> dict[str, float | None]:
    """Each pinned row's figure on ``catalog``, as it is recorded: ``None`` for a
    row that lands in band on this build (:func:`.price_report.pin_holds`)."""
    rows = {row.name: row for row in price_report.price_comparisons(catalog)}
    return {
        name: None
        if rows[name].within
        else round(rows[name].achieved, price_report.recorded_digits(name))
        for name in sorted(price.PINNED_SHORTFALLS)
    }


def figures(default: Catalog, hundred_k: Catalog) -> dict[str, Any]:
    """What the file holds, measured on the default and on the 100K build."""
    skus = Counter(line.type_key for line in hundred_k.lines for _ in line.children)
    return {
        "default": {"price_pins": _pins(default)},
        "hundred_k": {
            "lines": len(hundred_k.lines),
            "price_pins": _pins(hundred_k),
            "skus": sum(skus.values()),
            "skus_by_type": dict(sorted(skus.items())),
        },
    }


def render(built: dict[str, Any]) -> str:
    return json.dumps(built, indent=2, sort_keys=True) + "\n"


def main() -> int:
    built = figures(generate(GeneratorConfig()), generate(GeneratorConfig(lines=HUNDRED_K_LINES)))
    price.BUILDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    price.BUILDS_FILE.write_text(render(built), encoding="utf-8")
    print(f"wrote {price.BUILDS_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
