"""Retail gifts (gen#425): mugs, greeting cards, notebooks, money boxes and pamper hampers.

The Gifts department held photo frames, keyrings, candles, wrapping paper, decorations and bags,
and a search for a mug, a birthday card, a notebook or a money box found nothing. Five specs
(:mod:`type_specs.gift_mug`, ``greeting_card``, ``notebook``, ``money_box``, ``gift_hamper``) add
them, drawn by :mod:`kit_gifts`. These checks hold what the issue asked for: two styles from two
brands per type, structured key attributes, a shape of its own whose params change the drawing,
the six main colors (gen#275) with no exception, a place in the tree, each query shape ranking the
intended type first on the export, at least 150 new SKUs, and the text-match decoys of the
gen#294 rule (rows of the class-8 table of :mod:`decoy_product_words`, each tagged with the Gifts
type whose word its title holds).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_product_words as dpw  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import kit_gifts  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402
from distractors import tokens  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROOT = "Gifts"
#: spec key -> (product type, path, the structured entries every style states).
TYPES = {
    "gift_mug": ("Mug", ("Gifts", "Mugs & Drinkware"),
                 {"material", "capacity", "design", "dishwasher_safe", "color"}),
    "greeting_card": ("Greeting Card", ("Gifts", "Cards", "Greeting Cards"),
                      {"occasion", "recipient", "blank_inside", "color"}),
    "notebook": ("Notebook", ("Gifts", "Stationery", "Notebooks"),
                 {"page_size", "ruling", "cover", "color"}),
    "money_box": ("Money Box", ("Gifts", "Kids' Gifts", "Money Boxes"),
                  {"material", "shape", "color"}),
    "gift_hamper": ("Gift Hamper", ("Gifts", "Gift Sets", "Pamper Hampers"),
                    {"contents_kind", "items", "color"}),
}  # fmt: skip
#: shape -> param -> the values the drawing tells apart.
PARAMS = {
    "gift_mug": {"design": ("slogan", "initial", "pattern", "plain"),
                 "material": ("ceramic", "stoneware", "enamel")},
    "greeting_card": {"occasion": ("birthday", "anniversary", "thank_you", "wedding", "new_baby",
                                   "christmas")},
    "notebook": {"ruling": ("lined", "dotted", "plain"),
                 "cover": ("hardback", "softback", "leather")},
    "money_box": {"form": ("pig", "rocket", "house"), "material": ("ceramic", "tin", "wood")},
    "gift_hamper": {"contents": ("bath_body", "candle_diffuser", "sock_slipper")},
}  # fmt: skip
#: query -> the styles (codes) that may rank first: the intended type and attributes.
QUERIES = {
    "birthday card for mum": {"GCDMUM"},
    "thank you card": {"GCTHNK"},
    "wedding card": {"GCWEDD"},
    "ceramic mug 350 ml": {"GMGSLOG"},
    "personalised initial mug": {"GMGINIT"},
    "a5 dotted notebook": {"GNBA5DH"},
    "leather journal": {"GNBA5LL", "GNBA5DL"},
    "pig money box": {"GMBPIGC", "GMBPIGT"},
    "pamper hamper": {"GHPBATL", "GHPBATM", "GHPCAND", "GHPSOCK"},
}  # fmt: skip
COLOR_WORDS = {c.lower() for c in dpw.COLORS} - {"clear"}  # glass is clear, not a color


def _spec_rows(key: str) -> tuple:
    spec = type_registry.specs().get(key)
    return spec.rows if spec else ()


ALL_ROWS = tuple(r for key in TYPES for r in _spec_rows(key))
IDS = frozenset(f"BRD-{r.code}" for r in ALL_ROWS)


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _svg(row, **override) -> str:
    return kit.render(
        row.shape, kit.Fill("solid", "#123456", "#654321"), params={**dict(row.params), **override}
    )


@pytest.mark.parametrize("key", TYPES)
def test_each_type_has_two_styles_from_two_brands(key: str) -> None:
    rows = _spec_rows(key)
    assert rows, key
    assert len(rows) >= 2 and len({r.brand for r in rows}) >= 2, key


@pytest.mark.parametrize("key", TYPES)
def test_each_type_is_a_gifts_template_of_its_own(key: str) -> None:
    ptype, path, _ = TYPES[key]
    rows = _spec_rows(key)
    assert rows, key
    assert {r.department for r in rows} == {ROOT}
    assert {r.product_type for r in rows} == {ptype}
    assert {tuple(r.path) for r in rows} == {path}
    docs = [d for d in scale.templates() if d["product_id"] in {f"BRD-{r.code}" for r in rows}]
    assert len(docs) == len(rows), key
    assert not type_registry.specs()[key].derivable


@pytest.mark.parametrize("key", TYPES)
def test_every_key_attribute_is_a_structured_entry_in_the_export(key: str) -> None:
    rows = _spec_rows(key)
    assert rows, key
    missing = {}
    for row in rows:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if TYPES[key][2] - keys:
            missing[row.code] = sorted(TYPES[key][2] - keys)
    assert missing == {}


def test_a_mug_states_its_capacity_in_millilitres() -> None:
    rows = _spec_rows("gift_mug")
    assert rows
    for row in rows:
        entries = [
            e for e in export.standard_document(row.doc())["attributes"] if e["key"] == "capacity"
        ]
        assert [e["unit_code"] for e in entries] == ["MLT"], row.code
        assert [e["value_canonical"] for e in entries] and all(
            isinstance(e["value_canonical"], float) and e["value_canonical"] >= 250 for e in entries
        ), row.code
        # the description states the same capacity as the entry (one fact, said twice)
        assert f"{entries[0]['value_canonical']:g} ml" in row.description, row.code


def test_a_card_for_a_person_names_that_person_in_title_and_description() -> None:
    """The recipient entry, the title and the description say one fact, three times."""
    rows = _spec_rows("greeting_card")
    assert rows
    named = 0
    for row in rows:
        recipient = {e[0]: e[2] for e in row.attrs}["recipient"]
        if recipient == "Any":
            continue
        named += 1
        assert recipient.lower() in row.title.lower(), row.code
        assert recipient.lower() in row.description.lower(), row.code
    assert named >= 3


#: hamper code -> the number of items its description lists (a bundle counts as written).
HAMPER_ITEMS = {"GHPBATL": 7, "GHPBATM": 4, "GHPCAND": 3, "GHPSOCK": 4}


def test_a_hamper_item_count_matches_the_items_its_description_lists() -> None:
    rows = _spec_rows("gift_hamper")
    assert {r.code for r in rows} == set(HAMPER_ITEMS)
    for row in rows:
        assert int({e[0]: e[2] for e in row.attrs}["items"]) == HAMPER_ITEMS[row.code], row.code


@pytest.mark.parametrize("key", TYPES)
def test_each_type_draws_as_its_own_gifts_shape(key: str) -> None:
    rows = _spec_rows(key)
    assert rows, key
    shapes = {r.shape for r in rows}
    assert len(shapes) == 1 and shapes <= set(kit_gifts.SHAPES), key
    assert shapes.isdisjoint(
        {s for k in TYPES if k != key for s in {r.shape for r in _spec_rows(k)}}
    ), key


@pytest.mark.parametrize("key", TYPES)
def test_every_param_value_changes_the_drawing(key: str) -> None:
    rows = _spec_rows(key)
    assert rows, key
    for row in rows:
        for param, values in PARAMS[row.shape].items():
            assert dict(row.params)[param] in values, (row.code, param)
            drawn = {v: _svg(row, **{param: v}) for v in values}
            assert len(set(drawn.values())) == len(values), (row.code, param)


#: spec key -> (attribute key, drawing param, attribute value -> param value).
PARAM_OF_ATTR = {
    "gift_mug": (("design", "design"), ("material", "material")),
    "greeting_card": (("occasion", "occasion"),),
    "notebook": (("ruling", "ruling"), ("cover", "cover")),
    "money_box": (("shape", "form"), ("material", "material")),
    "gift_hamper": (("contents_kind", "contents"),),
}
SPELLED = {
    "leather-effect": "leather",
    "bath and body": "bath_body",
    "candle and diffuser": "candle_diffuser",
    "sock and slipper": "sock_slipper",
}


@pytest.mark.parametrize("key", TYPES)
def test_the_drawing_params_state_the_same_facts_as_the_attributes(key: str) -> None:
    """A drawing shows what the row says: a wooden rocket is drawn as wood, not as tin."""
    rows = _spec_rows(key)
    assert rows, key
    for row in rows:
        attrs = {e[0]: e[2] for e in row.attrs}
        for attr_key, param in PARAM_OF_ATTR[key]:
            said = attrs[attr_key].lower()
            drawn = SPELLED.get(said, said.replace(" ", "_"))
            assert dict(row.params)[param] == drawn, (row.code, attr_key, said)


def test_the_money_box_draws_one_coin_slot_in_every_form() -> None:
    rows = _spec_rows("money_box")
    assert rows
    for form in PARAMS["money_box"]["form"]:
        svg = _svg(rows[0], form=form)
        assert len(re.findall(r'class="slot"', svg)) == 1, form


def test_a_drawing_prints_no_capacity_size_or_price() -> None:
    assert ALL_ROWS
    for row in ALL_ROWS:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        assert not [w for w in words if re.search(r"\d", w)], row.code


@pytest.mark.parametrize("key", TYPES)
def test_each_type_offers_the_six_main_colors_with_no_exception(key: str) -> None:
    ptype = TYPES[key][0]
    rows = _spec_rows(key)
    assert rows, key
    assert ptype not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in rows for c in r.colors}


def test_each_type_sits_in_the_tree_under_the_guards_rules() -> None:
    assert ALL_ROWS
    paths = [tuple(r.path) for r in ALL_ROWS]
    assert {p for p in paths} == {t[1] for t in TYPES.values()}
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in ALL_ROWS]
    assert tree_guard.misplaced_title_findings(rows) == []


def test_the_department_grows_by_at_least_150_skus() -> None:
    assert ALL_ROWS
    assert sum(len(r.skus()) for r in ALL_ROWS) >= 150


@pytest.mark.timeout(300)
def test_the_styles_reach_the_100k_build_once_and_meet_the_standard() -> None:
    assert ALL_ROWS
    docs = [d for d in scale.documents(scale.build(100_000)) if d["product_id"] in IDS]
    assert sorted(d["product_id"] for d in docs) == sorted(IDS)
    assert check_catalog(docs, one_class_per_key=True) == []
    assert {d["category_path"][0] for d in docs} == {ROOT}


def _shopper_view(index: br.Index, query: str) -> list[dict]:
    """The results after the policies that fix the class-8 decoys: the department policy keeps
    Gifts, the category policy drops the decoy that sits in Gifts (:data:`dpw.BY_ID`)."""
    return [
        d
        for d in br.rank(index, query, 1000)
        if d["category_path"][0] == ROOT and d["product_id"] not in dpw.BY_ID
    ]


@pytest.mark.parametrize("query", QUERIES)
def test_each_query_shape_ranks_the_intended_type_first(index: br.Index, query: str) -> None:
    top = _shopper_view(index, query)[:5]
    assert top, query
    assert top[0]["product_id"] in {f"BRD-{c}" for c in QUERIES[query]}, (
        query,
        [(d["product_id"], d["title"]) for d in top],
    )


# -- the text-match decoys (the rule of gen#294, the class-8 table of gen#326) -----------------


def _rows(ptype: str) -> list[dpw.Row]:
    return [r for r in dpw.TABLE if r.gift_type == ptype]


@pytest.mark.parametrize("key", TYPES)
def test_each_type_has_at_least_two_decoys(key: str) -> None:
    ptype = TYPES[key][0]
    rows = _rows(ptype)
    assert len(rows) >= 2, (ptype, len(rows))
    assert all(r.decoy and r.policy and r.query for r in rows), ptype


@pytest.mark.parametrize("key", TYPES)
def test_each_decoy_holds_the_shoppers_word_and_is_another_product(
    by_id: dict[str, dict], key: str
) -> None:
    ptype, path, _ = TYPES[key]
    rows = _rows(ptype)
    assert rows, ptype
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        assert row.noun in tokens(doc["title"]), (row.code, doc["title"])
        assert set(tokens(row.query)) <= set(tokens(doc["title"] + " " + doc["description"]))
        assert doc["product_type"] != ptype, row.code
        assert path[-1] not in doc["category_path"], row.code
        assert len(doc["title"].split()) <= 5, doc["title"]
        # the department policy drops a decoy of another department; the one that sits in Gifts
        # is fixed by the category policy
        assert (doc["category_path"][0] == ROOT) == (row.policy == "category"), row.code


@pytest.mark.parametrize("key", TYPES)
def test_a_gifts_decoy_names_no_color_word_the_drawing_does_not_show(
    by_id: dict[str, dict], key: str
) -> None:
    rows = _rows(TYPES[key][0])
    assert rows, key
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        words = set(re.findall(r"[a-z]+", f"{doc['title']} {doc['description']}".lower()))
        assert not words & COLOR_WORDS, (row.code, words & COLOR_WORDS)


def test_every_gifts_decoy_can_be_found_by_its_query_word(
    index: br.Index, by_id: dict[str, dict]
) -> None:
    rows = [r for r in dpw.TABLE if r.gift_type]
    assert len(rows) >= 2 * len(TYPES)
    missing = []
    for row in rows:
        found = {d["product_id"] for d in br.rank(index, row.query, 1000)}
        if f"PLT-{row.code}" not in found:
            missing.append((row.code, row.query))
    assert not missing, missing


def test_the_decoys_name_exactly_the_gifts_types_of_the_live_catalog(
    ceiling: list[dict],
) -> None:
    """A census over the live catalog: a Gifts type of this issue without decoys reds here."""
    live = {r["product_type"] for r in ceiling if r["category_path"][0] == ROOT}
    mine = {t[0] for t in TYPES.values()}
    assert mine <= live
    # the gift card (gen#424) is the one Gifts type outside TYPES that carries decoys (gen#437)
    assert {r.gift_type for r in dpw.TABLE if r.gift_type} == mine | {"Gift Card"}
