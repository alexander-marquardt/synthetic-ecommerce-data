"""Toys depth (gen#424): kites, play kitchens, dolls' houses, card games, marble runs, water guns.

The Toys department had a few of each of these under other leaves and none drawn as its own
shape. Six type specs (:mod:`type_specs`) now hold them, :mod:`kit_toys_play` draws them. Every
check below runs once per type, so a type that loses a rule reds under its own key. The lookups
assert the key is registered, so a missing spec fails on an assertion, not on an import.
"""

from __future__ import annotations

import re
import sys
import xml.dom.minidom
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROOT = "Toys"
#: key -> the leaf path, the product type, the structured entries every row states (key -> unit
#: code, None for a text entry), the SKU axis and the drawing param the tests turn.
TYPES = {
    "kite": dict(
        path=("Toys", "Outdoor Toys", "Kites"), ptype="Kite", axis="color",
        entries={"toy_type": None, "span": "CMT", "age_range": None},
        turn=("kind", "diamond", "delta"), colored=True),
    "play_kitchen": dict(
        path=("Toys", "Pretend Play", "Play Kitchens"), ptype="Play Kitchen", axis="color",
        entries={"toy_type": None, "material": None, "item_height": "CMT", "has_sink": None,
                 "oven_door": None, "lights_and_sounds": None, "age_range": None},
        turn=("sink", "yes", "no"), colored=True),
    "dolls_house": dict(
        path=("Toys", "Dolls & Accessories", "Dolls' Houses"), ptype="Dolls' House",
        axis="house_style",
        entries={"toy_type": None, "rooms": "C62", "floors": "C62", "furniture_included": None,
                 "material": None, "age_range": None},
        turn=("floors", "2", "3"), colored=False),
    "card_game": dict(
        path=("Toys", "Games", "Card Games"), ptype="Card Game", axis="edition",
        entries={"toy_type": None, "min_players": "C62", "max_players": "C62",
                 "play_time": None, "age_range": None},
        turn=("kind", "family", "party"), colored=False),
    "marble_run": dict(
        path=("Toys", "Building & Construction", "Marble Runs"), ptype="Marble Run",
        axis="piece_count",
        entries={"toy_type": None, "material": None, "age_range": None},
        turn=("tiers", "3", "4"), colored=False),
    "water_gun": dict(
        path=("Toys", "Outdoor Toys", "Water Toys"), ptype="Water Gun", axis="color",
        entries={"toy_type": None, "tank_capacity": "MLT", "water_range": "MTR",
                 "age_range": None},
        turn=("kind", "pistol", "blaster"), colored=True),
}
KEYS = tuple(TYPES)
#: query -> the product types that may answer it in the Toys department. The older Role Play Toys
#: kitchens also hold "play kitchen".
QUERIES = {
    "kite": {"Kite"},
    "stunt kite": {"Kite"},
    "play kitchen": {"Play Kitchen", "Role Play Toy"},
    "dolls house": {"Dolls' House"},
    "card game": {"Card Game", "Board Game"},
    "party card game": {"Card Game", "Board Game"},
    "marble run": {"Marble Run"},
    "water gun": {"Water Gun"},
    "blaster water gun": {"Water Gun"},
}
#: query -> the cross-department decoy types the unfiltered ranking puts beside the answer.
DECOYS = {
    "play kitchen": {"Kitchen Roll", "Kitchen Scales"},
    "card game": {"Greeting Card", "Gift Card"},
    "water gun": {"Glue Gun", "Caulking Gun"},
}
#: spec key -> (the toy word its class-8 decoys hold, the Toys leaf that word names).
DECOY_SPECS = {
    "kitchen_roll": ("kitchen", "Play Kitchens"),
    "kitchen_scales": ("kitchen", "Play Kitchens"),
    "greeting_card": ("card", "Card Games"),
    "gift_card": ("card", "Card Games"),
    "glue_gun": ("gun", "Water Toys"),
    "caulking_gun": ("gun", "Water Toys"),
}
SPECS = type_registry.specs()


def _spec(key: str):
    assert key in SPECS, f"no type spec {key!r}"
    return SPECS[key]


