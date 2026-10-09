"""The grocery build (gen#154): flavor x pack SKUs, allergens, dietary labels, demo cases.

``prototypes/retail_drawings/grocery.py`` builds Food & Drink styles from
``grocery_rows.FAMILIES``. These tests hold it at its 10K target: the exact counts,
the output standard (nested and flat), allergen facts that never contradict each
other, titles that never claim a label their variants lack, determinism, one drawing
per style, and every planted demo case.
"""

from __future__ import annotations

import json
import subprocess
import sys
from functools import cache
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core.standard import check_catalog

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import grocery  # noqa: E402
import kit  # noqa: E402
from grocery_rows import ALLERGENS  # noqa: E402

STYLES = 3305
SKUS = 10_042
ALL = set(ALLERGENS.values())


@cache
def docs() -> tuple[dict, ...]:
    return tuple(grocery.documents(grocery.build(grocery.TARGET)))


def values(entries: list[dict], key: str) -> set[str]:
    return {e["value"] for e in entries if e["key"] == key}


def food(doc: dict) -> bool:
    return values(doc["attributes"], "department") == {"Food & Drink"}


def test_the_build_holds_its_exact_counts() -> None:
    assert (len(docs()), sum(len(d["variants"]) for d in docs())) == (STYLES, SKUS)


def test_every_document_meets_the_output_standard() -> None:
    assert check_catalog(docs()) == []


def test_the_flat_file_is_one_document_per_sku_with_the_retail_flat_keys() -> None:
    rows = grocery.flat(list(docs()))
    retail_keys = set(export.flat_documents()[0])
    assert len(rows) == SKUS
    assert {k for r in rows for k in r} == retail_keys


def test_every_food_sku_states_each_allergen_once_and_free_from_contradicts_nothing() -> None:
    bad = []
    for d in filter(food, docs()):
        for v in d["variants"]:
            has, may, free = (
                values(v["attributes"], k) for k in ("contains", "may_contain", "free_from")
            )
            if has & may or free & (has | may) or has | may | free != ALL:
                bad.append(v["sku"])
    assert bad == []


def test_no_flat_sku_contains_or_may_contain_what_it_is_free_from() -> None:
    """The flat file inherits a product's entries a variant lacks: it must not
    inherit another flavor's allergen into a SKU that states itself free from it."""
    bad = []
    for row in grocery.flat(list(docs())):
        if "Food & Drink" not in values(row["attributes"], "department"):
            continue
        has, may, free = (
            values(row["attributes"], k) for k in ("contains", "may_contain", "free_from")
        )
        if has & may or free & (has | may) or has | may | free != ALL:
            bad.append(row["sku"])
    assert bad == []


def test_a_flat_sku_states_its_own_variants_allergens() -> None:
    """Fruit Gums (GRC-SWT-0002-001) are free from milk: the Toffee next to it is not."""
    rows = {r["sku"]: r for r in grocery.flat(list(docs()))}
    nested = {v["sku"]: v for d in docs() for v in d["variants"]}
    for sku, row in rows.items():
        for key in ("contains", "may_contain"):
            assert values(row["attributes"], key) == values(nested[sku]["attributes"], key), sku
    assert "Milk" not in values(rows["GRC-SWT-0002-001"]["attributes"], "contains")
    assert "Milk" in values(rows["GRC-SWT-0002-001"]["attributes"], "free_from")


def test_a_product_is_free_from_an_allergen_only_when_every_variant_is() -> None:
    bad = []
    for d in filter(food, docs()):
        free = values(d["attributes"], "free_from")
        if any(free - values(v["attributes"], "free_from") for v in d["variants"]):
            bad.append(d["product_id"])
        if free & values(d["attributes"], "contains") | free & values(
            d["attributes"], "may_contain"
        ):
            bad.append(d["product_id"])
    assert bad == []


def test_every_dietary_label_agrees_with_the_allergens() -> None:
    bad = []
    for d in filter(food, docs()):
        for v in d["variants"]:
            diet, has = values(v["attributes"], "dietary"), values(v["attributes"], "contains")
            traced = has | values(v["attributes"], "may_contain")
            if "Vegan" in diet and has & {"Milk", "Egg"}:
                bad.append((v["sku"], "Vegan"))
            if ("Nut Free" in diet) != (not traced & {"Peanuts", "Tree Nuts"}):
                bad.append((v["sku"], "Nut Free"))
            if ("Gluten Free" in diet) != ("Gluten" not in traced):
                bad.append((v["sku"], "Gluten Free"))
    assert bad == []


@pytest.mark.parametrize("word", ["Vegan", "Gluten Free", "Organic"])
def test_a_title_never_claims_a_label_a_variant_lacks(word: str) -> None:
    bad = [
        d["product_id"]
        for d in docs()
        if word in d["title"]
        and any(word not in values(v["attributes"], "dietary") for v in d["variants"])
    ]
    assert bad == []


def test_an_organic_style_says_so_in_its_title() -> None:
    organic = [d for d in docs() if "Organic" in values(d["attributes"], "dietary")]
    assert organic
    assert [d["product_id"] for d in organic if "Organic" not in d["title"]] == []


