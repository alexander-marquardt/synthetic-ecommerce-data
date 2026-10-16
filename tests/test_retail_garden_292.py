"""Garden hoses (gen#292): the Garden department had no garden hose.

The demo replay ``green garden hose`` filters to Garden and Green; the department held 260
products and none whose title holds "garden hose", so the best tier was empty and the next
tier ranked frozen vegetables first. :mod:`type_specs.garden_hose` holds the hoses and
:mod:`kit_garden` draws them. These checks hold what the issue asked for: a Garden product
whose title holds
"garden hose" and offers green, the six main colors across the type (gen#275), a measured
length on the SKUs with its unit, two styles from two brands, a drawing of its own, a place in
the tree under the tree guard's rules, and no derived copies.
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

import export  # noqa: E402
import kit  # noqa: E402
import kit_garden  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

SPEC = type_registry.specs()["garden_hose"]
ROWS = SPEC.rows
HOSE_IDS = frozenset(f"BRD-{r.code}" for r in ROWS)
ROOT = "Garden"
PTYPE = "Garden Hose"
#: What every hose states as a structured entry (the length is the SKU axis, ``item_length``).
KEYS = {"material", "diameter", "item_length", "color"}


def _svg(row=None, **kw) -> str:
    shape = row.shape if row else kw.pop("shape")
    params = dict(row.params) if row else kw
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _docs() -> list[dict]:
    return [d for d in scale.templates() if d["product_id"] in HOSE_IDS]


def test_the_garden_department_has_a_product_titled_garden_hose_in_green() -> None:
    """The replay's query: title holds the phrase, the department is Garden, a SKU is Green."""
    found = [
        d
        for d in scale.templates()
        if d["category_path"][0] == ROOT
        and re.search(r"\bgarden hose\b", d["title"], re.IGNORECASE)
        and any(c["color"] == "Green" for c in d["color_options"])
    ]
    assert found, "no Garden product whose title holds 'garden hose' offers Green"


def test_the_hoses_are_garden_templates_of_their_own() -> None:
    assert ROWS
    assert {r.path[0] for r in ROWS} == {ROOT}
    assert {r.department for r in ROWS} == {ROOT}
    assert {r.product_type for r in ROWS} == {PTYPE}
    assert len(_docs()) == len(ROWS)
    assert {d["category_path"][0] for d in _docs()} == {ROOT}


def test_the_type_has_two_styles_from_two_brands() -> None:
    assert len(ROWS) >= 2
    assert len({r.brand for r in ROWS}) >= 2


def test_every_style_draws_as_its_own_garden_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_garden.SHAPES} == {}
    assert {r.shape for r in ROWS} == {"garden_hose"}


def test_every_key_attribute_is_a_structured_entry_in_the_export() -> None:
    assert ROWS
    missing = {}
    for row in ROWS:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if KEYS - keys:
            missing[row.code] = sorted(KEYS - keys)
    assert missing == {}


def test_the_length_is_on_every_sku_in_metres() -> None:
    assert ROWS
    for row in ROWS:
        assert row.size_key == "length_m", row.code
        assert row.sizes and all("length_m" in s for s in row.skus()), row.code
        doc = export.standard_document(row.doc())
        entries = [e for v in doc["variants"] for e in v["attributes"] if e["key"] == "item_length"]
        assert len(entries) == len(row.skus()), row.code
        assert {e["unit_code"] for e in entries} == {"MTR"}, row.code
        assert all(isinstance(e["value_canonical"], float) for e in entries), row.code


def test_a_longer_hose_costs_more() -> None:
    assert ROWS
    for row in ROWS:
        lengths = [float(n) for n, _ in row.sizes]
        prices = [p for _, p in row.sizes]
        assert len(lengths) >= 3 and lengths == sorted(lengths), row.code
        assert prices == sorted(prices) and len(set(prices)) == len(prices), row.code


def test_the_hose_offers_the_six_main_colors_with_no_exception() -> None:
    assert PTYPE not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in ROWS for c in r.colors}


def test_a_main_color_is_a_plain_swatch_in_the_built_templates() -> None:
    styles = _docs()
    groups = main_colors.groups(styles)
    assert {t for t, _ in groups} == {PTYPE}
    assert {k: main_colors.missing(styles).get(k) for k in groups} == {k: None for k in groups}


def test_a_param_changes_the_drawing() -> None:
    coiled = _svg(shape="garden_hose", style="coiled")
    assert coiled != _svg(shape="garden_hose", style="expandable")
    assert _svg(shape="garden_hose") == coiled, "the first reading is the default"


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg(row) -> None:
    xml.dom.minidom.parseString(_svg(row))


def test_no_hose_drawing_prints_a_length() -> None:
    """A style's lengths share one image, so a printed length would be wrong for all but one."""
    assert ROWS
    printed = {}
    for row in ROWS:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        sized = [w for w in words if re.search(r"\d", w)]
        if sized:
            printed[row.code] = sized
    assert printed == {}


def _paths() -> list[tuple[str, ...]]:
    return [tuple(r.path) for r in ROWS]


def test_the_hose_sits_in_the_tree_under_the_guards_rules() -> None:
    paths = _paths()
    assert paths and {p[:2] for p in paths} == {(ROOT, "Watering")}
    assert {p[-1] for p in paths} == {"Garden Hoses"}
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in ROWS]
    assert tree_guard.misplaced_title_findings(rows) == []


def test_the_hose_styles_are_left_out_of_the_derivation() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not SPEC.derivable
    assert HOSE_IDS and not (HOSE_IDS & kept)


def test_the_hoses_are_in_the_scaled_templates_once() -> None:
    """The golden figures count them with the other type specs (``test_retail_scale`` holds the
    committed total); here the build holds each hose row once."""
    ids = [d["product_id"] for d in scale.templates() if d["product_id"] in HOSE_IDS]
    assert sorted(ids) == sorted(HOSE_IDS)


@pytest.mark.timeout(300)
def test_every_hose_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in HOSE_IDS]
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
    assert mine and mine <= set(owners)
    assert {b: sorted(o) for b, o in owners.items() if b in mine and len(o) != 1} == {}
