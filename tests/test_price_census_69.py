"""The lock-nut and set-screw price census entries (#69 part A), and the
committed parser that measured them (``scripts/price_census_parse.py``).

The page fixtures below keep only the markup the parser reads, copied in shape
from the archived pages (a 2015 product-group page and a 2015 category list
page); the raw pages themselves never ship.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CENSUS = json.loads((ROOT / "reference-statistics" / "P2_price_census.json").read_text())
MANIFEST = json.loads((ROOT / "reference-statistics" / "MANIFEST.json").read_text())
NEW = ("lock_nuts_nylon_insert", "set_screws_hex_socket")


def _module():
    path = ROOT / "scripts" / "price_census_parse.py"
    spec = importlib.util.spec_from_file_location("price_census_parse", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["price_census_parse"] = module  # a dataclass resolves its module by name
    spec.loader.exec_module(module)
    return module


parse = _module()


# --- the entries --------------------------------------------------------------


@pytest.mark.parametrize("type_key", NEW)
def test_each_new_entry_carries_every_figure_a_census_entry_carries(type_key):
    entry = CENSUS["deep_types"].get(type_key, {})
    template = set(CENSUS["deep_types"]["nut_hex"])
    added = {"clearance_rows_priced_at_regular", "collected_by"}
    assert set(entry) == template | added
    assert entry["low_confidence"] is False
    assert entry["key_dimension_attribute"] == "Thread Size"


def test_the_new_entries_are_measured_on_30_or_more_skus_each():
    assert {k: CENSUS["deep_types"].get(k, {}).get("n") for k in NEW} == {
        "lock_nuts_nylon_insert": 100,
        "set_screws_hex_socket": 510,
    }


def test_the_lock_nuts_publish_no_brand_figure_because_they_are_one_brand():
    entry = CENSUS["deep_types"].get("lock_nuts_nylon_insert", {})
    assert entry.get("n_brands") == 1
    assert set(entry["brand_spread_same_spec"]) == {"not_measured"}
    assert "one label" in entry["brand_spread_same_spec"]["not_measured"]
    # A nut has no length, as the hex nut has none.
    assert entry["price_vs_length_at_fixed_diameter"] is None


def test_the_set_screws_publish_no_tier_figure_drawn_from_one_material_line():
    entry = CENSUS["deep_types"].get("set_screws_hex_socket", {})
    spread = entry.get("brand_spread_same_spec", {})
    assert set(spread) == {"n_specs_with_2plus_brands", "not_measured"}
    assert "Nylon" in spread["not_measured"]


def test_the_manifest_records_the_extension_run_and_its_user_agent():
    run = MANIFEST["P2_price_census"].get("extension_69", {})
    assert run.get("types") == list(NEW)
    assert "@" not in run["user_agent"]
    assert run["request_accounting"]["total_http_requests"] == sum(
        run["request_accounting"]["requests_by_phase"].values()
    )


# --- the parser ---------------------------------------------------------------


@pytest.mark.parametrize(
    "value,inches",
    [
        ("8-32", 0.164),  # a #8 screw, not 8 inches
        ("#10-24", 0.19),
        ("1-8", 1.0),
        ("1-14", 1.0),
        ("1-1/4-7", 1.25),
        ('3/4"-10', 0.75),
        ("M6X1mm", 6 / 25.4),
        ("M1.6 x 0.35mm", 1.6 / 25.4),
    ],
)
def test_a_thread_size_reads_as_its_major_diameter(value, inches):
    assert parse.thread_inches(value) == pytest.approx(inches)


@pytest.mark.parametrize(
    "value,inches",
    [("1 1/2 In", 1.5), ("3/8 In.", 0.375), ('3/8"', 0.375), ("6mm", 6 / 25.4)],
)
def test_a_length_reads_in_inches(value, inches):
    assert parse.length_inches(value) == pytest.approx(inches)


@pytest.mark.parametrize(
    "unit,read",
    [("/ each", ("each", 1)), ("/ pkg. of 5", ("pack", 5)), ("/ pkg. of 1,000", ("pack", 1000))],
)
def test_a_sale_unit_reads_as_each_or_a_pack_size(unit, read):
    assert parse.sale_unit(unit) == read


def test_quantiles_interpolate_as_the_57_census_does():
    """The flat-head screws' three each-sold prices are fixed by their census
    p25, p50 and p75 (10.23, 11.77, 12.19); their p10 is the census's."""
    each = CENSUS["deep_types"]["screw_flat_head"]["pack_vs_each"]["each_price_quantiles"]
    assert parse.quantiles([10.23, 11.77, 12.19]) == each


