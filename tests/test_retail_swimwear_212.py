"""Swimwear types (gen#212): swimsuits, bikini tops and bottoms, tankinis, swim shorts, kids' and
baby swimsuits, period swimwear, cover-ups and changing robes.

Each type is a spec of ``type_specs/`` (gen#351), its rows are in :mod:`swimwear_rows` and
:mod:`kit_swimwear` draws them. These checks hold what the issue asked for: every type has its
range (three styles, three brands), each style draws as its own shape, each key attribute the
issue lists is a structured entry in the export, a feature the record states is the feature the
drawing shows, the six main colors are sold, and the styles reach the scaled build.
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
import scale  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

#: Each spec key, its product type, and every key attribute the issue lists for it, by the export
#: key. Size, color and audience are pinned as well as the listed ones.
TYPES = {
    "swimsuit": ("Swimsuit", {"cut", "tummy_control", "padded", "coverage", "leg_cut", "size",
                              "cup_size", "color", "audience"}),
    "bikini_top": ("Bikini Top", {"top_shape", "padded", "size", "color", "audience"}),
    "bikini_bottoms": ("Bikini Bottoms", {"rise", "tie_side", "size", "color", "audience"}),
    "tankini": ("Tankini", {"length", "support", "matching_bottoms", "size", "color", "audience"}),
    "swim_shorts": ("Swim Shorts", {"length", "waist_type", "quick_dry", "size", "color",
                                    "audience"}),
    "kids_swimsuit": ("Kids Swimsuit", {"uv_protection", "sleeve", "nappy_friendly", "size",
                                        "color", "audience"}),
    "period_swimwear": ("Period Swimwear", {"absorbency", "cut", "size", "color", "audience"}),
    "cover_up": ("Cover-Up", {"length", "fabric", "size", "color", "audience"}),
    "changing_robe": ("Changing Robe", {"lining", "waterproof_shell", "length", "size", "color",
                                        "audience"}),
}  # fmt: skip
#: The keys a SKU states (the variant axes).
VARIANT_KEYS = {"swimsuit": {"color", "size", "cup_size"}}
MAIN_COLORS = {"Red", "Blue", "Green", "Yellow", "Black", "White"}


def _specs() -> dict[str, type_registry.TypeSpec]:
    return {k: s for k, s in type_registry.specs().items() if k in TYPES}


def _rows(key: str) -> tuple:
    spec = type_registry.specs().get(key)
    return spec.rows if spec else ()


ALL = [(k, r) for k in TYPES for r in _rows(k)]


def _attr(row, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _svg(row) -> str:
    return kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))


def _marks(row) -> dict[str, int]:
    return dict(collections.Counter(re.findall(r'<g class="([a-z-]+)"', _svg(row))))


def _expected(row) -> dict[str, int]:
    """The marked groups the record's attributes say the drawing must hold."""
    one = lambda key, yes: _attr(row, key) == [yes]  # noqa: E731
    s = row.shape
    out: dict[str, int] = {}
    if s == "swimsuit":
        out = {"leg-opening": 2}
        if one("tummy_control", "Yes"):
            out["ruching"] = 1
        if one("padded", "Yes"):
            out["cup"] = 2
    elif s == "bikini_top":
        shape = _attr(row, "top_shape")[0]
        out = {"Triangle": {"strap": 2, "cup": 2}, "Balcony": {"strap": 2, "cup": 2},
               "Underwired": {"strap": 2, "cup": 2, "underwire": 2},
               "Bandeau": {"band": 1, "tie": 2}}[shape]  # fmt: skip
    elif s == "bikini_bottoms":
        out = {"leg-opening": 2}
        if one("tie_side", "Yes"):
            out["tie"] = 2
    elif s == "tankini":
        out = {"strap": 2}
        if one("support", "Medium"):
            out["shelf-band"] = 1
        if one("support", "Underwired"):
            out["underwire"] = 2
    elif s == "swim_shorts":
        out = {"leg": 2, "waistband": 1}
        out["drawstring" if one("waist_type", "Drawstring") else "elastic"] = 1
    elif s == "kids_swimsuit":
        if _attr(row, "sleeve") != ["Sleeveless"]:
            out["sleeve"] = 2
        if _attr(row, "uv_protection") != ["None"]:
            out["upf-badge"] = 1
        if one("nappy_friendly", "Yes"):
            out["leg-band"] = 2
    elif s == "period_swimwear":
        out = {"waistband": 1, "absorbent-layer": 2 if one("absorbency", "Moderate") else 1}
    elif s == "cover_up":
        out = {"sleeve": 2}
    elif s == "changing_robe":
        out = {"hood": 1, "lining": 1, "sleeve": 2}
        if one("waterproof_shell", "Yes"):
            out["storm-flap"] = 1
    return out


def test_every_swimwear_type_is_a_registered_spec() -> None:
    specs = _specs()
    assert sorted(specs) == sorted(TYPES)
    assert {k: s.product_type for k, s in specs.items()} == {k: v[0] for k, v in TYPES.items()}
    assert {s.department for s in specs.values()} == {"Clothing"}


def test_every_type_has_three_styles_from_three_brands() -> None:
    thin = {k: (len(_rows(k)), len({r.brand for r in _rows(k)})) for k in TYPES}
    assert {k: n for k, n in thin.items() if min(n) < 3} == {}


def test_every_type_nests_under_the_swimwear_node_of_its_audience() -> None:
    paths = {k: {r.path[:3] if r.path[0] != "Kids" else r.path for r in _rows(k)} for k in TYPES}
    for k, ps in paths.items():
        assert ps, k
        assert all("Swimwear" in p and p[0] in ("Womens", "Mens", "Kids") for p in ps), (k, ps)


