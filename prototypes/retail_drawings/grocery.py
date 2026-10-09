"""The grocery catalog (gen#154): stub, the build lands in the next commit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import kit_grocery  # noqa: E402,F401 -- registers bar and bag
from grocery_rows import FAMILIES  # noqa: E402,F401

TARGET = 10_000


def build(skus: int = TARGET, seed: int = 0) -> list[dict]:
    return []


def documents(recs: list[dict]) -> list[dict[str, Any]]:
    return []


def flat(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return []


def main(argv: list[str] | None = None) -> int:
    print(json.dumps({"styles": 0, "skus": 0, "standard_problems": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
