"""A U-shaped sofa is drawn as a U by its own kit, ``u_sofa`` (#1105).

The U-shaped corner sofa (``CNASHU``) was drawn by ``corner_sofa``'s ``u`` branch. That branch
took three seats per return from six, so the run had no width, and the two returns met back to
back: their seat cushions filled the space a U opens, and the picture read as a gridded block.
These checks hold the U. It has a back along the run and along each return, seat cushions on
each, and no seat between the returns. Every U-shaped title or ``shape`` attribute in the built
catalogue is drawn by ``u_sofa``.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import kit, kit_seating, scale, sofa_rows
from synthetic_ecommerce_data.domains.retail.orientations import seating as seating_orientations

ks = kit_seating

#: How a title or a ``shape`` attribute says U-shaped: U-Shaped, U Shaped, U-Shape.
U_SHAPED = re.compile(r"\bU[- ]?Shaped?\b", re.IGNORECASE)


def _boxes_of(shape: str, params: dict, monkeypatch: pytest.MonkeyPatch) -> list[kit_seating.Box]:
    """The blocks a drawing is made of, as :func:`kit_seating._draw` receives them."""
    seen: list[list[kit_seating.Box]] = []
    real = kit_seating._draw

    def spy(boxes, paint, fill, extra=None):
        seen.append(boxes)
        return real(boxes, paint, fill, extra)

    monkeypatch.setattr(kit_seating, "_draw", spy)
    kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)
    return seen[-1]


def _seats(boxes: list[kit_seating.Box]) -> list[kit_seating.Box]:
    return [b for b in boxes if (b.y0, b.y1) == (ks.BASE, ks.CUSHION)]


def _assert_a_u(boxes: list[kit_seating.Box], seats: int) -> None:
    """A back along the run and each return, ``seats`` seat cushions, and an open middle."""
    center = (min(b.x0 for b in boxes) + max(b.x1 for b in boxes)) / 2
    run_back = [b for b in boxes if (b.y0, b.y1, b.z1) == (ks.BASE, ks.BACK - 6, ks.DEPTH)]
    assert len(run_back) == 1, "one back frame along the run"
    return_backs = [b for b in boxes if b.y1 >= ks.BACK - 6 and b.z0 < 0]
    assert {"left" if (b.x0 + b.x1) / 2 < center else "right" for b in return_backs} == {
        "left",
        "right",
    }
    assert len(_seats(boxes)) == seats
    forward = [b for b in _seats(boxes) if b.z1 <= 0]  # the returns' seats, in front of the run's
    left = max(b.x1 for b in forward if (b.x0 + b.x1) / 2 < center)
    right = min(b.x0 for b in forward if (b.x0 + b.x1) / 2 > center)
    assert right - left >= ks.SEAT - 2, f"the opening between the returns is {right - left:g} wide"
    between = [b for b in _seats(boxes) if b.z0 < 0 and b.x0 < right and b.x1 > left]
    assert between == []


def test_the_u_sofa_kit_is_registered_and_drawn_level() -> None:
    assert "u_sofa" in kit_seating.SHAPES
    assert "u_sofa" in seating_orientations.LEVEL


def test_the_u_shaped_sofa_draws_a_back_on_three_sides_and_an_open_middle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (row,) = [r for r in sofa_rows.ROWS if r.code == "CNASHU"]
    seats = int(dict(row.params)["seats"])
    assert seats == 6  # the seat count its record states
    _assert_a_u(_boxes_of(row.shape, dict(row.params), monkeypatch), seats)


@pytest.mark.parametrize("seats", ["5", "6", "7", "8", "9"])
def test_a_u_sofa_opens_at_every_seat_count_it_draws(
    seats: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    _assert_a_u(_boxes_of("u_sofa", {"seats": seats}, monkeypatch), int(seats))


@pytest.mark.parametrize("seats", ["2", "4"])
def test_a_u_sofa_refuses_a_seat_count_too_small_for_a_u(seats: str) -> None:
    with pytest.raises(ValueError, match="at least 5"):
        kit_seating.u_sofa("#123456", kit.Fill("solid", "#123456", "#654321"), None, seats)


@pytest.fixture(scope="module")
def built() -> list[dict]:
    """The records of the scaled build: each names the kit that draws it (``drawing.shape``)."""
    return scale.build(100_000).records


def _kits(rec: dict) -> set[str]:
    """The kits a record's pictures are drawn by: its own, and any a SKU draws instead."""
    return {rec["drawing"]["shape"]} | {
        s["drawing"]["shape"] for s in rec["skus"] if "drawing" in s
    }


def test_every_u_shaped_sofa_in_the_built_catalogue_is_drawn_by_the_u_sofa_kit(
    built: list[dict],
) -> None:
    (ashby,) = [r for r in built if r["product_id"] == "BRD-CNASHU"]
    assert all(s["sku"].startswith("BRD-CNASHU-") for s in ashby["skus"])
    assert _kits(ashby) == {"u_sofa"}
    u_shaped = {
        r["product_id"]: _kits(r)
        for r in built
        if U_SHAPED.search(r["title"])
        or any(U_SHAPED.search(a["value"]) for a in r["attributes"] if a["key"] == "shape")
    }
    assert "BRD-CNASHU" in u_shaped
    assert {pid: k for pid, k in u_shaped.items() if k != {"u_sofa"}} == {}


@pytest.mark.parametrize("side", ["u", "both", ""])
def test_the_corner_sofa_kit_refuses_any_side_but_left_or_right(side: str) -> None:
    """A U is ``u_sofa``'s to draw: ``corner_sofa`` has one return, on the left or the right."""
    with pytest.raises(ValueError, match="left or right"):
        kit_seating.corner_sofa("#123456", kit.Fill("solid", "#123456", "#654321"), None, "6", side)


def test_no_corner_sofa_row_or_built_drawing_has_a_side_but_left_or_right(
    built: list[dict],
) -> None:
    rows = {
        r.code: dict(r.params).get("side", "left")
        for r in sofa_rows.ROWS
        if r.shape == "corner_sofa"
    }
    assert rows and set(rows.values()) <= {"left", "right"}, rows
    drawings = [
        d
        for rec in built
        for d in (rec["drawing"], *(s["drawing"] for s in rec["skus"] if "drawing" in s))
        if d["shape"] == "corner_sofa"
    ]
    sides = {(d.get("params") or {}).get("side", "left") for d in drawings}
    assert drawings and sides <= {"left", "right"}, sides
