"""Realism as rules: one function per rule, each run over every row it applies to (gen#538).

A rule of how the catalogue must read ("a range name holds no color", "a two-color product has
one color value") used to be a test file per issue, each building its own catalogue and walking
it for one rule. A rule is now one function here that takes a list of documents and returns how
many it examined and one ``(id, note)`` per breach. ``tests/test_rules_538.py`` runs every rule over
every row set it is declared for, against an explicit allow-list (``rules_allow.toml``), a
minimum count of rows examined (a rule that examines nothing proves nothing) and a planted breach
of each rule that must be found. A new rule is a function and a line of :data:`RULES`; a new row
set is a loader in :data:`ROWSETS`; no new test file holds either.

A row set another domain builds is not loaded here: a domain reaches core only, never another
domain (#125). The layer above ``domains/`` hands it in as a :class:`RowSet`, its loader beside
the fewest rows each rule must examine in it, to :func:`run_all` (the industrial build's rows:
``synthetic_ecommerce_data.rule_rowsets``, #716).

The documents come in five shapes of one catalogue: ``templates`` (the retail products before
they are scaled, with SKUs and color options), ``retail`` and ``retail_flat`` (the exported
nested and per-SKU documents) and ``golden`` and ``golden_flat`` (the committed industrial and
retail catalogue the golden test holds equal to a fresh build). A rule reads only the fields its
shape has, and skips (does not count) a document it does not apply to.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GOLDEN = HERE.parents[3] / "golden-catalog"
ALLOW = HERE / "rules_allow.toml"

Doc = dict[str, Any]
#: ``(row id, note)``: what breaks a rule, and where.
Finding = tuple[str, str]
#: ``(rows examined, findings)``.
Report = tuple[int, list[Finding]]


# --------------------------------------------------------------------------------------------
# What a rule reads
# --------------------------------------------------------------------------------------------


def row_id(doc: Doc) -> str:
    return str(doc.get("product_id") or doc.get("id") or doc.get("sku") or "?")


def entries(doc: Doc) -> Iterable[Doc]:
    """The attribute entries of a nested or flat document, and of each nested variant."""
    yield from doc.get("attributes", ())
    for variant in doc.get("variants", ()):
        yield from variant.get("attributes", ())


def color_values(doc: Doc) -> list[str]:
    """Every color the document states: a ``color`` entry, a SKU's color or a color option."""
    out = [
        e["value"] for e in entries(doc) if e.get("key") == "color" and isinstance(e["value"], str)
    ]
    out += [s["color"] for s in doc.get("skus", ()) if isinstance(s.get("color"), str)]
    out += [o["color"] for o in doc.get("color_options", ()) if isinstance(o.get("color"), str)]
    return out


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


def per_row(check: Callable[[Doc], list[str] | None]) -> Callable[[list[Doc]], Report]:
    """A rule of one row at a time: ``None`` means it does not apply to the row."""

    def run(docs: list[Doc]) -> Report:
        seen = 0
        found: list[Finding] = []
        for doc in docs:
            notes = check(doc)
            if notes is None:
                continue
            seen += 1
            found += [(row_id(doc), note) for note in notes]
        return seen, found

    run.__doc__ = check.__doc__
    run.__name__ = check.__name__
    return run


# --------------------------------------------------------------------------------------------
# #444, #446: a range name is a place, never a color
# --------------------------------------------------------------------------------------------

#: Written out here, not read from the generator: the colors a title can claim.
TITLE_COLORS = frozenset({
    "red", "blue", "green", "yellow", "black", "white", "orange", "pink", "purple", "brown",
    "grey", "gray", "navy", "beige", "cream", "ivory", "gold", "silver", "teal", "olive",
})  # fmt: skip
TOY_RANGE_KEYS = ("kite", "play_kitchen", "dolls_house", "card_game", "marble_run", "water_gun")


def range_ids() -> frozenset[str]:
    """The product ids of the class-6 decoys that are named for a place (a range)."""
    from synthetic_ecommerce_data.domains.retail import (
        knitwear_rows,
        mens_depth_rows,
        needs_rows,
        type_registry,
    )

    ids = {
        f"BRD-{d.code}"
        for m in (knitwear_rows, mens_depth_rows, needs_rows)
        for d in m.TABLE
        if d.klass == 6
    }
    specs = type_registry.specs()
    ids |= {f"BRD-{d.row.code}" for key in TOY_RANGE_KEYS for d in specs[key].decoys if d.cls == 6}
    return frozenset(ids)


