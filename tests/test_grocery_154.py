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
import pack_scale  # noqa: E402
from grocery_ingredients import allergen_value, facet_value  # noqa: E402
from grocery_rows import ALLERGENS, DIETARY  # noqa: E402
from retail_figures import figures  # noqa: E402

#: The measured totals (``retail_figures.figures()``, gen#162): never typed here.
STYLES = figures()["templates"]["grocery"]["styles"]
SKUS = figures()["templates"]["grocery"]["skus"]
ALL = set(ALLERGENS.values())


def canon(names) -> set[str]:  # noqa: ANN001
    """The canonical facet values of allergen names (gen#294)."""
    return {allergen_value(n) for n in names}


def canon1(value: str, name: str) -> str:
    """One attribute value as its facet holds it: an allergen in its canonical form."""
    return allergen_value(value) if name in ("contains", "may_contain") else value


@cache
def docs() -> tuple[dict, ...]:
    return tuple(grocery.documents(grocery.build(grocery.TARGET)))


def values(entries: list[dict], key: str) -> set[str]:
    return {e["value"] for e in entries if e["key"] == key}


def food(doc: dict) -> bool:
    return doc["category_path"][0] == "Food & drink"


def test_the_build_holds_its_exact_counts() -> None:
    assert (len(docs()), sum(len(d["variants"]) for d in docs())) == (STYLES, SKUS)


def test_every_document_meets_the_output_standard() -> None:
    assert check_catalog(docs()) == []


def test_the_flat_file_is_one_document_per_sku_with_the_retail_flat_keys() -> None:
    rows = grocery.flat(list(docs()))
    # fibre_content is a fabric detail (gen#187): food never carries a blend, and the
    # first retail document (a garment) does, so it is not a key every row shares.
    retail_keys = set(export.flat_documents()[0]) - {"fibre_content"}
    assert len(rows) == SKUS
    assert {k for r in rows for k in r} == retail_keys | {"ingredients"}


def test_no_free_from_anywhere() -> None:
    """ "Free from X" is a query (exclude X from contains, and from may_contain when
    strict), not data: no entry, flat fact or option carries it."""
    assert "free_from" not in export.OPTIONS
    keys = {e["key"] for d in docs() for item in (d, *d["variants"]) for e in item["attributes"]}
    assert "free_from" not in keys
    flat_keys = {k for r in grocery.flat(list(docs())) for k in r["facets"]}
    assert "free_from" not in flat_keys
    assert "Free from" not in {n for r in grocery.flat(list(docs())) for n in r["attribute_names"]}


def test_every_food_sku_states_an_allergen_at_most_once_and_never_both_ways() -> None:
    bad = []
    for d in filter(food, docs()):
        for v in d["variants"]:
            has, may = (values(v["attributes"], k) for k in ("contains", "may_contain"))
            if has & may or not has | may <= ALL:
                bad.append(v["sku"])
    assert bad == []


def test_no_flat_sku_contains_what_another_flavor_of_its_style_contains() -> None:
    """The flat file inherits a product's entries a variant lacks: it must not
    inherit another flavor's allergen into a SKU that states none of its own."""
    nested = {v["sku"]: v for d in docs() for v in d["variants"]}
    bad = []
    for row in grocery.flat(list(docs())):
        if row["category_path"][0] != "Food & drink":
            continue
        for key in ("contains", "may_contain"):
            stated = values(nested[row["sku"]]["attributes"], key)
            if set(row["facets"].get(key, [])) != canon(stated):
                bad.append((row["sku"], key))
    assert bad == []


def test_a_flat_sku_states_its_own_variants_allergens() -> None:
    """Fruit Gums (GRC-SWT-0002-001) hold no milk: the Toffee next to it does."""
    rows = {r["sku"]: r for r in grocery.flat(list(docs()))}
    nested = {v["sku"]: v for d in docs() for v in d["variants"]}
    for sku, row in rows.items():
        for key in ("contains", "may_contain"):
            stated = values(nested[sku]["attributes"], key)
            assert set(row["facets"].get(key, [])) == canon(stated), sku
    assert "milk" not in rows["GRC-SWT-0002-001"]["facets"].get("contains", [])


