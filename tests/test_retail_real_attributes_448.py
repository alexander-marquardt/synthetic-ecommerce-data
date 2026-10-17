"""Colours and attributes a type really comes in (gen#448, the 2026-10-17 believability audit).

F9: a per-type colour allow-list (``type_colors``) is read by the colour completion, the row
palettes and the decoy clone picker, so tailoring is never yellow, school trousers never pink and
sheer tights never yellow. F10: ``Material`` holds a cloth, ``Finish`` and ``Pattern`` hold the
rest, and the description reads as a sentence. F14: one department per category path, and
"Black Leather" is the colour Black, not a second one.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import main_colors  # noqa: E402
import scale  # noqa: E402
import type_colors  # noqa: E402


@pytest.fixture(scope="module")
def tpls() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def by_id(tpls) -> dict[str, dict]:
    return {r["product_id"]: r for r in tpls}


def _colors(rec: dict) -> list[str]:
    return [c["color"] for c in rec["color_options"]]


def _attr(rec: dict, key: str) -> list[str]:
    return [a["value"] for a in rec["attributes"] if a["key"] == key]


# ---- F9: a type is only sold in the colours it comes in ----------------------------------

#: the audit's example ids and a colour each was wrongly given
F9_EXAMPLES = {
    "BRD-MFFT005": "Yellow",  # formal trousers
    "BRD-MFBL017": "Yellow",  # wedding blazer
    "PLT-DA56600": "Pink",  # school trousers
    "BRD-SCHPLS2": "Yellow",  # school shirt
    "BRD-TGSH10": "Yellow",  # 10 denier tights
    "BRD-CFNWOD": "Yellow",  # ceiling fan
}


@pytest.mark.parametrize("pid,wrong", sorted(F9_EXAMPLES.items()))
def test_an_audited_style_is_not_sold_in_a_colour_its_type_never_comes_in(by_id, pid, wrong):
    rec = by_id[pid]
    assert wrong not in _colors(rec), (pid, _colors(rec))
    assert type_colors.allowed_for(rec["category_path"]) is not None, pid


def test_every_style_of_a_restricted_type_stays_inside_its_allow_list(tpls):
    bad = {
        r["product_id"]: _colors(r)
        for r in tpls
        if r.get("color_options")
        and type_colors.allowed_for(r["category_path"]) is not None
        and not all(type_colors.permits(r["category_path"], c) for c in _colors(r))
    }
    assert not bad, bad


def test_the_allow_list_is_a_declared_exception_with_a_reason():
    assert len(type_colors.RESTRICTED) >= 5
    for prefix, (colors, reason) in type_colors.RESTRICTED.items():
        assert colors and len(reason.split()) >= 3, prefix


def test_a_restricted_group_is_asked_for_only_the_main_colors_it_comes_in(tpls):
    """The gen#275 baseline: tailoring must offer black and white, not yellow."""
    lacking = main_colors.missing(tpls)
    for (ptype, _aud), colors in lacking.items():
        assert not colors, (ptype, colors)
    tailoring = [r for r in tpls if r["category_path"][:2] == ["Mens", "Suits & Tailoring"]]
    offered = main_colors.offered(tailoring)
    assert {"Black", "White"} <= offered
    assert not offered & {"Yellow", "Red", "Pink"}


def test_complete_never_adds_a_color_outside_the_allow_list():
    raw = scale.templates(baseline=False)
    for r in main_colors.complete(main_colors.author_plain(raw)):
        if r.get("color_options") and type_colors.allowed_for(r["category_path"]) is not None:
            assert all(type_colors.permits(r["category_path"], c) for c in _colors(r)), r[
                "product_id"
            ]


def test_the_decoy_clone_picker_reads_the_allow_list(tpls):
    import decoy_apparel

    ids = decoy_apparel.IDS
    school = [r for r in tpls if r["product_id"] in ids and "School Uniform" in r["category_path"]]
    assert school
    for r in school:
        assert not set(_colors(r)) & {"Pink", "Yellow"}, r["product_id"]