def _ids(key: str) -> frozenset[str]:
    return frozenset(f"BRD-{r.code}" for r in _spec(key).rows)


def _svg(row, **override) -> str:
    params = {**dict(row.params), **override}
    return kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=params)


@pytest.mark.parametrize("key", KEYS)
def test_the_type_is_registered_in_the_toys_department_at_its_leaf(key) -> None:
    spec = _spec(key)
    cfg = TYPES[key]
    assert spec.department == ROOT and spec.product_type == cfg["ptype"]
    assert spec.rows and {tuple(r.path) for r in spec.rows} == {cfg["path"]}
    assert {r.product_type for r in spec.rows} == {cfg["ptype"]}
    docs = [d for d in scale.templates() if d["product_id"] in _ids(key)]
    assert len(docs) == len(spec.rows)
    assert {d["category_path"][0] for d in docs} == {ROOT}


@pytest.mark.parametrize("key", KEYS)
def test_the_type_has_two_styles_from_two_brands(key) -> None:
    rows = _spec(key).rows
    assert len(rows) >= 2 and len({r.brand for r in rows}) >= 2


@pytest.mark.parametrize("key", KEYS)
def test_the_type_draws_as_its_own_shape(key) -> None:
    rows = _spec(key).rows
    assert {r.shape for r in rows} == {key}
    assert key in kit.SHAPES


@pytest.mark.parametrize("key", KEYS)
def test_every_key_attribute_is_a_structured_entry_with_its_unit(key) -> None:
    rows = _spec(key).rows
    assert rows
    for row in rows:
        doc = export.standard_document(row.doc())
        found = {e["key"]: e for e in doc["attributes"]}
        for v in doc["variants"]:
            found.update({e["key"]: e for e in v["attributes"]})
        for entry, unit in TYPES[key]["entries"].items():
            assert entry in found, (row.code, entry)
            if unit:
                assert found[entry].get("unit_code") == unit, (row.code, entry)
                assert isinstance(found[entry].get("value_canonical"), float) or unit == "C62", (
                    row.code, entry)


@pytest.mark.parametrize("key", KEYS)
def test_the_sku_axis_is_the_one_the_type_sells_by(key) -> None:
    rows = _spec(key).rows
    axis = TYPES[key]["axis"]
    assert rows
    for row in rows:
        skus = row.skus()
        assert len(skus) >= 2, row.code
        if axis == "color":
            assert not row.sizes and len({s["color"] for s in skus}) == len(skus), row.code
        else:
            assert row.size_key == axis and len(row.sizes) >= 2, row.code
            doc = export.standard_document(row.doc())
            keys = {e["key"] for v in doc["variants"] for e in v["attributes"]}
            assert export.OPTIONS[axis][0] in keys, (row.code, keys)


@pytest.mark.parametrize("key", [k for k in KEYS if TYPES[k]["colored"]])
def test_the_type_offers_the_six_main_colors_with_no_exception(key) -> None:
    rows = _spec(key).rows
    assert TYPES[key]["ptype"] not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in rows for c in r.colors}
    styles = [d for d in scale.templates() if d["product_id"] in _ids(key)]
    assert main_colors.missing(styles) == {}


@pytest.mark.parametrize("key", KEYS)
def test_a_param_changes_the_drawing_and_the_first_reading_is_the_default(key) -> None:
    rows = _spec(key).rows
    name, first, other = TYPES[key]["turn"]
    row = next(r for r in rows if dict(r.params).get(name) == first or name not in dict(r.params))
    one, two = _svg(row, **{name: first}), _svg(row, **{name: other})
    assert one != two
    plain = {k: v for k, v in dict(row.params).items() if k != name}
    assert kit.render(key, kit.Fill("solid", "#123456", "#654321"), params=plain) == one


@pytest.mark.parametrize("key", KEYS)
def test_every_style_draws_well_formed_svg_and_prints_no_number(key) -> None:
    rows = _spec(key).rows
    assert rows
    for row in rows:
        svg = _svg(row)
        xml.dom.minidom.parseString(svg)
        words = re.findall(r"<text[^>]*>([^<]*)</text>", svg)
        assert [w for w in words if re.search(r"\d", w)] == [], row.code


