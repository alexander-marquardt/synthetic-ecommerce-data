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
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decor_rows  # noqa: E402
import decoy_apparel as da  # noqa: E402
import decoy_rows  # noqa: E402
import details  # noqa: E402
import export  # noqa: E402
import garden_rows  # noqa: E402
import image_release  # noqa: E402
import main_colors  # noqa: E402
import mens_depth_rows  # noqa: E402
import neckline_rows  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

DEPARTMENTS = {"Clothing", "Footwear", "Lingerie & Nightwear"}
ROOTS = {"Womens", "Mens", "Kids"}
MAIN = {"red", "blue", "green", "yellow", "black", "white"}
AUDIENCE_ROOT = {"mens": "Mens", "womens": "Womens", "boys": "Kids", "girls": "Kids"}


@pytest.fixture(scope="module")
def table_doc() -> str:
    """The docs table as the build writes it (``docs/retail-apparel-decoys.md``, not in git)."""
    return da.doc_text()


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
        assert len(six) >= 3 and not any(r.word in MAIN for r in six), ptype  # #444
    for r in rows:
        doc = by_id[r.pid]
        if r.cls in (6, 7):
            assert len(doc["title"].split()) <= 5, (r.pid, doc["title"])
        if r.cls == 7:
            brands.add(doc["brand"])
            assert doc["brand"].lower() in doc["title"].lower(), (r.pid, doc["title"])
    assert 6 <= len(brands) <= 8, brands
    assert {r.word for r in rows if r.cls == 7} >= MAIN


#: Every color word a title can hold: the main six and the shades a decoy is sold in.
COLOR_WORDS = MAIN | {"navy", "cream", "grey", "brown", "pink"}


def _color_words(title: str) -> set[str]:
    return {w for w in COLOR_WORDS if re.search(rf"\b{w}\b", title.lower())}