def color_in_range_name(docs: list[Doc]) -> Report:
    """#444: no place a range is named for, and no title of a range decoy, holds a color word, and
    the text of a range decoy states no color the product does not have. A color in a decoy's
    name is only ever the invented brand (class 7)."""
    from synthetic_ecommerce_data.domains.retail import place_ranges

    ids = range_ids()
    seen, found = _range_docs(ids)(docs)
    for name, gloss in place_ranges.PLACE_RANGES:
        seen += 1
        if words(f"{name} {gloss}") & TITLE_COLORS:
            found.append((name, f"the place {name!r} ({gloss}) holds a color word"))
    return seen, found


def _range_docs(ids: frozenset[str]) -> Callable[[list[Doc]], Report]:
    return per_row(lambda doc: _range_notes(doc, ids))


def _range_notes(doc: Doc, ids: frozenset[str]) -> list[str] | None:
    if doc.get("product_id") not in ids or "skus" not in doc:
        return None
    own = words(" ".join(color_values(doc)))
    notes = []
    if words(doc["title"]) & TITLE_COLORS:
        notes.append(f"the range name {doc['title']!r} holds a color word")
    stray = words(doc.get("description", "")) & TITLE_COLORS - own
    if stray:
        notes.append(f"the description states {sorted(stray)} and the product is {sorted(own)}")
    return notes


# --------------------------------------------------------------------------------------------
# #514: a product of two colors carries one color value, written in words
# --------------------------------------------------------------------------------------------

#: Written out here on purpose: the rule does not read the generator's own word list.
TWO_COLOR = re.compile(r"^[A-Z][a-z]+( [A-Z][a-z]+)? and [A-Z][a-z]+( [A-Z][a-z]+)?$")


@per_row
def blue_and_white(doc: Doc) -> list[str] | None:
    """#514: ``Blue and White``, never ``Blue / White`` and never a list of both colors (a list
    would put a mostly blue product into a White filter)."""
    values = color_values(doc)
    if not values:
        return None
    notes = [
        f"the color {v!r} holds a slash or an ampersand" for v in values if "/" in v or "&" in v
    ]
    notes += [
        f"the color {v!r} is not written 'A and B'"
        for v in values
        if " and " in v and not TWO_COLOR.match(v)
    ]
    notes += [f"the color {v!r} is a list" for v in values if "," in v]
    return notes


# --------------------------------------------------------------------------------------------
# #511: a dress style word beside a neckline, length, sleeve or material its table allows
# --------------------------------------------------------------------------------------------


@per_row
def dress_neckline_by_length(doc: Doc) -> list[str] | None:
    """#511: no title style word ("coat", "wrap", "maxi") sits beside a neckline, length, sleeve
    or material the style table does not allow (decoys included)."""
    from synthetic_ecommerce_data.domains.retail import style_table

    if "skus" not in doc:
        return None
    return list(style_table.violations(doc))


# --------------------------------------------------------------------------------------------
# #499: category nodes and attribute display names are in sentence case
# --------------------------------------------------------------------------------------------


@per_row
def sentence_case(doc: Doc) -> list[str] | None:
    """#499: every category node, the leaf and every attribute display name is its own
    sentence-case form."""
    from synthetic_ecommerce_data.core.letter_case import sentence_case as cased

    if "category_path" not in doc:
        return None
    strings = [*doc["category_path"], doc.get("category_leaf", "")]
    strings += [e["name"] for e in entries(doc) if "name" in e] + list(
        doc.get("attribute_names", ())
    )
    return [f"{s!r} is not {cased(s)!r}" for s in sorted(set(strings)) if s and cased(s) != s]


# --------------------------------------------------------------------------------------------
# #497: one key per concept
# --------------------------------------------------------------------------------------------

