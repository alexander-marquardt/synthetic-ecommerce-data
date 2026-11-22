"""The 14 cohort shoppers and their seeded purchases (gen#1131, slice 2).

Each purchase is checked against its shopper's cohort here, from the grocery build's own facts
(the flavor's animal flags, the SKU's dietary labels, the alcohol rule), not from the
classification :mod:`shoppers` draws with. The files are parsed as the loaders read them:
``prism-studio load-users`` keeps ``id`` as the profile id and needs ``name``, and
``load-purchases`` reads ``id`` and each purchase's ``product_id``, which it resolves as a
catalogue document id, so it is the SKU (the field map's ``id`` is ``sku``).
"""

from __future__ import annotations

import datetime as dt
from collections import Counter
from functools import cache
from pathlib import Path

import yaml

from synthetic_ecommerce_data.domains.retail import grocery, grocery_rows, shoppers
from synthetic_ecommerce_data.domains.retail.export import standard_document

FAMS = {f.code: f for f in grocery_rows.FAMILIES}
COHORTS = ("halal", "kosher", "organic", "vegan", "vegetarian", "sweet_tooth")
PROFILE_KEYS = {"id", "name", "description", "cohorts"}
PURCHASE_KEYS = {
    "product_id", "persona", "title", "brand", "image_url", "purchase_count", "last_purchase",
}


@cache
def _skus() -> dict[str, tuple]:
    """Every food SKU of the build: sku id -> (family, flavor, sku)."""
    out = {}
    for r in grocery.build():
        fam = FAMS[r["product_id"].split("-")[1]]
        if not fam.food:
            continue
        by_name = {f.name: f for f in fam.flavors}
        for sku in r["skus"]:
            out[sku["sku"]] = (fam, by_name[sku[fam.axis]], sku)
    return out


@cache
def _flat() -> dict[str, dict]:
    docs = [standard_document(r) for r in grocery.build()]
    return {row["sku"]: row for row in grocery.flat(docs)}


@cache
def _files(date: str = shoppers.DATE) -> tuple[list[dict], list[dict]]:
    return tuple(yaml.safe_load(t)["users"] for t in shoppers.texts(date))


def _flags(fam, fl) -> set[str]:
    return set(fl.codes) | set(fam.base)


def _fits(cohort: str, sku_id: str) -> bool:
    fam, fl, sku = _skus()[sku_id]
    labels, flags = set(sku.get("dietary", ())), _flags(fam, fl)
    if cohort == "halal":
        alcohol = grocery.alcoholic(fam, fl, sku.get("ingredients"))
        return "Halal" in labels and "p" not in flags and not alcohol
    if cohort == "kosher":
        return "Kosher" in labels and not {"p", "s"} & flags
    if cohort == "vegan":
        return "Vegan" in labels and not {"Milk", "Egg", "Fish"} & set(sku.get("contains", ()))
    if cohort == "vegetarian":
        return "Vegetarian" in labels and "x" not in flags
    if cohort == "organic":
        return "Organic" in labels
    if cohort == "sweet_tooth":
        return fam.path[1] == "Chocolate & Sweets"
    raise AssertionError(cohort)


def _by_id() -> dict[str, dict]:
    return {u["id"]: u for u in _files()[1]}


def test_the_roster_is_fourteen_shoppers_two_per_cohort() -> None:
    profiles = _files()[0]
    assert [u["id"] for u in profiles] == [f"gen_user_{n}" for n in range(1, 15)]
    cohorts = Counter(c for u in profiles for c in u["cohorts"])
    assert cohorts == {c: 2 for c in COHORTS}
    assert sum(not u["cohorts"] for u in profiles) == 2
    assert len({u["name"] for u in profiles}) == 14


def test_each_cohort_has_one_shopper_of_eight_and_one_of_four() -> None:
    profiles, bought = _files()[0], _by_id()
    for cohort in COHORTS:
        sizes = sorted(
            len(bought[u["id"]]["purchases"]) for u in profiles if cohort in u["cohorts"]
        )
        assert sizes == [4, 8], cohort
    plain = sorted(len(bought[u["id"]]["purchases"]) for u in profiles if not u["cohorts"])
    assert plain == [0, 8]


def test_every_purchase_fits_its_shoppers_cohort() -> None:
    bought = _by_id()
    checked = 0
    for user in _files()[0]:
        rows = bought[user["id"]]["purchases"]
        for cohort in user["cohorts"]:
            fit = [_fits(cohort, p["product_id"]) for p in rows]
            if cohort in ("organic", "sweet_tooth"):
                assert sum(fit) * 4 >= len(rows) * 3, (user["id"], fit)
            else:
                assert all(fit), (user["id"], cohort, fit)
            checked += len(rows)
    assert checked == 6 * 12


def test_the_meat_eater_buys_only_meat_and_some_pork() -> None:
    eater = _by_id().get("gen_user_13", {"purchases": []})
    assert len(eater["purchases"]) == 8
    flags = [_flags(*_skus()[p["product_id"]][:2]) for p in eater["purchases"]]
    assert all("x" in f for f in flags)
    assert any("p" in f for f in flags)


def test_each_purchase_is_a_grocery_sku_with_its_catalogue_title_brand_and_image() -> None:
    flat, start = _flat(), dt.date.fromisoformat(shoppers.DATE)
    rows = [p for u in _files()[1] for p in u["purchases"]]
    assert len(rows) == 6 * 12 + 8
    for user in _files()[1]:
        pids = [flat[p["product_id"]]["product_id"] for p in user["purchases"]]
        assert len(pids) == len(set(pids)), user["id"]
    for p in rows:
        row = flat[p["product_id"]]
        stated = (p["title"], p["brand"], p["image_url"])
        assert stated == (row["title"], row["brand"], row["image_url"])
        assert p["persona"] == "Combined"
        assert 1 <= p["purchase_count"] <= 6
        days = (start - dt.datetime.fromisoformat(p["last_purchase"]).date()).days
        assert 1 <= days <= 60, p


def test_the_files_hold_the_keys_the_loaders_read() -> None:
    profiles, purchases = _files()
    assert len(profiles) == 14
    assert all(set(u) == PROFILE_KEYS and u["name"] and u["description"] for u in profiles)
    assert all(isinstance(u["cohorts"], list) for u in profiles)
    assert [u["id"] for u in purchases] == [u["id"] for u in profiles]
    assert all(set(u) == {"id", "name", "purchases"} for u in purchases)
    assert all(set(p) == PURCHASE_KEYS for u in purchases for p in u["purchases"])


def test_the_entry_point_writes_the_same_bytes_twice_under_the_date(tmp_path: Path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    assert shoppers.main(["--out", str(first), "--date", "2026-03-01"]) == 0
    assert shoppers.main(["--out", str(second), "--date", "2026-03-01"]) == 0
    names = sorted(p.name for p in (first / "users").iterdir())
    assert names == ["profiles_2026-03-01.yaml", "purchases_2026-03-01.yaml"]
    for name in names:
        assert (first / "users" / name).read_bytes() == (second / "users" / name).read_bytes()
    users = yaml.safe_load((first / "users" / names[1]).read_text(encoding="utf-8"))["users"]
    last = max(p["last_purchase"] for u in users for p in u["purchases"])
    assert last < "2026-03-01"
