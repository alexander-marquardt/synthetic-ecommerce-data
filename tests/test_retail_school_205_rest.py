"""School uniform for Kids, the rest of the issue's table (gen#205).

The specs ``school_polo``, ``school_socks``, ``school_blazer`` and ``pe_shorts`` hold the polos,
socks, blazers and PE shorts and :mod:`kit_school` draws them. These checks hold what the issue
asked for: each type has its range, each style draws as its own shape with the params its record
states, each key attribute is a structured entry in the export, a pack draws its count, and every
style reaches the scaled build.
"""

from __future__ import annotations

import collections
import functools
import re
import xml.dom.minidom

import pytest

from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import (
    decoy_apparel,
    export,
    image_release,
    kit,
    kit_school,
    main_colors,
    scale,
    size_ladder,
    tree_guard,
    type_registry,
)

ROOT, FAMILY = "Kids", "School Uniform"
AGE = re.compile(r"\d{1,2}-\d{1,2} Yrs")

#: spec key -> (product type, leaf, shape, the key attributes every style states).
TYPES = {
    "school_polo": ("School Polo Shirt", "School Polo Shirts", "school_polo",
                    {"sleeve_length", "fabric", "pack_size", "color", "size"}),
    "school_socks": ("School Socks", "School Socks", "school_socks",
                     {"sock_style", "fabric", "pack_size", "color", "shoe_size_band"}),
    "school_blazer": ("School Blazer", "School Blazers", "school_blazer",
                      {"fit", "lining", "badge_ready", "fabric", "color", "size"}),
    "pe_shorts": ("PE Shorts", "PE Shorts", "pe_shorts",
                  {"leg_length", "fabric", "pack_size", "color", "size"}),
}  # fmt: skip
VARIANTS = [
    ("school_polo", {"sleeve": "short"}, {"sleeve": "long"}),
    ("school_socks", {"height": "ankle"}, {"height": "knee"}),
    ("school_socks", {"height": "ankle"}, {"height": "tights"}),
    ("school_blazer", {"fit": "regular"}, {"fit": "slim"}),
    ("school_blazer", {"fit": "regular"}, {"fit": "plus"}),
    ("school_blazer", {"badge": "outline"}, {"badge": "none"}),
    ("pe_shorts", {"leg": "short"}, {"leg": "mid"}),
]


@functools.cache
def _rows() -> dict[str, tuple]:
    specs = type_registry.specs()
    return {key: specs[key].rows if key in specs else () for key in TYPES}


def _all() -> list:
    return [r for rows in _rows().values() for r in rows]


@functools.cache
def _templates() -> dict[str, dict]:
    return {r["product_id"]: r for r in scale.templates()}


def _attr(row, key: str) -> str:
    return next(a[2] for a in row.attrs if a[0] == key)


def _svg(row=None, **kw) -> str:
    shape = row.shape if row else kw.pop("shape")
    params = dict(row.params) if row else kw
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _count(svg: str, cls: str) -> int:
    return len(re.findall(rf'<g class="{cls}"', svg))


@pytest.mark.parametrize("key", sorted(TYPES))
def test_every_type_has_three_styles_from_three_brands(key: str) -> None:
    rows = _rows()[key]
    assert len(rows) >= 3 and len({r.brand for r in rows}) >= 3, key


@pytest.mark.parametrize("key", sorted(TYPES))
def test_a_type_names_itself_and_sits_in_a_leaf_of_its_own(key: str) -> None:
    ptype, leaf, shape, _ = TYPES[key]
    rows = _rows()[key]
    assert rows
    assert {r.product_type for r in rows} == {ptype}
    assert {tuple(r.path) for r in rows} == {(ROOT, FAMILY, leaf)}
    assert {r.audience for r in rows} == {"kids"}
    assert {r.shape for r in rows} == {shape} and shape in kit_school.SHAPES


@pytest.mark.parametrize("key", sorted(TYPES))
def test_every_key_attribute_is_a_structured_entry_in_the_export(key: str) -> None:
    wanted = TYPES[key][3]
    missing = {}
    assert _rows()[key]
    for row in _rows()[key]:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if wanted - keys:
            missing[row.code] = sorted(wanted - keys)
    assert missing == {}


@pytest.mark.parametrize("key", ["school_polo", "school_blazer", "pe_shorts"])
def test_a_garment_is_sold_by_school_age(key: str) -> None:
    assert _rows()[key]
    for row in _rows()[key]:
        sizes = [s for s, _ in row.sizes]
        assert sizes[0] == "3-4 Yrs" and sizes[-1] == "15-16 Yrs", row.code
        assert all(AGE.fullmatch(s) for s in sizes), row.code


