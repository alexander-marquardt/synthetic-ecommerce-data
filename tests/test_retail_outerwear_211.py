"""Retail outerwear (gen#211): trench coats, raincoats, parkas, puffer jackets, gilets, peacoats,
utility jackets, shackets, boleros, windbreakers and hoodies.

Each type is its own spec under ``type_specs/`` (gen#351) and ``kit_outerwear`` draws it. These
checks hold what the issue asked for: every type has three styles from three invented brands for
Womens, most also for Mens, each style draws as its own shape with the variant axis as a param,
each key attribute is a structured entry in the export (the color and size keys too), a mark a
record states is a mark the drawing shows, each type carries text-match decoys (gen#294's rule),
and the styles reach the scaled build.
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

import decoy_apparel  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

SIZE = {"color", "size"}
#: product type -> (spec key, shape, the key attributes every style states).
TYPES = {
    "Trench Coat": ("trench_coat", "trench_coat",
                    {"garment_length", "belted", "breasting", "fabric", "water_repellent"} | SIZE),
    "Raincoat": ("raincoat", "raincoat",
                 {"garment_length", "hood", "waterproof_rating", "breathable", "lining", "fabric"}
                 | SIZE),
    "Parka": ("parka", "parka",
              {"garment_length", "hood", "hood_type", "fill", "warmth_rating",
               "waterproof"} | SIZE),
    "Puffer Jacket": ("puffer_jacket", "puffer",
                      {"garment_length", "hood", "fill", "packable", "quilting"} | SIZE),
    "Gilet": ("gilet", "gilet", {"fill", "use", "fabric"} | SIZE),
    "Peacoat": ("peacoat", "peacoat", {"garment_length", "breasting", "fabric"} | SIZE),
    "Utility Jacket": ("utility_jacket", "utility_jacket",
                       {"jacket_style", "fabric", "pocket_count", "collar"} | SIZE),
    "Shacket": ("shacket", "shacket", {"fabric", "texture", "garment_weight"} | SIZE),
    "Bolero": ("bolero", "bolero",
               {"bolero_style", "fabric", "sleeve_length", "occasion", "garment_length"} | SIZE),
    "Windbreaker": ("windbreaker", "windbreaker",
                    {"jacket_style", "packable", "hood", "zip_style", "fabric"} | SIZE),
    "Hoodie": ("hoodie", "hoodie", {"zip_style", "fabric", "fit"} | SIZE),
}  # fmt: skip
#: shape -> (parameter, readings): the first reading is the default; two readings must draw
#: differently.
VARIANTS = [
    ("trench_coat", "length", ("mid", "long", "short")),
    ("trench_coat", "belt", ("yes", "no")),
    ("trench_coat", "breasted", ("double", "single")),
    ("raincoat", "length", ("mid", "long", "short")),
    ("raincoat", "hood", ("none", "fixed", "packaway")),
    ("parka", "length", ("long", "mid", "short")),
    ("parka", "hood", ("fixed", "faux_fur")),
    ("puffer", "length", ("regular", "cropped", "longline")),
    ("puffer", "hood", ("no", "yes")),
    ("puffer", "quilt", ("channel", "diamond")),
    ("gilet", "padding", ("padded", "quilted", "fleece")),
    ("peacoat", "length", ("short", "mid", "long")),
    ("peacoat", "breasted", ("double", "single")),
    ("utility_jacket", "pockets", ("4", "2")),
    ("utility_jacket", "collar", ("point", "stand")),
    ("shacket", "teddy", ("no", "yes")),
    ("bolero", "style", ("bolero", "shrug", "cape")),
    ("bolero", "sleeve", ("long", "three_quarter", "short", "none")),
    ("windbreaker", "zip", ("full", "half")),
    ("windbreaker", "hood", ("no", "yes")),
    ("hoodie", "zip", ("pullover", "through")),
]
IDS = [f"{s}-{p}" for s, p, _ in VARIANTS]


def _spec(ptype: str) -> type_registry.TypeSpec:
    spec = type_registry.specs().get(TYPES[ptype][0])
    assert spec is not None, f"{ptype}: no spec type_specs/{TYPES[ptype][0]}.py"
    spec.docs()  # states the spec's brand owners
    return spec


def _rows(ptype: str) -> list:
    return list(_spec(ptype).rows)


def _all_rows() -> list:
    return [r for p in TYPES for r in _rows(p)]


def _svg(row=None, **kw) -> str:
    shape = row.shape if row else kw.pop("shape")
    params = dict(row.params) if row else kw
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _doc(row) -> dict:
    return export.standard_document(row.doc())


def _keys(row) -> set[str]:
    doc = _doc(row)
    return {e["key"] for e in doc["attributes"]} | {
        e["key"] for v in doc["variants"] for e in v["attributes"]
    }


def _values(row, key: str) -> list[str]:
    return [str(e["value"]) for e in _doc(row)["attributes"] if e["key"] == key]


def test_the_eleven_types_are_registered_each_as_its_own_spec() -> None:
    assert [_spec(p).key for p in TYPES] == [k for k, _, _ in TYPES.values()]
    assert {_spec(p).product_type for p in TYPES} == set(TYPES)
    assert not any(_spec(p).derivable for p in TYPES), "the range grows by authored rows"


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_has_three_styles_from_three_invented_brands(ptype: str) -> None:
    rows = _rows(ptype)
    assert len(rows) >= 3 and len({r.brand for r in rows}) >= 3
    assert len({r.title for r in rows}) == len(rows)
    assert {r.brand for r in rows} <= {b for b, _ in _spec(ptype).owners}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_style_draws_as_the_types_own_shape(ptype: str) -> None:
    shape = TYPES[ptype][1]
    assert {r.shape for r in _rows(ptype)} == {shape}
    assert shape in kit.SHAPES
    assert [p for p, t in TYPES.items() if t[1] == shape] == [ptype], "one shape per type"


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_the_type_is_named_and_filed_under_coats_and_jackets(ptype: str) -> None:
    roots = set()
    for row in _rows(ptype):
        assert row.department == "Clothing" and row.path[1] == "Coats & Jackets"
        assert _doc(row)["product_type"] == ptype
        assert row.path[-1] == _doc(row)["category_leaf"]
        roots.add(row.path[0])
    assert "Womens" in roots and roots <= {"Womens", "Mens"}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_key_attribute_is_a_structured_entry_not_a_word_in_the_title(ptype: str) -> None:
    want = TYPES[ptype][2]
    missing = {r.code: want - _keys(r) for r in _rows(ptype)}
    assert {c: m for c, m in missing.items() if m} == {}


def test_the_attribute_values_a_shopper_filters_on_are_all_stated() -> None:
    seen = {
        (p, k): {v for r in _rows(p) for v in _values(r, k)}
        for p, k in [("Trench Coat", "garment_length"), ("Trench Coat", "belted"),
                     ("Trench Coat", "breasting"), ("Raincoat", "garment_length"),
                     ("Raincoat", "hood_type"), ("Puffer Jacket", "fill"),
                     ("Puffer Jacket", "garment_length"), ("Gilet", "fill"), ("Gilet", "use"),
                     ("Shacket", "fabric"), ("Bolero", "bolero_style"),
                     ("Windbreaker", "zip_style"), ("Hoodie", "zip_style"),
                     ("Utility Jacket", "jacket_style")]
    }  # fmt: skip
    assert {"Short", "Mid Length", "Long"} <= seen["Trench Coat", "garment_length"]
    assert seen["Trench Coat", "belted"] == {"Yes", "No"}
    assert seen["Trench Coat", "breasting"] == {"Double-Breasted", "Single-Breasted"}
    assert {"Short", "Mid Length", "Long"} <= seen["Raincoat", "garment_length"]
    assert {"Fixed", "Packaway"} <= seen["Raincoat", "hood_type"]
    assert {"Down", "Feather", "Synthetic"} <= seen["Puffer Jacket", "fill"]
    assert {"Cropped", "Regular", "Longline"} <= seen["Puffer Jacket", "garment_length"]
    assert {"Padded", "Fleece", "Quilted"} <= seen["Gilet", "fill"]
    assert seen["Gilet", "use"] == {"Performance", "Casual"}
    assert {"Flannel", "Corduroy", "Fleece"} <= seen["Shacket", "fabric"]
    assert {"Bolero", "Shrug", "Cape"} <= seen["Bolero", "bolero_style"]
    assert seen["Windbreaker", "zip_style"] == {"Half-Zip", "Full-Zip"}
    assert seen["Hoodie", "zip_style"] == {"Zip-Through", "Pullover"}
    assert {"Utility", "Chore", "Field"} <= seen["Utility Jacket", "jacket_style"]


def test_puffer_jacket_left_the_legacy_list_and_the_ceiling_followed() -> None:
    legacy = type_registry.legacy_types()
    assert ("Clothing", "Puffer Jacket") not in legacy
    assert len(legacy) == type_registry.LEGACY_CEILING


# --------------------------------------------------------------------------
# Drawings: the variant axis is a param, two readings draw differently, and a record states
# what the drawing shows.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("variant", VARIANTS, ids=IDS)
def test_a_shapes_param_changes_the_drawing(variant: tuple) -> None:
    shape, param, readings = variant
    assert shape in kit.SHAPES, f"no {shape} shape registered"
    drawn = [_svg(shape=shape, **{param: r}) for r in readings]
    assert len(set(drawn)) == len(readings), "every reading draws differently"
    assert _svg(shape=shape) == drawn[0], "the default is the first reading"
    solid = kit.render(shape, kit.Fill("solid", "#123456", "#654321"), uid="a")
    striped = kit.render(shape, kit.Fill("stripe", "#abcdef", "#fedcba"), uid="b")
    assert "#123456" in solid and "url(#fill-b)" in striped
    xml.dom.minidom.parseString(solid)


def test_every_style_draws_its_params_and_prints_no_size() -> None:
    known: dict[str, set[str]] = {}
    for shape, param, _ in VARIANTS:
        known.setdefault(shape, set()).add(param)
    rows = _all_rows()
    assert len(rows) >= 11 * 4
    for row in rows:
        assert row.params and {k for k, _ in row.params} <= known[row.shape], row.code
        xml.dom.minidom.parseString(_svg(row))
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        assert [w for w in words if re.search(r"\d", w)] == [], row.code


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_styles_of_one_type_that_differ_on_the_axis_draw_differently(ptype: str) -> None:
    rows = _rows(ptype)
    drawn = {_svg(r) for r in rows}
    assert len(drawn) >= len({tuple(sorted(r.params)) for r in rows}) >= 2


def test_a_belted_trench_coat_draws_its_belt_and_a_hooded_one_its_hood() -> None:
    for row in _rows("Trench Coat"):
        belted = _values(row, "belted") == ["Yes"]
        assert belted == ('class="belt"' in _svg(row)), row.code
    for row in _rows("Raincoat") + _rows("Parka"):
        assert ('class="hood' in _svg(row)) == (_values(row, "hood") != ["No"]), row.code


# --------------------------------------------------------------------------
# A mark a record states is a mark the drawing shows (every stated axis, every row), and a
# feature the title states is a feature the description and the attribute state.
# --------------------------------------------------------------------------

#: The hem each stated length stamps on the torso; written here, not read from ``LEN``.
HEM_OF = {"Short": "hem-short", "Mid Length": "hem-mid", "Long": "hem-long",
          "Cropped": "hem-cropped", "Regular": "hem-regular",
          "Longline": "hem-longline"}  # fmt: skip
#: shape -> the axes a record of that shape states and the drawing marks.
AXES_OF = {
    "trench_coat": {"length", "breasting", "belt"},
    "raincoat": {"length", "hood"},
    "parka": {"length", "hood"},
    "puffer": {"length", "hood", "quilt"},
    "gilet": {"padding"},
    "peacoat": {"length", "breasting"},
    "utility_jacket": {"pockets", "collar"},
    "shacket": {"teddy"},
    "bolero": {"style", "sleeve"},
    "windbreaker": {"zip", "hood"},
    "hoodie": {"zip", "hood"},
}  # fmt: skip
ALL_AXES = {"length", "breasting", "belt", "pockets", "collar", "teddy", "zip", "hood", "quilt",
            "padding", "style", "sleeve"}  # fmt: skip


def _one(row, key: str) -> str | None:
    got = _values(row, key)
    return got[0] if got else None


def _classes(svg: str) -> list[str]:
    """Every class token in the drawing, once per element that carries it."""
    return [t for c in re.findall(r'class="([^"]+)"', svg) for t in c.split()]


def _stated_and_drawn(row) -> dict[str, tuple]:
    """axis -> (what the record states, what the drawing marks), for the axes of the row's shape."""
    svg = _svg(row)
    marks = _classes(svg)
    named = lambda *names: tuple(sorted({m for m in marks if m in names}))  # noqa: E731
    prefixed = lambda p: tuple(sorted({m for m in marks if m.startswith(p)}))  # noqa: E731
    v = lambda k: _one(row, k)  # noqa: E731
    zips = {"Full-Zip": ("zip-full",), "Half-Zip": ("zip-half",), "Zip-Through": ("zip-through",),
            "Pullover": ()}  # fmt: skip
    fills = {"Padded": "channel", "Quilted": "diamond", "Fleece": "pile"}
    styles = {"Cape": "cape", "Bolero": "hem-bolero", "Shrug": "hem-shrug"}
    out: dict[str, tuple] = {}
    for axis in AXES_OF[row.shape]:
        if axis == "length":
            got = ((HEM_OF[v("garment_length")],), prefixed("hem-"))
        elif axis == "belt":
            got = ((1 if v("belted") == "Yes" else 0,), (marks.count("belt"),))
        elif axis == "breasting":
            columns = set(re.findall(r'<circle class="button" cx="([\d.]+)"', svg))
            got = ((2 if v("breasting") == "Double-Breasted" else 1,), (len(columns),))
        elif axis == "pockets":
            got = ((int(v("pocket_count")),), (marks.count("pocket"),))
        elif axis == "collar":
            got = (("collar-" + v("collar").lower(),), prefixed("collar-"))
        elif axis == "teddy":
            got = ((v("texture") == "Teddy",), ("pile" in marks,))
        elif axis == "zip":
            got = (zips[v("zip_style")], named("zip-full", "zip-half", "zip-through"))
        elif axis == "hood":
            kind = v("hood_type")
            hooded = row.shape == "hoodie" or v("hood") == "Yes"
            got = ((hooded, kind == "Packaway", kind == "Faux-Fur Trim"),
                   ("hood" in marks, "hood-pack" in marks, "fur" in marks))  # fmt: skip
        elif axis == "quilt":
            got = ((v("quilting").lower(),), named("channel", "diamond"))
        elif axis == "padding":
            got = ((fills[v("fill")],), named("channel", "diamond", "pile"))
        elif axis == "style":
            got = ((styles[v("bolero_style")],), named("cape", "hem-bolero", "hem-shrug"))
        else:
            sleeve = v("sleeve_length")
            want = () if sleeve == "Sleeveless" else ("sleeve-" + sleeve.lower().replace("-", "_"),)
            got = (want, prefixed("sleeve-"))
        out[axis] = got
    return out


