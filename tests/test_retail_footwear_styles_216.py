"""Retail footwear styles (gen#216): plimsolls, clogs, wedges, espadrilles, platform trainers,
mules, jelly shoes and barefoot shoes.

:mod:`footwear_rows` holds the styles (each a :class:`FootwearStyle` of a new ``TYPES`` kind) and
:mod:`kit_footwear` draws them. These checks hold what the issue asked for: every type has its
range (three styles, three brands), a ``product_type`` that names it under the Shoes category,
each key attribute is a structured entry in the export, each style draws its own shape and the
variant axis that changes the look is a drawing param that agrees with the attribute.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import footwear_rows as fw  # noqa: E402
import kit  # noqa: E402
import kit_footwear as kf  # noqa: E402

#: product_type -> (footwear kind, the export keys the issue lists for it).
TYPES = {
    "Plimsolls": ("plimsoll", {"closure", "upper_material", "use", "audience"}),
    "Clogs": ("clog", {"material", "strap", "lined", "upper_material"}),
    "Wedges": ("wedge", {"heel_height", "upper_material"}),
    "Espadrilles": ("espadrille", {"heel_type", "upper_material"}),
    "Platform Trainers": ("platform_trainer", {"platform_height", "upper_material", "closure"}),
    "Mules": ("mule", {"heel_type", "toe_style", "heel_height"}),
    "Jelly Shoes": ("jelly", {"jelly_style", "glitter"}),
    "Barefoot Shoes": ("barefoot", {"sole_thickness", "drop", "closure"}),
}  # fmt: skip

DOCS = fw.docs()


def _of(ptype: str) -> list[dict]:
    return [d for d in DOCS if d["product_type"] == ptype]


def test_every_type_has_three_styles_from_three_brands() -> None:
    got = {t: (len(_of(t)), len({d["brand"] for d in _of(t)})) for t in TYPES}
    assert {t: n for t, n in got.items() if min(n) < 3} == {}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_a_type_names_itself_and_sits_in_the_shoes_category(ptype: str) -> None:
    docs = _of(ptype)
    assert docs, ptype
    for d in docs:
        # the leaf of a platform trainer is Platform Shoes: Platform Trainers beside Trainers
        # breaks the head-noun rule (gen#283) and nested under it the leaf-is-never-a-parent rule
        leaf = "Platform Shoes" if ptype == "Platform Trainers" else ptype
        assert d["category_path"][1:] == ["Shoes", leaf], d["product_id"]
        assert d["category_leaf"] == leaf
        assert d["department"][0] == "Footwear"
        assert fw.TYPES[next(k for k, v in fw.TYPES.items() if v[0] == ptype)][3] == TYPES[ptype][0]


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    assert _of(ptype), ptype
    missing = {}
    for d in _of(ptype):
        doc = export.standard_document(d)
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if TYPES[ptype][1] - keys:
            missing[d["product_id"]] = sorted(TYPES[ptype][1] - keys)
    assert missing == {}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_sku_is_a_color_and_a_size(ptype: str) -> None:
    assert _of(ptype), ptype
    for d in _of(ptype):
        assert len({s["color"] for s in d["skus"]}) >= 3, d["product_id"]
        assert all({"color", "size_uk", "size_eu", "size_us"} <= set(s) for s in d["skus"])


def test_each_type_has_its_own_drawing_kind() -> None:
    kinds = {k for k, _ in TYPES.values()}
    assert len(kinds) == len(TYPES)
    assert kinds <= set(kf.KINDS)
    for d in DOCS:
        if d["product_type"] in TYPES:
            assert d["drawing"]["params"]["kind"] == TYPES[d["product_type"]][0]


def _svg(**params: str) -> str:
    return kit.render("shoe", kit.Fill("solid", "#123456", "#654321"), params=params)


@pytest.mark.parametrize(
    ("kind", "axis", "values"),
    [
        ("wedge", "heel", ("40", "100")),
        ("platform_trainer", "platform", ("30", "60")),
        ("clog", "strap", ("back", "none")),
        ("clog", "body", ("wood", "eva")),
        ("mule", "heel", ("flat", "block")),
        ("mule", "heel", ("kitten", "block")),
        ("mule", "heel", ("flat", "kitten")),
        ("mule", "toe", ("open", "closed")),
        ("espadrille", "heel", ("flat", "wedge")),
        ("jelly", "style", ("sandal", "ballet")),
        ("jelly", "glitter", ("no", "yes")),
        ("barefoot", "sole", ("3", "10")),
    ],
)  # fmt: skip
def test_the_variant_axis_that_changes_the_look_changes_the_drawing(
    kind: str, axis: str, values: tuple[str, str]
) -> None:
    a, b = (_svg(kind=kind, **{axis: v}) for v in values)
    assert a != b


def test_the_eight_kinds_draw_eight_different_shoes() -> None:
    svgs = {k: _svg(kind=k) for k, _ in TYPES.values()}
    assert len(set(svgs.values())) == len(svgs)


def test_a_drawing_param_agrees_with_the_attribute_it_draws() -> None:
    assert all(_of(t) for t in TYPES)
    for d in DOCS:
        attrs = {a["key"]: a["value"] for a in d["attributes"]}
        p = d["drawing"]["params"]
        if d["product_type"] == "Wedges":
            assert float(p["heel"]) == float(attrs["heel_height"]), d["product_id"]
        if d["product_type"] == "Platform Trainers":
            assert float(p["platform"]) == float(attrs["platform_height"]), d["product_id"]
        if d["product_type"] == "Mules":
            assert p["toe"] == attrs["toe_style"].lower(), d["product_id"]
            assert p["heel"] == attrs["heel_type"].lower(), d["product_id"]
        if d["product_type"] == "Clogs":
            assert (p["strap"] == "back") == (attrs["strap"] == "Back strap"), d["product_id"]
            assert p["body"] == attrs["material"].lower(), d["product_id"]
        if d["product_type"] == "Espadrilles":
            assert p["heel"] == attrs["heel_type"].lower(), d["product_id"]
        if d["product_type"] == "Jelly Shoes":
            want = (attrs["jelly_style"].lower(), attrs["glitter"].lower())
            assert (p["style"], p["glitter"]) == want, d["product_id"]
        if d["product_type"] == "Barefoot Shoes":
            assert float(p["sole"]) == float(attrs["sole_thickness"]), d["product_id"]


def test_the_new_types_are_counted_with_the_rest_of_the_footwear() -> None:
    counts = collections.Counter(d["product_type"] for d in DOCS)
    assert sum(counts[t] for t in TYPES) == len(fw.NEW_STYLES) >= 24
