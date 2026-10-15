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
import decoy_apparel as da  # noqa: E402
import decoy_rows  # noqa: E402
import details  # noqa: E402
import export  # noqa: E402
import image_release  # noqa: E402
import main_colors  # noqa: E402
import mens_depth_rows  # noqa: E402
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
    named color on the named part, so the title is true of the picture."""
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
    # the other side: the drawing carries the named part, in the named color
    for r in named:
        doc = by_id[r.pid]
        drawing = image_release.colorway_drawing(doc, doc["skus"][0])
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
    named = [r for r in rows if r.cls in (1, 6, 7) and r.word in MAIN]
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
    """The picture shows what the title says: the part the title names (class 1), or the type's
    first part (classes 6 and 7, whose title names none), carries the named color, and no other
    element of the drawing does: a stripe across the whole garment is not a named part."""
    named = [r for r in rows if r.cls in (1, 6, 7) and r.word in MAIN]
    for r in named:
        doc = by_id[r.pid]
        hexv = da.DETAIL_HEX[r.word.title()].lower()
        marked, plain = _svg_parts(doc)
        assert marked, (r.pid, doc["title"], "no element is marked as the named part")
        if r.cls == 1:
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
    assert scale.DECOY_IDS == decoy_rows.IDS | da.IDS | scale.BEAUTY_DECOY_IDS
    real = [r["product_id"] for r in ceiling if r["product_id"] not in scale.DECOY_IDS]
    assert len(real) > 5 * len(scale.DECOY_IDS)
    assert not [i for i in real if i in scale.DECOY_IDS]
    assert all(i in scale.DECOY_IDS for i in decoy_rows.IDS | da.IDS)


def test_the_mens_types_the_census_exempts_hold_their_own_decoys() -> None:
    """The exemption of Polo Shirt, Jacket and Mens Trousers is safe only while the Mens depth
    table holds at least three decoys of each class 1 to 7 for each of them."""
    mens = {t for t in da.EXEMPT if any(d.ptype == t for d in mens_depth_rows.TABLE)}
    assert mens == {"Polo Shirt", "Jacket", "Mens Trousers"}
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