@pytest.mark.parametrize("row", _all_rows(), ids=lambda r: r.code)
def test_every_mark_a_record_states_is_the_mark_the_drawing_shows(row) -> None:
    pairs = _stated_and_drawn(row)
    assert set(pairs) == AXES_OF[row.shape]
    wrong = {axis: pair for axis, pair in pairs.items() if pair[0] != pair[1]}
    assert wrong == {}, f"{row.code}: axis -> (stated, drawn)"


def test_the_drawing_check_reaches_every_axis_the_issue_names() -> None:
    reached = {a for r in _all_rows() for a in _stated_and_drawn(r)}
    assert reached == ALL_AXES
    for axis in ALL_AXES:
        stated = {_stated_and_drawn(r)[axis][0] for r in _all_rows() if axis in AXES_OF[r.shape]}
        assert len(stated) >= 2, f"{axis}: one reading in every row hides a swap"


#: product types -> (title word, attribute key, attribute value that earns it, the description
#: pattern that states it). The title word is in the title exactly when the attribute says so, and
#: the description states it in the same case, never in another.
FEATURES = [
    (("Raincoat", "Parka", "Puffer Jacket", "Windbreaker"), r"\bHooded\b", "hood", "Yes",
     r"\bhood"),
    (("Raincoat",), r"\bLined\b", "lining", "Lined", r"\blin(ed|ing)\b"),
    (("Parka",), r"\bWaterproof\b", "waterproof", "Yes", r"\bwaterproof\b"),
    (("Windbreaker",), r"\bPackable\b", "packable", "Yes", r"\bpack"),
    (("Puffer Jacket",), None, "packable", "Yes", r"\bpacks\b"),
    (("Trench Coat",), r"\bBelted\b", "belted", "Yes", r"\bbelt\b"),
    (("Parka",), r"\bFaux-Fur\b", "hood_type", "Faux-Fur Trim", r"\bfaux-fur\b"),
    (("Raincoat",), r"\bPackaway\b", "hood_type", "Packaway", r"\bpackaway\b"),
    (("Shacket",), r"\bTeddy Fleece\b", "texture", "Teddy", r"\bteddy\b"),
    (("Shacket",), r"\bCheck Flannel\b", "fabric", "Flannel", r"\bflannel\b"),
    (("Gilet",), r"\bPerformance\b", "use", "Performance", r"\brunning\b"),
    (("Puffer Jacket",), r"\bDiamond Quilted\b", "quilting", "Diamond", r"\bdiamond\b"),
    (("Puffer Jacket",), r"\bChannel Quilted\b", "quilting", "Channel", r"\bchannel\b"),
    (("Trench Coat", "Peacoat"), r"\bDouble-Breasted\b", "breasting", "Double-Breasted",
     r"\bdouble-breasted\b"),
    (("Trench Coat", "Peacoat"), r"\bSingle-Breasted\b", "breasting", "Single-Breasted",
     r"\bsingle-breasted\b"),
]  # fmt: skip