@pytest.mark.parametrize("key", KEYS)
def test_the_type_sits_in_the_tree_under_the_guards_rules(key) -> None:
    rows = _spec(key).rows
    paths = [tuple(r.path) for r in rows]
    assert paths
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    triples = [(f"BRD-{r.code}", r.title, r.path) for r in rows]
    assert tree_guard.misplaced_title_findings(triples) == []


@pytest.mark.parametrize("key", KEYS)
def test_the_type_is_left_out_of_the_derivation(key) -> None:
    spec = _spec(key)
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not spec.derivable
    assert _ids(key) and not (_ids(key) & kept)


def test_the_six_types_add_at_least_150_skus() -> None:
    n = sum(len(r.skus()) for k in KEYS for r in _spec(k).rows)
    assert n >= 150, n


@pytest.fixture(scope="module")
def build_100k() -> list[dict]:
    return scale.documents(scale.build(100_000))


@pytest.mark.timeout(300)
@pytest.mark.parametrize("key", KEYS)
def test_the_type_reaches_the_100k_build_and_meets_the_standard(key, build_100k) -> None:
    ids = _ids(key)
    assert ids
    mine = [d for d in build_100k if d["product_id"] in ids]
    assert len(mine) == len(ids)
    assert check_catalog(mine, one_class_per_key=True) == []
    assert {d["category_path"][0] for d in mine} == {ROOT}


@pytest.fixture(scope="module")
def index() -> br.Index:
    return br.Index(scale.build(10**6).records)


@pytest.mark.timeout(300)
@pytest.mark.parametrize("query", QUERIES)
def test_the_toys_department_answers_the_query_with_the_intended_type(query, index) -> None:
    """The department policy drops the other departments' products; what is left holds the type
    this issue adds, in the first ten hits."""
    assert all(k in SPECS for k in KEYS), "a type is not registered"
    toys = br.Index([d for d in index.catalog if d["category_path"][0] == ROOT])
    hits = br.rank(toys, query, 10)
    assert hits, query
    got = [h["product_type"] for h in hits]
    assert set(got) & QUERIES[query], got
    assert set(got) & {t["ptype"] for t in TYPES.values()}, got


@pytest.mark.timeout(300)
@pytest.mark.parametrize("query", DECOYS)
def test_an_unfiltered_ranking_puts_a_decoy_beside_the_answer(query, index) -> None:
    """The window is the first 20 hits: the toys' own decoys (DECOY_PINS) share the top ten."""
    got = {h["product_type"] for h in br.rank(index, query, 20)}
    assert got & DECOYS[query], got


@pytest.mark.parametrize("key", DECOY_SPECS)
def test_a_toy_word_decoy_is_a_class_8_row_of_its_spec_outside_the_toys_department(key) -> None:
    """The decoy is the spec's own row (gen#351), titled with the toy word and sold in a leaf that
    is not the Toys leaf the word names, so the department policy drops it."""
    word, leaf = DECOY_SPECS[key]
    spec = _spec(key)
    assert spec.decoys, key
    for d in spec.decoys:
        assert d.cls == 8 and d.query == word, (d.row.code, d.cls, d.query)
        assert word in re.findall(r"[a-z]+", d.row.title.lower()), d.row.title
        assert d.row.path[0] == d.row.department != ROOT, d.row.path
        assert leaf not in d.row.path, d.row.path
        assert (d.row.department, d.row.product_type) == (spec.department, spec.product_type)
        assert d.row.code.startswith("DT"), d.row.code


