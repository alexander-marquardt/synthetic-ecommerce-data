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

import export  # noqa: E402
import kit  # noqa: E402
import kit_seating  # noqa: E402
import samples_round2  # noqa: E402
import sofa_rows  # noqa: E402
import variants  # noqa: E402

SHAPES = ("sofa_seats", "corner_sofa", "chaise_sofa")


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


def _depth(entries: list[dict]) -> list[dict]:
    return [e for e in entries if e["key"] == "depth"]


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
    (entry,) = _depth(samples_round2.HOME[0]["attributes"])
    _assert_cm_depth(entry)
