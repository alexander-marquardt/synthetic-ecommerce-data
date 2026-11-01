"""Package quantity is a line's second variant dimension, each pair with its own card (#14).

A pack line's every (size, quantity) pair is a child SKU with its own price, title and card, and
the pairs are a sparse matrix, never a cross product. The card draws N items fanned; the detail
stays the single unit's drawing. ``quantity > 10`` is a range over the published field.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter

import pytest
import yaml

from synthetic_ecommerce_data.core import emit, standard
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.drawing import draw_sku
from synthetic_ecommerce_data.core.drawing.sheet import FIGURE_HEIGHT
from synthetic_ecommerce_data.core.drawing.svg import WIDTH
from synthetic_ecommerce_data.core.model import Catalog
from synthetic_ecommerce_data.domains.industrial import pack
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.product_split import (
    distribution_problems,
    skus_per_product,
)
from synthetic_ecommerce_data.prism import field_map

PACK = "Units per Pack"
MILL = "end_mill_square"


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return generate(GeneratorConfig())


@pytest.fixture(scope="module")
def pack_lines(catalog):
    return [
        line
        for line in catalog.lines
        if line.type_key in pack.AXES
        and any(a.name == "Units per Pack" for c in line.children for a in c.attributes)
    ]


@pytest.fixture(scope="module")
def flat(catalog) -> list[dict]:
    return list(emit.iter_flat(catalog))


def _quantity(child) -> int:
    return int(child.get(PACK).value)


def _size(child) -> tuple:
    """A SKU's size: everything it publishes but its pack."""
    return tuple((a.name, a.value) for a in child.attributes if a.name != PACK)


def test_every_axis_type_sells_a_pack_line(pack_lines):
    assert {line.type_key for line in pack_lines} == set(pack.AXES)
    assert len(pack_lines) > 20


def test_the_matrix_is_sparse_and_quantity_one_offers_every_size(pack_lines):
    """Quantity 1 offers each size, and the larger quantities only some: a cross product of
    sizes and quantities would invent SKUs that do not exist."""
    for line in pack_lines:
        pairs = [(_size(child), _quantity(child)) for child in line.children]
        assert len(set(pairs)) == len(pairs), line.product_id
        sizes = {size for size, _ in pairs}
        quantities = {quantity for _, quantity in pairs}
        assert quantities == {1, *pack.AXES[line.type_key]}, line.product_id
        assert len(pairs) < len(sizes) * len(quantities), line.product_id
        assert {size for size, quantity in pairs if quantity == 1} == sizes, line.product_id
        rows = Counter(quantity for _, quantity in pairs)
        assert all(rows[q] < rows[1] for q in pack.AXES[line.type_key]), line.product_id


def test_a_line_with_a_pack_axis_has_two_variant_axes(catalog, pack_lines):
    for line in pack_lines:
        axes = emit.line_variant_axes(catalog, line)
        assert "units_per_pack" in axes and len(axes) >= 2, (line.product_id, axes)


def test_a_pack_is_a_discount_and_not_a_multiple_of_its_single(pack_lines):
    for line in pack_lines:
        singles = {_size(c): c.price_usd for c in line.children if _quantity(c) == 1}
        for child in line.children:
            quantity = _quantity(child)
            if quantity > 1:
                unit = singles[_size(child)]
                assert unit < child.price_usd < unit * quantity, child.sku


def test_the_title_leads_with_the_count_above_one_and_only_there(pack_lines):
    for line in pack_lines:
        for child in line.children:
            quantity = _quantity(child)
            led = re.match(r"(\d+)PCS ", child.title)
            if quantity == 1:
                assert led is None, child.title
            else:
                assert led is not None and int(led[1]) == quantity, child.title
                assert child.description.startswith(f"{quantity}PCS "), child.sku


def test_no_pack_title_passes_the_title_cap(pack_lines):
    longest = max(len(child.title) for line in pack_lines for child in line.children)
    assert longest <= pack.TITLE_CAP