def test_the_build_is_deterministic_and_the_seed_changes_it() -> None:
    a = json.dumps(grocery.build(2000, seed=3), sort_keys=True)
    assert a == json.dumps(grocery.build(2000, seed=3), sort_keys=True)
    assert a != json.dumps(grocery.build(2000, seed=4), sort_keys=True)


def test_one_drawing_per_style() -> None:
    images = {v["image_id"] for d in docs() for v in d["variants"]}
    assert len(images) == STYLES


@pytest.mark.parametrize("shape", ["bar", "bag"])
def test_a_grocery_pack_shape_paints_the_records_fill(shape: str) -> None:
    svg = kit.render(shape, kit.Fill("solid", "#a1b2c3", "#ffffff"), "Label")
    assert 'fill="#a1b2c3"' in svg


def test_every_grocery_shape_is_a_kit_shape() -> None:
    assert {d["image_id"].split("/")[0] for d in docs()}
    assert {f.shape for f in grocery.FAMILIES} <= set(kit.SHAPES)


# --------------------------------------------------------------------------
# The planted demo cases: each exists, in the department its meaning flips to.
# --------------------------------------------------------------------------


def find(leaf: str, **want: str) -> list[dict]:
    """Variants under ``leaf`` (a path step) whose attributes hold every ``key=value``."""
    out = []
    for d in docs():
        if leaf not in d["category_path"]:
            continue
        for v in d["variants"]:
            if all(val in values(v["attributes"], k) for k, val in want.items()):
                out.append(v)
    return out


def test_chocolate_with_and_without_peanuts() -> None:
    assert find("Chocolate Bars", contains="Peanuts")
    assert find("Chocolate Bars", may_contain="Peanuts")
    assert find("Chocolate Bars", free_from="Peanuts")


def test_nut_free_and_vegan_chocolate() -> None:
    assert find("Chocolate Bars", dietary="Nut Free")
    assert find("Chocolate Bars", dietary="Vegan")


@pytest.mark.parametrize(
    ("food_leaf", "food_want", "other_leaf", "other_want"),
    [
        ("Fruit", {"variety": "Unwaxed Lemons"}, "Kitchen Cleaners", {"scent": "Lemon"}),
        ("Jam & Honey", {"flavor": "Lemon Curd"}, "Kitchen Cleaners", {"scent": "Lemon"}),
        ("Fruit", {"variety": "Oranges"}, "Kitchen Cleaners", {"scent": "Orange"}),
        ("Juice", {"flavor": "Smooth Orange"}, "Kitchen Cleaners", {"scent": "Orange"}),
        ("Jam & Honey", {"flavor": "Clear Honey"}, "Body Lotion", {"scent": "Honey"}),
        ("Tinned", {"flavor": "Coconut Milk"}, "Body Lotion", {"scent": "Coconut"}),
        ("Chocolate Bars", {"flavor": "Mint Dark"}, "Kitchen Cleaners", {"scent": "Mint"}),
        ("Milk", {"flavor": "Whole"}, "Body Lotion", {"scent": "Coconut"}),
        ("Chocolate Bars", {"flavor": "Milk"}, "Body Lotion", {"scent": "Honey"}),
    ],
)
def test_a_word_a_food_shares_with_another_department(
    food_leaf, food_want, other_leaf, other_want
) -> None:
    assert find(food_leaf, **food_want)
    assert find(other_leaf, **other_want)


def test_pizza_is_chilled_with_a_vegan_and_a_cheese_style() -> None:
    pizzas = [d for d in docs() if d["category_path"][-2:] == ["Chilled", "Pizza"]]
    assert pizzas
    assert find("Pizza", flavor="Vegan Garden", dietary="Vegan")
    assert find("Pizza", flavor="Four Cheese", contains="Milk")
    assert not find("Pizza", flavor="Four Cheese", dietary="Vegan")
    assert all(
        "Gluten" in values(v["attributes"], "contains") for d in pizzas for v in d["variants"]
    )


def test_a_honey_jar_is_labelled_honey() -> None:
    honey = [d for d in grocery.build(2000) if d["category_leaf"] == "Jam & Honey"]
    labels = {r["drawing"]["label"]: r["skus"][0]["flavor"] for r in honey}
    assert {lab for lab, flavor in labels.items() if "Honey" in flavor} == {"Honey"}


def test_milk_names_a_dairy_milk_a_milk_chocolate_and_a_body_milk() -> None:
    titles = [d["title"] for d in docs()]
    assert any(d["title"].endswith(" Milk") for d in docs() if d["category_leaf"] == "Milk")
    assert find("Chocolate Bars", flavor="Milk", contains="Milk")
    assert any(t.endswith("Body Milk") for t in titles)


def test_the_cli_writes_the_nested_and_flat_files(tmp_path: Path) -> None:
    run = subprocess.run(
        [sys.executable, str(RETAIL / "grocery.py"), "--skus", "300", "--out", str(tmp_path)],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert run.returncode == 0, run.stderr
    report = json.loads(run.stdout)
    assert report["standard_problems"] == 0
    nested = (tmp_path / "nested.jsonl").read_text().splitlines()
    flat = (tmp_path / "flat.jsonl").read_text().splitlines()
    assert (len(nested), len(flat)) == (report["styles"], report["skus"])