#: spec key -> {decoy code: (class, the query it targets)}: the text-match decoys of gen#294 that
#: each toy type carries. A class 4 names a material or feature the product lacks, a class 6 holds
#: a color word or another toy's word as a range name, a class 7 holds another toy's word in its
#: brand. Every toy type carries all three, as the gen#311 rule asks of every type.
DECOY_PINS = {
    "kite": {
        "DT08": (6, "red kite"), "DT09": (6, "card game"), "DT10": (4, "silk kite"),
        "DT11": (7, "marble run")},
    "play_kitchen": {
        "DT12": (6, "green play kitchen"), "DT13": (6, "water gun"),
        "DT14": (4, "wooden play kitchen"), "DT15": (7, "card game")},
    "dolls_house": {
        "DT16": (6, "yellow dolls house"), "DT17": (6, "kite"),
        "DT18": (4, "wooden dolls house"), "DT19": (7, "kite")},
    "card_game": {
        "DT20": (6, "black card game"), "DT21": (6, "marble run"),
        "DT22": (4, "foil card game"), "DT23": (7, "water gun")},
    "marble_run": {
        "DT24": (6, "white marble run"), "DT25": (6, "dolls house"),
        "DT26": (4, "wooden marble run"), "DT27": (7, "play kitchen")},
    "water_gun": {
        "DT28": (6, "blue water gun"), "DT29": (6, "play kitchen"),
        "DT30": (4, "neon water gun"), "DT31": (7, "dolls house")},
}
PINNED = [(k, c) for k, pins in DECOY_PINS.items() for c in pins]
MATERIAL_CLAIM = "special: material claim"


def _decoy(key: str, code: str):
    found = {d.row.code: d for d in _spec(key).decoys}
    assert code in found, f"{key} has no decoy {code}: it holds {sorted(found)}"
    return found[code]


@pytest.mark.parametrize("key", KEYS)
def test_every_toy_spec_carries_its_pinned_decoys_and_all_three_classes(key) -> None:
    """Each toy type declares exactly the pinned decoys, a class 4, 6 and 7 among them and at
    least two of class 6, as the gen#311 rule asks of every type."""
    got = {d.row.code: (d.cls, d.query) for d in _spec(key).decoys if d.cls != 8}
    assert got == DECOY_PINS[key], got
    classes = [c for c, _ in got.values()]
    assert {4, 6, 7} <= set(classes) and classes.count(6) >= 2, classes


@pytest.mark.parametrize(("key", "code"), PINNED)
def test_a_toy_decoy_is_a_row_of_its_type_in_the_toys_leaf_that_holds_its_word(key, code) -> None:
    """The decoy is a Toys row of its own type and leaf, so the department policy keeps it and
    only the type policy repairs it. Its short title holds the query's words (class 6 and 7) or
    names a material or feature its structured entries lack (class 4)."""
    spec, d = _spec(key), _decoy(key, code)
    row, title = d.row, set(re.findall(r"[a-z]+", d.row.title.lower()))
    assert (row.department, row.product_type) == (spec.department, spec.product_type)
    assert row.path == TYPES[key]["path"] and row.code.startswith("DT"), row.path
    assert d.policy, code
    words = d.query.split()
    if d.cls == 4:
        assert d.policy == MATERIAL_CLAIM, d.policy
        assert "-" in row.title and words[0] in title, row.title
        facts = " ".join(str(v).lower() for _, _, v, *_ in row.attrs)
        assert words[0] not in facts, (words[0], facts)
    else:
        assert set(words) <= title and len(row.title.split()) <= 5, (row.title, d.query)
    if d.cls == 6 and words[0] in ("red", "green", "yellow", "black", "white", "blue"):
        assert row.colors[0][0].lower() != words[0], "the color word names a range, not the color"
    if d.cls == 7:
        assert row.brand in row.title and set(words) <= set(row.brand.lower().split()), row.brand
        assert dict(spec.owners).get(row.brand) == "own", spec.owners


@pytest.mark.timeout(300)
@pytest.mark.parametrize(("key", "code"), PINNED)
def test_an_unfiltered_ranking_puts_each_toy_decoy_among_the_hits_of_its_query(
    key, code, index
) -> None:
    """The decoy is in the build and the ranking finds it for the query it targets (the first 50
    hits), so the policy that repairs it has something to repair."""
    d = _decoy(key, code)
    ids = [h["product_id"] for h in br.rank(index, d.query, 50)]
    assert f"BRD-{code}" in ids, (d.query, ids[:10])
