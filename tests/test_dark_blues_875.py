"""Denim washes and navy read as blue on screen, not black (gen#875).

At thumbnail size a blue of relative luminance under about 0.05 reads as the Black swatch
(``#2a2a2e``, 0.023): Rinse ``#1f2a44`` was 0.024 and Navy ``#26365c`` 0.038. The dark blues
are one constant each in ``dark_blues``; no swatch table copies the hex.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import dark_blues, export, image_release, variants
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS

SRC = Path(__file__).resolve().parents[1] / "src" / "synthetic_ecommerce_data"

#: The hexes this issue retired: none may be drawn again.
RETIRED = ("#1f2a44", "#25345a", "#34466e", "#26365c", "#2c3a5e")

#: The darkest a drawn blue may be: twice the Black swatch's luminance, above every retired hex.
FLOOR = 0.05

DARK_BLUES = {
    "RINSE": dark_blues.RINSE, "DARK_INDIGO": dark_blues.DARK_INDIGO,
    "INDIGO": dark_blues.INDIGO, "MID_WASH": dark_blues.MID_WASH,
    "NAVY": dark_blues.NAVY, "NAVY_LIGHT": dark_blues.NAVY_LIGHT,
}  # fmt: skip


def luminance(hex_: str) -> float:
    """WCAG relative luminance of ``#rrggbb``."""

    def channel(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def test_the_washes_draw_the_lighter_blues():
    got = {k: variants.WASHES[k] for k in ("Rinse", "Dark Indigo", "Indigo", "Mid Wash")}
    assert got == {
        "Rinse": "#2b4a80", "Dark Indigo": "#32548c", "Indigo": "#3d5f97", "Mid Wash": "#5578a8",
    }  # fmt: skip


def test_the_wash_order_by_lightness_is_kept():
    order = (
        "Rinse", "Dark Indigo", "Indigo", "Mid Wash", "Vintage Blue", "Light Wash", "Bleach Wash",
    )  # fmt: skip
    lums = [luminance(variants.WASHES[w]) for w in order]
    assert lums == sorted(lums) and len(set(lums)) == len(lums)


def test_navy_is_the_issue_hex_and_darker_than_blue():
    assert (dark_blues.NAVY, dark_blues.NAVY_LIGHT) == ("#2c477e", "#34508a")
    navy, light, blue = (dark_blues.NAVY, dark_blues.NAVY_LIGHT, MAIN_COLORS["Blue"])
    assert luminance(navy) < luminance(light) < luminance(blue)


@pytest.mark.parametrize("name", sorted(DARK_BLUES))
def test_every_dark_blue_reads_as_blue(name):
    hex_ = DARK_BLUES[name]
    r, g, b = (int(hex_[i : i + 2], 16) for i in (1, 3, 5))
    assert luminance(hex_) >= FLOOR, f"{name} {hex_}: {luminance(hex_):.3f} reads as black"
    assert b > g > r, f"{name} {hex_} is not a blue"


def test_no_swatch_table_copies_a_dark_blue():
    """One definition each: a retired hex is drawn nowhere, and a dark blue's hex is typed only
    in ``dark_blues``."""
    own = SRC / "domains" / "retail" / "dark_blues.py"
    pattern = re.compile("|".join([*RETIRED, *DARK_BLUES.values()]), re.IGNORECASE)
    copies = [
        f"{p.relative_to(SRC)}:{n}: {line.strip()}"
        for p in sorted(SRC.rglob("*.py"))
        if p != own
        for n, line in enumerate(p.read_text().splitlines(), 1)
        if pattern.search(line)
    ]
    assert copies == []


def test_every_solid_navy_swatch_draws_a_navy_constant():
    navy = {
        sw["hex"]
        for rec in image_release.records()
        for sku in rec["skus"]
        if (sw := export.drawing_spec(rec, sku)["swatch"]) and sw["color"] == "Navy"
        and sw["pattern"] == "solid"
    }  # fmt: skip
    assert navy and navy <= {dark_blues.NAVY, dark_blues.NAVY_LIGHT}, navy
