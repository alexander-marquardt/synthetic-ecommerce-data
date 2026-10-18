"""The seating kit's words, seat counts and depths agree with the data it draws (gen#225).

Three things the review of gen#219 found: the chaise sofa's docs said it had no back while
the drawing gives it one, a corner sofa was drawn with the same seats whatever its record
said, and a sofa bed's mattress depth was free text ("14 cm") where every other measurement
is a bare number with a ``CMT`` ``unit_code`` and a millimetre canonical value.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_rows  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import kit_seating  # noqa: E402
import samples_round2  # noqa: E402
import sofa_rows  # noqa: E402
import variants  # noqa: E402

SHAPES = ("sofa_seats", "corner_sofa", "chaise_sofa")


def _boxes(row: sofa_rows.Row, monkeypatch: pytest.MonkeyPatch) -> list[kit_seating.Box]:
    """The blocks a style's drawing is made of, as :func:`kit_seating._draw` receives them."""
    return _boxes_of(row.shape, dict(row.params), monkeypatch)


def _boxes_of(shape: str, params: dict, monkeypatch: pytest.MonkeyPatch) -> list[kit_seating.Box]:
    seen: list[list[kit_seating.Box]] = []
    real = kit_seating._draw

    def spy(boxes, paint, fill, extra=None):
        seen.append(boxes)
        return real(boxes, paint, fill, extra)

    monkeypatch.setattr(kit_seating, "_draw", spy)
    kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)
    return seen[-1]


def _seat_cushions(boxes: list[kit_seating.Box]) -> int:
    return sum(1 for b in boxes if (b.y0, b.y1) == (kit_seating.BASE, kit_seating.CUSHION))


@pytest.mark.parametrize("shape", SHAPES)
def test_a_sofa_is_drawn_with_the_seat_cushions_its_record_states(
    shape: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    rows = [r for r in sofa_rows.ROWS if r.shape == shape]
    assert rows
    wrong = {}
    for r in rows:
        stated = int(float(next(a[2] for a in r.attrs if a[0] == "seat_count")))
        drawn = _seat_cushions(_boxes(r, monkeypatch))
        if drawn != stated:
            wrong[r.code] = (stated, drawn)
    assert wrong == {}


def test_the_chaise_docs_describe_the_back_the_drawing_gives_it() -> None:
    fill = kit.Fill("solid", "#123456", "#654321")
    drawn = "".join(kit.render("chaise_sofa", fill, params={"seats": "3"}))
    assert drawn  # it draws at all
    for text in (kit_seating.__doc__, kit_seating.chaise_sofa.__doc__):
        assert "no back" not in " ".join(text.split())


@pytest.mark.parametrize("side", ["left", "right"])
def test_the_chaise_has_its_back_along_the_whole_rear(
    side: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    boxes = _boxes_of("chaise_sofa", {"seats": "3", "side": side}, monkeypatch)
    ks = kit_seating
    frame = [b for b in boxes if (b.y0, b.y1, b.z1) == (ks.BASE, ks.BACK - 6, ks.DEPTH)]
    backs = [b for b in boxes if (b.y1, b.z1) == (kit_seating.BACK, kit_seating.DEPTH - 14)]
    assert len(frame) == 1
    assert (min(b.x0 for b in frame), max(b.x1 for b in frame)) in ((0.0, 180.0), (-180.0, 0.0))
    assert len(backs) == 3  # a back cushion per seat, the chaise end's too
    assert max(b.x1 for b in backs) - min(b.x0 for b in backs) > 175.0


@pytest.mark.parametrize("kind", [k for k in decoy_rows.KINDS.values() if k.shape == "corner_sofa"])
def test_every_corner_sofa_decoy_draws_a_run_beside_its_corner_and_return(
    kind: decoy_rows.Kind, monkeypatch: pytest.MonkeyPatch
) -> None:
    boxes = _boxes_of(kind.shape, dict(kind.params), monkeypatch)
    assert _seat_cushions(boxes) > 3  # a bare corner seat and a two-seat return is no corner sofa


def _depth(entries: list[dict]) -> list[dict]:
    return [e for e in entries if e["key"] == "mattress_depth"]


def _assert_cm_depth(entry: dict) -> None:
    assert entry["value"].replace(".", "", 1).isdigit(), entry
    assert entry["unit_code"] == "CMT", entry
    assert entry["value_canonical"] == float(entry["value"]) * 10, entry


@pytest.mark.parametrize("row", [r for r in sofa_rows.ROWS if r.product_type == "Sofa Bed"],
                         ids=lambda r: r.code)
def test_a_sofa_beds_mattress_depth_is_a_measured_centimeter_entry(row: sofa_rows.Row) -> None:
    (entry,) = _depth(export.standard_document(row.doc())["attributes"])
    _assert_cm_depth(entry)


def test_a_toppers_depth_is_a_measured_centimeter_entry_in_both_samples() -> None:
    shallow = next(r for r in variants.BEDDING if r.code == "TOPMEM")
    (entry,) = _depth(shallow.doc()["attributes"])
    _assert_cm_depth(entry)
    topper = next(i for i in samples_round2.HOME if "Mattress Topper" in i["title"])
    (entry,) = _depth(topper["attributes"])
    _assert_cm_depth(entry)
