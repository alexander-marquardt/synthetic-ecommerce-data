"""Living-room seating (gen#196): sofas by seat count and form, sofa beds, armchairs, footstools.

:mod:`sofa_rows` holds the styles and :mod:`kit_seating` draws them. These checks hold
what the issue asked for: every type has its range (three styles, three brands), each
style draws as its own kind with the params that change how it looks, each key attribute
is a structured entry in the export, and the styles reach the scaled build.
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
import kit  # noqa: E402
import kit_seating  # noqa: E402
import scale  # noqa: E402
import sofa_rows  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = sofa_rows.ROWS

#: Each type and the key attributes a shopper filters or searches it on (the issue's table).
KEYS = {
    "Sofa": {"seat_count", "item_width", "item_depth", "item_height", "material", "arm_style",
             "leg_finish", "filling", "firmness", "removable_covers", "pet_friendly"},
    "Corner Sofa": {"seat_count", "item_width", "item_depth", "item_height", "material",
                    "shape"},
    "Chaise Sofa": {"seat_count", "orientation", "material"},
    "Modular Sofa": {"piece_count", "module_type", "material"},
    "Recliner Sofa": {"seat_count", "recline", "usb_port", "headrest", "material"},
    "Sofa Bed": {"seat_count", "mechanism", "bed_size", "mattress_type", "material"},
    "Armchair": {"style", "material", "leg_finish"},
    "Footstool": {"shape", "storage_compartment", "material"},
}  # fmt: skip


def _attr(row: sofa_rows.Row, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _boxes(row: sofa_rows.Row, monkeypatch: pytest.MonkeyPatch) -> list[kit_seating.Box]:
    """The blocks a style's drawing is made of, as :func:`kit_seating._draw` receives them."""
    seen: list[list[kit_seating.Box]] = []
    real = kit_seating._draw

    def spy(boxes, paint, fill, extra=None):
        seen.append(boxes)
        return real(boxes, paint, fill, extra)

    monkeypatch.setattr(kit_seating, "_draw", spy)
    kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))
    return seen[-1]


def test_every_type_has_three_styles_from_three_brands() -> None:
    styles: dict[str, list[sofa_rows.Row]] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 3} == {}


def test_every_style_draws_as_its_own_seating_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_seating.SHAPES} == {}


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if KEYS[ptype] - keys:
            missing[row.code] = sorted(KEYS[ptype] - keys)
    assert missing == {}


def test_a_handed_style_draws_its_return_on_the_side_its_orientation_names() -> None:
    wrong = {
        r.code: (hand, dict(r.params).get("side"))
        for r in ROWS
        for hand in _attr(r, "orientation")
        if dict(r.params).get("side") != hand.split()[0].lower()
    }
    assert wrong == {}


def test_a_sofa_drawn_by_seat_count_draws_the_seats_its_record_states() -> None:
    drawn = [r for r in ROWS if "seats" in dict(r.params) and r.shape != "corner_sofa"]
    assert drawn
    assert {
        r.code: (dict(r.params)["seats"], _attr(r, "seat_count"))
        for r in drawn
        if _attr(r, "seat_count") != [dict(r.params)["seats"]]
    } == {}


def test_two_and_three_seaters_draw_different_cushion_counts() -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    two = kit.render("sofa_seats", fill, params={"seats": "2"})
    three = kit.render("sofa_seats", fill, params={"seats": "3"})
    assert two != three
    assert kit_seating._seats("2.5") == (2, 2.5 * kit_seating.SEAT)


def test_depth_runs_up_and_left_so_the_left_side_the_kit_draws_is_the_one_that_shows() -> None:
    """``_box`` draws a block's left side, top and front, and :func:`kit_seating._before`
    orders blocks for a viewer on the left. Depth must move the drawing left, or every right
    arm shows a floating top with no side under it."""
    x, y = kit_seating._Sheet._raw(0.0, 0.0, 10.0)
    assert x < 0 and y < 0


#: The styles drawn as blocks (a round footstool is drawn as an ellipse and a drum).
BLOCKED = [r for r in ROWS if dict(r.params).get("form") != "round"]


@pytest.mark.parametrize("row", BLOCKED, ids=lambda r: r.code)
def test_every_style_has_a_painters_order_without_a_forced_pick(
    row: sofa_rows.Row, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pair of blocks whose outlines do not overlap orders nothing; were it ordered, the
    order would contradict the pairs between them, and :func:`kit_seating._order` would
    have to break a cycle by authored order, painting a seat over its neighbor."""
    boxes = _boxes(row, monkeypatch)
    after = {
        i: {j for j, b in enumerate(boxes) if j != i and kit_seating._before(a, b)}
        for i, a in enumerate(boxes)
    }
    waiting = {i: sum(i in after[j] for j in after) for i in after}
    while waiting:
        ready = [i for i, n in waiting.items() if n == 0]
        assert ready, f"{row.code}: blocks {sorted(waiting)} order each other in a cycle"
        for j in after[ready[0]]:
            if j in waiting:
                waiting[j] -= 1
        del waiting[ready[0]]


def test_an_armless_chair_stands_on_legs_under_its_seat(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [r for r in ROWS if r.shape == "armchair" and dict(r.params)["style"] == "nursing"]
    assert rows
    boxes = _boxes(rows[0], monkeypatch)
    seat = [b for b in boxes if b.paint == "fill"]
    legs = [b for b in boxes if b.paint == kit_seating.LEG_FINISHES[dict(rows[0].params)["legs"]]]
    left, right = min(b.x0 for b in seat), max(b.x1 for b in seat)
    assert legs
    assert [(b.x0, b.x1) for b in legs if b.x0 < left or b.x1 > right] == []


@pytest.mark.timeout(300)
def test_every_seating_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.SOFA_IDS]
    assert check_catalog(mine, one_class_per_key=True) == []