GROUP_PAGE = """
<div class="brand-container">GRAINGER APPROVED</div>
<div class="childProductContainer"><div class="childProductData item">Item # &nbsp;
<span class="childDataValue">4FHY6</span></div>
<p class="gcprice gcprice-clearance gcprice-child-listing-details">
<span class="gcprice-label">Clearance Price</span> <span class="gcprice-value">$2.00</span>
<span class="gcprice-unit">/ pkg. of 5</span></p>
<p class="gcprice gcprice-reduced gcprice-child-listing-details">
<span class="gcprice-reduced-label">Price</span> <span class="gcprice-reduced-value">$19.01</span>
<span class="gcprice-reduced-unit">/ pkg. of 5</span></p>
<div class="childTechDetails">
<span class="techSpecName">Type</span><span class="techSpecValue">With Nylon Insert</span>
<span class="techSpecName">Material</span><span class="techSpecValue">Steel</span>
<span class="techSpecName">Dia./Thread Size</span><span class="techSpecValue">3/4"-10</span>
<span class="techSpecName">Width</span><span class="techSpecValue">1-1/4"</span>
<span class="techSpecName">Package Quantity</span><span class="techSpecValue">5</span></div>
<div class="table-row"><span class="gcprice-value">$99.00</span></div></div>
"""


def test_a_group_row_is_priced_at_its_regular_price_and_holds_no_size():
    (row,) = parse.group_rows(GROUP_PAGE, "20151120064326", "page")
    assert (row.sku, row.brand, row.price, row.pack, row.clearance) == (
        "4FHY6", "GRAINGER APPROVED", 19.01, 5, True,
    )
    assert row.key == pytest.approx(0.75)
    assert row.held == (("Material", "Steel"), ("Package Quantity", "5"),
                        ("Type", "With Nylon Insert"))


def test_a_group_page_that_is_not_nylon_insert_gives_no_rows():
    assert parse.group_rows(GROUP_PAGE.replace("With Nylon Insert", "Conical Top Lock"),
                            "20151120064326", "page") is None


def _listed(sku: str, description: str, price: str) -> str:
    return (
        f'<div class="productBrand">GRAINGER APPROVED</div><div>Item # '
        f'<span class="productInfoValueList">{sku}</span></div>'
        f'<div class="LD hidden">{description}</div>'
        f'<span class="price">${price}</span><span class="bottomText">/ pkg. of 100</span>'
    )


def test_both_list_description_styles_read_as_one_spec():
    page = _listed(
        "3KE72",
        "Socket Set Screw, Alloy Steel, Plain Finish, Cup Point, Hex Socket, "
        "Drive Size 1/8 In, Thread Size 1/4-20, Length 3/8 In, Package Qty 100",
        "9.98",
    ) + _listed(
        "5MMU5",
        "Socket Set Screw, Standard, Alloy Steel, Finish Plain, Thread Size 1/4-28, "
        "Point Type Cup, Drive Type Hex Socket, Overall Length 3/8\", Package Quantity 100",
        "11.20",
    ) + _listed(
        "9ABC1",
        "Slotted Set Screw, Nylon, Natural Finish, Thread Size 1/4-20, Length 3/8 In",
        "4.00",
    )
    rows = parse.list_rows(page, "20150408043348", "page")
    assert [r.sku for r in rows] == ["3KE72", "5MMU5"]
    assert {r.held for r in rows} == {
        (("Finish", "Plain"), ("Material", "Alloy Steel"), ("Point Type", "Cup"))
    }
    assert [r.length for r in rows] == [0.375, 0.375]


def test_one_brand_gives_no_brand_spread():
    (row,) = parse.group_rows(GROUP_PAGE, "20151120064326", "page")
    assert set(parse.brand_spread([row, row])) == {"not_measured"}


def _screw(brand: str, material: str, price: float) -> object:
    return parse.Row("X", brand, "20150408043348", "page", price, False, 100, "pack", 0.25,
                     0.375, (("Material", material),))


def test_specs_shared_in_one_material_only_give_no_brand_spread():
    one_line = [_screw("A", "Nylon", 4.0), _screw("B", "Nylon", 6.0)]
    assert parse.brand_spread(one_line) == {
        "n_specs_with_2plus_brands": 1,
        "not_measured": "every spec two brands share is Nylon (2 brands); no other material "
                        "is offered by two brands, so a spread, brand index or house-label "
                        "ratio would describe that one line, not the type",
    }
    two_lines = one_line + [_screw("A", "Alloy Steel", 10.0), _screw("B", "Alloy Steel", 12.0)]
    spread = parse.brand_spread(two_lines)
    assert (spread["n_specs_with_2plus_brands"], spread["max_over_min_ratio"]["p50"]) == (2, 1.35)
