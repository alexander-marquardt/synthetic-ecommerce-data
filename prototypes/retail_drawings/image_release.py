"""The retail image release (gen#125): stub, the render lands in the next commit."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import export  # noqa: E402


def member_path(image_id: str) -> str:
    return f"{export.IMAGE_ROOT}/{image_id}.svg"


def colorway_drawing(rec: dict, sku: dict) -> dict:
    return rec["drawing"]


def render(rec: dict, sku: dict) -> bytes:
    return b""


def image_files(records: list[dict] | None = None) -> list[tuple[str, bytes]]:
    return []


def main(argv: list[str] | None = None) -> int:
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
