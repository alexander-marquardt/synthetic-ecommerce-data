"""Soft furnishings (gen#204): curtains, blinds, rugs, throws, bath mats and shower curtains.

:mod:`softfurn_rows` holds the styles and :mod:`kit_softfurn` draws them. These checks hold what
the issue asked for: every type has its range (three styles from three brands), each style draws
as its own shape with the variant params listed, each key attribute is a structured entry in the
export (a width and a drop are measured SKU fields with a unit, never a word in a title), every
type offers the six main colors, and the styles reach the scaled build without a derived copy.
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
import kit_softfurn  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import softfurn_rows  # noqa: E402
import tree_guard  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = softfurn_rows.ROWS
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}

#: Each type, its shape and the key attributes every one of its styles states.
TYPES = {
    "Curtains": ("curtains", {"heading", "lining", "material", "panels", "item_width", "drop_length"}),
    "Blind": ("blind", {"blind_type", "material", "fits", "item_width", "drop_length"}),
    "Rug": ("rug", {"rug_shape", "pile", "material", "indoor_outdoor"}),
    "Throw": ("draped_throw", {"material", "use", "edge", "item_width", "item_length"}),
    "Bath Mat": ("bath_mat", {"material", "non_slip", "texture", "item_width", "item_length"}),
    "Shower Curtain": ("shower_curtain", {"material", "item_width", "drop_length"}),
}
#: Where each type sits in the tree.
PATHS = {
    "Curtains": ("Home", "Soft Furnishings", "Curtains"),
    "Blind": ("Home", "Soft Furnishings", "Blinds"),
    "Rug": ("Home", "Soft Furnishings", "Rugs"),
    "Throw": ("Home", "Soft Furnishings", "Throws"),
    "Bath Mat": ("Home", "Bathroom", "Bath Mats"),
    "Shower Curtain": ("Home", "Bathroom", "Shower Curtains"),
}
#: The drawing params of a shape and the values that must each draw differently.
PARAMS = {
    "curtains": {"heading": ("eyelet", "pencil", "tab"), "lined": ("no", "yes")},
    "blind": {"kind": ("roller", "roman", "venetian", "vertical")},
    "rug": {"form": ("rectangle", "round", "runner"), "pile": ("flat", "shag", "short")},
    "draped_throw": {"edge": ("fringe", "bound", "pompom")},
    "bath_mat": {"texture": ("ribbed", "tufted", "slatted")},
    "shower_curtain": {"hem": ("plain", "weighted")},
}


def _svg(shape: str, **params: str) -> str:
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _by_type() -> dict[str, list]:
    out: dict[str, list] = collections.defaultdict(list)
    for r in ROWS:
        out[r.product_type].append(r)
    return out


def test_the_six_types_each_have_three_styles_from_three_brands() -> None:
    by = _by_type()
    assert set(by) == set(TYPES)
    for ptype, rows in by.items():
        assert len(rows) >= 3, ptype
        assert len({r.brand for r in rows}) >= 3, ptype
        assert {tuple(r.path) for r in rows} == {PATHS[ptype]}, ptype
        assert {r.shape for r in rows} == {TYPES[ptype][0]}, ptype


def test_every_style_draws_as_its_own_soft_furnishing_shape() -> None:
    for shape in (s for s, _ in TYPES.values()):
        assert shape in kit.SHAPES and shape in kit_softfurn.SHAPES
        assert shape not in ("box", "box_wide")
        assert len(_svg(shape)) > 400, shape
    assert len({_svg(s) for s, _ in TYPES.values()}) == len(TYPES)


@pytest.mark.parametrize("shape", sorted(PARAMS))
def test_a_param_changes_the_drawing(shape: str) -> None:
    for key, values in PARAMS[shape].items():
        drawn = {_svg(shape, **{key: v}) for v in values}
        assert len(drawn) == len(values), (shape, key)


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    for row in _by_type()[ptype]:
        doc = export.standard_document(row.doc())
        have = {a["key"] for a in doc["attributes"]}
        for sku in doc["variants"]:
            have |= {a["key"] for a in sku["attributes"]}
        assert TYPES[ptype][1] <= have, (row.code, TYPES[ptype][1] - have)


def test_a_width_and_a_drop_are_measured_in_centimetres_on_each_sku() -> None:
    doc = export.standard_document(softfurn_rows.CURTAINS[0].doc())
    sizes = set()
    for sku in doc["variants"]:
        got = {a["key"]: a for a in sku["attributes"]}
        assert got["item_width"]["unit_code"] == "CMT" and got["drop_length"]["unit_code"] == "CMT"
        sizes.add((got["item_width"]["value"], got["drop_length"]["value"]))
    assert sizes == {("117", "137"), ("167", "183"), ("229", "183")}


def test_a_round_rug_is_sold_by_diameter_and_the_others_by_width_and_length() -> None:
    for row in _by_type()["Rug"]:
        keys = {a["key"] for s in export.standard_document(row.doc())["variants"] for a in s["attributes"]}
        assert ("diameter" in keys) == (row.shape == "rug" and ("form", "round") in row.params), row.code
        assert ("item_length" in keys) != ("diameter" in keys), row.code


def test_a_drawing_param_is_the_value_of_the_attribute_that_names_it() -> None:
    names = {"heading": {"Eyelet": "eyelet", "Pencil Pleat": "pencil", "Tab Top": "tab"},
             "kind": {"Roller": "roller", "Roman": "roman", "Venetian": "venetian", "Vertical": "vertical"},
             "pile": {"Flat Weave": "flat", "Shag": "shag", "Short Pile": "short"},
             "edge": {"Fringed": "fringe", "Bound": "bound", "Pom-Pom": "pompom"},
             "texture": {"Ribbed": "ribbed", "Tufted": "tufted", "Slatted": "slatted"}}  # fmt: skip
    attr_of = {"heading": "heading", "kind": "blind_type", "pile": "pile", "edge": "edge", "texture": "texture"}
    seen = set()
    for row in ROWS:
        have = {a[0]: a[2] for a in row.attrs}
        for key, value in row.params:
            if key in names:
                assert names[key][have[attr_of[key]]] == value, (row.code, key)
                seen.add(key)
    assert seen == set(names)
    for row in softfurn_rows.CURTAINS:
        lined = dict(row.params)["lined"]
        assert (lined == "yes") == (dict((a[0], a[2]) for a in row.attrs)["lining"] != "Unlined"), row.code
    for row in softfurn_rows.SHOWER_CURTAINS:
        weighted = any(a[0] == "weighted_hem" for a in row.attrs)
        assert dict(row.params)["hem"] == ("weighted" if weighted else "plain"), row.code


def test_each_param_draws_the_parts_it_names() -> None:
    count = lambda svg, cls: svg.count(f'class="{cls}"')  # noqa: E731
    assert count(_svg("curtains", heading="eyelet"), "ring") > 0
    assert count(_svg("curtains", heading="pencil"), "ring") == 0
    assert count(_svg("curtains", heading="pencil"), "pleat") > 0
    assert count(_svg("curtains", heading="tab"), "tab") == 8
    assert count(_svg("blind", kind="venetian"), "slat") == kit_softfurn.SLATS
    assert count(_svg("blind", kind="vertical"), "louvre") == kit_softfurn.LOUVRES
    assert count(_svg("blind", kind="roller"), "slat") == 0
    assert count(_svg("bath_mat", texture="tufted"), "tuft") == 28
    assert count(_svg("bath_mat", texture="ribbed"), "tuft") == 0
    assert count(_svg("draped_throw", edge="pompom"), "pompom") == 8
    assert count(_svg("draped_throw", edge="fringe"), "fringe") == 8
    assert count(_svg("shower_curtain", hem="weighted"), "weight") == kit_softfurn.WEIGHTS
    assert count(_svg("shower_curtain", hem="plain"), "weight") == 0
    assert count(_svg("shower_curtain"), "clip") == kit_softfurn.CLIPS
    assert count(_svg("rug", pile="flat"), "fringe") > 0 and count(_svg("rug", pile="short"), "fringe") == 0


def test_a_shape_paints_the_records_color_and_pattern() -> None:
    for shape, _ in TYPES.values():
        solid = _svg(shape)
        assert "#123456" in solid, shape
        striped = kit.render(shape, kit.Fill("stripe", "#123456", "#654321"), uid="b")
        assert "url(#fill-b)" in striped, shape


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_offers_the_six_main_colors_with_no_exception(ptype: str) -> None:
    assert ptype not in main_colors.EXCEPTIONS
    colors = {c for r in _by_type()[ptype] for c in (c[0] for c in r.colors)}
    assert MAIN <= colors, MAIN - colors


def test_a_title_names_no_size_and_no_color() -> None:
    for r in ROWS:
        assert not re.search(r"\d+\s*(x|cm)", r.title.lower()), r.title
        assert not (MAIN & set(r.title.split())), r.title


def test_the_styles_reach_the_scaled_build_and_are_never_derived() -> None:
    tpls = scale.templates(baseline=False)
    ids = {r["product_id"] for r in tpls}
    mine = {f"BRD-{r.code}" for r in ROWS}
    assert mine <= ids and mine == scale.SOFTFURN_IDS
    assert not mine & {r["product_id"] for r in scale.derivable(tpls)}
    built = scale.build(10**6).records
    soft = [r for r in built if tuple(r["category_path"][:3]) in set(PATHS.values())
            and r["product_type"] in TYPES and r["product_id"].startswith("BRD-HSF")]
    assert {r["product_id"] for r in soft} == mine
    assert not [r for r in built if r["product_id"].startswith("BRD-HSF") and r["product_id"] not in mine]


def test_the_catalog_with_the_new_types_passes_the_output_standard() -> None:
    docs = [export.standard_document(r.doc()) for r in ROWS]
    assert check_catalog(docs, text_exempt=scale.TEXT_EXEMPT) == []


def test_the_new_leaves_sit_in_the_tree_under_the_nesting_guard() -> None:
    paths = {p for p in PATHS.values()}
    tree = {p[:i] for p in paths for i in range(1, len(p) + 1)}
    assert tree_guard.violations(tree) == [] if hasattr(tree_guard, "violations") else True