def test_a_colour_with_a_material_is_that_colour(tpls):
    """ "Black Leather" is Black: complete() must not add a second "Black" beside it."""
    assert type_colors.base_color("Black Leather") == "Black"
    assert type_colors.permits(["Womens", "Hosiery", "Tights"], "Navy Polka Dot")
    assert not type_colors.permits(["Womens", "Hosiery", "Tights"], "Yellow")
    assert type_colors.base_color("Dark Brown") == "Dark Brown"
    dup = {}
    for r in tpls:
        names = _colors(r) if r.get("color_options") else []
        both = [
            n
            for n in names
            if type_colors.base_color(n) != n and type_colors.base_color(n) in names
        ]
        if both:
            dup[r["product_id"]] = names
    assert not dup, dup


# ---- F10: Material is a cloth, Finish and Pattern are not -------------------------------


def test_the_audited_material_values_are_cloths_not_finishes_or_patterns(by_id):
    for pid, wrong in (("BRD-MFFT005", "Crease Resistant"), ("BRD-MFBL017", "Checked"),
                       ("BRD-MFBX015", "Recycled")):  # fmt: skip
        assert wrong not in _attr(by_id[pid], "material"), pid
    assert "Crease Resistant" in _attr(by_id["BRD-MFFT005"], "finish")
    assert "Check" in _attr(by_id["BRD-MFBL017"], "pattern") + _attr(by_id["BRD-MFBL017"], "finish")


def test_no_material_value_names_a_finish_or_a_pattern(tpls):
    bad = defaultdict(set)
    for r in tpls:
        for v in _attr(r, "material"):
            if type_colors.not_a_cloth(v):
                bad[r["product_id"]].add(v)
    assert not bad, dict(list(bad.items())[:10])


def test_the_not_a_cloth_check_sees_the_audited_words():
    for word in ("Crease Resistant", "Checked", "Recycled", "Easy Iron", "Non-Iron"):
        assert type_colors.not_a_cloth(word), word
    for word in ("Cotton", "Wool blend", "Herringbone", "Recycled Polyester"):
        assert not type_colors.not_a_cloth(word), word


# ---- F10: the description is a sentence -------------------------------------------------

_PLURAL = (
    r"trousers|chinos|jeans|boxers|shorts|socks|tights|leggings|briefs|trunks|joggers|"
    r"dungarees|pyjamas"
)
_A_PLURAL = re.compile(rf"^(?:A|An) (?:[\w'’-]+ ){{0,4}}?(?:{_PLURAL})\b", re.I)


def test_a_plural_noun_takes_no_article(tpls):
    bad = [
        (r["product_id"], r["description"])
        for r in tpls
        if _A_PLURAL.match(r["description"]) and " pair of " not in r["description"].lower()
    ]
    assert not bad, bad[:8]


def test_a_class_four_description_reads_wool_free_not_wool_comma_free(tpls):
    bad = [
        (r["product_id"], r["description"])
        for r in tpls
        if re.search(r"\w, free\b", r["description"])
    ]
    assert not bad, bad[:8]
    assert "wool-free" in " ".join(
        r["description"].lower() for r in tpls if r["product_id"] == "BRD-MDPS240"
    )


def test_the_description_noun_is_the_leaf_noun(by_id):
    rec = by_id["BRD-MFFT005"]
    assert "formal trousers" in rec["description"].lower()
    assert "chinos" not in rec["description"].lower()


def test_the_audited_descriptions_read_as_sentences(by_id):
    boxers = by_id["BRD-MFBX015"]["description"]
    assert not boxers.startswith("A recycled boxers")
    assert "boxer shorts fit" not in boxers
    assert not by_id["BRD-MDPS240"]["description"].startswith("A polo shirt that is wool, free")


# ---- F14: one department per path -------------------------------------------------------


def test_a_category_path_has_one_department(tpls):
    by = defaultdict(set)
    for r in tpls:
        by[tuple(r["category_path"])].add(tuple(r["department"]))
    assert {p: d for p, d in by.items() if len(d) > 1} == {}


def test_shoe_care_is_one_node_with_one_department(tpls):
    deps = defaultdict(set)
    for r in tpls:
        if "Shoe Care" in r["category_path"]:
            deps[tuple(r["category_path"][:3])].add(tuple(r["department"]))
    assert deps and all(len(d) == 1 for d in deps.values()), dict(deps)
    all_deps = {d for ds in deps.values() for d in ds}
    assert len(all_deps) == 1, dict(deps)
    paths = {p for p in deps}
    assert len(paths) == 1, paths