def test_a_range_name_never_holds_a_color_and_a_brand_color_is_the_brand_field(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    """#444: "Red Harbour Dress" read as a red dress with a strange brand. A class 6 title holds
    no color word (a range name is a place, never a color) and its drawing colors nothing. A
    class 7 title holds a color word only as the invented brand, which is the product's brand
    field, and its drawing shows no part in that color: "Yellow Wagtail Co-ord Set" is a blue
    co-ord set with no yellow waistband (#444 F1)."""
    for r in (r for r in rows if r.cls in (6, 7)):
        doc = by_id[r.pid]
        named = _color_words(doc["title"]) - {_real_color(doc)}
        assert "detail" not in doc["drawing"], (r.pid, doc["title"], doc["drawing"].get("detail"))
        if r.cls == 6:
            assert not named, (r.pid, doc["title"], named)
        else:
            assert named <= {w for w in named if re.search(rf"\b{w}\b", doc["brand"].lower())}, (
                r.pid,
                doc["title"],
                doc["brand"],
            )
    sevens = [r for r in rows if r.cls == 7]
    assert any(r.word in MAIN for r in sevens)
    for r in (r for r in sevens if r.word in MAIN):
        assert re.search(rf"\b{r.word}\b", by_id[r.pid]["brand"].lower()), r


#: The REVIEWED list of real retail terms (#444), written by hand and not a mirror of
#: ``decoy_apparel.COMPOUNDS``: each phrase was checked as a name a shopper meets at a mainstream
#: retailer (when in doubt it is left out). The generator's table must be a subset of it, and a
#: new compound is added here only after the same review, never copied across.
REAL_COMPOUNDS = frozenset({
    "Skirted Swimsuit", "Tank Swimsuit", "Bralette Bikini Top", "Crop Bikini Top",
    "Sports Bra Bikini Top", "Skirted Bikini Bottoms", "Boyshort Bikini Bottoms",
    "Brief Bikini Bottoms", "Skirted Tankini", "Tunic Tankini", "Cami Tankini",
    "Cargo Swim Shorts", "Chino Swim Shorts", "Tailored Swim Shorts", "Skirted Kids Swimsuit",
    "Rash Vest Kids Swimsuit", "Skirted Period Swimwear", "Short Period Swimwear",
    "Brief Period Swimwear", "Kimono Cover-Up", "Shirt Cover-Up", "Tunic Cover-Up",
    "Dress Cover-Up", "Poncho Changing Robe", "Parka Changing Robe", "Hoodie Changing Robe",
    "Tuxedo Trouser Suit", "Waistcoat Trouser Suit", "Culotte Trouser Suit",  # gen#215
    "Sailor Suit", "Tuxedo Suit", "Page Boy Suit",  # gen#215
    # Babywear (gen#213): each is a title a baby shop sells.
    "Pyjama Sleepsuit", "Babygrow Sleepsuit", "Romper Sleepsuit", "Vest Bodysuit",
    "Romper Bodysuit", "Sleep Bodysuit", "Snowsuit Trousers", "Snowsuit Jacket",
    "Fleece Snowsuit", "Rain Puddlesuit", "Waterproof Puddlesuit", "Fleece Puddlesuit",
    "Jumpsuit All-in-One", "Onesie All-in-One", "Pyjama All-in-One",
    "Dress Blouse", "Shirt Blouse", "Tunic Blouse",
    "Shirt Bodysuit", "Corset Bodysuit", "Cami Bodysuit", "Bodysuit Top",
    "Shirt Jacket", "Blazer Jacket", "Biker Jacket", "Bomber Jacket", "Dress Jacket",
    "Denim Shirt Jacket", "Denim Bomber Jacket", "Denim Biker Jacket", "Shacket",
    "Kimono Cardigan", "Duster Cardigan", "Bomber Cardigan",
    "Dress Coat", "Puffer Coat", "Duffle Coat",
    # outerwear (gen#211)
    "Cardigan Shacket",
    "Bomber Shacket",
    "Blazer Shacket",
    "Bomber Utility Jacket",
    "Parka Utility Jacket",
    "Gilet Utility Jacket",
    "Blazer Trench Coat",
    "Cape Trench Coat",
    "Shirt Trench Coat",
    "Bomber Gilet",
    "Denim Gilet",
    "Shirt Gilet",
    "Bomber Hoodie",
    "Denim Hoodie",
    "Poncho Hoodie",
    "Poncho Raincoat",
    "Cape Raincoat",
    "Bomber Raincoat",
    "Puffer Parka",
    "Bomber Parka",
    "Fishtail Parka",
    "Bomber Windbreaker",
    "Track Windbreaker",
    "Poncho Windbreaker",
    "Cardigan Bolero",
    "Blazer Bolero",
    "Denim Bolero",
    "Blazer Peacoat",
    "Bomber Peacoat",
    "Cape Peacoat",
    "Skirt Co-ord Set", "Trouser Co-ord Set", "Shirt Co-ord Set", "Short Co-ord Set",
    "Dress Shorts", "Cargo Shorts", "Tailored Shorts", "Jean Shorts", "Chino Shorts",
    "Pyjama Shorts", "Bermuda Shorts", "Cycling Shorts", "Boxer Shorts",
    "Shirt Dress", "Jumper Dress", "Blazer Dress", "Hoodie Dress", "Tunic Dress", "Coat Dress",
    "Sweatshirt Dress", "Slip Dress",
    "Chino Joggers", "Cargo Joggers", "Denim Joggers",
    "Tunic Jumper", "Polo Jumper",
    "Cargo Leggings", "Denim Leggings", "Cycling Leggings",
    "Skirt Set", "Trouser Set", "Short Set", "Blazer Set", "Trouser Suit", "Skort",
    "Dress Shirt", "Polo Shirt", "Tunic Shirt",
    "Jean Skirt", "Slip Skirt", "Cargo Skirt",
    "Polo Sweatshirt", "Hoodie Sweatshirt", "Tunic Sweatshirt",
    "Polo T-Shirt", "Tunic T-Shirt",
    "Polo Tee", "Tunic Tee",
    "Vest Top", "Cami Top", "Polo Top", "Tunic Top",
    "Knitted Vest Top", "Knitted Cami Top", "Knitted Polo Top", "Knitted Tunic Top",
    "Hoodie Tracksuit", "Short Tracksuit", "Jogger Tracksuit",
    "Cargo Trousers", "Chino Trousers", "Jogger Trousers", "Dress Trousers",
    "Cargo Jeans", "Jogger Jeans",
    "Chino School Trousers", "Jogger School Trousers", "Cargo School Trousers",
    "Pinafore School Skirt", "School Pinafore Dress",
    "School Polo Shirt", "Oxford School Shirt",
    "Bikini Period Pants", "Boyshort Period Pants", "Thong Period Pants",
    "Boot Socks", "Trouser Socks", "Slipper Socks", "Trainer Socks", "Sneaker Socks",
    "Welly Boot Socks", "Wellington Boot Socks", "Walking Boot Socks",
    "Sandal Boots", "Sneaker Boots", "Loafer Boots", "Shoe Boots", "Slipper Boots", "Biker Boots",
    "Sock Boots", "Wellington Safety Boots", "Chelsea Safety Boots", "Hiker Safety Boots",
    "Chukka Walking Boots",
    "Mule Heels", "Loafer Heels", "Sandal Heels",
    "Ballet Slippers", "Ballet Sandals", "Ballet Pumps",
    "Dress Brogues", "Derby Brogues", "Oxford Brogues",
    "Dress Shoes", "Court Shoes", "Walking Shoes", "Tennis Shoes", "Training Shoes",
    "Loafer School Shoes", "Brogue School Shoes",
    "Mule Loafers", "Brogue Loafers",
    "Loafer Sandals", "Mule Sandals", "Espadrille Sandals",
    "Boot Slippers", "Sock Slippers", "Loafer Slippers", "Mule Slippers",
    "Sneaker Plimsolls", "Mule Clogs", "Sneaker Wedges", "Sneaker Espadrilles",
    "Sock Platform Trainers", "Loafer Mules", "Slipper Mules", "Sandal Mules",
    "Mary Jane Jelly Shoes", "Sandal Barefoot Shoes",
    "Sock Trainers", "Running Trainers", "Walking Trainers", "Chelsea Wellies",
    "Cami Bra", "Corset Bra",
    "Boxer Briefs", "Boxer Trunks",
    "Hoodie Dressing Gown", "Kimono Dressing Gown", "Dressing Gown",
    "Short Knickers", "Cami Knickers", "Bikini Knickers",
    "Short Pyjamas", "Cami Pyjamas",
    "Bodysuit Shapewear", "Cami Shapewear", "Slip Shapewear",
    "Dress Slip", "Skirt Slip", "Cami Slip",
    "Running Tights", "Cycling Tights",
    "Cami Vest", "Dress Vest", "Sweater Vest",
})  # fmt: skip


def test_no_class_2_title_is_outside_the_real_compounds(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    """#444: "Red Dress Pyjamas" is not a retail term. A class 2 title is the product's color,
    an optional fit, then a compound of :data:`REAL_COMPOUNDS`."""
    twos = [r for r in rows if r.cls == 2]
    assert len(twos) >= 3 * len(da.TYPES)
    phrases = set()
    for r in twos:
        doc = by_id[r.pid]
        color = doc["color_options"][0]["color"]
        assert doc["title"].startswith(color + " "), (r.pid, doc["title"])
        rest = doc["title"][len(color) + 1 :]
        hit = [p for p in REAL_COMPOUNDS if rest == p or rest.endswith(" " + p)]
        assert hit, (r.pid, doc["title"])
        assert r.word in doc["title"].lower(), (r.pid, r.word, doc["title"])
        phrases.add(max(hit, key=len))
    assert len(phrases) >= 60, len(phrases)  # the table is varied, not three words reused


#: The class 2 phrases the reviewer named as invented (#444): no shopper meets them as a product.
INVENTED_COMPOUNDS = frozenset(
    {
        "Dress Pyjamas",
        "Trouser Blouse",
        "Poncho Dressing Gown",
        "Dress Tights",
        "Legging Tights",
        "Sweatshirt Tracksuit",
        "Dress Trainers",
        "Ballet Sneakers",
        "Sneaker Loafers",
        "Trainer School Shoes",
        "Sock Shoes",
        "Pump Heels",
        "Trouser Shorts",
        "Pyjama Boxers",
        # #444 review: each names a class the product itself belongs to, not another product's noun
        "Ballet Flats",
        "Henley Tee",
        "Henley T-Shirt",
        "Slider Sandals",
        "T-Shirt Bra",
        # the live "Wedge Sandals" in another word order (15 of 51 live Wedges)
        "Sandal Wedges",
    }
)


def test_no_invented_compound_is_planned_or_titled() -> None:
    """#444: the reviewed list is a list of real retail terms, not a mirror of the generator's
    table, so an invented phrase is named here and found in neither."""
    planned = {p for t in da.TYPES for _, p in (t.compounds or da.COMPOUNDS[t.product_type])}
    assert not planned & INVENTED_COMPOUNDS, planned & INVENTED_COMPOUNDS
    assert planned <= REAL_COMPOUNDS, sorted(planned - REAL_COMPOUNDS)
    assert not REAL_COMPOUNDS & INVENTED_COMPOUNDS


def _stems(text: str) -> list[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return [w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words]


def test_no_class_2_phrase_is_a_live_title_reworded(ceiling: list[dict]) -> None:
    """#444: a class 2 decoy is not the live product in another word order ("Sandal Wedges" is
    the live "Wedge Sandals"), so "Not a sandal" would be false of it. Live = every non-decoy
    title. Only the reversed order is guarded: the wider "incidental word is in a live title"
    reading reds on about fifteen reviewed phrases (Mule Slippers, Boxer Shorts), a design call."""
    live: dict[str, list[list[str]]] = {}
    for rec in ceiling:
        if rec["product_id"] not in da.IDS and not rec["product_id"].startswith("PLT-D"):
            live.setdefault(rec["product_type"], []).append(_stems(rec["title"]))
    bad = []
    for spec in da.TYPES:
        titles = live.get(spec.product_type, [])
        for _, phrase in spec.compounds or da.COMPOUNDS[spec.product_type]:
            rev = _stems(phrase)[::-1]
            for t in titles:
                if any(t[i : i + len(rev)] == rev for i in range(len(t))):
                    bad.append((spec.product_type, phrase, " ".join(t)))
                    break
    assert not bad, bad


def test_every_type_has_three_real_compounds_or_a_declared_reason(table_doc: str) -> None:
    """#444: a type with fewer than three real compounds is a declared exception, with its
    reason, and the generator text of the docs says so; an exception that no longer applies reds.
    Only a phrase some exemplar of the type can carry counts: ``_in_path`` blocks Shirt Blouse,
    Shoe Boots and Ballet Flats on every path of their types, and a planned phrase never built
    is no phrase."""
    body = [d for d in scale.templates(baseline=False) if d["product_id"] not in da.IDS]
    built: dict[str, set[str]] = {t.product_type: set() for t in da.TYPES}
    for ex in body:
        for spec in da.TYPES:
            if ex["product_type"] == spec.product_type and ex.get("color_options"):
                built[spec.product_type] |= {o["phrase"] for o in da._options(2, spec, ex)}
    short = {t.product_type for t in da.TYPES if len(built[t.product_type]) < 3}
    assert short == set(da.SHORT_COMPOUNDS), short ^ set(da.SHORT_COMPOUNDS)
    assert all(len(reason.split()) >= 4 for reason in da.SHORT_COMPOUNDS.values())
    for ptype in short:
        assert ptype in table_doc, ptype


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


def test_docs_table_is_generated_and_lists_every_row(rows: list[da.Row], table_doc: str) -> None:
    table = da.table_markdown(rows)
    assert len(table.splitlines()) == len(rows) + 2 and len(rows) > 500
    assert table in table_doc
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
    named color on the named part, so the title is true of the picture."""
    named = [r for r in rows if r.cls in (1, 7) and r.word in MAIN]
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
    # the other side: the drawing carries the named part, in the named color
    for r in named:
        doc = by_id[r.pid]
        drawing = image_release.colorway_drawing(doc, doc["skus"][0])
        if r.cls == 7:  # the brand holds the color word; the drawing colors no part (#444)
            assert "detail" not in drawing, r.pid
            continue
        assert drawing["detail"]["color"].lower() == da.DETAIL_HEX[r.word.title()].lower(), r.pid
        assert drawing.get("pattern") != "stripe", r.pid
        assert doc["color_options"][0]["color"] != r.word.title(), r.pid


def _real_color(doc: dict) -> str:
    return doc["color_options"][0]["color"].lower()


def test_a_decoy_title_names_only_the_misleading_color(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    """The maintainer ruling: "Bra with Red Straps" on a white bra, with no "White" in the title.
    It holds for class 1 (a part), 6 (a range name) and 7 (a brand) alike."""
    named = [r for r in rows if r.cls in (1, 7) and r.word in MAIN]
    assert len(named) >= 3 * len(da.TYPES)
    for r in named:
        real = _real_color(by_id[r.pid])
        title = by_id[r.pid]["title"].lower()
        assert real != r.word, (r.pid, real)
        assert not re.search(rf"\b{real}\b", title), (r.pid, real, title)
        assert re.search(rf"\b{r.word}\b", title), (r.pid, r.word, title)


def _svg_parts(doc: dict, bare: bool = False) -> tuple[list[ET.Element], list[ET.Element]]:
    """(the elements marked as a named part, every other drawn element outside defs and masks).
    ``bare`` draws the same product without its named part."""
    if bare:
        doc = doc | {"drawing": {k: v for k, v in doc["drawing"].items() if k != "detail"}}
    root = ET.fromstring(image_release.render(doc, doc["skus"][0]))
    marked: list[ET.Element] = []
    plain: list[ET.Element] = []

    def walk(el: ET.Element, hidden: bool) -> None:
        tag = el.tag.split("}")[-1]
        hidden = hidden or tag in ("defs", "mask", "clipPath")
        if not hidden and el.get("data-part"):
            marked.append(el)
        elif not hidden:
            plain.append(el)
        for child in el:
            walk(child, hidden)

    walk(root, False)
    return marked, plain


def test_the_named_part_is_drawn_in_the_named_color_and_nothing_else_is(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    """The picture shows what the title says: the part the title names (class 1) carries the named
    color, and no other element of the drawing does: a stripe across the whole garment is not a
    named part. A class 7 brand names no part and colors none (#444)."""
    named = [r for r in rows if r.cls == 1 and r.word in MAIN]
    for r in named:
        doc = by_id[r.pid]
        hexv = da.DETAIL_HEX[r.word.title()].lower()
        marked, plain = _svg_parts(doc)
        assert marked, (r.pid, doc["title"], "no element is marked as the named part")
        part = doc["title"].split()[-1].lower()
        assert {e.get("data-part") for e in marked} == {part}, (r.pid, doc["title"])
        for e in marked:
            assert hexv in (e.get("fill", "").lower(), e.get("stroke", "").lower()), (
                r.pid,
                e.attrib,
            )
        # the kit's own fixed trim (a white collar, buttons) may hold the color; the named part
        # must add nothing else of it, so every plain element holding it is also in the bare drawing
        own = [sorted(e.attrib.items()) for e in _svg_parts(doc, bare=True)[1]]
        for e in plain:
            if hexv in (e.get("fill", "").lower(), e.get("stroke", "").lower()):
                assert sorted(e.attrib.items()) in own, (r.pid, doc["title"], e.attrib)


def test_decoy_ids_are_the_two_tables_and_no_real_product_is_in_them(
    ceiling: list[dict],
) -> None:
    """The exemption is keyed on the decoy tables: a real catalog id is outside it. Membership
    is read with ``in``, the way ``check_catalog`` reads it."""
    tables = (decoy_rows.IDS | da.IDS | garden_rows.decoy_ids() | decor_rows.decoy_ids()
              | neckline_rows.decoy_ids())
    assert tables == scale.DECOY_IDS
    real = [r["product_id"] for r in ceiling if r["product_id"] not in scale.DECOY_IDS]
    assert len(real) > 5 * len(scale.DECOY_IDS)
    assert not [i for i in real if i in scale.DECOY_IDS]
    assert all(i in scale.DECOY_IDS for i in tables)


def test_the_mens_types_the_census_exempts_hold_their_own_decoys() -> None:
    """The exemption of Polo Shirt, Jacket, Mens Trousers and the tailoring types is safe only
    while the Mens depth table holds at least three decoys of each class 1 to 7 for each of them."""
    mens = {t for t in da.EXEMPT if any(d.ptype == t for d in mens_depth_rows.TABLE)}
    assert mens == {
        "Polo Shirt",
        "Jacket",
        "Mens Trousers",
        "Suit Trousers",
        "Waistcoat",
        "Dinner Suit",
        "Formal Accessories",
    }
    for ptype in mens:
        for klass in range(1, 8):
            n = sum(1 for d in mens_depth_rows.TABLE if d.ptype == ptype and d.klass == klass)
            assert n >= 3, (ptype, klass, n)


#: Where each named part sits on its garment: the share of the garment's height (from its top)
#: that the part's own box lies in. A hem is at the bottom, a waistband at the top.
BOTTOM = (0.75, 1.0)
TOP = (-0.3, 0.25)  # a strap rises above the garment's body
ZONE = {
    "hem": BOTTOM,
    "cuffs": BOTTOM,
    "sole": (0.5, 1.0),  # under the shoe (a heel lifts the sole), not across its upper
    "waistband": TOP,
    "collar": TOP,
    "straps": TOP,
    "cuff": TOP,  # a boot sock's fold-over cuff
}
#: The shapes whose parts are not a band of the whole drawing (a pack's socks are rotated).
NO_ZONE_SHAPES = {"socks"}


def _svg(doc: dict) -> str:
    out = image_release.render(doc, doc["skus"][0])
    return out.decode() if isinstance(out, bytes) else out


def _product(svg: str) -> str:
    """The product group's elements, without defs and masks (a mask's shapes are no drawing)."""
    body = svg.split('<g class="product"', 1)[1].split('<g class="brand">', 1)[0]
    return re.sub(r"<mask\b.*?</mask>", "", body, flags=re.S)


def _garment_box(doc: dict) -> tuple[float, float, float, float]:
    bare = doc | {"drawing": {k: v for k, v in doc["drawing"].items() if k != "detail"}}
    # the kit's trim (lace scallops) is drawn with relative commands, which the box reader skips
    body = [
        p
        for p in details._body([_product(_svg(bare))], "", "all")
        if ' d="' not in p[3]
        or not re.search(r"[mlcqzhva]", re.search(r' d="([^"]*)"', p[3]).group(1))
    ]
    box = details._bbox(body)
    assert box, doc["title"]
    return box


def test_the_named_part_sits_where_the_part_sits_on_the_garment(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    """A hem is drawn at the bottom of the garment, a waistband or a collar at the top, a shoe's
    sole at the bottom of the shoe: the part's own box lies in that share of the garment's height.
    A color block anywhere else on the garment is not the named part."""
    seen: set[str] = set()
    for r in (r for r in rows if r.cls in (1, 6, 7) and r.word in MAIN):
        doc = by_id[r.pid]
        if doc["drawing"]["shape"] in NO_ZONE_SHAPES:
            continue
        _, top, _, bottom = _garment_box(doc)
        placed = [p for p in details._flat([_product(_svg(doc))]) if " data-part=" in p[3]]
        for tx, ty, sc, el in placed:
            part = re.search(r' data-part="([^"]*)"', el).group(1)
            if part not in ZONE:
                continue
            box = details._bbox([(tx, ty, sc, el)])
            assert box, (r.pid, part)
            lo, hi = ZONE[part]
            centre = ((box[1] + box[3]) / 2 - top) / (bottom - top)
            assert lo <= centre <= hi, (r.pid, doc["title"], part, round(centre, 2))
            if part == "sole":  # drawn on the kit's own sole path, not on a band across the upper
                bare = doc | {"drawing": {k: v for k, v in doc["drawing"].items() if k != "detail"}}
                own = re.findall(
                    r'class="sole"[^>]* d="([^"]*)"|<path d="([^"]*)"[^>]*class="sole"', _svg(bare)
                )
                assert re.search(r' d="([^"]*)"', el).group(1) in {a or b for a, b in own}, r.pid
            seen.add(part)
    assert seen == set(ZONE), set(ZONE) - seen


def test_a_relative_path_command_is_not_read_as_a_page_point() -> None:
    """#444: a lace trim writes relative scallops (``l``, ``q``); read as absolute, their small
    offsets pulled a part's box to the corner of the page. A relative command adds no point."""
    assert details._coords("M10 20 L30 40 l3 4 q1 2 3 4 Z") == [(10.0, 20.0), (30.0, 40.0)]


def test_a_hem_is_the_torsos_and_does_not_color_the_sleeve_cuffs(
    rows: list[da.Row], by_id: dict[str, dict]
) -> None:
    """The hem band is cut by the garment's torso: every shape it is cut by crosses the middle
    of the garment, so a sleeve (which reaches the same bottom) stays its own color."""
    n = 0
    for r in (r for r in rows if r.cls in (1, 6, 7) and r.word in MAIN):
        doc = by_id[r.pid]
        if (
            "hem" not in details.parts_of(doc["drawing"]["shape"])
            or doc["drawing"].get("detail", {}).get("part") != "hem"
        ):
            continue
        svg = _svg(doc)
        mask = re.search(r"<mask\b.*?</mask>", svg, flags=re.S)
        assert mask, (r.pid, "a hem is cut by a mask of the body")
        box = details._bbox(details._flat([mask.group(0)]))
        assert box
        mid = (box[0] + box[2]) / 2
        for placed in details._flat([mask.group(0)]):
            b = details._bbox([placed])
            assert b and b[0] <= mid <= b[2], (r.pid, doc["title"], b, mid)
        n += 1
    assert n >= 5
