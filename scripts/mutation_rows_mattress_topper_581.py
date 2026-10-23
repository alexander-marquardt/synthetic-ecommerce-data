"""Mutation rows for the mattress topper drawing (#581), kept out of ``mutation_check.py``.

Each row plants one defect in ``kit_home.py`` and names the test that must go red.
``--only "mattress topper:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import RETAIL_DRAWINGS, Row

PREFIX = "mattress topper"

_T = "prototypes/retail_drawings/test_mattress_topper.py"
_FILE = "kit_home.py"


def _row(name: str, old: str, new: str, test: str, prop: str) -> Row:
    return Row(name, _FILE, old, new, test, prop, RETAIL_DRAWINGS)


def rows() -> list[Row]:
    return [
        _row(
            "the topper is a fixed 38 px again",
            "    t = _cm(depth) * PX_PER_CM\n",
            "    t = 38\n",
            (
                f"{_T}::test_a_5_cm_and_a_10_cm_topper_differ_visibly",
                f"{_T}::test_a_topper_is_thin_not_a_mattress",
            ),
            "the thickness follows the stated depth, and it is thin",
        ),
        _row(
            "the topper is drawn at twice the mattress's scale",
            "    t = _cm(depth) * PX_PER_CM\n",
            "    t = _cm(depth) * PX_PER_CM * 2\n",
            f"{_T}::test_the_topper_depth_is_drawn_at_the_mattress_scale",
            "one scale for the topper and the mattress under it",
        ),
        _row(
            "the mattress outline is as strong as the topper",
            '<g opacity=".4" data-part="mattress">',
            '<g opacity="1" data-part="mattress">',
            f"{_T}::test_the_topper_lies_on_a_faint_mattress",
            "the mattress is a faint outline",
        ),
        _row(
            "the topper floats off the mattress",
            '_slab(paint, t, -t, "topper")',
            '_slab(paint, t, -t - 20, "topper")',
            f"{_T}::test_the_topper_lies_on_a_faint_mattress",
            "the topper's bottom is the mattress's top",
        ),
        _row(
            "a topper without a depth is drawn as 9 cm",
            'def mattress_topper(paint: str, fill: Fill, label: str | None, depth: str = "5cm")',
            'def mattress_topper(paint: str, fill: Fill, label: str | None, depth: str = "9cm")',
            f"{_T}::test_a_topper_without_a_depth_is_drawn_as_5_cm",
            "no stated depth reads as the 5 cm default",
        ),
    ]