def test_an_allergen_warning_is_a_facet_only_never_a_flat_attribute() -> None:
    """The attributes are a searchable surface in the industrial field map: an allergen
    warning there would let a "peanut" query match through it. ``contains`` and
    ``may_contain`` live in their facets only; ``dietary`` (a pack claim) stays."""
    rows = grocery.flat(list(docs()))
    for row in rows:
        assert not {e["key"] for e in row["attributes"]} & {"contains", "may_contain"}, row["sku"]
        assert not {"Contains", "May contain"} & set(row["attribute_names"]), row["sku"]
    assert any(r["facets"].get("may_contain") for r in rows)
    assert any(e["key"] == "dietary" for r in rows for e in r["attributes"])


#: The four food facts a hard filter must reach: only a facet can be a hard filter.
FOOD_FACETS = ("ingredients", "contains", "may_contain", "dietary")
#: The facts that are warnings or claims, not description: they stay out of the text.
WARNINGS = frozenset({"contains", "may_contain", "dietary"})


def test_every_food_fact_is_a_flat_facet_equal_to_what_the_sku_states() -> None:
    """``facets.<name>`` is a keyword list: the label list, the allergens, the traces and
    the pack claims, each as the SKU states it (an empty list is absent)."""
    nested = {v["sku"]: v for d in docs() for v in d["variants"]}
    seen = {name: 0 for name in FOOD_FACETS}
    for row in grocery.flat(list(docs())):
        own = nested[row["sku"]]
        for name in FOOD_FACETS:
            want = (
                list(dict.fromkeys(facet_value(i) for i in own.get("ingredients", [])))
                if name == "ingredients"
                else [canon1(e["value"], name) for e in own["attributes"] if e["key"] == name]
            )
            assert row["facets"].get(name, []) == want, (row["sku"], name)
            seen[name] += bool(want)
    assert all(seen.values()), seen


def test_the_facet_values_are_the_closed_vocabularies() -> None:
    rows = grocery.flat(list(docs()))
    pool = lambda name: {v for r in rows for v in r["facets"].get(name, [])}  # noqa: E731
    assert pool("contains") == canon(ALL)
    assert pool("may_contain") <= canon(ALL)
    assert pool("dietary") == set(DIETARY)
    assert len(pool("ingredients")) > 100


def test_an_allergen_or_a_claim_never_feeds_the_search_text() -> None:
    """A "peanut" query must not match a product through an allergen warning, nor a
    "gluten" one through a "Gluten Free" claim: the flat ``text`` is the title, brand,
    series, category path and the values of every entry except these three.

    One exemption, stated so a new path-only hit shows: 150 Tree Nuts SKUs (98 under
    "Nuts & Popcorn", 52 under "Nut Butters & Spreads") carry the word "Nuts" in the text
    only through the category path. That is the product's identity, not a warning, and the
    check compares the text to the path-built string, so it does not flag them."""
    bad = []
    for row in grocery.flat(list(docs())):
        words = [row["title"], row["brand"], row.get("series"), *row["category_path"]]
        words += [e["value"] for e in row["attributes"] if e["key"] not in WARNINGS]
        if row["text"] != " ".join(w for w in words if w):
            bad.append(row["sku"])
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


def test_one_drawing_per_style_and_pack_scale() -> None:
    """A style's sizes share a drawing unless its line draws a size smaller (gen#543) or a SKU
    draws its own params (a pizza's flavour and size, gen#604)."""
    images = {v["image_id"] for d in docs() for v in d["variants"]}
    recs = grocery.build(grocery.TARGET)

    def own(rec: dict, sku: dict) -> tuple:
        return tuple(sorted(export.drawing_spec(rec, sku).get("params", {}).items()))

    drawn = {(r["product_id"], pack_scale.factor(r, s), own(r, s)) for r in recs for s in r["skus"]}
    assert len(images) == len(drawn) >= STYLES
    assert len({img.rsplit("/", 1)[0] for img in images}) == STYLES


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
    assert find("Chocolate bars", contains="Peanuts")
    assert find("Chocolate bars", may_contain="Peanuts")


def test_nut_free_and_vegan_chocolate() -> None:
    assert find("Chocolate bars", dietary="Nut Free")
    assert find("Chocolate bars", dietary="Vegan")


