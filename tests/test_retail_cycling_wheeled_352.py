"""Bicycles, bike helmets, kayaks, kick scooters and skateboards in Sports & Outdoors (gen#352).

The maintainer's ask: the demo catalog shows that it carries sports and outdoor goods, a few
products per type. The department and its tents, sleeping bags and bike pumps were there already
(gen#265, gen#368); this file holds the five types that were missing: each is a type of its own
with its facets, the six main colors, a drawing of its own, two text-match decoys, and a query
that finds it ("bicycle", "bike helmet", "kayak", "scooter", "skateboard"; "tent" is held too).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_product_words as dpw  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import kit_sports  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import sports_rows  # noqa: E402
import tree_guard  # noqa: E402

ROOT = "Sports & Outdoors"
#: The five types, the facets every style states (a variant's or a product's) and its SKU axis:
#: the export key and unit, or None when the SKU axis is a plain word.
TYPES = {
    "Bicycle": {"bike_type", "frame_material", "gears", "brake_type", "color"},
    "Bike Helmet": {"helmet_type", "impact_protection", "visor", "size", "color"},
    "Kayak": {"kayak_type", "seats", "max_load_kg", "material", "item_length", "color"},
    "Kick Scooter": {"scooter_type", "wheel_size", "max_load_kg", "folds", "color"},
    "Skateboard": {"board_type", "material", "deck_width", "color"},
}
#: query -> the type its first page must hold.
QUERIES = {
    "bicycle": "Bicycle",
    "bike helmet": "Bike Helmet",
    "tent": "Tent",
    "kayak": "Kayak",
    "scooter": "Kick Scooter",
    "skateboard": "Skateboard",
}


def _rows(ptype: str) -> list:
    return [r for r in sports_rows.ROWS if r.product_type == ptype]


def _keys(row) -> set[str]:
    doc = export.standard_document(row.doc())
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


def test_the_five_types_are_live_in_the_department(ceiling: list[dict]) -> None:
    live = {r["product_type"] for r in ceiling if r["category_path"][0] == ROOT}
    assert set(TYPES) <= live, set(TYPES) - live


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_style_states_the_types_facets(ptype: str) -> None:
    rows = _rows(ptype)
    assert len(rows) >= 3 and len({r.brand for r in rows}) >= 2, ptype
    missing = {r.code: sorted(TYPES[ptype] - _keys(r)) for r in rows if TYPES[ptype] - _keys(r)}
    assert missing == {}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_the_type_offers_the_six_main_colors_with_no_exception(ptype: str) -> None:
    rows = _rows(ptype)
    assert rows and ptype not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in rows for c in r.colors}


def test_the_types_are_sold_in_the_sizes_a_shopper_filters_on() -> None:
    def values(ptype: str, key: str) -> set[str]:
        out = set()
        for row in _rows(ptype):
            doc = export.standard_document(row.doc())
            out |= {e["value"] for v in doc["variants"] for e in v["attributes"] if e["key"] == key}
        return out

    assert values("Bike Helmet", "size") == {"S", "M", "L"}
    assert {"50", "54", "58"} <= values("Bicycle", "frame_size")
    assert {"16", "20", "24"} <= values("Bicycle", "wheel_size")
    assert {"270", "370"} <= values("Kayak", "item_length")
    assert {"8", "9"} <= values("Skateboard", "deck_width")


def test_a_bicycle_comes_in_the_four_kinds_the_issue_names() -> None:
    kinds = {a[2] for r in _rows("Bicycle") for a in r.attrs if a[0] == "bike_type"}
    assert kinds == {"Road", "Mountain", "Kids", "Electric"}
    assert {r.path[-1] for r in _rows("Bicycle")} == {
        "Road Bikes", "Mountain Bikes", "Kids Bikes", "Electric Bikes"
    }


def test_a_kayak_is_sit_on_top_or_inflatable_for_one_or_two() -> None:
    styles = {(a[2]) for r in _rows("Kayak") for a in r.attrs if a[0] == "kayak_type"}
    seats = {a[2] for r in _rows("Kayak") for a in r.attrs if a[0] == "seats"}
    assert styles == {"Sit-on-Top", "Inflatable"} and seats == {"1", "2"}


def test_the_tents_the_issue_lists_were_there_already() -> None:
    """Tents (gen#265) already sell two, four and six berths: nothing new is built for them."""
    berths = {b for r in _rows("Tent") for b, _ in r.sizes}
    assert {"2", "4", "6"} <= berths
    assert {r.path[-1] for r in _rows("Tent")} == {"Dome Tents", "Tunnel Tents"}


@pytest.mark.parametrize(
    ("shape", "one", "other"),
    [
        ("bicycle", {"style": "road"}, {"style": "mountain"}),
        ("bicycle", {"style": "kids"}, {"style": "electric"}),
        ("bike_helmet", {"style": "road"}, {"style": "mountain"}),
        ("bike_helmet", {"style": "road"}, {"style": "kids"}),
        ("kayak", {"style": "sit_on_top"}, {"style": "inflatable"}),
        ("kayak", {"seats": "1"}, {"seats": "2"}),
        ("kick_scooter", {"style": "folding"}, {"style": "stunt"}),
        ("kick_scooter", {"style": "folding"}, {"style": "commuter"}),
        ("skateboard", {"style": "street"}, {"style": "cruiser"}),
        ("skateboard", {"style": "street"}, {"style": "longboard"}),
    ],
)
def test_a_param_changes_the_drawing(shape: str, one: dict, other: dict) -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    assert kit.render(shape, fill, params=one) != kit.render(shape, fill, params=other)
    assert shape in kit_sports.SHAPES


def test_every_style_draws_as_its_own_shape() -> None:
    rows = [r for t in TYPES for r in _rows(t)]
    assert {r.shape for r in rows} == {
        "bicycle", "bike_helmet", "kayak", "kick_scooter", "skateboard"
    }
    assert {t: {r.shape for r in _rows(t)} for t in TYPES} == {
        "Bicycle": {"bicycle"}, "Bike Helmet": {"bike_helmet"}, "Kayak": {"kayak"},
        "Kick Scooter": {"kick_scooter"}, "Skateboard": {"skateboard"},
    }  # fmt: skip


def test_the_new_leaves_sit_in_the_tree_under_the_guards_rules() -> None:
    paths = [tuple(r.path) for r in sports_rows.ROWS]
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in sports_rows.ROWS]
    assert tree_guard.misplaced_title_findings(rows) == []
    families = {p[1] for p in paths}
    assert {"Cycling", "Water Sports", "Wheeled Sports"} <= families


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_the_type_carries_two_class_8_decoys_of_other_departments(
    ceiling: list[dict], ptype: str
) -> None:
    by_id = {r["product_id"]: r for r in ceiling}
    rows = [r for r in dpw.TABLE if r.target == ptype]
    assert len(rows) >= 2, ptype
    for row in rows:
        doc = by_id[f"PLT-{row.code}"]
        assert doc["category_path"][0] != ROOT and doc["product_type"] != ptype, row.code


@pytest.mark.parametrize(("query", "ptype"), sorted(QUERIES.items()))
def test_a_query_finds_the_type_on_its_first_page(
    index: br.Index, ceiling: list[dict], query: str, ptype: str
) -> None:
    by_id = {r["product_id"]: r for r in ceiling}
    top = [by_id[d["product_id"]] for d in br.rank(index, query, 24)]
    hits = [d for d in top if d["product_type"] == ptype and d["category_path"][0] == ROOT]
    assert hits, (query, [d["title"] for d in top])
