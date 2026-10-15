"""School uniform for Kids, first increment (gen#205): trousers, skirts, pinafores and shirts.

:mod:`school_rows` holds the styles and :mod:`kit_school` draws them. These checks hold what the
issue asked for: each type has its range (three styles from three brands), each style draws as its
own school shape with the variant params the record states, each key attribute is a structured
entry in the export, the sizes are school ages, every type offers the six main colors, carries
text-match decoys of all seven classes, sits in the tree under the tree guard's rules, and
reaches the scaled build.
"""

from __future__ import annotations

import collections
import re
import sys
import xml.dom.minidom
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_apparel  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import kit_school  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import school_rows  # noqa: E402
import tree_guard  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = school_rows.ROWS
ROOT, FAMILY = "Kids", "School Uniform"

#: Each type, its drawing shape, its leaf and the key attributes every one of its styles states.
TYPES = {
    "School Trousers": ("school_trousers", "School Trousers",
                        {"fit", "fabric", "adjustable_waist", "pack_size", "color", "size"}),
    "School Skirt": ("school_skirt", "School Skirts",
                     {"skirt_style", "fabric", "adjustable_waist", "skirt_length", "color",
                      "size"}),
    "School Pinafore": ("school_pinafore", "School Pinafores",
                        {"pinafore_style", "fabric", "color", "size"}),
    "School Shirt": ("school_shirt", "School Shirts",
                     {"sleeve_length", "fit", "easy_care", "fabric", "pack_size", "color",
                      "size"}),
}  # fmt: skip
AGE = re.compile(r"\d{1,2}-\d{1,2} Yrs")


def _keys(row) -> set[str]:
    doc = export.standard_document(row.doc())
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


def _attr(row, key: str) -> str:
    return next(a[2] for a in row.attrs if a[0] == key)


def _svg(row=None, **kw) -> str:
    shape = row.shape if row else kw.pop("shape")
    params = dict(row.params) if row else kw
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _count(svg: str, cls: str) -> int:
    return len(re.findall(rf'<g class="{cls}"', svg))


def test_the_school_types_are_all_authored() -> None:
    assert ROWS
    assert {r.product_type for r in ROWS} == set(TYPES)
    docs = [d for d in scale.templates() if d["product_id"] in scale.SCHOOL_IDS]
    assert len(docs) == len(ROWS)


def test_every_type_has_three_styles_from_three_brands() -> None:
    styles: dict[str, list] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 3} == {}
    assert len(styles) == len(TYPES)


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_a_type_sits_under_kids_school_uniform_in_a_leaf_of_its_own(ptype: str) -> None:
    _, leaf, _ = TYPES[ptype]
    rows = [r for r in ROWS if r.product_type == ptype]
    assert rows
    assert {tuple(r.path) for r in rows} == {(ROOT, FAMILY, leaf)}
    assert {r.audience for r in rows} == {"kids"}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_style_draws_as_its_types_own_school_shape(ptype: str) -> None:
    shape = TYPES[ptype][0]
    assert shape in kit_school.SHAPES
    rows = [r for r in ROWS if r.product_type == ptype]
    assert rows and {r.shape for r in rows} == {shape}
    assert len({TYPES[t][0] for t in TYPES}) == len(TYPES), "no two types share a shape"


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        if TYPES[ptype][2] - _keys(row):
            missing[row.code] = sorted(TYPES[ptype][2] - _keys(row))
    assert missing == {}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_sizes_are_school_ages(ptype: str) -> None:
    for row in (r for r in ROWS if r.product_type == ptype):
        sizes = [s for s, _ in row.sizes]
        assert sizes and all(AGE.fullmatch(s) for s in sizes), row.code
        assert len(sizes) >= 6, row.code
        assert all(AGE.fullmatch(s["size"]) for s in row.skus()), row.code


def test_trousers_run_from_three_to_sixteen_years() -> None:
    for row in (r for r in ROWS if r.product_type == "School Trousers"):
        sizes = [s for s, _ in row.sizes]
        assert sizes[0].startswith("3-") and sizes[-1] == "15-16 Yrs", row.code


