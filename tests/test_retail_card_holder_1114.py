"""Women's card holders, a type of their own under ``Womens > Accessories > Purses & Wallets`` (gen#1114).

The catalog's card holders were four styles of other types: two Purse styles whose ``purse_type`` is
Card Holder and two men's Wallet styles. A shopper who looked for a card holder found no leaf for it.
Card Holder is now a derivable spec with its own drawing (``card_holder``, a slim, zip or bifold case
whose surface shows the material). A style's SKUs are its colors. These checks hold the leaf, the six
main colors, the drawing, the text-match decoys, the range at the ceiling build, the rule that a
derived style keeps the form, closure, card slots and RFID blocking its text and drawing show, and
the demo query of the PR. The four older styles stay where they are.
"""

# ruff: noqa: E501 -- the long comprehensions read better whole.

from __future__ import annotations

import importlib
import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core.letter_case import sentence_case
from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import (
    audience,
    facet_leaves,
    kit,
    line_grammar,
    main_colors,
    scale,
    scale_text,
    type_registry,
)

KEY, PTYPE, SHAPE = "card_holder", "Card Holder", "card_holder"
PATH = ("Womens", "Accessories", "Purses & Wallets", "Card Holders")
FORMS = {"Slim", "Zip", "Bifold"}
MATERIALS = {"Leather", "Faux Leather", "Suede", "Canvas"}
#: The attributes a derived style keeps from its template (the text and the drawing follow them).
BUILD_KEYS = {"holder_style", "closure", "card_slots", "rfid_blocking"}
#: The SKUs the ceiling build (seed 0) holds at least.
FLOOR = 150
#: The PR's demo query -> the material a matching style holds.
QUERY, QUERY_MATERIAL = "leather card holder", "Leather"


def _values(row) -> dict[str, str]:  # noqa: ANN001
    return {a[0]: str(a[2]) for a in row.attrs}


@pytest.fixture(scope="module")
def spec() -> type_registry.TypeSpec | None:
    # None while the type is missing, so a test that reads it fails on its own assertion, not in setup.
    return type_registry.specs().get(KEY)


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def _mine(ceiling) -> list[dict]:
    return [r for r in ceiling.records if r["product_type"] == PTYPE]


def test_the_type_is_a_derivable_leaf_of_its_own_under_purses_and_wallets(spec) -> None:
    assert spec is not None, f"{KEY} is not a registered type"
    assert spec.product_type == PTYPE and spec.derivable
    assert len(spec.rows) >= 4 and len({r.brand for r in spec.rows}) >= 3
    for row in (*spec.rows, *(d.row for d in spec.decoys)):
        values = _values(row)
        assert row.path == PATH, row.code
        assert row.shape == SHAPE and SHAPE in kit.shapes(), row.code
        assert dict(row.params) == {k: values[k].lower() for k in ("holder_style", "material")}, (
            row.code
        )
        assert values["audience"] == audience.WOMENS, row.code
        assert values["rfid_blocking"] in {"Yes", "No"} and int(values["card_slots"]) > 0, row.code
    for row in spec.rows:  # the title shows the form and the material
        values = _values(row)
        assert values["holder_style"] in row.title and values["material"] in row.title, row.code
    assert {_values(r)["holder_style"] for r in spec.rows} == FORMS
    assert {_values(r)["material"] for r in spec.rows} == MATERIALS


def test_the_type_offers_the_six_main_colors_with_no_exception(spec) -> None:
    assert PTYPE not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in spec.rows for c in r.colors}


def test_each_form_and_each_material_draws_a_different_figure(spec) -> None:
    fill = kit.Fill("solid", "#c8312e", "#2a2a2e")
    drawn = {(f, m): kit.render(SHAPE, fill, uid="f", params={"holder_style": f.lower(), "material": m.lower()})
             for f in FORMS for m in MATERIALS}  # fmt: skip
    assert len(set(drawn.values())) == len(drawn)


def test_a_card_holder_is_no_garment_so_its_material_is_no_fabric(spec) -> None:
    for row in spec.rows:
        rec = {"department": [row.department], "product_type": row.product_type}
        assert not facet_leaves.is_textile(rec), row.code


def test_the_family_names_the_type_and_no_lead_word_is_in_any_template_text() -> None:
    assert line_grammar.family({"product_type": PTYPE}) == "card_holder"
    family = importlib.import_module(
        "synthetic_ecommerce_data.domains.retail.line_grammar_families.card_holder"
    )
    words = line_grammar.text_words(scale.templates(baseline=False))
    assert [w for w in family.LEADS if w.lower() in words] == []


def test_the_type_plants_text_match_decoys(spec) -> None:
    decoys = spec.decoys
    assert len(decoys) >= 3
    assert any(d.cls == 6 for d in decoys), "no incidental-word decoy (class 6)"
    for d in decoys:  # the text holds the query's word and the entries say another value
        word = d.query.split()[0]
        assert word in f"{d.row.title} {d.row.description}".lower(), d.row.code
        stated = {_values(d.row)["material"].lower(), *(c[0].lower() for c in d.row.colors)}
        assert word not in stated, d.row.code


def test_the_ceiling_holds_the_range(ceiling) -> None:
    assert sum(r["sku_count"] for r in _mine(ceiling)) >= FLOOR


def test_a_template_offers_no_build_key_for_a_derived_style_to_change(ceiling) -> None:
    authored = [r for r in _mine(ceiling) if r["product_id"] not in ceiling.template_of]
    assert authored
    pools = scale_text.value_pools(authored)
    offered = {k for r in authored for k in scale_text.variable_keys(r, pools)}
    assert offered & BUILD_KEYS == set()
    assert "material" in offered


def test_a_derived_style_keeps_the_form_and_draws_the_material_it_states(ceiling) -> None:
    by_id = {r["product_id"]: r for r in ceiling.records}
    derived = [r for r in _mine(ceiling) if r["product_id"] in ceiling.template_of]
    assert derived
    wrong = []
    for r in derived:
        new = {a["key"]: str(a["value"]) for a in r["attributes"]}
        old = {
            a["key"]: str(a["value"])
            for a in by_id[ceiling.template_of[r["product_id"]]]["attributes"]
        }
        params = r["drawing"]["params"]
        if any(new.get(k) != old.get(k) for k in BUILD_KEYS):
            wrong.append((r["title"], "build"))
        if (
            params["material"] != new["material"].lower()
            or params["holder_style"] != new["holder_style"].lower()
        ):
            wrong.append((r["title"], "drawing"))
        if not re.search(rf"\b{new['material']}\b", r["title"]):
            wrong.append((r["title"], "title"))
    assert wrong == []


def test_census_the_type_meets_the_output_standard_under_purses_and_wallets(ceiling) -> None:
    mine = _mine(ceiling)
    assert mine
    docs = scale.documents(scale.Scaled(mine, {}))
    assert check_catalog(docs, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    assert {tuple(d["category_path"]) for d in docs} == {tuple(map(sentence_case, PATH))}
    titles = [r["title"] for r in mine]
    assert len(set(titles)) == len(titles)


def test_the_demo_query_has_matching_styles_and_a_decoy_to_tell_apart(spec, ceiling) -> None:
    match = [
        r
        for r in _mine(ceiling)
        if any(a["key"] == "material" and a["value"] == QUERY_MATERIAL for a in r["attributes"])
    ]
    assert len(match) >= 8
    assert any(d.query == QUERY for d in spec.decoys)
