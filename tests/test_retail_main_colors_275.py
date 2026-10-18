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
import type_colors  # noqa: E402


@pytest.fixture(scope="module")
def tpls() -> list[dict]:
    return scale.templates()


def test_every_type_and_audience_offers_the_main_colors_or_declares_why_not(tpls):
    """A type declared in ``type_colors.RESTRICTED`` (gen#448) is asked for only the main colors
    it comes in: no yellow suit trousers."""
    groups = main_colors.groups(tpls)
    assert len({t for t, _ in groups}) > 100
    lacking = {
        k: [
            c
            for c in main_colors.MAIN_COLORS
            if c not in main_colors.offered(styles)
            and any(type_colors.permits(r["category_path"], c) for r in styles)
        ]
        for k, styles in groups.items()
        if k[0] not in main_colors.EXCEPTIONS
    }
    lacking = {k: c for k, c in lacking.items() if c}
    assert not lacking, f"(type, audience) lacking a main color, no exception: {lacking}"


@pytest.mark.parametrize("audience", ["Mens", "Womens"])
def test_red_shirt_finds_a_red_shirt_for_each_audience(tpls, audience):
    shirts = main_colors.groups(tpls)[("Shirt", audience)]
    assert main_colors.MAIN_COLORS.keys() <= main_colors.offered(shirts)


def test_an_excepted_type_that_gains_all_six_colors_fails(tpls):
    """EXCEPTIONS cannot go stale: a type listed there offers fewer than all six."""
    assert main_colors.stale_exceptions(tpls) == []
    fake = copy.deepcopy(tpls)
    for r in fake:
        if r["product_type"] == "Lemons":
            r["color_options"] = [
                {"color": c, "hex": h, "pattern": "solid", "family": c.lower()}
                for c, h in main_colors.MAIN_COLORS.items()
            ]
    assert main_colors.stale_exceptions(fake) == ["Lemons"]


def test_every_added_color_is_copied_from_a_solid_color_of_a_plain_style():
    raw = {r["product_id"]: r for r in scale.templates(baseline=False)}
    for r in scale.templates():
        if "color_options" not in r:
            continue
        old = raw.get(r["product_id"], {"color_options": []})["color_options"]
        before = {c["color"] for c in old}
        added = [c for c in r["color_options"] if c["color"] not in before]
        if not added:
            continue
        assert all(c["pattern"] == "solid" for c in added), r["product_id"]
        assert any(c["pattern"] == "solid" for c in old or r["color_options"])
        assert not main_colors.PATTERN_WORDS.search(f"{r['title']} {r['description']}"), r[
            "product_id"
        ]


def test_a_style_without_a_solid_color_cannot_take_one():
    raw = scale.templates(baseline=False)
    pattern_only = next(r for r in raw if r["product_id"] == "PLT-SUITCK")
    with pytest.raises(ValueError):
        main_colors._add(pattern_only, ["Red"])


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
    plain = {p[1] for p in main_colors.PLAIN_STYLES}
    kept = [r["product_id"] for r in full if r["product_id"] not in plain]
    assert [r["product_id"] for r in raw] == kept
    by_id = {r["product_id"]: r for r in full}
    for a in raw:
        b = by_id[a["product_id"]]
        assert {c["color"] for c in a.get("color_options", ())} <= {
            c["color"] for c in b.get("color_options", ())
        }


def test_mutant_shirts_without_red_are_caught():
    """Dropping red from every shirt style reds the guard, and the baseline restores it."""
    raw = copy.deepcopy(scale.templates(baseline=False))
    for r in raw:
        if r["product_type"] == "Shirt":
            r["color_options"] = [c for c in r["color_options"] if c["color"] != "Red"]
    assert "Red" in main_colors.missing(raw)[("Shirt", "Mens")]
    restored = main_colors.complete(main_colors.author_plain(raw))
    assert not [k for k in main_colors.missing(restored) if k[0] == "Shirt"]


def test_mutant_womens_shirts_without_red_are_caught():
    """Red dropped from the women's shirts only: the per-type guard is blind to it (the
    men's shirts still hold red), the per-audience guard names Womens."""
    raw = copy.deepcopy(scale.templates())
    for r in raw:
        if r["product_type"] == "Shirt" and main_colors.audience(r) == "Womens":
            r["color_options"] = [c for c in r["color_options"] if c["color"] != "Red"]
    lacking = main_colors.missing(raw)
    assert lacking[("Shirt", "Womens")] == ["Red"]
    assert ("Shirt", "Mens") not in lacking


def _non_plain_exports(tpls: list[dict]) -> dict[str, str]:
    """Pattern a plain-authored style, or a style that gained a color, exports when it is not
    plain: a check relabelled plain must not keep the source's ``Pattern: Check``."""
    raw = {r["product_id"]: r for r in scale.templates(baseline=False)}
    authored = {p[1] for p in main_colors.PLAIN_STYLES}
    out = {}
    for r in tpls:
        pid = r["product_id"]
        old = raw.get(pid)
        gained = old is not None and {c["color"] for c in r.get("color_options", ())} > {
            c["color"] for c in old.get("color_options", ())
        }
        if (pid in authored or gained) and r.get("pattern") not in (None, "plain"):
            out[pid] = r["pattern"]
    return out


def test_an_authored_plain_style_and_a_style_that_gained_a_color_export_a_plain_pattern(tpls):
    assert {p[1] for p in main_colors.PLAIN_STYLES} <= {r["product_id"] for r in tpls}
    assert _non_plain_exports(tpls) == {}


def test_mutant_a_plain_style_copying_a_check_pattern_is_caught(tpls):
    """The suit jacket's plain twin keeping the source's ``check`` is named by the helper."""
    mutant = copy.deepcopy(tpls)
    for r in mutant:
        if r["product_id"] == "PLT-SUITPL":
            r["pattern"] = "check"
    assert _non_plain_exports(mutant) == {"PLT-SUITPL": "check"}