def test_a_sock_is_sold_by_uk_shoe_size_band_and_the_bands_rank_by_foot() -> None:
    assert _rows()["school_socks"]
    for row in _rows()["school_socks"]:
        assert tuple(s for s, _ in row.sizes) == size_ladder.SOCK_BANDS, row.code
    rec = _templates()["BRD-SCSAN5"]
    assert {s.get("shoe_size_band") for s in rec["skus"]} == set(size_ladder.SOCK_BANDS)
    biggest = next(s for s in rec["skus"] if s["shoe_size_band"] == "UK 4-7")
    second = next(s for s in rec["skus"] if s["shoe_size_band"] == "UK 12.5-3.5")
    smallest = next(s for s in rec["skus"] if s["shoe_size_band"] == "UK 6-8.5")
    scales = [size_ladder.size_scale(rec, s) for s in (smallest, second, biggest)]
    assert None not in scales, "the band is not on the type's size axis"
    assert scales[0] < scales[1] < scales[2], scales


def test_a_sock_lists_its_bands_on_the_product_under_their_own_key() -> None:
    rec = _templates()["BRD-SCSAN5"]
    assert rec.get("size_options") == {"shoe_size_band": list(size_ladder.SOCK_BANDS)}


def test_the_styles_cover_the_issues_values() -> None:
    def values(key: str, attr: str) -> set[str]:
        return {_attr(r, attr) for r in _rows()[key]}

    assert values("school_polo", "pack_size") == {"Single", "2 pack", "3 pack"}
    assert values("school_polo", "sleeve_length") == {"Short", "Long"}
    assert values("school_socks", "pack_size") == {"3 pack", "5 pack", "7 pack"}
    assert values("school_socks", "sock_style") == {"Ankle", "Knee High", "Tights"}
    assert values("school_blazer", "fit") == {"Regular", "Slim", "Plus Fit"}
    assert values("school_blazer", "lining") == {"Half Lined", "Fully Lined"}
    assert values("school_blazer", "badge_ready") == {"Yes", "No"}
    assert values("pe_shorts", "pack_size") >= {"Single", "2 pack"}


# --------------------------------------------------------------------------
# Drawings: each param changes the picture, and what the record states is what is drawn.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("shape", "one", "other"),
    VARIANTS,
    ids=[f"{s}-{next(iter(p.values()))}" for s, _, p in VARIANTS],
)
def test_a_param_changes_the_drawing(shape: str, one: dict, other: dict) -> None:
    assert _svg(shape=shape, **one) != _svg(shape=shape, **other)
    assert _svg(shape=shape) == _svg(shape=shape, **one), "the default is the first reading"


def test_every_style_draws_well_formed_svg_with_no_size_printed() -> None:
    assert _all()
    for row in _all():
        svg = _svg(row)
        xml.dom.minidom.parseString(svg)
        assert len(svg) > 700, row.code
        assert not re.findall(r"<text[^>]*>[^<]*\d[^<]*</text>", svg), row.code


def test_a_polo_draws_a_placket_a_ribbed_collar_and_the_sleeve_it_states() -> None:
    rows = _rows()["school_polo"]
    assert rows
    for row in rows:
        svg = _svg(row)
        assert _count(svg, "placket") == 1 and _count(svg, "rib") == 3, row.code
        sleeve = _attr(row, "sleeve_length").lower()
        assert dict(row.params)["sleeve"] == sleeve, row.code
        assert f'<g class="sleeve-{sleeve}"' in svg, row.code


def test_a_long_sleeve_hangs_lower_than_a_short_one() -> None:
    def lowest(sleeve: str) -> float:
        svg = _svg(shape="school_polo", sleeve=sleeve)
        d = re.search(rf'<g class="sleeve-{sleeve}">(.*?)</g>', svg, re.S).group(1)
        return max(float(n) for n in re.findall(r",(\d+)", d))

    assert lowest("short") < lowest("long")


def test_a_knee_sock_stands_taller_than_an_ankle_sock() -> None:
    def tallest(height: str) -> float:
        svg = _svg(shape="school_socks", height=height)
        return float(re.search(r'class="rib"><path d="M\d+,(-?\d+)', svg).group(1))

    assert tallest("knee") < tallest("ankle")


def test_a_sock_style_draws_the_height_it_states_and_only_tights_a_waistband() -> None:
    rows = _rows()["school_socks"]
    assert rows
    want = {"Ankle": "ankle", "Knee High": "knee", "Tights": "tights"}
    for row in rows:
        height = want[_attr(row, "sock_style")]
        assert dict(row.params)["height"] == height, row.code
        svg = _svg(row)
        assert _count(svg, f"height-{height}") == 1, row.code
        assert _count(svg, "sock") == (0 if height == "tights" else 2), row.code
    assert _count(_svg(shape="school_socks", lone="1"), "sock") == 1


def test_a_blazer_shows_two_buttons_and_a_badge_outline_only_when_badge_ready() -> None:
    rows = _rows()["school_blazer"]
    assert rows
    for row in rows:
        svg = _svg(row)
        assert _count(svg, "button") == 2 and _count(svg, "chest-pocket") == 1, row.code
        ready = _attr(row, "badge_ready") == "Yes"
        assert _count(svg, "badge") == (1 if ready else 0), row.code
    widths = {f: kit_school.BLAZER_HEM[f] for f in ("slim", "regular", "plus")}
    assert widths["slim"] < widths["regular"] < widths["plus"]


