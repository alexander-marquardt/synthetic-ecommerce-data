"""Every color-bearing retail type offers the main colors (gen#275).

Red, blue, green, yellow, black and white are a baseline as plain color values, not the full
set. A type whose color is its material or natural finish declares an exception with a
one-line reason in ``main_colors.EXCEPTIONS``. The guard lists every color-bearing type
and reds when one lacks a main color without that exception.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import main_colors  # noqa: E402
import scale  # noqa: E402


@pytest.fixture(scope="module")
def tpls() -> list[dict]:
    return scale.templates()


def test_every_color_bearing_type_offers_the_main_colors_or_declares_why_not(tpls):
    types = main_colors.colored_types(tpls)
    assert len(types) > 100
    lacking = {
        t: [c for c in main_colors.MAIN_COLORS if c not in main_colors.offered(styles)]
        for t, styles in types.items()
        if t not in main_colors.EXCEPTIONS
    }
    lacking = {t: c for t, c in lacking.items() if c}
    assert not lacking, f"types without a main color and no declared exception: {lacking}"


def test_an_exception_has_a_reason_and_names_a_color_bearing_type(tpls):
    types = main_colors.colored_types(tpls)
    for t, reason in main_colors.EXCEPTIONS.items():
        assert t in types, f"{t}: an exception for a type that carries no color"
        assert len(reason.split()) >= 3 and "\n" not in reason, t


def test_a_main_color_is_a_plain_value_never_a_shade(tpls):
    for r in tpls:
        for c in r.get("color_options", ()):
            assert "shade_name" not in c, r["product_id"]
        for s in r["skus"]:
            assert "shade_name" not in s


def test_the_baseline_adds_colors_and_removes_none():
    raw = scale.templates(baseline=False)
    full = scale.templates()
    assert [r["product_id"] for r in raw] == [r["product_id"] for r in full]
    for a, b in zip(raw, full, strict=True):
        assert {c["color"] for c in a.get("color_options", ())} <= {
            c["color"] for c in b.get("color_options", ())
        }


def test_mutant_shirts_without_red_are_caught():
    """Dropping red from every shirt style reds the guard, and the baseline restores it."""
    raw = copy.deepcopy(scale.templates(baseline=False))
    for r in raw:
        if r["product_type"] == "Shirt":
            r["color_options"] = [c for c in r["color_options"] if c["color"] != "Red"]
    assert "Red" in main_colors.missing(raw)["Shirt"]
    assert "Shirt" not in main_colors.missing(main_colors.complete(raw))
