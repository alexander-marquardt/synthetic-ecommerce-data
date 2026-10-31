"""A food or drink title reads like a real product: no generation number, no empty word (gen#729).

``Deal.owned`` used to build a food model as a lead word, a sub-model and a number ("Finest
Reserve 2") so that every model was unique, which suits a running shoe and no food: of 3,000
grocery styles on the shared cluster, 2,697 carried the pattern. A model is now a lead word and
at most one style word of the kind, and a brand past those words stays distinct by a true
ingredient or claim on the end of its title, so the catalogue keeps its count.
"""

from __future__ import annotations

import random
import re
from collections import Counter
from typing import Any

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    grocery,
    line_grammar,
    scale,
)
from synthetic_ecommerce_data.domains.retail.grocery_rows import DECOY_ANCHORS, FAMILIES
from synthetic_ecommerce_data.domains.retail.retail_figures import TIER_SKUS

FOOD = ("pantry", "drink", "alcohol")
SPECS = {name: line_grammar._NUMBERED[name] for name in FOOD}
#: Words the sub-model list used to hold: they name no property of a food.
EMPTY_WORDS = {"Reserve", "Special", "Deluxe", "Edition", "Batch", "Series"}
#: "Small Batch" is a phrase a label uses; the empty word was "Batch" on its own.
PHRASES = {"Small Batch"}
GENERATION = re.compile(r"\b(Reserve|Special|Deluxe|Edition|Batch|Series) [2-9]\b")
#: The endings a title may carry, written out so a new row is a change here too.
KNOWN_ENDINGS = {
    "Real Butter", "Real Sugar", "Real Vanilla", "Real Cream", "Real Egg",
    "Real Tomato", "Real Garlic", "Real Ginger", "Cocoa Butter", "Rolled Oats", "Sea Salt",
    "Black Pepper", "Rapeseed Oil", "Sunflower Oil", "Whole Milk", "Live Cultures",
    "Natural Flavoring", "Natural Colors", "Added Vitamin C", "Added Vitamin D",
    "Added Vitamin A", "Added Calcium", "Added Riboflavin", "Added Vitamins", "Added Iron",
    "No Added Sugar", "No Palm Oil", "No Preservatives", "No Artificial Colors",
    "No Artificial Flavors", "No Artificial Ingredients",
}  # fmt: skip


