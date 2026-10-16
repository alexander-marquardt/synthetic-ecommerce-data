"""Womens sizes above UK 16 (gen#434): the red commit's stub, which extends nothing."""

from __future__ import annotations

import zlib

LEAVES = frozenset({"Dresses", "Tops", "Trousers", "Jeans", "Knitwear"})
TOP = 24
SHARE = (3, 5)


def chosen(rec: dict) -> bool:
    path = rec.get("category_path", [])
    if len(path) < 2 or path[0] != "Womens" or path[1] not in LEAVES:
        return False
    return zlib.crc32(rec["product_id"].encode()) % SHARE[1] < SHARE[0]


def extend(rec: dict) -> dict:
    return rec


def extend_all(recs: list[dict], skip: frozenset[str] = frozenset()) -> list[dict]:
    return [extend(r) if chosen(r) and r["product_id"] not in skip else r for r in recs]