def _feature_cases() -> list:
    cases = []
    for ptypes, title, key, value, desc in FEATURES:
        for ptype in ptypes:
            for row in _rows(ptype):
                case = pytest.param(row, title, key, value, desc, id=f"{row.code}-{key}-{value}")
                cases.append(case)
    return cases


@pytest.mark.parametrize(("row", "title", "key", "value", "desc"), _feature_cases())
def test_a_feature_the_title_states_is_in_the_description_and_agrees_with_the_attribute(
    row, title: str | None, key: str, value: str, desc: str
) -> None:
    earned = _one(row, key) == value
    if title:
        assert bool(re.search(title, row.title)) == earned, f"{row.code}: the title and {key}"
    assert bool(re.search(desc, row.description, re.IGNORECASE)) == earned, (
        f"{row.code}: the description and {key}: {row.description}"
    )


def test_every_title_names_the_fabric_or_fill_its_description_names() -> None:
    for row in _all_rows():
        fabric = _one(row, "fabric")
        unnamed = {"Raincoat", "Parka", "Puffer Jacket", "Windbreaker", "Gilet"}
        if fabric and row.product_type not in unnamed:
            assert fabric.lower() in row.title.lower(), row.code
        assert fabric is None or fabric.lower() in row.description.lower(), row.code
        fill = _one(row, "fill")
        assert fill is None or fill.lower() in row.description.lower(), row.code


