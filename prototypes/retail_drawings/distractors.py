"""Planted distractors of gen#125 (prototype, round 4).

The catalog must hold ordinary products that win the top results when no
policy is applied, so the demo can show what a policy fixes. Each
:class:`Row` of :data:`TABLE` is (query, the intended products, 3 to 10
distractors, the policy that fixes each one).

:func:`check` refuses a row whose distractors cannot outrank the best
intended product on text alone, scored by :class:`BM25` over title plus
description against the whole catalog. Self-contained: standard library,
:mod:`departments` and :mod:`variants` only. Every brand name is invented.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass

from departments import check as check_departments
from variants import attr, cw, docs, drawing

MIN_DISTRACTORS, MAX_DISTRACTORS = 3, 10

# ==========================================================================
# A simple BM25 over title + description
# ==========================================================================


def tokens(text: str) -> list[str]:
    """Lower-cased words, with a naive plural strip (``lemons`` -> ``lemon``)."""
    out = []
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def text_of(doc: dict) -> list[str]:
    return tokens(f"{doc['title']} {doc.get('description', '')}")


class BM25:
    """Okapi BM25 (k1 = 1.2, b = 0.75) over each doc's title plus description."""

    def __init__(self, corpus: list[dict], k1: float = 1.2, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.n = len(corpus)
        self.avgdl = sum(len(text_of(d)) for d in corpus) / self.n
        self.df: Counter[str] = Counter(t for d in corpus for t in set(text_of(d)))

    def idf(self, term: str) -> float:
        df = self.df[term]
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def score(self, query: str, doc: dict) -> float:
        words = text_of(doc)
        tf = Counter(words)
        norm = self.k1 * (1 - self.b + self.b * len(words) / self.avgdl)
        return sum(
            self.idf(t) * tf[t] * (self.k1 + 1) / (tf[t] + norm) for t in tokens(query) if tf[t]
        )


# ==========================================================================
# The table
# ==========================================================================


@dataclass(frozen=True)
class Distractor:
    doc: dict
    fixed_by: str


@dataclass(frozen=True)
class Row:
    cls: str
    query: str
    intended: str
    is_intended: Callable[[dict], bool]
    policy: str
    distractors: tuple[Distractor, ...]


def product(
    code: str,
    title: str,
    brand: str,
    department: str,
    path: tuple[str, ...],
    price: float,
    description: str,
    draw: dict,
    attrs: tuple[tuple[str, str, str], ...] = (),
) -> dict:
    """One single-SKU product doc in the variant model's shape (its own variant group)."""
    check_departments([department], title)
    return {
        "product_id": f"PLT-{code}-01",
        "sku": f"PLT{code}01",
        "variant_group": f"PLT-{code}",
        "sku_count": 1,
        "title": title,
        "brand": brand,
        "department": [department],
        "category_path": list(path),
        "price": price,
        "description": description,
        "attributes": [attr(k, n, v) for k, n, v in attrs],
        "drawing": draw,
        "collections": [],
        "currency": "GBP",
    }


YELLOW, WHITE = "#f2d14b", "#ffffff"

#: Intended products that are not part of a variant family.
LEMONS = product(
    "LEMONS", "Unwaxed Lemons, Pack of 4", "Goldfield Farms", "Food & Drink",
    ("Food", "Fresh Produce", "Fruit", "Citrus"), 1.25,
    "Fresh unwaxed lemons for zesting, juicing and baking, grown in sunny groves.",
    drawing("round_produce", cw("Lemon", YELLOW), "Lemons"),
    (("colour", "Colour", "Yellow"), ("pack_size", "Pack size", "4")),
)  # fmt: skip

LEMON = (
    Distractor(product(
        "LEMDRS", "Lemon Print Tea Dress", "Larkmoor", "Clothing",
        ("Women", "Dresses", "Tea Dresses"), 38.0,
        "A floaty tea dress in our lemon print: yellow lemons and green leaves on white. "
        "The lemon print is back for summer.",
        drawing("dress", cw("Lemon Print", WHITE, "polka", YELLOW)),
        (("colour", "Colour", "White / Yellow"), ("pattern", "Pattern", "Lemon Print")),
    ), "department boost: Food & Drink above Clothing"),
    Distractor(product(
        "LEMCAK", "Lemon Drizzle Cake", "Crofter's Bakehouse", "Food & Drink",
        ("Food", "Bakery", "Cakes"), 3.5,
        "A lemon sponge soaked in lemon syrup and topped with lemon icing. Serves 8.",
        drawing("cake", cw("Lemon", "#f6e08a"), "Lemon"),
        (("flavour", "Flavour", "Lemon"),),
    ), "category intent: Fresh Produce above Bakery"),
    Distractor(product(
        "LEMGEL", "Lemon & Bergamot Shower Gel 250ml", "Velling Apothecary", "Beauty",
        ("Beauty", "Bath & Body", "Shower Gel"), 6.0,
        "A zesty lemon shower gel with lemon peel oil and bergamot. Smells of fresh lemons.",
        drawing("bottle", cw("Lemon", YELLOW), "Lemon"),
        (("fragrance", "Fragrance", "Lemon & Bergamot"),),
    ), "persona boost: a grocery shopper's lemon is Food & Drink"),
    Distractor(product(
        "LEMFLR", "Lemon Floor Cleaner 1L", "Pantry Mill", "Cleaning & Janitorial",
        ("Cleaning", "Floor Care", "Floor Cleaners"), 2.2,
        "A lemon fresh floor cleaner with real lemon oil that leaves floors smelling of lemon.",
        drawing("bottle", cw("Lemon", "#f7e27a"), "Lemon"),
        (("fragrance", "Fragrance", "Lemon"),),
    ), "department boost: Food & Drink above Cleaning & Janitorial"),
    Distractor(product(
        "LEMSPR", "Lemon Multi-Surface Cleaner Spray", "Pantry Mill", "Cleaning & Janitorial",
        ("Cleaning", "Kitchen & Surfaces", "Multi-Surface Sprays"), 1.9,
        "Lemon scented spray that cuts through grease. Lemon fresh kitchens in seconds.",
        drawing("trigger_spray", cw("Lemon", YELLOW, "solid", "#2f6b3c"), "Lemon"),
        (("fragrance", "Fragrance", "Lemon"),),
    ), "department boost: Food & Drink above Cleaning & Janitorial"),
)  # fmt: skip

DENIM = "#4a6a94"
JEANS = (
    Distractor(product(
        "JNSBLT", "Leather Jeans Belt", "Ferrowick Denim", "Clothing",
        ("Men", "Accessories", "Belts"), 22.0,
        "A wide leather belt cut for jeans, with a brass roller buckle that sits flat in "
        "jeans belt loops.",
        drawing("belt", cw("Tan", "#b07a45")),
        (("colour", "Colour", "Tan"), ("material", "Material", "Leather")),
    ), "product-type demotion: accessories below jeans"),
    Distractor(product(
        "JNSJKT", "Belted Denim Jacket", "Harbour & Pine", "Clothing",
        ("Women", "Coats & Jackets", "Denim Jackets"), 45.0,
        "Cut from the same rigid denim as our jeans, in a jeans blue mid wash. Wear it with "
        "jeans for double denim.",
        drawing("coat", cw("Mid Wash", DENIM)),
        (("colour", "Colour", "Mid Wash"),),
    ), "category intent: Jeans"),
    Distractor(product(
        "JNSHNG", "Jeans Hanger, Pack of 5", "Brackenmere Home", "Home",
        ("Home", "Storage", "Hangers"), 8.0,
        "Clip hangers that hold jeans by the waistband, so jeans hang straight without creases.",
        drawing("hanger", cw("Black", "#2a2a2e")),
        (("colour", "Colour", "Black"), ("pack_size", "Pack size", "5")),
    ), "category intent: Jeans (a Home item never answers a clothing word)"),
    Distractor(product(
        "JNSSET", "Kids' Jeans & Tee Set", "Little Fernby", "Clothing",
        ("Kids", "Outfits & Sets", "Two-Piece Sets"), 18.0,
        "A two-piece set: slim stretch jeans with an adjustable waist and a cotton tee. "
        "Jeans and tee sold together.",
        drawing("outfit_set", cw("Mid Wash", DENIM), tee="#f2d14b"),
        (("colour", "Colour", "Mid Wash / Yellow"), ("audience", "Audience", "Boys")),
    ), "product-type demotion: sets below single items"),
)  # fmt: skip

DUVET = (
    Distractor(product(
        "DUVCOV", "Cotton Duvet Cover", "Brackenmere Home", "Home",
        ("Home", "Bedding", "Duvet Covers"), 26.0,
        "A plain cotton duvet cover with a button closure. Fits over any duvet; duvet sold "
        "separately.",
        drawing("duvet", cw("Oyster", "#e4ddd0")),
        (("colour", "Colour", "Oyster"),),
    ), "type-exact intent: Duvets, not Duvet Covers"),
    Distractor(product(
        "DUVSET", "Duvet Cover Set with Pillowcases", "Brackenmere Home", "Home",
        ("Home", "Bedding", "Bedding Sets"), 32.0,
        "A duvet set: one duvet cover and two matching pillowcases. Duvet not included.",
        drawing("duvet", cw("Ticking Stripe", WHITE, "stripe", "#26365c")),
        (("colour", "Colour", "Navy / White"), ("pattern", "Pattern", "Stripe")),
    ), "type-exact intent: Duvets, not Bedding Sets"),
    Distractor(product(
        "DUVKID", "Kids' Dinosaur Duvet Set", "Little Fernby", "Home",
        ("Home", "Kids' Bedding", "Bedding Sets"), 20.0,
        "A printed single duvet set for kids: a duvet cover and pillowcase. Duvet sold "
        "separately.",
        drawing("duvet", cw("Green Spot", "#7fae6a", "polka", "#ffffff")),
        (("colour", "Colour", "Green"), ("audience", "Audience", "Boys")),
    ), "type-exact intent: Duvets, not Bedding Sets"),
    Distractor(product(
        "DUVSSK", "Seersucker Duvet Cover", "Quillon Sleep", "Home",
        ("Home", "Bedding", "Duvet Covers"), 30.0,
        "A puckered seersucker duvet cover in gingham check. Duvet cover only; duvet not "
        "included.",
        drawing("duvet", cw("Blue Gingham", WHITE, "gingham", "#5b84b8")),
        (("colour", "Colour", "Blue / White"), ("pattern", "Pattern", "Gingham")),
    ), "type-exact intent: Duvets, not Duvet Covers"),
)  # fmt: skip

TABLE = (
    Row("Print, flavour and scent words", "lemon", "fresh lemons",
        lambda d: d["category_path"][:2] == ["Food", "Fresh Produce"]
        and "lemon" in tokens(d["title"]),
        "department or persona boost", LEMON),
    Row("Complements and accessories", "jeans", "a pair of jeans",
        lambda d: d["variant_group"].startswith("JEA-"),
        "category intent; product-type demotion", JEANS),
    Row("Bedding types", "duvet", "a duvet",
        lambda d: d["category_path"][-1] == "Duvets",
        "type-exact intent", DUVET),
)  # fmt: skip


def distractor_docs() -> list[dict]:
    return [x.doc for row in TABLE for x in row.distractors]


def corpus() -> list[dict]:
    """The catalog the text score is taken over: every variant doc, LEMONS, every distractor."""
    return [*docs(), LEMONS, *distractor_docs()]


def scores(row: Row, catalog: list[dict]) -> tuple[float, list[tuple[str, float]]]:
    """The best intended score for ``row.query``, and each distractor's (product_id, score)."""
    bm = BM25(catalog)
    intended = [d for d in catalog if row.is_intended(d)]
    if not intended:
        raise ValueError(f"{row.query!r}: no intended product in the catalog")
    best = max(bm.score(row.query, d) for d in intended)
    return best, [(x.doc["product_id"], bm.score(row.query, x.doc)) for x in row.distractors]


def check(table: tuple[Row, ...] = TABLE, catalog: list[dict] | None = None) -> None:
    """ValueError naming every distractor that cannot outrank the best intended product."""
    catalog = corpus() if catalog is None else catalog
    problems = []
    for row in table:
        n = len(row.distractors)
        if not MIN_DISTRACTORS <= n <= MAX_DISTRACTORS:
            problems.append(
                f"{row.query!r}: {n} distractors, not {MIN_DISTRACTORS}-{MAX_DISTRACTORS}"
            )
        for x in row.distractors:
            if row.is_intended(x.doc):
                problems.append(f"{row.query!r}: {x.doc['product_id']} is an intended product")
        best, each = scores(row, catalog)
        problems += [
            f"{row.query!r}: {pid} scores {s:.3f}, not above the intended {best:.3f}"
            for pid, s in each
            if s <= best
        ]
    if problems:
        raise ValueError("refused distractors:\n" + "\n".join(problems))


def table_markdown() -> str:
    """The table as the demo script and persona tests read it."""
    out = [
        "| Class | Query → intended | Distractors that outrank without policies | Fixed by |",
        "|---|---|---|---|",
    ]
    for row in TABLE:
        names = "; ".join(
            f"{x.doc['title']} [{x.doc['product_id']}] ({x.fixed_by})" for x in row.distractors
        )
        out.append(f"| {row.cls} | *{row.query}* → {row.intended} | {names} | {row.policy} |")
    return "\n".join(out)


if __name__ == "__main__":
    check()
    cat = corpus()
    for row in TABLE:
        best, each = scores(row, cat)
        print(row.query, f"intended {best:.3f}", [f"{s:.3f}" for _, s in each])
    print(table_markdown())