def test_the_trouser_fits_a_shopper_names_are_all_sold() -> None:
    fits = {_attr(r, "fit") for r in ROWS if r.product_type == "School Trousers"}
    assert fits >= {"Regular", "Slim", "Longer Length", "Plus Fit"}
    waists = {_attr(r, "adjustable_waist") for r in ROWS if r.product_type == "School Trousers"}
    assert waists == {"Yes", "No"}


def test_packs_are_sold_as_one_two_or_three() -> None:
    packs = collections.defaultdict(set)
    for row in ROWS:
        if row.product_type in ("School Trousers", "School Shirt"):
            packs[row.product_type].add(_attr(row, "pack_size"))
    assert packs["School Trousers"] >= {"Single", "2 pack"}
    assert packs["School Shirt"] >= {"Single", "2 pack", "3 pack"}


# --------------------------------------------------------------------------
# Drawings: each param changes the picture, and what the record states is what is drawn.
# --------------------------------------------------------------------------

VARIANTS = [
    ("school_trousers", {"fit": "regular"}, {"fit": "slim"}),
    ("school_trousers", {"fit": "regular"}, {"fit": "plus"}),
    ("school_trousers", {"length": "regular"}, {"length": "longer"}),
    ("school_skirt", {"style": "pleated"}, {"style": "a_line"}),
    ("school_skirt", {"style": "pleated"}, {"style": "kilt"}),
    ("school_skirt", {"length": "knee"}, {"length": "midi"}),
    ("school_pinafore", {"style": "pinafore"}, {"style": "jumper_dress"}),
    ("school_shirt", {"sleeve": "long"}, {"sleeve": "short"}),
    ("school_shirt", {"pack": "1"}, {"pack": "3"}),
]


@pytest.mark.parametrize(
    ("shape", "one", "other"),
    VARIANTS,
    ids=[
        f"{s}-{next(iter(o))}-{next(iter(o.values()))}-{next(iter(p.values()))}"
        for s, o, p in VARIANTS
    ],
)
def test_a_param_changes_the_drawing(shape: str, one: dict, other: dict) -> None:
    assert _svg(shape=shape, **one) != _svg(shape=shape, **other)
    assert _svg(shape=shape) == _svg(shape=shape, **one), "the default is the first reading"


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg_with_its_own_marks(row) -> None:
    svg = _svg(row)
    xml.dom.minidom.parseString(svg)
    assert len(svg) > 700, "a stub that draws nothing is no drawing"
    assert not re.findall(r"<text[^>]*>[^<]*\d[^<]*</text>", svg), "a size is never printed"


def test_trousers_draw_two_pockets_a_crease_and_the_fit_they_state() -> None:
    for row in (r for r in ROWS if r.product_type == "School Trousers"):
        svg = _svg(row)
        assert _count(svg, "pocket") == 2 and _count(svg, "crease") == 2, row.code
        fit = _attr(row, "fit")
        want = {"Slim": "slim", "Plus Fit": "plus"}.get(fit, "regular")
        assert dict(row.params)["fit"] == want, row.code
        assert (dict(row.params)["length"] == "longer") == (fit == "Longer Length"), row.code
        assert f'<g class="leg-{want}"' in svg, row.code
        assert f'<g class="hem-{dict(row.params)["length"]}"' in svg, row.code


def _leg_extent(**params) -> tuple[float, float]:
    """The lowest point and the widest span of the legs' outline."""
    svg = _svg(shape="school_trousers", **params)
    d = re.search(r'<g class="leg-[a-z]+"><path d="([^"]+)"', svg).group(1)
    pts = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", d)]
    xs, ys = pts[0::2], pts[1::2]
    return max(ys), max(xs) - min(xs)


def test_the_longer_length_hangs_lower_and_the_fit_sets_the_width_of_the_leg() -> None:
    (regular_y, regular_w), (longer_y, _) = _leg_extent(), _leg_extent(length="longer")
    assert longer_y > regular_y
    assert _leg_extent(fit="slim")[1] < regular_w < _leg_extent(fit="plus")[1]