@pytest.mark.parametrize("row", _all_rows(), ids=lambda r: r.code)
def test_a_description_reads_as_shop_copy(row) -> None:
    """No repeated clause, no dangling comma-clause, no adjective standing as a noun."""
    d = row.description
    assert d.endswith(".") and all(s[:1].isupper() for s in d.split(". ")), d
    assert not re.search(r"\b(\w+) \1\b", d, re.IGNORECASE), f"a word twice: {d}"
    assert not re.search(r",\s+(an?|the)\s+\w+(\s+\w+)?\.", d), f"a dangling clause: {d}"
    parts = re.findall(r"\b(\w+ (?:pocket|hood|collar|belt|zip|lining|cut))\b", d.lower())
    assert len(parts) == len(set(parts)), f"a part said twice: {d}"
    assert "fill rated" not in d and not re.search(r"filled with synthetic(?! insulation)", d), d
    assert not re.search(r"\bcut (regular|slim|oversized)\b", d), f"a fit as a noun: {d}"
    assert not re.search(r"\bA regular\b", d), f"a fit as a noun: {d}"


def test_mens_rows_carry_the_mens_size_run_and_womens_rows_the_womens_one() -> None:
    mens = [r for r in _all_rows() if r.path[0] == "Mens"]
    womens = [r for r in _all_rows() if r.path[0] == "Womens"]
    assert len(mens) >= 6 and len(womens) >= 33
    for row in mens:
        assert row.title.startswith("Mens "), row.code
        assert tuple(s for s, _ in row.sizes) == ("S", "M", "L", "XL", "XXL"), row.code
    for row in womens:
        assert not row.title.startswith("Mens "), row.code
        assert tuple(s for s, _ in row.sizes) == ("XS", "S", "M", "L", "XL"), row.code


