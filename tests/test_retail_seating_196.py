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


def test_a_handed_style_draws_its_return_on_the_side_its_orientation_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The blocks that come forward of the seats (z < 0) are the return or the chaise; they
    must lie left of the sofa's center for a left hand and right of it for a right hand."""
    wrong = {}
    seen = 0
    for r in ROWS:
        for hand in _attr(r, "orientation"):
            want = hand.split()[0].lower()
            boxes = _boxes(r, monkeypatch)
            center = (min(b.x0 for b in boxes) + max(b.x1 for b in boxes)) / 2
            forward = [b for b in boxes if b.z0 < 0]
            assert forward, r.code
            seen += 1
            got = {"left" if (b.x0 + b.x1) / 2 < center else "right" for b in forward}
            if got != {want}:
                wrong[r.code] = (hand, sorted(got))
    assert seen >= 4
    assert wrong == {}


def test_the_corner_and_chaise_drawings_are_both_handed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Both the corner sofa and the chaise sofa appear among the checked hands."""
    shapes = {r.shape for r in ROWS if _attr(r, "orientation")}
    assert {"corner_sofa", "chaise_sofa"} <= shapes


def test_a_sofa_drawn_by_seat_count_draws_the_seats_its_record_states() -> None:
    drawn = [r for r in ROWS if "seats" in dict(r.params)]
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


def _sofa_bed_drawing(
    mechanism: str, seats: str, monkeypatch: pytest.MonkeyPatch
) -> tuple[list[kit_seating.Box], list[str], kit_seating._Sheet]:
    """A sofa bed's blocks, the marks its ``extra`` adds on the fitted sheet, and the sheet."""
    seen: list[tuple[list[kit_seating.Box], object]] = []
    real = kit_seating._draw

    def spy(boxes, paint, fill, extra=None):
        seen.append((boxes, extra))
        return real(boxes, paint, fill, extra)

    monkeypatch.setattr(kit_seating, "_draw", spy)
    fill = kit.Fill("solid", "#123456", "#654321")
    kit.render("sofa_bed", fill, params={"mechanism": mechanism, "seats": seats})
    boxes, extra = seen[-1]
    sheet = kit_seating._Sheet(boxes)
    return boxes, (extra(sheet) if extra else []), sheet


@pytest.mark.parametrize("seats", ["2", "3"])
def test_a_click_clack_draws_a_sofa_with_a_seat_cushion_per_seat_and_a_back(
    seats: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """gen#223: the click-clack was two flat slabs on a frame, so at thumbnail size it read as a
    bed. It now shows the sofa: one seat cushion per seat, each with a back cushion upright
    behind it, rising above the seat."""
    boxes, _, _ = _sofa_bed_drawing("click_clack", seats, monkeypatch)
    upholstery = [b for b in boxes if b.paint == "fill"]
    seat = [b for b in upholstery if b.y1 == kit_seating.CUSHION]
    back = [b for b in upholstery if b.y1 == kit_seating.BACK]
    assert len(seat) == int(seats)
    assert len(back) == int(seats)
    assert min(b.z0 for b in back) >= max(b.z1 for b in seat)


def test_a_click_clack_is_a_sofa_deep_with_a_hinge_line_where_the_back_meets_the_seat(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The click-clack's back folds down about the seat's rear edge, so the hinge is marked
    there, across the seat's width; the piece is one sofa deep, not a double-depth bed."""
    boxes, marks, sheet = _sofa_bed_drawing("click_clack", "2", monkeypatch)
    assert max(b.z1 for b in boxes) == kit_seating.DEPTH
    seat = [b for b in boxes if b.paint == "fill" and b.y1 == kit_seating.CUSHION]
    x0, x1, z = min(b.x0 for b in seat), max(b.x1 for b in seat), max(b.z1 for b in seat)
    hinge = f'd="M{sheet.p(x0, kit_seating.CUSHION, z)} L{sheet.p(x1, kit_seating.CUSHION, z)}"'
    assert [m for m in marks if hinge in m]


def test_the_three_sofa_bed_mechanisms_draw_three_different_pictures() -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    mechanisms = ("pull_out", "click_clack", "fold_out")
    drawn = {
        m: kit.render("sofa_bed", fill, params={"mechanism": m, "seats": "2"}) for m in mechanisms
    }
    assert len(set(drawn.values())) == 3


@pytest.mark.timeout(300)
def test_every_seating_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.SOFA_IDS]
    assert check_catalog(mine, one_class_per_key=True) == []


def test_a_line_names_one_brand_across_the_retail_rows() -> None:
    brands: dict[str, set[str]] = collections.defaultdict(set)
    for r in ROWS:
        for line in _attr(r, "line"):
            brands[line].add(r.brand)
    assert {line: sorted(b) for line, b in brands.items() if len(b) > 1} == {}


def _drawn_after(a: kit_seating.Box, b: kit_seating.Box) -> bool:
    """Whether ``a`` must be painted after ``b``: it sits on ``b``, else it is nearer, else it
    is further left. The first axis on which the two are apart decides (y, then z, then x)."""
    for lo_a, hi_a, lo_b, hi_b, flip in (
        (a.y0, a.y1, b.y0, b.y1, False),
        (a.z0, a.z1, b.z0, b.z1, True),
        (a.x0, a.x1, b.x0, b.x1, True),
    ):
        if lo_a >= hi_b:
            return not flip
        if lo_b >= hi_a:
            return flip
    return False


@pytest.mark.parametrize("row", BLOCKED, ids=lambda r: r.code)
def test_the_painters_order_draws_the_nearer_higher_and_left_block_later(
    row: sofa_rows.Row, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The oracle does not call ``_before``: of two blocks whose outlines overlap, the one
    that is higher (larger y), else nearer (smaller z), else further left is drawn later."""
    boxes = _boxes(row, monkeypatch)
    place = {id(b): i for i, b in enumerate(kit_seating._order(boxes))}
    wrong = 0
    checked = 0
    for a in boxes:
        for b in boxes:
            if a is b or not kit_seating._overlap(a, b):
                continue
            if not _drawn_after(a, b):
                continue
            checked += 1
            wrong += place[id(a)] < place[id(b)]
    assert checked
    assert wrong == 0, f"{row.code}: {wrong} pairs drawn in the wrong order"