@pytest.mark.parametrize(
    ("food_leaf", "food_want", "other_leaf", "other_want"),
    [
        ("Lemons", {"variety": "Unwaxed Lemons"}, "Kitchen cleaners", {"scent": "Lemon"}),
        ("Jam", {"flavor": "Lemon Curd"}, "Kitchen cleaners", {"scent": "Lemon"}),
        ("Oranges", {"variety": "Oranges"}, "Kitchen cleaners", {"scent": "Orange"}),
        ("Juice", {"flavor": "Smooth Orange"}, "Kitchen cleaners", {"scent": "Orange"}),
        ("Honey", {"flavor": "Clear Honey"}, "Body lotion", {"scent": "Honey"}),
        ("Tinned", {"flavor": "Coconut Milk"}, "Body lotion", {"scent": "Coconut"}),
        ("Chocolate bars", {"flavor": "Mint Dark"}, "Kitchen cleaners", {"scent": "Mint"}),
        ("Milk", {"flavor": "Whole"}, "Body lotion", {"scent": "Coconut"}),
        ("Chocolate bars", {"flavor": "Milk"}, "Body lotion", {"scent": "Honey"}),
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
    honey = [d for d in grocery.build(2000) if d["category_leaf"] == "Honey"]
    labels = {r["drawing"]["label"]: r["skus"][0]["flavor"] for r in honey}
    assert {lab for lab, flavor in labels.items() if "Honey" in flavor} == {"Honey"}


def test_milk_names_a_dairy_milk_a_milk_chocolate_and_a_body_milk() -> None:
    titles = [d["title"] for d in docs()]
    assert any(d["title"].endswith(" Milk") for d in docs() if d["category_leaf"] == "Milk")
    assert find("Chocolate bars", flavor="Milk", contains="Milk")
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


@pytest.mark.parametrize(
    ("label", "want"),
    [
        ("Roasted Peanuts (94%)", "roasted peanut"),
        ("natural flavorings", "natural flavoring"),
        ("carrots", "carrot"),
        ("red peppers", "red pepper"),
        ("cherries", "cherry"),
        ("molasses", "molasses"),
        ("hummus", "hummus"),
        ("Butter (80%)", "butter"),
        ("emulsifier (soya lecithin)", "emulsifier (soya lecithin)"),
    ],
)
def test_facet_value_strips_the_percentage_and_the_regular_plural(label: str, want: str) -> None:
    assert facet_value(label) == want


def test_a_product_states_the_union_of_its_skus_allergens_and_the_common_diet() -> None:
    """Product ``contains`` is the union over its SKUs, ``may_contain`` the union minus
    ``contains``, ``dietary`` the intersection (a variant lacking a label drops it)."""
    union_seen = diet_seen = 0
    for d in filter(food, docs()):
        per = [{k: set(values(v["attributes"], k)) for k in WARNINGS} for v in d["variants"]]
        contains = set.union(*(p["contains"] for p in per))
        may = set.union(*(p["may_contain"] for p in per)) - contains
        diet = set.intersection(*(p["dietary"] for p in per))
        assert values(d["attributes"], "contains") == contains, d["product_id"]
        assert values(d["attributes"], "may_contain") == may, d["product_id"]
        assert values(d["attributes"], "dietary") == diet, d["product_id"]
        union_seen += any(p["contains"] != contains for p in per)
        diet_seen += any(p["dietary"] != diet for p in per)
    assert union_seen and diet_seen, (union_seen, diet_seen)


def test_no_label_starts_on_a_dangling_modifier_and_each_names_its_product() -> None:
    """ "Gluten Free Penne" draws "Penne", not "Free Penne"; a chocolate box is not "Selection"."""
    built = grocery.build(grocery.TARGET)
    labels = {(r["title"], r["drawing"]["label"]) for r in built}
    assert labels
    for title, label in labels:
        assert label.split()[0] not in grocery.DANGLING, (title, label)
        assert label != "Selection", title
    by_title = dict(labels)
    penne = [t for t in by_title if t.endswith("Gluten Free Penne")]
    milk = [t for t in by_title if t.endswith("Lactose Free Milk")]
    box = [t for t in by_title if t.endswith("Chocolate Selection")]
    assert penne and milk and box
    assert {by_title[t] for t in penne} == {"Penne"}
    assert {by_title[t] for t in milk} == {"Milk"}
    assert {by_title[t] for t in box} == {"Chocolate Selection"}
    for title, label in labels:  # the label's last word is a word of the title: its noun
        assert label.split()[-1].lower() in title.lower(), (title, label)


def test_butter_is_a_block_or_tub_never_a_bag_and_ice_cream_a_tub_never_a_bottle() -> None:
    shapes = {(r["category_leaf"], r["drawing"]["shape"]) for r in grocery.build(grocery.TARGET)}
    butter = {s for leaf, s in shapes if leaf == "Butter & Spreads"}
    ice = {s for leaf, s in shapes if leaf == "Ice Cream"}
    assert butter == {"butter_block", "lidded_tub"}
    assert ice == {"lidded_tub"}
