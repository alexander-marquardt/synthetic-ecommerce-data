"""The redraw order puts the named redraws first, then retail by the demo's top 12 (gen#1129).

``scripts/redraw_order_1129.py`` orders the sweep's type rows into one redraw issue per kit group.
These tests hold the order to fixed rows, and the recorded top 12 and the group list to their
shape: no drawn-to-scale type and no type at or over the floor is ever in the order, no row falls
outside the groups, and every group names its own filed issue.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "redraw_order_1129", REPO / "scripts" / "redraw_order_1129.py"
)
ro = importlib.util.module_from_spec(_spec)
sys.modules["redraw_order_1129"] = ro
_spec.loader.exec_module(ro)

NAMED = (
    ro.Group("First", ("kit_first",), 11, ro.NAMED_TIER),
    ro.Group("Second", ("kit_second",), 12, ro.NAMED_TIER, ("Cider",)),
)
GROUPS = (
    ro.Group("Boots", ("kit_boots",), 1),
    ro.Group("Dresses", ("kit:dress",), 2),
    ro.Group("Tins", ("kit:tin",), 3),
    ro.Group("Hammers", ("industrial/figures",), 4, ro.INDUSTRIAL_TIER),
)
NO_HITS = {"queries": {}}


def _row(kit: str, ptype: str, shape: str = "s", area: float = 0.1, **over: object) -> dict:
    return {"kit": kit, "type": ptype, "shape": shape, "skus": 10, "area": area} | {
        "in_scope": True,
        **over,
    }


def _order(types: list[dict], hits: dict = NO_HITS) -> list[dict]:
    return ro.order(types, hits, NAMED, GROUPS)


def _titles(rows: list[dict]) -> list[str]:
    return [r["group"].title for r in rows]


def _hits(*rows: list) -> dict:
    return {"queries": {"q": list(rows)}}


def test_the_named_redraws_come_first_in_their_own_order_even_with_no_type_left() -> None:
    hits = _hits(["retail", "Boot", "s", 12])
    rows = _order([_row("kit_boots", "Boot"), _row("kit_second", "Milk")], hits)
    assert _titles(rows) == ["First", "Second", "Boots"]
    assert rows[0]["types"] == []
    assert rows[0]["area"] is None


def test_retail_groups_order_by_top_12_slots_before_area() -> None:
    types = [
        _row("kit_boots", "Boot", area=0.01),
        _row("kit", "Dress", "dress", area=0.4),
        _row("kit", "Beans", "tin", area=0.2),
    ]
    hits = _hits(["retail", "Dress", "dress", 5], ["retail", "Dress", "other", 9])
    assert _titles(_order(types, hits))[2:] == ["Dresses", "Boots", "Tins"]
    assert _order(types, hits)[2]["slots"] == 5


def test_groups_with_equal_slots_order_by_worst_median_area() -> None:
    types = [
        _row("kit_boots", "Boot", area=0.1),
        _row("kit_boots", "Shoe", area=0.3),
        _row("kit_boots", "Clog", area=0.4),
        _row("kit", "Dress", "dress", area=0.2),
    ]
    assert _titles(_order(types))[2:] == ["Dresses", "Boots"]
    assert _order(types)[3]["area"] == 0.3


def test_the_industrial_groups_come_last_whatever_they_fill() -> None:
    types = [_row("industrial/figures", "hammer_claw"), _row("kit_boots", "Boot", area=0.45)]
    hits = _hits(["industrial", "hammer_claw", "s", 12])
    assert _titles(_order(types, hits))[2:] == ["Boots", "Hammers"]


def test_a_drawn_to_scale_type_is_never_in_the_order() -> None:
    types = [
        _row("industrial/figures", "hex_bolt", in_scope=False),
        _row("industrial/figures", "hammer_claw"),
        _row("industrial/nuts", "nut_hex", in_scope=False),
    ]
    hits = _hits(["industrial", "hex_bolt", "s", 12])
    rows = _order(types, hits)
    assert [t["type"] for r in rows for t in r["types"]] == ["hammer_claw"]
    assert rows[-1]["slots"] == 0


@pytest.mark.parametrize(("area", "listed"), [(0.499, True), (0.5, False), (0.7, False)])
def test_only_a_picture_under_half_the_product_area_is_redrawn(area: float, listed: bool) -> None:
    assert ("Boots" in _titles(_order([_row("kit_boots", "Boot", area=area)]))) is listed


def test_a_row_of_no_group_raises() -> None:
    with pytest.raises(KeyError, match="kit_unknown Widget"):
        _order([_row("kit_unknown", "Widget")])
    with pytest.raises(KeyError, match="kit Cake"):
        _order([_row("kit", "Cake", "cake")])


def test_a_kit_that_holds_several_kinds_is_split_by_shape() -> None:
    types = [_row("kit", "Dress", "dress"), _row("kit", "Beans", "tin")]
    assert {r["group"].title: [t["type"] for t in r["types"]] for r in _order(types)[2:]} == {
        "Dresses": ["Dress"],
        "Tins": ["Beans"],
    }


def test_a_named_type_goes_to_its_named_redraw_wherever_it_is_drawn() -> None:
    rows = _order([_row("kit", "Cider", "tin"), _row("kit", "Beans", "tin")])
    assert [t["type"] for t in rows[1]["types"]] == ["Cider"]
    assert [t["type"] for t in rows[2]["types"]] == ["Beans"]


def test_the_table_names_each_groups_issue_kits_and_numbers() -> None:
    hits = _hits(["retail", "Boot", "s", 7])
    lines = ro.order_table(_order([_row("kit_boots", "Boot", area=0.25)], hits)).splitlines()
    assert lines[2] == "| 1 | First | gen#11 | `kit_first` | 0 | 0 | - | 0 |"
    assert lines[4] == "| 3 | Boots | gen#1 | `kit_boots` | 1 | 10 | 25% | 7 |"


def test_the_script_prints_the_table_of_a_rows_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rows = tmp_path / "rows.json"
    rows.write_text(json.dumps({"types": [_row("kit_footwear", "Sandals", "shoe", area=0.05)]}))
    assert ro.main(["--rows", str(rows)]) == 0
    assert "| Shoes and boots | gen#" in capsys.readouterr().out


def test_the_recorded_top_12_holds_every_slot_of_the_60_seeds() -> None:
    hits = json.loads(ro.HITS.read_text(encoding="utf-8"))
    assert "seed_queries.json" in hits["_recorded"]
    assert len(hits["queries"]) == 60
    assert {sum(n for *_, n in rows) for rows in hits["queries"].values()} == {hits["top"]} == {12}
    assert sum(ro.slots(hits).values()) == sum(hits["_resolved"].values()) == 720


def test_every_group_names_its_own_filed_issue_and_its_own_kits() -> None:
    issues = [g.issue for g in (*ro.NAMED, *ro.GROUPS)]
    assert all(issues)
    assert len(set(issues)) == len(issues)
    kits = [k for g in (*ro.NAMED, *ro.GROUPS) for k in g.kits]
    assert len(set(kits)) == len(kits)