#: Keys that restate the product type (the shopper reads the type in the title and the category),
#: or that were two or three spellings of one fact.
REMOVED_KEYS = frozenset({"item", "end_mill_style", "tap_style", "lock_type", "insert_material"})
#: Merged-away key -> the one key that now carries its values.
MERGED_AWAY = {
    "dimension_type": "measurement_system",
    "system_of_measurement": "measurement_system",
    "meets_exceeds": "standards",
    "rockwell_hardness": "hardness",
    "length_under_head": "length",
    "wheel_dia": "diameter",
    "end_mill_application": "application",
    "connector_type": "mounting_type",
    "dowel_dia_in": "dowel_dia",
    "dowel_dia_mm": "dowel_dia",
    "thread_dia": "thread_size",
    "package_quantity": "units_per_pack",
    "number_of_pieces": "piece_count",
}


def one_key_per_concept(docs: list[Doc]) -> Report:
    """#497: no removed or merged-away key is published, and one key has one display name and
    one display name one key."""
    names_of: dict[str, set[str]] = defaultdict(set)
    keys_of: dict[str, set[str]] = defaultdict(set)
    found: list[Finding] = []
    seen = 0
    for doc in docs:
        rows = [e for e in entries(doc) if "key" in e]
        if not rows:
            continue
        seen += 1
        for e in rows:
            if e["key"] in REMOVED_KEYS | set(MERGED_AWAY):
                found.append((row_id(doc), f"the key {e['key']!r} is retired"))
            if "name" in e:
                names_of[e["key"]].add(e["name"])
                keys_of[e["name"]].add(e["key"])
    found += [
        (k, f"the key {k!r} has display names {sorted(n)}")
        for k, n in names_of.items()
        if len(n) > 1
    ]
    found += [
        (n, f"the display name {n!r} has keys {sorted(k)}")
        for n, k in keys_of.items()
        if len(k) > 1
    ]
    return seen, sorted(set(found))


# --------------------------------------------------------------------------------------------
# #420: footwear offers Orange
# --------------------------------------------------------------------------------------------

TRAINER_TYPES = ("Trainers", "Running Shoes")
AUDIENCES = ("Mens", "Womens", "Kids")