def test_a_skirt_draws_the_folds_its_style_has() -> None:
    folds = {"pleated": 12, "kilt": 8, "a_line": 0}
    for style, n in folds.items():
        assert _count(_svg(shape="school_skirt", style=style), "pleat") == n, style
    assert _count(_svg(shape="school_skirt", style="kilt"), "kilt-pin") == 1
    assert _count(_svg(shape="school_skirt", style="pleated"), "kilt-pin") == 0
    for row in (r for r in ROWS if r.product_type == "School Skirt"):
        want = _attr(row, "skirt_style").lower().replace("-", "_")
        assert dict(row.params)["style"] == want, row.code
        assert _count(_svg(row), "waistband") == 1, row.code
        length = _attr(row, "skirt_length").lower()
        assert dict(row.params)["length"] == length, row.code
        assert f'<g class="hem-{length}"' in _svg(row), row.code


def test_a_pinafore_draws_a_bib_and_straps_a_jumper_dress_a_scoop_neck() -> None:
    pina = _svg(shape="school_pinafore", style="pinafore")
    jump = _svg(shape="school_pinafore", style="jumper_dress")
    assert _count(pina, "strap") == 2 and _count(pina, "bib") == 1 and _count(pina, "blouse") == 1
    assert _count(jump, "strap") == 0 and _count(jump, "scoop") == 1
    assert _count(pina, "pleat") >= 8


def test_a_pinafore_row_draws_the_style_and_the_straps_it_states() -> None:
    rows = [r for r in ROWS if r.product_type == "School Pinafore"]
    assert rows
    for row in rows:
        style = _attr(row, "pinafore_style").lower().replace(" ", "_")
        assert dict(row.params)["style"] == style, row.code
        assert _count(_svg(row), "strap") == (2 if style == "pinafore" else 0), row.code


def test_a_shirt_draws_a_collar_buttons_and_the_sleeve_and_pack_it_states() -> None:
    for row in (r for r in ROWS if r.product_type == "School Shirt"):
        svg = _svg(row)
        assert _count(svg, "collar") == 1 and _count(svg, "button") >= 5, row.code
        sleeve = _attr(row, "sleeve_length").lower()
        assert dict(row.params)["sleeve"] == sleeve, row.code
        assert f'<g class="sleeve-{sleeve}"' in svg, row.code
        pack = _attr(row, "pack_size")
        packs = 1 if pack == "Single" else int(pack[0])
        assert dict(row.params)["pack"] == str(packs), row.code
        assert _count(svg, "pack-item") == (packs if packs > 1 else 0), row.code


# --------------------------------------------------------------------------
# Colors, decoys, tree and build.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_offers_the_six_main_colors_with_no_exception(ptype: str) -> None:
    assert ptype not in main_colors.EXCEPTIONS
    styles = [d for d in scale.templates() if d["product_id"] in scale.SCHOOL_IDS]
    groups = main_colors.groups(styles)
    assert ptype in {t for t, _ in groups}
    assert {k: main_colors.missing(styles).get(k) for k in groups} == {k: None for k in groups}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_carries_decoys_of_all_seven_classes(ptype: str) -> None:
    planned = {s.product_type for s in decoy_apparel.TYPES}
    assert ptype in planned and ptype not in decoy_apparel.EXEMPT
    docs = [d for d in scale.templates(baseline=False) if d["product_id"] in decoy_apparel.IDS]
    mine = [d for d in docs if d["product_type"] == ptype]
    classes = collections.Counter(d["product_id"].split("-D")[1][3] for d in mine)
    assert len(mine) >= 21, (ptype, len(mine))
    assert len(classes) == 7 and min(classes.values()) >= 3, classes


def _paths() -> list[tuple[str, ...]]:
    return [tuple(r.path) for r in ROWS]


def test_the_types_sit_in_the_tree_under_the_guards_rules() -> None:
    paths = [*_paths(), (ROOT, FAMILY, "School Socks")]
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in ROWS]
    assert tree_guard.misplaced_title_findings(rows) == []
    assert {p[-1] for p in _paths()} == {leaf for _, leaf, _ in TYPES.values()}


def test_the_school_styles_are_left_out_of_the_derivation() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert scale.SCHOOL_IDS and not (scale.SCHOOL_IDS & kept)


@pytest.mark.timeout(300)
def test_every_school_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.SCHOOL_IDS]
    assert len(mine) == len(ROWS)
    assert check_catalog(mine, one_class_per_key=True) == []
    assert {d["category_path"][0] for d in mine} == {ROOT}
