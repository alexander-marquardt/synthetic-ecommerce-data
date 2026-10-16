"""Womens sizes above UK 16 on a share of the Womens clothing (gen#434).

The Womens UK size charts stopped at 16 (some at 18 or 20), so a query for "dress size 22" read
the size, filtered the dresses and found no dress that carried it. :func:`extend` runs over the
templates (:func:`scale.templates`), so a derived style inherits the longer run: a digest-chosen
:data:`SHARE` of the Womens dresses, tops, trousers, jeans and knitwear whose SKUs carry a UK
size gain every size up to :data:`TOP` in the same UK/EU/US chart as the shorter run
(``samples.WOMENS``: EU = UK + 28, US = UK - 4). Each new SKU copies the largest-size SKU of its
color (same price, stock and other options); the new SKUs are appended, so no existing SKU id
moves. A record that is a decoy, or whose largest UK size is already :data:`TOP`, is left alone.
"""

from __future__ import annotations

import zlib

#: The Womens leaves (second path node) whose styles may gain the larger sizes.
LEAVES = frozenset({"Dresses", "Tops", "Trousers", "Jeans", "Knitwear"})
#: The largest UK size the extended run reaches, and the smallest run end that is extended.
TOP = 24
#: Out of ``SHARE[1]`` styles, ``SHARE[0]`` are extended, chosen by a digest of the product id.
SHARE = (3, 5)


def chosen(rec: dict) -> bool:
    """Is this record's size run extended: Womens, one of :data:`LEAVES`, in the digest's share."""
    path = rec.get("category_path", [])
    if len(path) < 2 or path[0] != "Womens" or path[1] not in LEAVES:
        return False
    return zlib.crc32(rec["product_id"].encode()) % SHARE[1] < SHARE[0]


#: The SKU fields that change with a size (or are the SKU's own); the rest name a color or option.
_PER_SIZE = frozenset({"sku", "size", "size_uk", "size_eu", "size_us", "price", "in_stock"})
#: The keys a Womens UK dress size is stored under: ``size`` (a bare number, which the Combined
#: projection reads as the UK size) or ``size_uk`` with its EU and US sizes beside it.
KEYS = ("size_uk", "size")


def _uk(sku: dict) -> tuple[str, int] | None:
    for key in KEYS:
        value = sku.get(key)
        if isinstance(value, str) and value.isdigit():
            return key, int(value)
    return None


def extend(rec: dict) -> dict:
    """The record with its UK size run carried up to :data:`TOP`, or ``rec`` itself."""
    skus = rec.get("skus", [])
    found = [(s, _uk(s)) for s in skus]
    uks = [u[1] for _, u in found if u]
    if not uks or max(uks) >= TOP or max(uks) % 2:
        return rec
    top = max(uks)
    last: dict[tuple, tuple[dict, str]] = {}
    for s, u in found:
        if u and u[1] == top:
            own = tuple(sorted((k, str(v)) for k, v in s.items() if k not in _PER_SIZE))
            last[own] = (s, u[0])
    pid = rec["product_id"]
    added = []
    for base, key in last.values():
        for uk in range(top + 2, TOP + 1, 2):
            sizes = {key: str(uk)}
            if key == "size_uk":
                sizes |= {"size_eu": str(uk + 27), "size_us": str(uk - 3)}
            added.append({**{k: v for k, v in base.items() if k != "sku"}, **sizes})
    rows = [*skus, *({"sku": f"{pid}-{n:03d}", **s} for n, s in enumerate(added, len(skus) + 1))]
    options = dict(rec.get("size_options", {}))
    for key in ("size_uk", "size_eu", "size_us", "size"):
        if any(key in s for s in added):
            seen = list(options.get(key, []))
            for s in added:
                if s[key] not in seen:
                    seen.append(s[key])
            options[key] = seen
    return {**rec, "skus": rows, "sku_count": len(rows), "size_options": options}


def extend_all(recs: list[dict], skip: frozenset[str] = frozenset()) -> list[dict]:
    """:func:`extend` over every chosen record not in ``skip``."""
    return [extend(r) if chosen(r) and r["product_id"] not in skip else r for r in recs]
