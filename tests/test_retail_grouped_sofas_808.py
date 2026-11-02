"""Grouped sofas and sofa cushions (gen#808): one product, several versions.

A search for a blue sofa cushion or a sofa with grouping on showed no grouped card: the cushions
held no blue and the sofas sold each seat count as its own product. :mod:`sofa_groups` adds
cushions sold by color and size, and sofas sold as a 2 seater, a 3 seater and a corner sofa.
These checks hold the issue's Done-when lines: the SKUs of each product, the fields they share,
the axes they vary on, one drawing per SKU, and a product name that states no axis value.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import export, kit, scale, sofa_groups, sofa_rows

CUSHIONS = ("Home", "Soft Furnishings", "Cushions")
SOFAS = ("Home", "Furniture", "Sofas")
CORNER = (*SOFAS, "Corner Sofas")
CONFIGURATIONS = {"2 Seater", "3 Seater", "Corner"}
SIZES = {"40 x 40cm", "45 x 45cm", "50 x 50cm"}


def _docs(rows) -> list[tuple[dict, dict]]:
    """Each row's build record and its exported document."""
    return [(rec, export.standard_document(rec)) for rec in (r.doc() for r in rows)]


def _values(doc: dict, key: str) -> list[str]:
    """The value of ``key`` on each SKU, in SKU order (one value each)."""
    return [
        next(e["value"] for e in v["attributes"] if e["key"] == key) for v in doc["variants"]
    ]


def _style(doc: dict, key: str) -> set[str]:
    return {e["value"] for e in doc["attributes"] if e["key"] == key}


SOFA_DOCS = _docs(sofa_groups.SOFAS)
CUSHION_DOCS = _docs(sofa_groups.CUSHIONS)


def test_there_are_two_or_three_of_each_group() -> None:
    assert 2 <= len(SOFA_DOCS) <= 3
    assert 2 <= len(CUSHION_DOCS) <= 3


@pytest.mark.parametrize("pair", SOFA_DOCS, ids=lambda p: p[1]["product_id"])
def test_a_sofa_is_one_product_sold_as_a_2_seater_a_3_seater_and_a_corner(pair) -> None:
    _rec, doc = pair
    assert doc["variant_count"] == 3
    assert set(_values(doc, "configuration")) == CONFIGURATIONS
    assert doc["variant_axes"] == ["configuration"]
    # one brand, name, fabric and color across the versions
    assert len({v["title"] for v in doc["variants"]}) == 1
    assert len(set(_values(doc, "color"))) == 1
    assert len(_style(doc, "material")) == 1
    # the seat count follows the version, so a seat-count filter still narrows
    seats = dict(zip(_values(doc, "configuration"), _values(doc, "seat_count"), strict=True))
    assert seats["2 Seater"] == "2" and seats["3 Seater"] == "3"
    assert int(seats["Corner"]) > 3


@pytest.mark.parametrize("pair", SOFA_DOCS, ids=lambda p: p[1]["product_id"])
def test_a_sofa_with_a_corner_version_is_filed_under_sofas_and_corner_sofas(pair) -> None:
    _rec, doc = pair
    assert doc["product_type"] == "Sofa"
    assert tuple(doc["category_path"]) == SOFAS
    assert [tuple(p) for p in doc.get("category_paths", ())] == [SOFAS, CORNER]


@pytest.mark.parametrize("pair", CUSHION_DOCS, ids=lambda p: p[1]["product_id"])
def test_a_cushion_is_one_product_sold_by_color_and_size(pair) -> None:
    _rec, doc = pair
    assert tuple(doc["category_path"]) == CUSHIONS
    assert doc["product_type"] == "Cushion"
    colors, sizes = _values(doc, "color"), _values(doc, "size")
    assert "Blue" in colors
    assert set(sizes) == SIZES
    assert doc["variant_count"] == len(set(colors)) * len(SIZES)
    assert doc["variant_axes"] == ["color", "size"]
    assert len({v["title"] for v in doc["variants"]}) == 1
    assert len(_style(doc, "fabric")) == 1


def test_no_two_skus_share_a_drawing() -> None:
    seen: dict[str, str] = {}
    clash = []
    for rec, _doc in (*SOFA_DOCS, *CUSHION_DOCS):
        for sku in rec["skus"]:
            drawn = export.drawing_id(rec, sku).rsplit("/", 1)[1]
            if drawn in seen:
                clash.append((seen[drawn], sku["sku"]))
            seen[drawn] = sku["sku"]
    assert len(seen) == sum(len(rec["skus"]) for rec, _ in (*SOFA_DOCS, *CUSHION_DOCS))
    assert clash == []


def test_each_sofa_version_draws_its_own_shape() -> None:
    assert SOFA_DOCS
    fill = kit.Fill("solid", "#123456", "#654321")
    rec, _doc = SOFA_DOCS[0]
    drawn = {
        c: kit.render(rec["drawing"]["shape"], fill, params=rec["drawing"]["params"] | {
            "configuration": c})
        for c in CONFIGURATIONS
    }
    assert len(set(drawn.values())) == 3
    rest = {k: v for k, v in rec["drawing"]["params"].items() if k != "configuration"}
    assert drawn["2 Seater"] == kit.render("sofa_seats", fill, params={"seats": "2", **rest})


def test_no_product_name_states_a_value_of_its_axes() -> None:
    stated = {}
    for _rec, doc in (*SOFA_DOCS, *CUSHION_DOCS):
        words = doc["title"].lower()
        values = {e["value"] for v in doc["variants"] for e in v["attributes"]
                  if e["key"] in doc["variant_axes"]}  # fmt: skip
        hits = sorted(v for v in values if str(v).lower() in words)
        hits += ["seater"] if "seater" in words else []
        if hits:
            stated[doc["product_id"]] = hits
    assert stated == {}


def test_the_groups_are_seating_templates_that_meet_the_standard() -> None:
    ids = {r.product_id for r in (*sofa_groups.SOFAS, *sofa_groups.CUSHIONS)}
    assert ids <= {r.product_id for r in sofa_rows.ROWS}
    assert ids <= scale.left_out()
    assert check_catalog([doc for _rec, doc in (*SOFA_DOCS, *CUSHION_DOCS)]) == []
