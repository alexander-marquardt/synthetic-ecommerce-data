"""The 14 cohort shoppers of the combined demo and their seeded purchases (gen#1131). Stub."""

from __future__ import annotations

import argparse
from pathlib import Path

DATE = "2026-11-22"


def texts(date: str = DATE) -> tuple[str, str]:
    return "users: []\n", "users: []\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--date", default=DATE)
    args = ap.parse_args(argv)
    users = args.out / "users"
    users.mkdir(parents=True, exist_ok=True)
    profiles, purchases = texts(args.date)
    (users / f"profiles_{args.date}.yaml").write_text(profiles, encoding="utf-8")
    (users / "purchases.yaml").write_text(purchases, encoding="utf-8")
    return 0