def test_the_price_is_quoted_per_pack_on_a_pack_and_each_on_a_single(pack_lines):
    for line in pack_lines:
        for child in line.children:
            wanted = "Each" if _quantity(child) == 1 else "Per Pack"
            assert child.pricing_unit == wanted, child.sku


def test_the_pass_moves_no_sku_of_a_catalog_without_it(catalog):
    """Additive, as the grouped pass is: only the ear plug's own line changes."""
    without = generate(GeneratorConfig(pack_axis=False))
    built = {child.sku: child for _, child in catalog.all_skus()}
    for line, child in without.all_skus():
        if line.type_key != "foam_ear_plugs":
            assert built[child.sku] == child, child.sku
    assert catalog.sku_count > without.sku_count


# --- the card and the detail --------------------------------------------------


MILL_RECORD = {
    "Milling Dia.": '1/2"',
    "Shank Dia.": '1/2"',
    "Length of Cut": '1"',
    "Overall Length": '3"',
    "Flutes": "4",
    "Material": "Solid Carbide",
}


def _card(quantity: int | None, product_type: str = MILL) -> bytes:
    record = dict(MILL_RECORD)
    if quantity is not None:
        record[PACK] = str(quantity)
    return draw_sku(product_type, "Braddlestow", record)[0]


def _outlines(data: bytes) -> list[list[tuple[float, float]]]:
    """The items a card draws behind its top one: the tilted four-cornered closed subpaths, in
    sheet units. Nothing else on a sheet is one: a figure stands square to it."""
    found: list[list[tuple[float, float]]] = []
    for element in ET.fromstring(data).iter():
        d = element.attrib.get("d", "")
        if not element.tag.endswith("path") or element.attrib.get("fill", "").startswith("url"):
            continue
        for sub in re.findall(r"M[^MZ]*Z", d):
            numbers = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", sub)]
            points = list(zip(numbers[::2], numbers[1::2], strict=True))
            square = len(points) != 4 or points[0][1] == points[1][1]
            if not square and re.fullmatch(r"M[-\d. ]+(L[-\d. ]+){3}Z", sub):
                found.append(points)
    return found


@pytest.mark.parametrize("quantity", [2, 5, 10])
def test_a_pack_card_draws_its_published_quantity(quantity):
    assert len(_outlines(_card(quantity))) == quantity - 1


def test_a_single_draws_no_fan_at_all():
    assert _outlines(_card(1)) == []
    assert _card(1) == _card(None)


def test_a_different_quantity_draws_different_bytes():
    assert len({_card(q) for q in (1, 2, 5, 10)}) == 4


def test_the_fan_leans_out_to_both_sides_of_the_top_item():
    """Bites a row of copies and a one-sided lean alike: the outlines' tips are spread."""
    points = [p for outline in _outlines(_card(5)) for p in outline]
    middle = WIDTH / 2
    assert min(x for x, _ in points) < middle - 30
    assert max(x for x, _ in points) > middle + 30


def test_a_bolts_pack_is_how_its_price_is_quoted_and_is_not_drawn():
    record = {"Dia./Thread Size": "1/4-20", "Length": '1"', "Material": "Steel"}
    single = draw_sku("bolt_hex", "Braddlestow", {**record, PACK: "1"})[0]
    box = draw_sku("bolt_hex", "Braddlestow", {**record, PACK: "100"})[0]
    assert single == box


def test_every_pack_card_stays_on_its_sheet_above_the_plate(catalog):
    checked = 0
    for _, child, data, _ in emit.iter_drawings(catalog):
        if child.detail_image_id:
            points = [p for outline in _outlines(data) for p in outline]
            assert points, child.sku
            assert all(0 <= x <= WIDTH and 0 <= y <= FIGURE_HEIGHT for x, y in points), child.sku
            checked += 1
    assert checked > 100


