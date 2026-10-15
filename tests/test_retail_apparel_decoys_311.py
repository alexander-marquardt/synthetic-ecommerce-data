"""Every clothing, footwear and lingerie type carries text-match decoys (gen#311).

The rule is gen#294's: a decoy's title or description holds a word that misleads a plain text
search, and its structured fields tell the truth, so a policy that reads the fields is right.
:mod:`decoy_apparel` plants them per product type; this file walks every such type of the built
catalog and pins that each class has at least three, that each contradicts its misleading word
in the fields, and that the docs table lists every row.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_apparel as da  # noqa: E402
import export  # noqa: E402
import image_release  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

DEPARTMENTS = {"Clothing", "Footwear", "Lingerie & Nightwear"}
ROOTS = {"Womens", "Mens", "Kids"}
MAIN = {"red", "blue", "green", "yellow", "black", "white"}
AUDIENCE_ROOT = {"mens": "Mens", "womens": "Womens", "boys": "Kids", "girls": "Kids"}
TABLE_DOC = ROOT / "docs" / "retail-apparel-decoys.md"


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def by_id(ceiling: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in ceiling}


@pytest.fixture(scope="module")
def rows() -> list[da.Row]:
    body = [d for d in scale.templates(baseline=False) if d["product_id"] not in da.IDS]
    return da.build(body)


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def _live_types(ceiling: list[dict]) -> set[str]:
    return {
        r["product_type"]
        for r in ceiling
        if r["product_id"] not in da.IDS
        and r["department"][0] in DEPARTMENTS
        and r["category_path"][0] in ROOTS
    }


def _text(doc: dict) -> str:
    """Every attribute value and every text SKU field, lowercased: what the fields say."""
    vals = [str(a["value"]) for a in doc["attributes"]]
    vals += [
        str(v)
        for s in doc["skus"]
        for k, v in s.items()
        if isinstance(v, str) and not k.startswith("size") and k != "sku"
    ]
    return " ".join(vals).lower()


def _by_type(rows: list[da.Row]) -> dict[str, list[da.Row]]:
    out: dict[str, list[da.Row]] = {}
    for r in rows:
        out.setdefault(r.product_type, []).append(r)
    return out


def test_every_clothing_footwear_and_lingerie_type_is_planned(ceiling: list[dict]) -> None:
    """A census over the live catalog, not over a list: a new type reds here until it carries
    decoys (or is exempted with a reason)."""
    live = _live_types(ceiling)
    planned = {t.product_type for t in da.TYPES}
    assert planned, "no type is planned"
    assert live - set(da.EXEMPT) == planned, live - set(da.EXEMPT) ^ planned
    assert set(da.EXEMPT) <= live | {"Belt", "Shoe Care Kit"}
    assert all(reason.strip() for reason in da.EXEMPT.values())


def test_every_type_has_three_decoys_per_class_in_the_built_catalog(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    grouped = _by_type(rows)
    assert grouped and set(grouped) == {t.product_type for t in da.TYPES}
    assert {r.pid for r in rows} == da.IDS == {p for p in by_id if p in da.IDS}
    for ptype, rs in grouped.items():
        for cls in (1, 2, 3, 4, 5, 6, 7):
            n = sum(r.cls == cls for r in rs)
            assert n >= 3, (ptype, cls, n)
        assert all(by_id[r.pid]["product_type"] == ptype for r in rs), ptype


def test_each_decoys_fields_contradict_its_misleading_word(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    assert rows
    for r in rows:
        doc = by_id[r.pid]
        colors = {c["color"] for c in doc["color_options"]}
        path = " ".join(doc["category_path"]).lower() + " " + doc["product_type"].lower()
        text = f"{doc['title']} {doc['description']}".lower()
        assert len(colors) == 1, (r.pid, colors)
        assert r.word in text, (r.pid, r.word, doc["title"])
        if r.cls in (1, 6, 7) and r.word in MAIN:
            assert r.word.title() not in colors, (r.pid, r.word, colors)
        elif r.cls in (2, 6, 7):
            assert not re.search(rf"\b{r.word}s?\b", path), (r.pid, r.word, path)
        elif r.cls == 3:
            assert AUDIENCE_ROOT[r.word] != doc["category_path"][0], (r.pid, r.word)
        elif r.cls == 4:
            assert r.word not in _text(doc), (r.pid, r.word)
        elif r.cls == 5:
            assert r.word not in doc["title"].lower(), (r.pid, r.word)
            assert colors == {r.word.title()}, (r.pid, r.word, colors)


def test_class_6_and_7_name_a_short_title_and_class_7_names_a_brand(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    brands = set()
    for ptype, rs in _by_type(rows).items():
        six = [r for r in rs if r.cls == 6]
        assert sum(r.word in MAIN for r in six) >= 3, ptype
        assert any(r.word not in MAIN for r in six), ptype
    for r in rows:
        doc = by_id[r.pid]
        if r.cls in (6, 7):
            assert len(doc["title"].split()) <= 5, (r.pid, doc["title"])
        if r.cls == 7:
            brands.add(doc["brand"])
            assert doc["brand"].lower() in doc["title"].lower(), (r.pid, doc["title"])
    assert 6 <= len(brands) <= 8, brands
    assert {w for r in rows if r.cls == 6 for w in [r.word]} >= MAIN


def test_large_types_carry_ten_percent_decoys(rows: list[da.Row], ceiling: list[dict]) -> None:
    for ptype, rs in _by_type(rows).items():
        real = sum(
            1
            for d in ceiling
            if d["product_type"] == ptype
            and d["product_id"] not in da.IDS
            and d["category_path"][0] in ROOTS
        )
        assert len(rs) >= math.ceil(real / 10), (ptype, len(rs), real)


def test_policy_is_marked_generic_or_special_on_every_row(rows: list[da.Row]) -> None:
    assert rows
    for r in rows:
        assert r.policy == "generic" or re.fullmatch(r"special: [a-z][a-z -]+", r.policy), r
    assert {r.policy for r in rows if r.cls != 4} == {"generic"}


def test_docs_table_is_generated_and_lists_every_row(rows: list[da.Row]) -> None:
    table = da.table_markdown(rows)
    assert len(table.splitlines()) == len(rows) + 2 and len(rows) > 500
    assert table in TABLE_DOC.read_text()
    for r in rows:
        assert r.pid in table


def test_decoys_are_templates_never_copied_or_color_completed() -> None:
    tpls = scale.templates()
    assert da.IDS and not da.IDS & {r["product_id"] for r in scale.derivable(tpls)}
    assert not da.IDS & {r["product_id"] for g in main_colors.groups(tpls).values() for r in g}


@pytest.mark.parametrize("query", ["red bra", "blue dress", "white trainers", "black jeans"])
def test_sibling_color_queries_find_decoys_in_the_baseline_top_10(
    index: br.Index, query: str
) -> None:
    top = [d["product_id"] for d in br.rank(index, query, 10)]
    planted = [i for i in top if i in da.IDS]
    assert len(planted) >= 3 and any(i in da.IDS for i in top[:3]), (query, top)


def test_a_decoy_may_name_only_the_misleading_color_and_only_when_it_is_drawn(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    """The maintainer ruling on #311: the output standard's refusal of a text naming only another
    color stays for ordinary products; a decoy row is exempt by id, and its drawing shows the
    named color (a stripe in it), so the title is true of the picture."""
    named = [r for r in rows if r.cls in (1, 6, 7) and r.word in MAIN]
    assert len(named) >= 3 * len(da.TYPES)
    docs = [export.standard_document(by_id[r.pid]) for r in named]
    assert check_catalog(docs, text_exempt=scale.DECOY_IDS) == []
    # one side: a non-decoy row naming only another color is still refused
    ordinary = json.loads(json.dumps(docs[0]).replace("PLT-D", "ORDINARY-1-"))
    ordinary["description"] = ordinary["title"]  # the text names only the other color
    refused = check_catalog([*docs, ordinary], text_exempt=scale.DECOY_IDS)
    assert [p for p in refused if p.startswith("ORDINARY-1")], refused
    # and the exemption is keyed on the id: without it the decoys are refused
    assert check_catalog(docs) != []
    # the other side: the drawing renders the named color as the accent
    for r in named:
        doc = by_id[r.pid]
        drawing = image_release.colorway_drawing(doc, doc["skus"][0])
        assert drawing["pattern"] == "stripe", (r.pid, drawing)
        assert drawing["accent"].lower() == da.DETAIL_HEX[r.word.title()].lower(), (r.pid, r.word)
        assert doc["color_options"][0]["color"] != r.word.title(), r.pid
