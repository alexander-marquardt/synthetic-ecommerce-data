"""The 14 cohort shoppers of the combined demo and their seeded purchases (gen#1131).

    uv run python -m synthetic_ecommerce_data.domains.retail.shoppers --out out/retail

writes ``users/profiles_<date>.yaml`` and ``users/purchases_<date>.yaml`` under ``--out``, in
grocery's schema, so ``prism-studio load-users`` and ``load-purchases`` load them unchanged
(docs/retail-prototype/shoppers-1131.md). The roster mirrors grocery's: two shoppers for each
dietary cohort (:data:`COHORTS`), one of 8 purchases and one of 4, then a meat eater of 8 (pork
included) and a shopper with no preferences and no purchases. Neither of those two is in a
cohort.

A purchase is a food SKU of the grocery build that fits its shopper: Halal, Kosher, Vegan or
Vegetarian shoppers buy only SKUs that carry that label (slice 1's rules already keep pork and
alcohol off Halal, pork and shellfish off Kosher), and half of a Halal or Kosher basket is
certified meat or fish (:data:`CERTIFIED`); Organic and sweet-tooth shoppers buy
:data:`MOSTLY` of theirs from their kind and the rest from any food. Its ``product_id`` is the
SKU, the catalogue document id the loader's ``ids`` lookup resolves (the flat field map's ``id``
is ``sku``), and its title, brand and image URL are that flat document's. Every draw comes from
an RNG seeded by the shopper's id, so a run writes the same bytes. The date only names the files
and dates the purchases: each was last bought 1 to 60 days before it.

The YAML is written by hand, every string JSON-quoted (a JSON string is a YAML double-quoted
one): ``pyyaml`` is a dev dependency only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from synthetic_ecommerce_data.domains.retail import grocery, grocery_rows
from synthetic_ecommerce_data.domains.retail.export import standard_document

#: The default date: it names the files and ends the purchase window.
DATE = "2026-11-22"
#: The persona every purchase is recorded under: the combined catalogue's.
PERSONA = "Combined"
#: A purchase was last bought this many days before the date, at most.
WINDOW_DAYS = 60
#: The share of an Organic or sweet-tooth shopper's purchases drawn from its kind.
MOSTLY = 0.75


@dataclass(frozen=True)
class Item:
    """One food SKU, with the facts a cohort reads."""

    sku: str
    product_id: str
    title: str
    brand: str
    image_url: str
    dietary: frozenset[str]
    meat: bool  # the ``x`` flag: meat or fish
    pork: bool
    sweets: bool  # in Chocolate & Sweets


@dataclass(frozen=True)
class Shopper:
    id: str
    name: str
    description: str
    kind: str  # a cohort of COHORTS, "meat_eater" or "none"
    purchases: int

    @property
    def cohorts(self) -> list[str]:
        return [self.kind] if self.kind in COHORTS else []


#: Each kind's fit: a purchase of its shopper is an item this holds for.
FITS: dict[str, Callable[[Item], bool]] = {
    "halal": lambda i: "Halal" in i.dietary,
    "kosher": lambda i: "Kosher" in i.dietary,
    "organic": lambda i: "Organic" in i.dietary,
    "vegan": lambda i: "Vegan" in i.dietary,
    "vegetarian": lambda i: "Vegetarian" in i.dietary,
    "sweet_tooth": lambda i: i.sweets,
    "meat_eater": lambda i: i.meat,
}
#: grocery's cohort names, each one the Dietary value (or, for ``sweet_tooth``, the aisle) its
#: cohort policy boosts.
COHORTS = ("halal", "kosher", "organic", "vegan", "vegetarian", "sweet_tooth")
#: The certifications: half of such a shopper's purchases are certified meat or fish.
CERTIFIED = frozenset({"halal", "kosher"})
#: The kinds whose shoppers buy only :data:`MOSTLY` of their purchases from it.
PARTLY = frozenset({"organic", "sweet_tooth"})

ROSTER: tuple[Shopper, ...] = tuple(
    Shopper(f"gen_user_{n}", name, description, kind, size)
    for n, (name, description, kind, size) in enumerate(
        (
            ("Ava", "Buys Halal: certified meat, ready meals and sweets", "halal", 8),
            ("Ben", "Buys Halal, now and then", "halal", 4),
            ("Cora", "Buys Kosher: certified meat, fish and chocolate", "kosher", 8),
            ("Dev", "Buys Kosher, now and then", "kosher", 4),
            ("Elin", "Buys Organic when there is a choice", "organic", 8),
            ("Finn", "Buys Organic, now and then", "organic", 4),
            ("Gwen", "Vegan: no milk, egg, meat, fish or honey", "vegan", 8),
            ("Hugo", "Vegan, a small weekly shop", "vegan", 4),
            ("Iris", "Vegetarian: no meat or fish", "vegetarian", 8),
            ("Jack", "Vegetarian, a small weekly shop", "vegetarian", 4),
            ("Kit", "Sweet tooth: chocolate and sweets first", "sweet_tooth", 8),
            ("Leo", "Sweet tooth, now and then", "sweet_tooth", 4),
            ("Maya", "Meat eater: steaks, sausages and bacon", "meat_eater", 8),
            ("Noel", "No dietary preferences, no purchases yet", "none", 0),
        ),
        start=1,
    )
)


@cache
def items() -> tuple[Item, ...]:
    """Every food SKU of the grocery build, in build order."""
    fams = {f.code: f for f in grocery_rows.FAMILIES}
    # Two builds: the standard document may rewrite the record it is given.
    flat = {r["sku"]: r for r in grocery.flat([standard_document(r) for r in grocery.build()])}
    out = []
    for rec in grocery.build():
        fam = fams[rec["product_id"].split("-")[1]]
        if not fam.food:
            continue
        by_name = {f.name: f for f in fam.flavors}
        for sku in rec["skus"]:
            flags = set(by_name[sku[fam.axis]].codes) | set(fam.base)
            row = flat[sku["sku"]]
            out.append(Item(
                sku=sku["sku"],
                product_id=rec["product_id"],
                title=row["title"],
                brand=row["brand"],
                image_url=row["image_url"],
                dietary=frozenset(sku.get("dietary", ())),
                meat="x" in flags,
                pork="p" in flags,
                sweets=fam.path[1] == "Chocolate & Sweets",
            ))
    return tuple(out)


def _draw(rng: random.Random, pool: list[Item], n: int, taken: set[str]) -> list[Item]:
    """``n`` items of ``pool``, each of a product the shopper has not bought yet."""
    picked: list[Item] = []
    for item in rng.sample(pool, len(pool)):
        if len(picked) == n:
            break
        if item.product_id not in taken:
            taken.add(item.product_id)
            picked.append(item)
    if len(picked) < n:
        raise ValueError(f"only {len(picked)} of {n} distinct products to draw from")
    return picked


def basket(shopper: Shopper) -> list[Item]:
    """The shopper's purchases, from an RNG seeded by its id."""
    if not shopper.purchases:
        return []
    rng = random.Random(f"gen#1131:{shopper.id}")
    every = list(items())
    fits = [i for i in every if FITS[shopper.kind](i)]
    taken: set[str] = set()
    if shopper.kind == "meat_eater":
        pork = _draw(rng, [i for i in fits if i.pork], 1, taken)
        return pork + _draw(rng, fits, shopper.purchases - 1, taken)
    if shopper.kind in CERTIFIED:
        # Most certified SKUs are chocolate: half the basket is certified meat or fish.
        meat = _draw(rng, [i for i in fits if i.meat], shopper.purchases // 2, taken)
        return meat + _draw(rng, fits, shopper.purchases - len(meat), taken)
    if shopper.kind in PARTLY:
        own = round(shopper.purchases * MOSTLY)
        return _draw(rng, fits, own, taken) + _draw(rng, every, shopper.purchases - own, taken)
    return _draw(rng, fits, shopper.purchases, taken)


def _q(text: str) -> str:
    return json.dumps(text, ensure_ascii=True)


def texts(date: str = DATE) -> tuple[str, str]:
    """The profiles file and the purchases file, as text."""
    end = dt.date.fromisoformat(date)
    head = f"# The 14 cohort shoppers (gen#1131), written by shoppers.py for {date}.\n"
    profiles, purchases = [head, "users:\n"], [head, "users:\n"]
    for s in ROSTER:
        profiles.append(f"  - id: {s.id}\n    name: {_q(s.name)}\n")
        profiles.append(f"    description: {_q(s.description)}\n")
        profiles.append("    cohorts:" + "".join(f"\n      - {c}" for c in s.cohorts)
                        + ("\n" if s.cohorts else " []\n"))  # fmt: skip
        purchases.append(f"  - id: {s.id}\n    name: {_q(s.name)}\n")
        bought = basket(s)
        purchases.append("    purchases:\n" if bought else "    purchases: []\n")
        rng = random.Random(f"gen#1131:{s.id}:counts")
        for item in bought:
            last = end - dt.timedelta(days=rng.randint(1, WINDOW_DAYS))
            purchases.append(
                f"      - product_id: {_q(item.sku)}\n"
                f"        persona: {PERSONA}\n"
                f"        title: {_q(item.title)}\n"
                f"        brand: {_q(item.brand)}\n"
                f"        image_url: {_q(item.image_url)}\n"
                f"        purchase_count: {rng.randint(1, 6)}\n"
                f"        last_purchase: {_q(last.isoformat() + 'T00:00:00')}\n"
            )
    return "".join(profiles), "".join(purchases)


def write(out: Path, date: str = DATE) -> tuple[Path, Path]:
    """Write both files into ``out/users``; returns their paths."""
    users = out / "users"
    users.mkdir(parents=True, exist_ok=True)
    paths = (users / f"profiles_{date}.yaml", users / f"purchases_{date}.yaml")
    for path, text in zip(paths, texts(date), strict=True):
        path.write_text(text, encoding="utf-8")
    return paths


def _date(text: str) -> str:
    try:
        return dt.date.fromisoformat(text).isoformat()
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"--date must be YYYY-MM-DD: {error}") from error


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True, help="the files go in OUT/users")
    ap.add_argument("--date", type=_date, default=DATE, help=f"YYYY-MM-DD (default {DATE})")
    args = ap.parse_args(argv)
    for path in write(args.out, args.date):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