def test_a_blazer_row_states_the_fit_it_draws() -> None:
    rows = _rows()["school_blazer"]
    assert rows
    want = {"Regular": "regular", "Slim": "slim", "Plus Fit": "plus"}
    for row in rows:
        assert dict(row.params)["fit"] == want[_attr(row, "fit")], row.code


def test_pe_shorts_draw_an_elastic_waist_and_the_leg_they_state() -> None:
    rows = _rows()["pe_shorts"]
    assert rows
    for row in rows:
        svg = _svg(row)
        leg = _attr(row, "leg_length").lower()
        assert dict(row.params)["leg"] == leg, row.code
        assert _count(svg, "elastic") == 1 and f'<g class="leg-{leg}"' in svg, row.code
    assert kit_school.PE_HEM["short"] < kit_school.PE_HEM["mid"]


@pytest.mark.parametrize("key", ["school_polo", "school_socks", "pe_shorts"])
def test_a_pack_draws_as_many_items_as_it_states(key: str) -> None:
    assert _rows()[key]
    for row in _rows()[key]:
        pack = _attr(row, "pack_size")
        packs = 1 if pack == "Single" else int(pack[0])
        rec = _templates()[row.product_id]
        drawn = image_release.render(rec, rec["skus"][0]).decode()
        assert drawn.count('class="pack-copy"') == (packs if packs > 1 else 0), row.code


def test_a_pack_of_socks_fans_one_sock_a_pair_and_tights_fold_to_one_leg() -> None:
    rec = _templates()["BRD-SCSAN5"]
    drawn = image_release.render(rec, rec["skus"][0]).decode()
    assert 'class="pack-edge"' in drawn, "socks fan rather than stand in rows"
    item = re.search(r'<g id="pack-item-[^"]*">(.*?)</defs>', drawn, re.S).group(1)
    assert _count(item, "sock") == 1
    pair = _svg(shape="school_socks", height="tights")
    folded = _svg(shape="school_socks", height="tights", lone="1")
    assert "L254,84 Q260,190" in pair and "L254,84 Q260,190" not in folded, "one leg, folded"
    assert len(re.findall(r"M\d+,64 L", folded)) < len(re.findall(r"M\d+,64 L", pair))


# --------------------------------------------------------------------------
# Colors, decoys, tree and build.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key", sorted(TYPES))
def test_every_type_offers_the_main_colors_it_comes_in(key: str) -> None:
    ptype = TYPES[key][0]
    assert ptype not in main_colors.EXCEPTIONS
    assert _rows()[key]
    styles = [_templates()[r.product_id] for r in _rows()[key]]
    assert main_colors.missing(styles) == {}
    assert {"Black"} <= main_colors.offered(styles)


def test_a_blazer_comes_only_in_the_dress_code_colors() -> None:
    assert _rows()["school_blazer"]
    for row in _rows()["school_blazer"]:
        colors = {c["color"] for c in _templates()[row.product_id]["color_options"]}
        assert colors and colors <= {"Black", "Navy", "Grey", "Charcoal", "Green", "Burgundy"}


@pytest.mark.parametrize("key", sorted(TYPES))
def test_every_type_carries_decoys_of_all_six_classes(key: str) -> None:
    ptype = TYPES[key][0]
    planned = {s.product_type for s in decoy_apparel.TYPES}
    assert ptype in planned and ptype not in decoy_apparel.EXEMPT
    docs = [d for d in scale.templates(baseline=False) if d["product_id"] in decoy_apparel.IDS]
    mine = [d for d in docs if d["product_type"] == ptype]
    classes = collections.Counter(re.search(r"(\d)\d\d$", d["product_id"]).group(1) for d in mine)
    audience = ptype in decoy_apparel.AUDIENCE_TYPES  # class 3 sits only on these (#781)
    assert len(mine) >= (18 if audience else 15), (ptype, len(mine))
    assert len(classes) == (6 if audience else 5) and min(classes.values()) >= 3, classes


def test_the_types_sit_in_the_tree_under_the_guards_rules() -> None:
    rows = _all()
    assert rows
    paths = [tuple(r.path) for r in rows]
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    titled = [(r.product_id, r.title, r.path) for r in rows]
    assert tree_guard.misplaced_title_findings(titled) == []


def test_the_styles_are_left_out_of_the_derivation() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    ids = {r.product_id for r in _all()}
    assert ids and not (ids & kept)


@pytest.mark.timeout(300)
def test_every_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    assert _all()
    ids = {r.product_id for r in _all()}
    mine = [d for d in scale.documents(scale.build(100_000)) if d["product_id"] in ids]
    assert {d["product_id"] for d in mine} == ids
    assert check_catalog(mine, one_class_per_key=True) == []
    assert {d["category_path"][0] for d in mine} == {ROOT}