def orange_shoes(docs: list[Doc]) -> Report:
    """#420: trainers and running shoes offer Orange as a plain, solid, orange-hued color word on
    at least three styles in each audience, and the Knacks ones are among them."""
    import colorsys

    trainers = [d for d in docs if d.get("product_type") in TRAINER_TYPES and "color_options" in d]
    found: list[Finding] = []
    orange = []
    for d in trainers:
        options = [o for o in d["color_options"] if o["color"] == "Orange"]
        if not options:
            continue
        orange.append(d)
        for o in options:
            h, s, v = colorsys.rgb_to_hsv(
                *(int(o["hex"].lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
            )
            if (
                o.get("family") != "orange"
                or o.get("pattern") != "solid"
                or not (15 <= h * 360 <= 35 and s >= 0.7 and v >= 0.8)
            ):
                found.append((row_id(d), f"Orange is not a solid orange: {o}"))
        if not any(s["in_stock"] for s in d["skus"] if s["color"] == "Orange"):
            found.append((row_id(d), "no Orange SKU exists, or none is in stock"))
    if trainers:
        for audience in AUDIENCES:
            n = sum(1 for d in orange if d["category_path"][0] == audience)
            if n < 3:
                found.append(
                    (audience, f"{n} Orange trainer styles for {audience}, at least 3 wanted")
                )
        knacks = [d for d in orange if d.get("brand") == "Knacks"]
        if {d["product_type"] for d in knacks} != set(TRAINER_TYPES) or {
            d["category_path"][0] for d in knacks
        } != set(AUDIENCES):
            found.append(
                (
                    "Knacks",
                    "the Knacks trainers and running shoes do not offer Orange in each audience",
                )
            )
    return len(orange), found


# --------------------------------------------------------------------------------------------
# #460, #461: a seed query meets decoys that hold every word of it
# --------------------------------------------------------------------------------------------

#: seed phrase -> the product types (#460) or category leaves (#461) the shopper means by it; a
#: decoy of the seed is never one of them.
SEED_TYPES: dict[str, frozenset[str]] = {
    seed: frozenset(kinds)
    for seed, kinds in {
        "high rise jeans": {"Jeans"},
        "skinny jeans": {"Jeans"},
        "jeans": {"Jeans"},
        "barrel trousers": {"Trousers", "Mens Trousers"},
        "tea dress": {"Tea Dress", "Dress"},
        "denim jacket": {"Denim Jacket", "Jacket"},
        "womens boat neck top": {"Top", "Knitted Top", "Blouse", "Tee", "T-Shirt"},
        "pyjamas": {"Pyjamas", "Pyjama Shorts"},
        "leather boots": {"Ankle Boots", "Chelsea Boots", "Chukka Boots", "Knee High Boots",
                          "Safety Boots", "Walking Boots", "Wellies"},
        "running shoes": {"Running Shoes", "Trainers", "Plimsolls"},
        "brogues": {"Brogues"},
        "navy dresses": {"Dress", "Tea Dress"},
        "large dresses": {"Dress", "Tea Dress"},
        "duvet cover": {"Duvet Covers"},
        "mattress topper": {"Mattress Toppers"},
        "bed frame": {"Beds"},
        "tea towels": {"Tea Towels"},
        "lipstick": {"Lipstick"},
        "foundation": {"Foundation"},
        "lemon drizzle cake": {"Cakes"},
        "gift hamper": {"Hampers"},
        "olive tree": {"Olive Trees", "Gift Plants"},
    }.items()
}  # fmt: skip
#: Served by the protectors of gen#155 (distractor_rows): no row of the word table holds it.
SEEDS_SERVED_ELSEWHERE = frozenset({"mattress topper"})
MIN_ROWS_PER_SEED = 2
MAX_TITLE_WORDS = 5


def seed_rows() -> dict[str, list[Any]]:
    """The word-table rows that serve a seed, by seed: a row's ``seeds`` (#460) or ``seed``."""
    from synthetic_ecommerce_data.domains.retail import decoy_product_words as dpw

    by_seed: dict[str, list[Any]] = defaultdict(list)
    for row in dpw.ROWS:
        for seed in (*row.seeds, *([row.seed] if row.seed else [])):
            by_seed[seed].append(row)
    return by_seed


def two_word_seeds(docs: list[Doc]) -> Report:
    """#460, #461: a seed has at least two decoy rows, each holds every word of the seed in its
    title (#461) or its text (#460), is another type than the seed names, has a title of at most
    five words and states no color it does not have."""
    by_id = {d["product_id"]: d for d in docs if "product_id" in d}
    rows = seed_rows()
    found: list[Finding] = []
    seen = 0
    for seed in sorted(set(rows) | set(SEED_TYPES)):
        if seed not in SEED_TYPES:
            found.append((seed, "a row names a seed the pool lacks"))
            continue
        if seed in SEEDS_SERVED_ELSEWHERE:
            continue
        if len(rows.get(seed, ())) < MIN_ROWS_PER_SEED:
            found.append(
                (seed, f"{len(rows.get(seed, ()))} decoy rows, at least {MIN_ROWS_PER_SEED} wanted")
            )
        for row in rows.get(seed, ()):
            doc = by_id.get(f"PLT-{row.code}")
            if doc is None:
                continue
            seen += 1
            found += [(row_id(doc), note) for note in _seed_notes(seed, row, doc)]
    return seen, found


def _seed_notes(seed: str, row: Any, doc: Doc) -> list[str]:
    from synthetic_ecommerce_data.domains.retail.distractors import tokens

    want = set(tokens(seed))
    title = set(tokens(doc["title"]))
    text = title | set(tokens(doc["description"]))
    notes = []
    if not want <= (title if row.seed == seed else text):
        notes.append(
            f"the {'title' if row.seed == seed else 'text'} lacks a word of the seed {seed!r}"
        )
    if {doc["product_type"], doc["category_leaf"]} & SEED_TYPES[seed]:
        notes.append(f"it is a {doc['product_type']}, the type the seed {seed!r} names")
    if len(doc["title"].split()) > MAX_TITLE_WORDS:
        notes.append(f"the title {doc['title']!r} is over {MAX_TITLE_WORDS} words")
    from synthetic_ecommerce_data.domains.retail import decoy_product_words as dpw

    own = {row.color.lower(), *words(" ".join(color_values(doc)))}
    stray = (
        words(f"{doc['title']} {doc['description']}")
        & ({c.lower() for c in dpw.COLORS} - {"clear"}) - own
    )
    if stray:
        notes.append(f"the text states {sorted(stray)}, a color the product does not show")
    return notes


# --------------------------------------------------------------------------------------------
# The registry
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Rule:
    """A rule, the issue that ruled it, the row sets it runs over and the fewest rows it must
    examine in each (a rule that examines nothing proves nothing)."""

    check: Callable[[list[Doc]], Report]
    issue: str
    minimum: dict[str, int]

    @property
    def name(self) -> str:
        return self.check.__name__


RULES: tuple[Rule, ...] = (
    Rule(color_in_range_name, "#444", {"templates": 60}),
    Rule(blue_and_white, "#514", {"templates": 5000, "retail": 200, "retail_flat": 5000}),
    Rule(dress_neckline_by_length, "#511", {"templates": 5000}),
    Rule(
        sentence_case,
        "#499",
        {"retail": 250, "retail_flat": 5000, "golden": 5000, "golden_flat": 8000},
    ),
    Rule(one_key_per_concept, "#497", {"retail": 250, "golden": 5000}),
    Rule(orange_shoes, "#420", {"templates": 9}),
    Rule(two_word_seeds, "#460, #461", {"templates": 40}),
)  # fmt: skip


# --------------------------------------------------------------------------------------------
# The row sets
# --------------------------------------------------------------------------------------------


def _golden(name: str) -> list[Doc]:
    return [json.loads(line) for line in (GOLDEN / name).read_text("utf-8").splitlines()]


def _templates() -> list[Doc]:
    from synthetic_ecommerce_data.domains.retail import scale

    return scale.templates(baseline=False)


def _retail() -> list[Doc]:
    from synthetic_ecommerce_data.domains.retail import export

    return export.documents()


def _retail_flat() -> list[Doc]:
    from synthetic_ecommerce_data.domains.retail import export

    return export.flat_documents()


ROWSETS: dict[str, Callable[[], list[Doc]]] = {
    "templates": _templates,
    "retail": _retail,
    "retail_flat": _retail_flat,
    "golden": lambda: _golden("nested.jsonl"),
    "golden_flat": lambda: _golden("flat.jsonl"),
}


def allow_table() -> dict[str, Any]:
    """``rules_allow.toml``: per rule, ``[[<rule>.allow]]`` entries of ``id`` and ``why``, so an
    exception is a line, with its reason, that a reviewer reads."""
    import tomllib

    return tomllib.loads(ALLOW.read_text("utf-8"))


def allowed() -> dict[str, set[str]]:
    """The ids each rule is excused, by rule name."""
    return {rule: {e["id"] for e in body.get("allow", ())} for rule, body in allow_table().items()}


@dataclass(frozen=True)
class RowSet:
    """A row set the layer above ``domains/`` hands the rules: its loader and, by rule name, the
    fewest rows each rule it is declared for must examine in it (#716)."""

    load: Callable[[], list[Doc]]
    minimum: dict[str, int]


def declared(more: Mapping[str, RowSet] | None = None) -> list[tuple[Rule, str, int]]:
    """``(rule, row set, fewest rows)`` for every rule over every row set it is declared for: by
    the rule over :data:`ROWSETS`, and by each row set of ``more``."""
    by_name = {rule.name: rule for rule in RULES}
    out = [(rule, name, least) for rule in RULES for name, least in rule.minimum.items()]
    for name, rowset in (more or {}).items():
        out += [(by_name[rule], name, least) for rule, least in rowset.minimum.items()]
    return out


def run_all(more: Mapping[str, RowSet] | None = None) -> dict[tuple[str, str], Report]:
    """``{(rule, row set): report}`` for every rule over every row set it is declared for, the
    row sets of ``more`` too."""
    loaders = {**ROWSETS, **{name: rowset.load for name, rowset in (more or {}).items()}}
    loaded: dict[str, list[Doc]] = {}
    out: dict[tuple[str, str], Report] = {}
    for rule, name, _ in declared(more):
        if name not in loaded:
            loaded[name] = loaders[name]()
        out[(rule.name, name)] = rule.check(loaded[name])
    return out