#: product type -> the leaf under Coats & Jackets, parents first.
LEAF_OF = {
    "Trench Coat": ("Coats", "Trench Coats"), "Peacoat": ("Coats", "Peacoats"),
    "Raincoat": ("Raincoats",), "Parka": ("Parkas",), "Puffer Jacket": ("Puffer Jackets",),
    "Gilet": ("Gilets",), "Utility Jacket": ("Utility Jackets",), "Shacket": ("Shackets",),
    "Bolero": ("Boleros & Capes",), "Windbreaker": ("Windbreakers",), "Hoodie": ("Hoodies",),
}  # fmt: skip


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_type_sits_in_its_named_leaf(ptype: str) -> None:
    for row in _rows(ptype):
        assert tuple(row.path[1:]) == ("Coats & Jackets", *LEAF_OF[ptype]), row.code
        assert _doc(row)["category_leaf"] == LEAF_OF[ptype][-1], row.code


# --------------------------------------------------------------------------
# Colors: the six main colors across the styles of each type and audience.
# --------------------------------------------------------------------------


def test_every_type_and_audience_offers_the_six_main_colors() -> None:
    assert not set(TYPES) & set(main_colors.EXCEPTIONS)
    groups = main_colors.groups(scale.templates())
    mine = {k: v for k, v in groups.items() if k[0] in TYPES}
    assert {k[0] for k in mine} == set(TYPES)
    lacking = {k: [c for c in main_colors.MAIN_COLORS if c not in main_colors.offered(v)]
               for k, v in mine.items()}  # fmt: skip
    assert {k: c for k, c in lacking.items() if c} == {}


