"""Print how many products of a set share a picture, for the figure alone and in each finish.

    uv run python scripts/picture_share_1022.py [ROWS.json]

ROWS.json is a list of ``{"product_id", "type", "attributes", "brand"}`` rows
(``synthetic_ecommerce_data.drawings.picture_share``); it defaults to the fixture of 200
sideboards, ``tests/fixtures/drawings_1022/sideboards_200.json`` (gen#1022, Done-when 6).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from synthetic_ecommerce_data import drawings

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "drawings_1022"
    / "sideboards_200.json"
)


def main(argv: list[str]) -> int:
    path = Path(argv[0]) if argv else FIXTURE
    rows = json.loads(path.read_text())
    types = sorted({r["type"] for r in rows})
    print(f"drawings: {len(rows)} of {', '.join(types)} ({path.name})")
    for name, (shared, total) in drawings.picture_share(rows).items():
        share = f"{100 * shared / total:.1f}%" if shared else "none"
        print(f"{name}: {shared} of {total} share a picture ({share})")
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