def _food(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The Food & Drink styles the line grammar names, the decoy rows aside."""
    skip = scale.source_ids("seasonal_rows") | scale.source_ids("color_word_brand_rows")
    return [
        r
        for r in records
        if r["category_path"][0] == "Food & Drink"
        and line_grammar.family(r) in FOOD
        and scale._line(r)
        and r["product_id"] not in skip
    ]


@pytest.fixture(scope="module", params=["grocery", "tier", "ceiling"])
def styles(request):
    if request.param == "grocery":
        return _food(grocery.build())
    if request.param == "tier":
        return _food(grocery.build(TIER_SKUS))
    return _food(ceiling_build().records)


def test_no_food_or_drink_model_carries_a_number(styles):
    """Guard (gen#729): the issue's own count of 2,498 in 3,000. Metric: the models with a digit,
    and the titles that still show the old pattern, in the 10K build, the 50K tier and the
    ceiling build."""
    assert len(styles) > 300
    assert [scale._line(r) for r in styles if re.search(r"\d", scale._line(r))][:10] == []
    assert [r["title"] for r in styles if GENERATION.search(r["title"])][:10] == []


def test_a_food_model_is_its_lead_word_and_at_most_one_style_word_of_its_kind(styles):
    """Guard (gen#729): "Finest Greek Style" is a yogurt, so "Finest Greek Style" on crisps, or a
    word from no row, is what the issue calls a meaningless word. Metric: the models that are
    not a lead word of the family plus a style word of the style's own kind."""
    bad = []
    for r in styles:
        spec = line_grammar._NUMBERED[line_grammar.family(r)]
        lead, _, rest = scale._line(r).partition(" ")
        if lead not in (*spec.leads, *spec.grocery_leads) or (
            rest and rest not in spec.styles[r["product_type"]]
        ):
            bad.append((r["product_type"], scale._line(r)))
    assert bad[:10] == []


def test_a_title_says_a_style_word_once(styles):
    """Guard (gen#729): a style row reaches every flavor of its kind, so a word the product
    already says would double it ("Chunky Beer Battered Chunky Chips"). Metric: the titles that
    repeat a word of their model's style."""
    bad = []
    for r in styles:
        rest = scale._line(r).split()[1:]
        words = re.findall(r"[\w']+", r["title"])
        if any(w != "&" and words.count(w) > 1 for w in rest):
            bad.append(r["title"])
    assert bad[:10] == []


def test_the_numbers_that_belong_to_a_product_stay(styles):
    """Guard (gen#729): the issue keeps a pack count and a percentage. Metric: the styles whose
    title or pack attribute still states one."""
    percent = [r for r in styles if re.search(r"\d%", r["title"])]
    packs = [
        a["value"]
        for r in styles
        for a in r["attributes"]
        if a["key"] == "pack_size" and re.search(r"\d", str(a["value"]))
    ]
    assert percent and packs


def test_every_food_kind_has_a_row_of_real_style_words():
    """Guard (gen#729): ``Deal.owned`` reads a row per kind, and a row may hold no number, no
    empty word, no food lead word (a model would read "Finest Crisp Fried") and no duplicate.
    Metric: the kinds short of a row, and the words a row may not hold."""
    leads = {w for s in SPECS.values() for w in (*s.leads, *s.grocery_leads)}
    for name, spec in SPECS.items():
        assert spec.bare and spec.numbers == (), name
        assert sorted(set(spec.kinds) ^ set(spec.styles)) == [], name
        for kind, row in spec.styles.items():
            assert len(row) >= 6 and len(row) == len(set(row)), kind
            words = {w for phrase in row for w in phrase.split()}
            assert sorted(w for w in words if re.search(r"\d", w)) == [], kind
            assert sorted(words & leads) == [], kind
            assert sorted(p for p in row if EMPTY_WORDS & set(p.split()) and p not in PHRASES) == []


def test_a_later_round_of_a_slot_repeats_a_model_and_counts_the_round():
    """Guard (gen#729): every slot past the row names a model the row already named, so only
    the round can keep the title distinct, and a model never gains a number. Metric: the models
    of 2,000 slots against lead words times the row, and the round of the first slot past it."""
    deal = line_grammar.Deal("pantry", ["Acme", "Bolt"], {}, "grocery")
    row = deal.spec.styles["Yogurt"]
    got = {deal.owned("Acme", slot, "Yogurt") for slot in range(2000)}
    leads = deal.of("Acme")
    assert got == {*leads, *(f"{w} {s}" for w in leads for s in row)}
    past = len(leads) * (len(row) + 1)
    assert deal.round("Acme", past - 1, "Yogurt") == 0
    assert deal.round("Acme", past, "Yogurt") == 1
    assert deal.owned("Acme", past, "Yogurt") == deal.owned("Acme", 0, "Yogurt")
    assert line_grammar.is_model("pantry", "Acme", f"{leads[0]} {row[0]}")
    assert not line_grammar.is_model("pantry", "Acme", f"{leads[0]} {row[0]} 2")
    assert not line_grammar.is_model("pantry", "Acme", f"{leads[0]} 2")


#: The issue's "the product count does not drop": (food styles, food SKUs) of main before this
#: change, in the 10K build, the 50K tier and the ceiling build.
BEFORE = {"grocery": (4110, 11678), "tier": (15843, 44897), "ceiling": (4462, 12155)}


def _all_food(name: str) -> list[dict[str, Any]]:
    recs = {"grocery": grocery.build, "tier": lambda: grocery.build(TIER_SKUS)}
    records = recs[name]() if name in recs else ceiling_build().records
    return [r for r in records if r["category_path"][0] == "Food & Drink"]


@pytest.mark.parametrize("name", list(BEFORE))
def test_the_product_count_does_not_drop(name):
    """Guard (gen#729): the maintainer on a brand running out of words: "can't you just add in
    some ingredients, or something?". Metric: food styles and SKUs against main's in each build."""
    food = _all_food(name)
    assert (len(food), sum(r["sku_count"] for r in food)) >= BEFORE[name]
    assert len(food) >= BEFORE[name][0]


def test_a_planted_decoy_draws_from_its_own_stream():
    """Guard (gen#729): a decoy is planted among its family's draws, so one that drew from the
    family's stream would move every style after it. Metric: the decoys' grades in the 10K build
    against the decoy stream's, family by family in build order."""
    stream = random.Random("grocery-decoys:0")
    by_id = {r["product_id"]: r for r in grocery.build()}
    for fam in sorted(FAMILIES, key=lambda f: f.depth):
        for k in range(sum(code == fam.code for code, *_ in DECOY_ANCHORS)):
            attrs = by_id[f"GRC-{fam.code}-{k + 1:04d}"]["attributes"]
            said = {a["value"] for a in attrs if a["key"] == "nutrition_grade"}
            assert said == {f"Grade {stream.choice(fam.grades)}"}, (fam.code, k)


def test_every_grocery_family_reaches_its_budget():
    """Guard (gen#729): a family short of titles would stop under its SKU budget, a loss a total
    could hide. Metric: the 10K families under budget, each family of a build of TARGET SKUs."""
    held: Counter[str] = Counter()
    for r in grocery.build():
        held[r["product_id"].split("-")[1]] += r["sku_count"]
    budget = grocery.budgets(grocery.TARGET)
    assert [
        (f.code, held[f.code], budget[f.code])
        for f in FAMILIES
        if f.food and not f.depth and held[f.code] < budget[f.code]
    ] == []


#: Words of a claim -> the words no variant's label list may hold, written apart from the rows
#: of ``food_title_words`` so that a wrong row fails here.
REFUSED = {
    "No Added Sugar": ("sugar", "syrup", "honey", "glucose", "molasses", "treacle", "caramel"),
    "No Palm Oil": ("palm",),
    "No Preservatives": ("preservative",),
    "No Artificial Colors": ("color",),
    "No Artificial Flavors": (),
    "No Artificial Ingredients": ("preservative", "color", "sweetener", "stabiliser"),
}
#: An ingredient phrase whose last words are no label word as written.
BACKED_BY = {
    "Real Tomato": ("tomato",),
    "Real Egg": ("egg",),
    "Rolled Oats": ("rolled oat",),
    "Live Cultures": ("live yoghurt culture",),
    "Natural Colors": ("anthocyanins", "carotenes"),
    "Added Vitamin C": ("vitamin c",),
    "Added Vitamin D": ("vitamin d",),
    "Added Vitamin A": ("vitamin a",),
    "Added Vitamins": ("vitamins",),
    "Added Calcium": ("calcium",),
    "Added Riboflavin": ("riboflavin",),
    "Added Iron": ("iron",),
    "Real Cream": ("cream",),
}


def _ending(title: str) -> str | None:
    return m[1] if (m := re.search(r" with (.+)$", title)) else None


def _labels(rec: dict[str, Any]) -> list[str]:
    return [", ".join(s["ingredients"]).lower() for s in rec["skus"] if s.get("ingredients")]


@pytest.fixture(scope="module", params=list(BEFORE))
def endings(request):
    food = _all_food(request.param)
    return [(r, e) for r in food if (e := _ending(r["title"])) and "with" not in e.split()]


def test_a_title_ending_is_true_of_every_variant(endings):
    """Guard (gen#729): "an ingredient named in the title is in its ingredient list, a claim does
    not contradict the list". Metric: the styles of each build whose ending a variant's own list
    does not back, read from the record's SKUs."""
    assert len(endings) > 300
    false = []
    for rec, ending in endings:
        if not ending.startswith(("No ", "Real ", "Added ")) and " " not in ending:
            continue  # an authored title's own "with Basil"
        labels = _labels(rec)
        if ending in REFUSED:
            bad = [w for label in labels for w in REFUSED[ending] if w in label]
            flavored = ending.endswith(("Flavors", "Ingredients")) and any(
                re.search(r"(?<!natural )flavoring", label) for label in labels
            )
            if bad or flavored or not labels:
                false.append((rec["title"], bad))
        elif ending in KNOWN_ENDINGS:
            names = BACKED_BY.get(ending, (ending.removeprefix("Real ").lower(),))
            if (
                not labels
                or len(labels) != len(rec["skus"])
                or not all(any(n in label for n in names) for label in labels)
            ):
                false.append((rec["title"], names))
    assert false[:10] == []


def test_a_title_ending_says_no_variant_value(endings):
    """Guard (gen#729): "a flavour that is a variant axis is not in the shared title". Metric:
    the styles whose ending names a word of a value of their variant axis."""
    bad = []
    for rec, ending in endings:
        if ending not in KNOWN_ENDINGS or ending in REFUSED:
            continue
        axis = rec["skus"][0].keys() & {"flavor", "variety"}
        values = {str(s[k]) for s in rec["skus"] for k in axis}
        words = {w.lower().rstrip("es") for v in values for w in re.findall(r"\w+", v)}
        said = {w.lower().rstrip("es") for w in ending.split()} - {"real", "added", "natural"}
        if said & words:
            bad.append((rec["title"], sorted(values)))
    assert bad[:10] == []


def test_every_ending_row_reaches_the_catalogue():
    """Guard (gen#729): a row no product can take is a dead word. Metric: the ending rows of the
    tier's titles, against the rows of ``food_title_words``."""
    said = {e for r in _all_food("tier") if (e := _ending(r["title"]))}
    assert sorted(KNOWN_ENDINGS - said) == []


def test_a_recipe_decides_the_ending():
    """Guard (gen#729): the rule itself on small lists. Metric: the phrases ``true_words`` gives
    for each case the issue names."""
    from synthetic_ecommerce_data.domains.retail.food_title_words import true_words

    label = ["wheat flour", "butter", "sugar", "natural flavoring"]
    got = true_words("Biscuits", "Finest Biscuits", ["Shortbread"], [label])
    assert "with Real Butter" in got and "with Real Sugar" in got
    assert "with No Palm Oil" in got and "with No Artificial Flavors" in got
    # every variant must carry the ingredient, and a claim must hold of them all
    other = ["wheat flour", "palm oil", "sugar", "orange flavoring"]
    got = true_words("Biscuits", "Finest Biscuits", ["Shortbread", "Orange"], [label, other])
    assert "with Real Butter" not in got and "with Real Sugar" in got
    assert "with No Palm Oil" not in got and "with No Artificial Flavors" not in got
    # a word a flavor or the title says stays out
    assert "with Real Butter" not in true_words("Biscuits", "Finest Biscuits", ["Butter"], [label])
    assert "with Real Sugar" not in true_words("Biscuits", "Sugar Biscuits", ["Plain"], [label])
    # "Real" says nothing of what is in the pack, so a title that says it keeps its ending
    assert "with Real Butter" in true_words("Biscuits", "Real Bakes Biscuits", ["Plain"], [label])
    # a recipe the label names no word for gains none, and a title with a "with" gains no second
    assert true_words("Biscuits", "Finest Biscuits", ["Plain"], []) == []
    assert true_words("Biscuits", "Finest Biscuits", ["Plain"], [label, []]) == []
    assert true_words("Tinned Food", "Tomatoes with Basil", ["Plain"], [label]) == []
    assert true_words("Wine", "Finest Merlot", ["Merlot"], [label]) == []


def test_the_first_round_past_the_row_gains_an_ending():
    """Guard (gen#729): a repeated model stays distinct only by its ending, so the first slot past
    the row needs its word as much as a later one. Metric: one style's title at rounds 0 to 2."""
    fam = next(f for f in FAMILIES if f.product_type == "Biscuits")
    brand = sorted(grocery.OWNERS)[0]

    def title(turn: int) -> str:
        pid = f"GRC-{fam.code}-0001"
        args = (pid, "Finest", brand, [fam.flavors[0]], list(fam.packs), "", False, "", turn)
        return grocery.style(fam, *args)["title"]

    assert _ending(title(0)) is None
    assert _ending(title(1)) in KNOWN_ENDINGS
    assert title(1).startswith(title(0))
    assert title(1) != title(2)


def test_a_style_word_a_recipe_contradicts_is_on_no_row():
    """Guard (gen#729): a row reaches every product of its kind, so a word only some recipes
    bear cannot sit on it: a juice from concentrate, blended tea, coffee and honey, rolled oats,
    an unaged tequila. Metric: the words a kind's row may not hold."""
    refused = {
        ("drink", "Juice"): {"Not From Concentrate", "Just Squeezed", "Freshly Pressed", "Pure"},
        ("drink", "Tea"): {"Single Estate"},
        ("drink", "Coffee"): {"Single Origin"},
        ("pantry", "Honey"): {"Single Origin", "Unblended"},
        ("pantry", "Porridge"): {"Steel Cut"},
        ("alcohol", "Tequila"): {"Oak Aged", "Barrel Rested"},
        ("alcohol", "Beer"): {"Cold Filtered"},
    }
    held = {k: sorted(set(SPECS[k[0]].styles[k[1]]) & words) for k, words in refused.items()}
    assert not any(held.values()), held


def test_the_pack_label_stops_before_the_ending():
    """Guard (gen#729): the drawing's label is the product noun, so "with Real Butter" stays off
    the pack. Metric: the label of an ending title."""
    head = "Finest Slow Baked"
    assert grocery.pack_label(f"{head} Biscuits with Real Butter", head) == "Biscuits"
    assert grocery.pack_label(f"{head} Crisps with No Palm Oil", head) == "Crisps"


@pytest.mark.parametrize("fam", ["trainers", "cleaning", "toys"])
def test_a_numbered_model_keeps_its_generation(fam):
    """Guard (gen#729): "Tempo 3" stays; only the food families lost their number. Metric: the
    models of a numbered family's first slots, each with a digit."""
    deal = line_grammar.Deal(fam, ["Acme"], {})
    got = [deal.owned("Acme", slot) for slot in range(10)]
    assert all(any(c.isdigit() for c in model) for model in got), got
    assert deal.spec.numbers and not deal.spec.bare
    assert line_grammar.is_model(fam, "Acme", got[0])