# --------------------------------------------------------------------------
# Text-match decoys (gen#294's rule): the decoy plan of the clothing department covers them.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_carries_its_text_match_decoys(ptype: str) -> None:
    planned = {s.product_type for s in decoy_apparel.types()}
    assert ptype in planned
    spec = _spec(ptype)
    if spec.apparel is not None:
        assert len(spec.apparel.compounds) >= 2, "real class 2 compounds, never an invented one"


def test_the_decoy_table_lists_the_new_types() -> None:
    doc = Path(__file__).resolve().parent.parent / "docs" / "retail-apparel-decoys.md"
    table = doc.read_text()
    assert [p for p in TYPES if p not in table] == []


# --------------------------------------------------------------------------
# Tree and build.
# --------------------------------------------------------------------------


def test_the_new_nodes_sit_in_the_tree_under_the_guards_rules() -> None:
    rows = _all_rows()
    paths = [tuple(r.path) for r in rows]
    assert paths
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    assert (
        tree_guard.misplaced_title_findings([(f"BRD-{r.code}", r.title, r.path) for r in rows])
        == []
    )


@pytest.mark.timeout(300)
def test_every_outerwear_style_reaches_the_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    want = {f"BRD-{r.code}" for r in _all_rows()}
    assert want and want <= got
    mine = [d for d in docs if d["product_id"] in want]
    assert check_catalog(mine, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    assert {d["product_type"] for d in mine} == set(TYPES)
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not (want & kept), "templates only: the seeded derivation is what it was"
