"""A share of every people department's styles is reduced (gen#359).

Only the styles a template authored carried a ``was_price``, and every authored sale was
Womens. A derived style drops its template's was-price (its price is redrawn, so the old one is
not its own). So Mens, Kids and Baby had no reduced product, and "mens sale shirts" found nothing
once ``sale`` became the exact filter ``promotion`` = "On sale" (gen#189).

A style under a people root (Womens, Mens and Kids, Baby being the Baby audience under Kids) can
be reduced. :data:`SHARE` says what share of each department's SKUs is: the issue asks for a few
hundred in each, and Baby has only about 1,400 SKUs, so its share is the largest. A reduced style
gets a was-price over its price and the three facts that follow, the same way :mod:`class_model`
states them: ``was_price``, ``discount_pct`` and ``promotion`` ("On sale", with the seeded campaign
on a subset, :mod:`promotion`).

- :func:`apply_all` reduces the authored templates (:func:`scale.templates`), which are most of
  each department's SKUs. It takes styles in the order of a hash of their id until the
  department's reduced SKUs reach its share, so the share holds whatever a later change adds.
- :func:`apply` reduces a derived style (:func:`scale.derive`), each with the department's share
  as its chance, a hash of its id.

Nothing here draws from the build's random generator: which styles are reduced, and by how much,
is a hash of the style id, so adding the share moves no other style's draws.

Never reduced: a petite style, so "petite sale" stays a pair only a policy may honour
(``tests/test_retail_distractors.py``, gen#125, gen#275); a style already reduced; and a planted
decoy or failure-class row, whose price is part of what it plants.
"""

from __future__ import annotations

import collections
import zlib
from collections.abc import Iterable
from typing import Any

import audience
import promotion

#: Department -> the share of its SKUs that is reduced. Baby is the Baby audience, which sits
#: under the Kids root; Kids here are the other Kids-root styles.
SHARE = {"Womens": 0.08, "Mens": 0.08, "Kids": 0.10, "Baby": 0.25}
#: The share taken off the was-price, in percent: a was-price is the price over (1 - this).
CUTS = (10, 15, 20, 25, 30, 40)
#: A was-price lands on a whole pound at or above this, otherwise on 50p.
WHOLE_POUNDS_FROM = 20.0


def _hash(product_id: str, salt: str) -> int:
    return zlib.crc32(f"{salt}:{product_id}".encode())


def department(rec: dict[str, Any]) -> str | None:
    """``Womens``, ``Mens``, ``Kids`` or ``Baby``; None for a style outside the people roots."""
    root = rec["category_path"][0]
    if root not in ("Womens", "Mens", "Kids"):
        return None
    stated = [a["value"] for a in rec["attributes"] if a["key"] == "audience"]
    kind = stated[0] if stated else audience.audience_of_path(
        rec["category_path"], rec.get("audience", "adult")
    )
    return "Baby" if kind == audience.BABY else root


def eligible(rec: dict[str, Any]) -> bool:
    """A style in a department that is not petite and does not say "petite" anywhere."""
    text = f"{rec['title']} {rec['description']}".lower()
    return (
        department(rec) is not None
        and "was_price" not in rec
        and "petite" not in rec.get("size_range", ())
        and "petite" not in text
    )


def reduce(rec: dict[str, Any]) -> None:
    """Give ``rec`` a was-price over its price, and the facts that follow, in place.

    The was-price is taken off the dearest SKU, so every size sits under it (``price <
    was_price`` is the sale filter); ``discount_pct`` states the cheapest SKU's, the price the
    style is shown from, as :mod:`class_model` does."""
    price = max(s["price"] for s in rec["skus"])
    cheapest = min(s["price"] for s in rec["skus"])
    cut = CUTS[_hash(rec["product_id"], "cut") % len(CUTS)]
    step = 1.0 if price >= WHOLE_POUNDS_FROM else 0.5
    was = round(price / (1 - cut / 100) / step) * step
    if was <= price:
        was += step
    rec["was_price"] = was
    rec["discount_pct"] = round(100 * (was - cheapest) / was)
    rec["promotion"] = promotion.values(rec["product_id"])


def apply(rec: dict[str, Any]) -> None:
    """Reduce the derived style ``rec`` in place when its id says so."""
    dept = department(rec)
    if dept and eligible(rec) and _hash(rec["product_id"], "reduced") % 1000 < SHARE[dept] * 1000:
        reduce(rec)


def apply_all(templates: list[dict[str, Any]], planted: Iterable[str]) -> list[dict[str, Any]]:
    """``templates`` with each department at its :data:`SHARE`, but no id in ``planted`` reduced.

    A reduced style is a copy: the authored records are shared between calls of
    :func:`scale.templates`, which must not see each other's reductions."""
    keep = frozenset(planted)
    total: collections.Counter[str] = collections.Counter()
    held: collections.Counter[str] = collections.Counter()
    open_: dict[str, list[int]] = collections.defaultdict(list)
    for i, rec in enumerate(templates):
        dept = department(rec)
        if dept is None:
            continue
        total[dept] += rec["sku_count"]
        if "was_price" in rec:
            held[dept] += rec["sku_count"]
        elif rec["product_id"] not in keep and eligible(rec):
            open_[dept].append(i)
    out = list(templates)
    for dept, indexes in open_.items():
        indexes.sort(key=lambda i: _hash(templates[i]["product_id"], "reduced"))
        for i in indexes:
            if held[dept] >= SHARE[dept] * total[dept]:
                break
            out[i] = dict(templates[i])
            reduce(out[i])
            held[dept] += out[i]["sku_count"]
    return out