def test_a_pack_detail_is_its_singles_own_asset(flat, pack_lines):
    by_sku = {doc["sku"]: doc for doc in flat}
    for line in pack_lines:
        singles = {_size(c): c for c in line.children if _quantity(c) == 1}
        for child in line.children:
            doc = by_sku[child.sku]
            assert doc["image_url"].endswith(f"/{child.image_id}.svg")
            single = by_sku[singles[_size(child)].sku]
            assert doc["image_detail_url"] == single["image_url"], child.sku
            assert single["image_detail_url"] == single["image_url"], child.sku


def test_a_nested_variant_of_a_pack_names_its_singles_drawing_too(catalog, flat):
    details = {doc["sku"]: doc["image_detail_url"] for doc in flat}
    variants = [v for doc in emit.iter_nested(catalog) for v in doc["variants"]]
    assert {v["sku"]: v["image_detail_url"] for v in variants} == details


def test_no_drawing_is_rendered_for_a_pack_detail(catalog, flat):
    """One row per SKU: the card. A detail adds no asset, so no dimensioned five-up exists."""
    manifest = list(emit.iter_image_manifest(catalog))
    assert len(manifest) == len(flat) == catalog.sku_count
    rendered = {row["url"] for row in manifest}
    assert {doc["image_detail_url"] for doc in flat} <= rendered


def test_a_detail_that_names_another_products_drawing_is_refused(pack_lines):
    line = pack_lines[0]
    other = pack_lines[1].children[0].image_id
    (first, *rest) = line.children
    planted = type(line)(**{**line.__dict__, "children": ((_with_detail(first, other)), *rest)})
    with pytest.raises(emit.UnresolvedImageError, match="detail"):
        emit.check_image_ids(Catalog(lines=(planted,)))


def _with_detail(child, detail: str):
    return type(child)(**{**child.__dict__, "detail_image_id": detail})


def test_the_standard_takes_a_detail_of_the_product_and_refuses_one_of_another():
    image = "end_mill_square/OST-K663-0001/97NR28"
    row = {
        "image_id": image,
        "image_url": f"/i/{image}.svg",
        "image_detail_url": "/i/end_mill_square/OST-K663-0001/11AA11.svg",
    }
    assert standard._image("V", row) == []  # noqa: SLF001
    row["image_detail_url"] = "/i/end_mill_square/OST-K663-0002/11AA11.svg"
    assert len(standard._image("V", row)) == 1  # noqa: SLF001


# --- quantity > 10 ------------------------------------------------------------


def test_quantity_over_ten_is_a_range_over_the_published_field(flat):
    rendered = yaml.safe_load(field_map.render(flat))
    (entry,) = [f for f in rendered["fields"] if f["name"] == "units_per_pack"]
    assert entry["type"] == "numeric"
    assert entry["source"] == "facets_num.units_per_pack"
    # The committed reason names the threshold, so nobody turns it back into a list.
    assert "# Units per pack -- a range: a shopper asks for a threshold" in field_map.render(flat)


def test_the_product_audit_counts_the_pairs_of_a_pack_line(catalog):
    """A type's largest product is its sizes across its quantities, not its sizes alone."""
    assert distribution_problems(skus_per_product(catalog), GeneratorConfig()) == []


def test_quantity_over_ten_returns_exactly_the_published_packs_over_ten(flat):
    """The filter a range facet runs, against what each SKU publishes: a SKU whose count reached
    the attribute and not ``facets_num`` would drop out of the filter silently."""
    wanted = {
        doc["sku"]
        for doc in flat
        for a in doc["attributes"]
        if a["key"] == "units_per_pack" and a["value_canonical"] > 10
    }
    got = {
        doc["sku"]
        for doc in flat
        if doc["facets_num"].get("units_per_pack", 0) > 10
    }
    assert got == wanted

    plugs = {doc["sku"]: doc for doc in flat if doc["product_type"] == "foam_ear_plugs"}
    numbers = {sku: doc["facets_num"]["units_per_pack"] for sku, doc in plugs.items()}
    assert {sku for sku, n in numbers.items() if n > 10} == plugs.keys() & got
    assert sorted(set(numbers.values())) == [1.0, 10.0, 25.0, 50.0]
