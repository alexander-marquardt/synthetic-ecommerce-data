"""Footwear (gen#125): about thirty styles across women's, men's and kids', one doc each.

Every style is one product whose SKUs are color x size x width; a size is held
in one field per size system (``size_uk``, ``size_eu``, ``size_us``), each
read from the audience's chart, so the three can never disagree. The boots
row plants three products that say *boot* more than a boot does.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_preview4  # noqa: E402
import distractors as dz  # noqa: E402
import footwear_rows as fw  # noqa: E402
import house_styles as hs  # noqa: E402
import kit_footwear as kf  # noqa: E402
import real_classes as rc  # noqa: E402
from build_preview import drawing_svg  # noqa: E402
from class_model import COLOR_FAMILIES  # noqa: E402
from departments import DEPARTMENTS  # noqa: E402

DOCS = fw.docs()
BY_ID = {d["product_id"]: d for d in DOCS}


def _doc(pid: str) -> dict:
    assert pid in BY_ID, pid
    return BY_ID[pid]


def _attrs(doc: dict) -> dict[str, str]:
    return {a["key"]: a["value"] for a in doc["attributes"]}


def test_thirty_one_styles_across_womens_mens_and_kids() -> None:
    assert len(DOCS) == len(fw.FOOTWEAR) == 31
    assert Counter(d["category_path"][0] for d in DOCS) == {"Women": 16, "Men": 10, "Kids": 5}
    assert len(BY_ID) == 31
    assert all(d["department"][0] == "Footwear" for d in DOCS)


def test_every_kind_of_shoe_the_range_needs_is_sold() -> None:
    types = Counter(d["product_type"] for d in DOCS)
    for t in ("Trainers", "Running Shoes", "Ankle Boots", "Chelsea Boots", "Knee High Boots",
              "Walking Boots", "Sandals", "Court Shoes", "Block Heels", "Kitten Heels",
              "Ballet Pumps", "Loafers", "Brogues", "Slippers", "Wellies",
              "Safety Boots"):  # fmt: skip
        assert types[t] >= 1, t
    assert sum(d["sku_count"] for d in DOCS) == 2392


def test_each_size_system_is_its_own_field_read_from_the_audiences_chart() -> None:
    for d in DOCS:
        chart = fw.CHARTS[fw.chart_of(d)]
        for k in d["skus"]:
            assert (k["size_uk"], k["size_eu"], k["size_us"]) in chart.values(), k["sku"]
    assert fw.WOMEN.get("5") == ("5", "38", "7")
    assert fw.MEN.get("9") == ("9", "43", "10")
    assert fw.MEN.get("8.5") == ("8.5", "42.5", "9.5")
    assert fw.KIDS.get("10 Infant") == ("10 Infant", "28", "10.5C")
    assert fw.KIDS.get("2 Junior") == ("2 Junior", "34", "2.5Y")
    assert fw.SLIPPERS_WOMEN.get("M") == ("5-6", "38-39", "7-8")


def test_a_slipper_is_sized_s_m_l_and_says_each_systems_range() -> None:
    d = _doc("FTW-WSLMOC")
    assert d["size_options"]["size"] == ["S", "M", "L"]
    assert d["size_options"]["size_uk"] == ["3-4", "5-6", "7-8"]


def test_half_sizes_only_where_a_shoe_is_really_cut_in_them() -> None:
    def halves(pid: str) -> list[str]:
        return [s for s in _doc(pid)["size_options"]["size_uk"] if s.endswith(".5")]

    assert halves("FTW-WRUNCR") == ["3.5", "4.5", "5.5", "6.5", "7.5", "8.5"]
    assert halves("FTW-MBRODB") == ["6.5", "7.5", "8.5", "9.5", "10.5"]
    for pid in ("FTW-WWELGL", "FTW-KWELPD", "FTW-KSCHLL", "FTW-MSAFS3"):
        assert halves(pid) == [], pid


def test_width_is_a_selector_and_wide_is_cut_only_in_its_sizes() -> None:
    run = _doc("FTW-WRUNCR")
    assert run["size_options"]["width"] == ["Standard", "Wide"]
    wide = {k["size_uk"] for k in run["skus"] if k["width"] == "Wide"}
    assert wide == {"4", "4.5", "5", "5.5", "6", "6.5", "7", "7.5", "8"}
    school = _doc("FTW-KSCHLL")
    assert school["size_options"]["width"] == ["F", "G", "H"]
    assert _doc("FTW-WBALLT")["size_options"]["width"] == ["Standard", "Wide", "Extra Wide"]
    for d in DOCS:
        assert all("width" in k for k in d["skus"]), d["product_id"]


def test_a_kids_style_costs_more_in_junior_sizes() -> None:
    d = _doc("FTW-KTRHLT")
    by = {k["size_uk"]: k["price"] for k in d["skus"] if k["color"] == "Navy"}
    assert by["13 Infant"] == 18.0 and by["1 Junior"] == 22.0
    assert (d["price_min"], d["price_max"]) == (18.0, 22.0)


def test_two_to_six_colors_each_with_one_material_and_family() -> None:
    for d in DOCS:
        n = len(d["color_options"])
        assert 2 <= n <= 6, d["product_id"]
        for k in d["skus"]:
            assert k["upper_material"] in fw.MATERIALS
            assert k["color_family"] in COLOR_FAMILIES
        assert {o["family"] for o in d["color_options"]} <= set(COLOR_FAMILIES)
    mats = {k["upper_material"] for d in DOCS for k in d["skus"]}
    assert {"leather", "suede", "canvas", "synthetic"} <= mats


def test_closures_and_materials_are_attributes_a_filter_reads() -> None:
    for d in DOCS:
        a = _attrs(d)
        assert a["closure"] in fw.CLOSURES, d["product_id"]
        assert a["sole"], d["product_id"]
    heels = {pid: float(_attrs(_doc(pid))["heel_height"]) for pid in
             ("FTW-WCRTST", "FTW-WBLKAS", "FTW-WKITSB", "FTW-WBALLT")}  # fmt: skip
    assert heels == {"FTW-WCRTST": 95.0, "FTW-WBLKAS": 60.0, "FTW-WKITSB": 35.0,
                     "FTW-WBALLT": 5.0}  # fmt: skip


def test_the_safety_boot_bridges_footwear_and_workwear() -> None:
    d = _doc("FTW-MSAFS3")
    assert d["department"] == ["Footwear", "Workwear & PPE"]
    a = _attrs(d)
    assert a["safety_rating"] == "S3"
    assert a["toe_cap"] == "Steel"
    assert d["drawing"]["label"] == "S3"
    others = [x["product_id"] for x in DOCS if "Workwear & PPE" in x["department"]]
    assert others == ["FTW-MSAFS3"]


def test_departments_paths_and_brands_hold_the_corpus_rules() -> None:
    for d in DOCS:
        assert set(d["department"]) <= set(DEPARTMENTS)
    assert rc.check_category_paths(DOCS) == []
    assert sorted({d["brand"] for d in DOCS} - set(hs.HOUSE_STYLES)) == []
    ranks = sorted(d["bestseller_rank"] for d in DOCS)
    assert ranks == list(range(1, 32))


def test_option_lists_are_the_sku_set() -> None:
    for d in DOCS:
        assert [o["color"] for o in d["color_options"]] == list(
            dict.fromkeys(k["color"] for k in d["skus"])
        )
        for key, values in d["size_options"].items():
            assert values == list(dict.fromkeys(k[key] for k in d["skus"] if key in k))


def test_an_unknown_size_material_or_too_few_colors_is_refused() -> None:
    assert fw.FOOTWEAR
    base = fw.FOOTWEAR[0]
    with pytest.raises(ValueError, match="not on the women chart"):
        fw.FootwearStyle(**{**base.__dict__, "sizes": ("3", "21")})
    with pytest.raises(ValueError, match="material"):
        fw.FootwearStyle(**{**base.__dict__, "colors": (fw.sh("Red", "#c00", "red", "vinyl"),
                                                        *base.colors[1:])})  # fmt: skip
    with pytest.raises(ValueError, match="2 to 6 colors"):
        fw.FootwearStyle(**{**base.__dict__, "colors": base.colors[:1]})
    with pytest.raises(ValueError, match="wide"):
        fw.FootwearStyle(**{**base.__dict__, "wide": ("2",)})


# --------------------------------------------------------------------------
# Drawings: one side-view shoe, parametric on kind and material
# --------------------------------------------------------------------------


def test_every_footwear_drawing_is_well_formed_and_shows_its_material() -> None:
    for d in DOCS:
        svg = drawing_svg(d)
        assert ET.fromstring(svg).tag.endswith("svg")
        assert f'class="tex-{d["drawing"]["params"]["material"]}"' in svg, d["product_id"]


def test_the_shaft_height_tells_a_shoe_from_an_ankle_boot_from_a_knee_boot() -> None:
    top = {k: kf.top(k) for k in ("ballet", "trainer", "ankle_boot", "knee_boot")}
    assert top["knee_boot"] < top["ankle_boot"] < top["trainer"] < top["ballet"]


def test_a_heel_kind_draws_a_heel_and_a_flat_does_not() -> None:
    def svg(kind: str) -> str:
        return "".join(kf.shoe("#000000", kf.Fill(), None, kind=kind, material="leather"))

    assert 'class="heel"' in svg("court")
    assert 'class="heel"' not in svg("ballet")
    assert svg("court") != svg("kitten")


def test_every_kind_draws_and_an_unknown_kind_is_refused() -> None:
    assert len(kf.KINDS) == 17
    for kind in kf.KINDS:
        for mat in fw.MATERIALS:
            ET.fromstring(f"<g>{''.join(kf.shoe('#336699', kf.Fill(), None, kind, mat))}</g>")
    with pytest.raises(KeyError):
        kf.shoe("#000000", kf.Fill(), None, kind="clog", material="leather")


# --------------------------------------------------------------------------
# The boots row: three planted products say "boot" more than a boot does
# --------------------------------------------------------------------------


def test_the_boots_distractors_outrank_every_boot_on_text() -> None:
    cat = fw.catalog()
    assert [d for d in cat if fw.BOOTS.is_intended(d)]
    dz.check((fw.BOOTS,), cat)
    best, each = dz.scores(fw.BOOTS, cat)
    assert best > 0
    assert [pid for pid, _ in each] == ["PLT-BOOTORG", "PLT-BOOTPOL", "PLT-BOOTSOK"]
    assert fw.BOOTS.cls == "Complements and accessories"


def test_footwear_leaves_the_round_four_rows_holding() -> None:
    assert len(fw.catalog()) > len(dz.corpus())
    dz.check(dz.TABLE, fw.catalog())


def test_the_preview_shows_footwear_and_its_planted_distractors() -> None:
    sections = build_preview4.samples()
    shown = [r["product_id"] for r in sections.get("Footwear", [])]
    assert shown == [d["product_id"] for d in DOCS]
    assert len(sections.get("Footwear distractors", [])) == 3
    html, _ = build_preview4.outputs()
    assert html.count("Distractor for <b>boots</b>") == 3
    assert re.search(r"<i>boots</i> → a pair of boots", html)


def test_the_readme_names_the_boots_row() -> None:
    readme = (HERE.parents[1] / "README.md").read_text(encoding="utf-8")
    assert f"| {fw.BOOTS.cls} | *{fw.BOOTS.query}*" in readme
