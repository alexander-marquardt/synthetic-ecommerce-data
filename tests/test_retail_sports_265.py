"""Sports & Outdoors, first increment (gen#265): camping and yoga & fitness.

:mod:`sports_rows` holds the styles and :mod:`kit_sports` draws them. These checks hold what the
issue asked for: the department is a root of its own, every type has its range (two styles from
two brands), each style draws as its own shape, each key attribute is a structured entry in the
export with its unit, a measured axis is on the SKUs, every type offers the six main colors, the
department sits in the tree under the tree guard's rules, and the styles reach the scaled build.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import kit  # noqa: E402
import kit_sports  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import sports_rows  # noqa: E402
import tree_guard  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = sports_rows.ROWS
ROOT = "Sports & Outdoors"

#: Each type and the key attributes every one of its styles states (the issue's attributes: a
#: tent's berth and season rating, a mat's thickness, a dumbbell's weight).
KEYS = {
    "Tent": {"tent_type", "season_rating", "hydrostatic_head", "material", "berth", "color"},
    "Sleeping Bag": {"bag_shape", "season_rating", "fill", "material", "item_length", "color"},
    "Camping Chair": {"frame_material", "max_load_kg", "arms", "color"},
    "Yoga Mat": {"material", "surface", "thickness", "color"},
    "Dumbbell": {"material", "head_shape", "sold_as", "weight", "color"},
    "Kettlebell": {"material", "weight", "color"},
    "Foam Roller": {"surface", "material", "item_length", "color"},
}

#: The SKU axis of a type that has one, the export key it becomes and its unit code.
AXES = {
    "Tent": ("berth", "berth", "C62"),
    "Sleeping Bag": ("length_cm", "item_length", "CMT"),
    "Yoga Mat": ("thickness_mm", "thickness", "MMT"),
    "Dumbbell": ("weight_kg", "weight", "KGM"),
    "Kettlebell": ("weight_kg", "weight", "KGM"),
    "Foam Roller": ("length_cm", "item_length", "CMT"),
}


def _keys(row) -> set[str]:
    doc = export.standard_document(row.doc())
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


def _svg(row=None, **kw) -> str:
    shape = row.shape if row else kw.pop("shape")
    params = dict(row.params) if row else kw
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def test_the_department_is_a_root_of_its_own() -> None:
    assert ROWS
    assert {r.path[0] for r in ROWS} == {ROOT}
    assert {r.department for r in ROWS} == {ROOT}
    docs = [d for d in scale.templates() if d["product_id"] in scale.SPORTS_IDS]
    assert len(docs) == len(ROWS)
    assert {d["category_path"][0] for d in docs} == {ROOT}


def test_every_type_has_two_styles_from_two_brands() -> None:
    styles: dict[str, list] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 2} == {}


def test_every_style_draws_as_its_own_sports_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_sports.SHAPES} == {}
    assert len({r.shape for r in ROWS}) == len(KEYS)


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        if KEYS[ptype] - _keys(row):
            missing[row.code] = sorted(KEYS[ptype] - _keys(row))
    assert missing == {}


@pytest.mark.parametrize("ptype", sorted(AXES))
def test_a_measured_axis_is_on_every_sku_with_its_unit(ptype: str) -> None:
    sku_key, export_key, unit = AXES[ptype]
    for row in (r for r in ROWS if r.product_type == ptype):
        assert row.size_key == sku_key, row.code
        assert row.sizes and all(sku_key in s for s in row.skus()), row.code
        doc = export.standard_document(row.doc())
        entries = [e for v in doc["variants"] for e in v["attributes"] if e["key"] == export_key]
        assert len(entries) == len(row.skus()), row.code
        assert {e["unit_code"] for e in entries} == {unit}, row.code
        assert all(isinstance(e["value_canonical"], float) for e in entries), row.code


def test_a_tent_sells_each_berth_and_the_berths_grow_with_the_price() -> None:
    for row in (r for r in ROWS if r.product_type == "Tent"):
        berths = [int(b) for b, _ in row.sizes]
        prices = [p for _, p in row.sizes]
        assert len(berths) >= 2 and berths == sorted(berths), row.code
        assert prices == sorted(prices) and len(set(prices)) == len(prices), row.code


def test_a_weight_is_sold_in_kilograms_that_differ_by_style() -> None:
    weights = {r.code: [w for w, _ in r.sizes] for r in ROWS if r.size_key == "weight_kg"}
    assert len(weights) == 4 and all(len(set(w)) == len(w) >= 3 for w in weights.values())
    assert weights["KTBCST"] != weights["KTBVIN"]


@pytest.mark.parametrize("ptype", ["Tent", "Sleeping Bag"])
def test_the_season_rating_is_one_attribute_for_tents_and_bags(ptype: str) -> None:
    ratings = {
        a[2] for r in ROWS if r.product_type == ptype for a in r.attrs if a[0] == "season_rating"
    }
    assert ratings and all(re.fullmatch(r"[1-4] Season", v) for v in ratings)
    assert len(ratings) >= 2, "a range filter needs more than one rating"


# --------------------------------------------------------------------------
# Drawings: each param changes the picture, and the count the record states is the count drawn.
# --------------------------------------------------------------------------

VARIANTS = [
    ("tent", {"style": "dome"}, {"style": "tunnel"}),
    ("sleeping_bag", {"style": "mummy"}, {"style": "rectangular"}),
    ("camp_chair", {"arms": "no"}, {"arms": "yes"}),
    ("yoga_mat", {"state": "flat"}, {"state": "rolled"}),
    ("dumbbell", {"style": "hex"}, {"style": "round"}),
    ("foam_roller", {"texture": "smooth"}, {"texture": "grid"}),
]


@pytest.mark.parametrize(("shape", "one", "other"), VARIANTS, ids=[v[0] for v in VARIANTS])
def test_a_param_changes_the_drawing(shape: str, one: dict, other: dict) -> None:
    assert _svg(shape=shape, **one) != _svg(shape=shape, **other)
    assert _svg(shape=shape) == _svg(shape=shape, **one), "the default is the first reading"


def test_the_kettlebell_draws_bare() -> None:
    assert _svg(shape="kettlebell").startswith("<svg")


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg(row) -> None:
    import xml.dom.minidom

    xml.dom.minidom.parseString(_svg(row))


def test_a_grid_foam_roller_draws_one_marked_group_per_bump_and_a_smooth_one_none() -> None:
    grid = len(re.findall(r'<g class="bump"', _svg(shape="foam_roller", texture="grid")))
    assert grid == kit_sports.BUMP_COLUMNS * kit_sports.BUMP_ROWS == 12
    assert '<g class="bump"' not in _svg(shape="foam_roller", texture="smooth")
    for row in (r for r in ROWS if r.shape == "foam_roller"):
        want = 12 if dict(row.params)["texture"] == "grid" else 0
        assert len(re.findall(r'<g class="bump"', _svg(row))) == want, row.code


def test_no_sports_drawing_prints_a_size() -> None:
    """A style's sizes share one image, so a printed berth, thickness or weight would be wrong
    for all but one."""
    printed = {}
    for row in ROWS:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        sized = [w for w in words if re.search(r"\d", w)]
        if sized:
            printed[row.code] = sized
    assert printed == {}


# --------------------------------------------------------------------------
# Colors, tree and build.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_type_offers_the_six_main_colors_with_no_exception(ptype: str) -> None:
    assert ptype not in main_colors.EXCEPTIONS
    offered = {c[0] for r in ROWS if r.product_type == ptype for c in r.colors}
    assert set(main_colors.MAIN_COLORS) <= offered


def test_a_main_color_is_a_plain_swatch_in_the_built_templates() -> None:
    styles = [d for d in scale.templates() if d["product_id"] in scale.SPORTS_IDS]
    groups = main_colors.groups(styles)
    assert {t for t, _ in groups} == set(KEYS)
    assert {k: main_colors.missing(styles).get(k) for k in groups} == {k: None for k in groups}


def _paths() -> list[tuple[str, ...]]:
    return [tuple(r.path) for r in ROWS]


def test_the_department_sits_in_the_tree_under_the_guards_rules() -> None:
    paths = _paths()
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in ROWS]
    assert tree_guard.misplaced_title_findings(rows) == []


def test_the_tree_has_camping_and_yoga_and_fitness_under_the_root() -> None:
    families = {p[1] for p in _paths()}
    assert families == {"Camping", "Yoga & Fitness"}
    assert {p[-1] for p in _paths()} >= {"Dome Tents", "Tunnel Tents", "Sleeping Bags", "Dumbbells"}
    assert all(len(p) >= 3 for p in _paths())


def test_a_tent_filed_beside_its_generic_node_is_caught_by_the_guard() -> None:
    """Mutant: ``Tents`` back beside ``Dome Tents`` (the node the nesting guard exists for)."""
    mutant = [*_paths(), (ROOT, "Camping", "Tents")]
    assert tree_guard.sibling_head_noun_findings(mutant) == []  # Tents is the parent of both
    flat = [(ROOT, "Camping", "Dome Tents"), (ROOT, "Camping", "Tents")]
    assert tree_guard.sibling_head_noun_findings(flat) != []


def test_a_title_naming_a_deeper_node_must_sit_in_it() -> None:
    row = [("BRD-X", "Dome Tent", (ROOT, "Camping", "Tents"))]
    assert tree_guard.misplaced_title_findings(row) == []  # no deeper node in this tree
    rows = [*row, ("BRD-Y", "Family Dome Tent", (ROOT, "Camping", "Tents", "Dome Tents"))]
    assert tree_guard.misplaced_title_findings(rows) != []


def test_the_sports_styles_are_left_out_of_the_derivation() -> None:
    tpls = scale.templates()
    kept = {r["product_id"] for r in scale.derivable(tpls)}
    assert scale.SPORTS_IDS and not (scale.SPORTS_IDS & kept)


@pytest.mark.timeout(300)
def test_every_sports_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.SPORTS_IDS]
    assert len(mine) == len(ROWS)
    assert check_catalog(mine, one_class_per_key=True) == []
    assert {d["category_path"][0] for d in mine} == {ROOT}


@pytest.mark.timeout(300)
def test_every_brand_has_exactly_one_owner_across_templates_and_derived_styles() -> None:
    records = scale.build(100_000).records
    owners: dict[str, set[str]] = collections.defaultdict(set)
    for rec in [*scale.templates(), *records]:
        if "brand_owner" in rec:
            owners[rec["brand"]].add(rec["brand_owner"])
    mine = {r.brand for r in ROWS}
    assert mine <= set(owners)
    assert {b: sorted(o) for b, o in owners.items() if b in mine and len(o) != 1} == {}