def test_every_style_draws_as_its_own_swimwear_shape() -> None:
    own = {k: {r.shape for r in _rows(k)} for k in TYPES}
    assert own == {k: {k} for k in TYPES}
    assert {k for k in TYPES if k not in kit.SHAPES} == set()


@pytest.mark.parametrize("key", sorted(TYPES))
def test_every_key_attribute_is_a_structured_entry_in_the_export(key: str) -> None:
    missing = {}
    for row in _rows(key):
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if TYPES[key][1] - keys:
            missing[row.code] = sorted(TYPES[key][1] - keys)
    assert missing == {}
    assert _rows(key)


def test_a_swimsuit_sku_states_its_size_color_and_cup() -> None:
    short = {}
    for row in _rows("swimsuit"):
        for v in export.standard_document(row.doc())["variants"]:
            got = {e["key"] for e in v["attributes"]}
            if VARIANT_KEYS["swimsuit"] - got:
                short[row.code] = sorted(VARIANT_KEYS["swimsuit"] - got)
    assert short == {}
    assert _rows("swimsuit")


@pytest.mark.parametrize(("key", "row"), ALL, ids=lambda v: v if isinstance(v, str) else v.code)
def test_the_drawing_shows_the_marks_its_record_states(key: str, row) -> None:
    """Cups, ruching, straps, ties, sleeves, a hood, absorbent layers: one marked group per
    piece the record's attributes state, and no other."""
    assert _marks(row) == _expected(row)


def test_every_param_axis_changes_the_drawing() -> None:
    """Two readings of one axis draw differently, so a style's param is not decoration."""
    pairs = [
        ("swimsuit", "cut", "scoop", "halter"), ("swimsuit", "leg", "regular", "high"),
        ("bikini_top", "top_shape", "triangle", "bandeau"),
        ("bikini_bottoms", "rise", "high", "low"), ("tankini", "length", "crop", "long"),
        ("swim_shorts", "length", "short", "long"), ("kids_swimsuit", "sleeve", "none", "long"),
        ("period_swimwear", "cut", "bikini", "high_waisted"),
        ("cover_up", "length", "mini", "maxi"),
        ("changing_robe", "length", "hip", "full"),
        ("changing_robe", "lining", "fleece", "towelling"),
        ("kids_swimsuit", "sleeve", "short", "long"),
    ]  # fmt: skip
    fill = kit.Fill("solid", "#123456", "#654321")
    same = [p for p in pairs if kit.render(p[0], fill, params={p[1]: p[2]})
            == kit.render(p[0], fill, params={p[1]: p[3]})]  # fmt: skip
    assert same == []


def test_a_short_sleeve_ends_high_and_a_long_one_runs_to_the_wrist() -> None:
    """The sleeve the record states is the length drawn, on both arms."""
    fill = kit.Fill("solid", "#123456", "#654321")

    def ends(sleeve: str) -> list[int]:
        svg = kit.render("kids_swimsuit", fill, params={"sleeve": sleeve})
        paths = re.findall(r'<g class="sleeve"><path d="([^"]+)"', svg)
        return [max(int(y) for y in re.findall(r",(\d+)", d)) for d in paths]

    short, long_ = ends("short"), ends("long")
    assert len(short) == len(long_) == 2
    assert max(short) < 150 < 200 < min(long_)


@pytest.mark.parametrize("key", sorted(TYPES))
def test_every_type_sells_the_six_main_colors(key: str) -> None:
    colors = {c[0] for r in _rows(key) for c in r.colors}
    assert colors >= MAIN_COLORS
    assert _rows(key)


def test_the_range_states_each_value_the_issue_names() -> None:
    def seen(key: str, attr: str) -> set[str]:
        return {v for r in _rows(key) for v in _attr(r, attr)}

    assert {"Scoop", "Plunge", "Halter", "One Shoulder"} <= seen("swimsuit", "cut")
    assert {"Triangle", "Bandeau", "Balcony", "Underwired"} <= seen("bikini_top", "top_shape")
    assert {"High-Waisted", "Mid-Rise", "Low-Rise"} <= seen("bikini_bottoms", "rise")
    assert {"Short", "Mid", "Long"} <= seen("swim_shorts", "length")
    assert {"Drawstring", "Elasticated"} <= seen("swim_shorts", "waist_type")
    assert {"Light", "Moderate"} <= seen("period_swimwear", "absorbency")
    assert {"Fleece", "Towelling"} <= seen("changing_robe", "lining")
    assert {"Cotton", "Viscose"} <= seen("cover_up", "fabric")
    assert {"Sleeveless", "Short", "Long"} <= seen("kids_swimsuit", "sleeve")
    assert {"Girls", "Boys", "Baby"} <= {r.path[1] for r in _rows("kids_swimsuit")}


def test_no_swimwear_drawing_prints_a_size() -> None:
    """A style's sizes share one image, so a printed one would be wrong for most."""
    printed = {r.code: re.findall(r"<text[^>]*>([^<]*)</text>", _svg(r)) for _, r in ALL}
    assert {c: w for c, w in printed.items() if w} == {}
    assert ALL


@pytest.mark.timeout(300)
def test_every_swimwear_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    ids = {f"BRD-{r.code}" for _, r in ALL}
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert ids
    assert sorted(ids - got) == []
    mine = [d for d in docs if d["product_id"] in ids]
    assert len(mine) == len(ids)
    assert check_catalog(mine, one_class_per_key=True) == []
