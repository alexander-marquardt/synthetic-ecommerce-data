"""Peanut butter cups, coated peanuts, the advent calendar, a box of cherries and bags of coated
fruit draw as the chocolate they are and fill their picture (gen#1125, slice 4).

Before this slice the peanut butter cups and the coated peanuts (GRC-PNT) were drawn as a bar,
the chocolate advent calendar (BRD-SEAADV) and the dark chocolate cherries (PLT-DXQ42) as the
generic closed ``box``, and the chocolate covered strawberries and bananas (PLT-DXQ19, DXQ39) as
the generic grocery ``bag`` at 47% of the product area, with no chocolate in sight. Each now
draws its own shape: ``peanut_butter_cups`` (fluted cups before their opened wrapper, one cut to
show its filling), ``chocolate_bag`` with peanuts, strawberries or banana slices in its window,
``chocolate_box`` with a cherry and its stalk in each paper cup, and ``advent_calendar`` (a
board of 24 numbered doors, two open on a chocolate). Fill is measured as
``tests/test_chocolate_fill_1125.py`` measures it: the share of ``TURN_AREA`` the drawing paints
(:mod:`sheet_cover`), the ground shadow not counted.
"""

from __future__ import annotations

import functools
import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    decoy_rows,
    export,
    grocery,
    kit,
    scale,
    sheet_cover,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import Fill

FLOOR = 0.5
#: The grocery flavours drawn as their own chocolate: (family, flavour) -> (shape, piece).
FLAVOURS = {
    ("PNT", "Chocolate Peanut Butter Cups"): ("peanut_butter_cups", None),
    ("PNT", "Chocolate Coated Peanuts"): ("chocolate_bag", "peanuts"),
}
#: The authored rows drawn as their own chocolate: product id -> (shape, piece).
AUTHORED = {
    "PLT-DXQ42": ("chocolate_box", "cherries"),
    "PLT-DXQ19": ("chocolate_bag", "strawberries"),
    "PLT-DXQ39": ("chocolate_bag", "bananas"),
    "BRD-SEAADV": ("advent_calendar", None),
}
#: The least number of glossed chocolates each shape shows.
LEAST = {"peanut_butter_cups": 3, "chocolate_bag": 10, "chocolate_box": 12, "advent_calendar": 2}


@functools.lru_cache(maxsize=1)
def _flavour_records() -> dict[tuple[str, str], dict]:
    out = {}
    for rec in grocery.build(grocery.TARGET):
        for code, name in FLAVOURS:
            if rec["product_id"].startswith(f"GRC-{code}-") and rec["title"].endswith(name):
                out.setdefault((code, name), rec)
    return out


@functools.lru_cache(maxsize=1)
def _authored() -> dict[str, dict]:
    return {r["product_id"]: r for r in scale.templates() if r["product_id"] in AUTHORED}


def _parts(rec: dict, sku: dict | None = None, **over: str | None) -> list[str]:
    """The record's drawing as the renderer draws it: its params, the SKU's own over them."""
    d = rec["drawing"]
    params = dict(d.get("params") or {})
    if sku is not None:
        params |= export.drawing_spec(rec, sku).get("params", {})
    params |= over
    fill = Fill("solid", d["base"], d.get("accent") or "#ffffff")
    return kit._drawn(kit.shapes()[d["shape"]], d["base"], fill, d.get("label"), params)


def _svg(parts: list[str]) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{"".join(parts)}</svg>'


def _fill(parts: list[str]) -> float:
    return sheet_cover.cover(_svg(parts), TURN_AREA, step=4.0, skip=("ground",))


def _cases() -> list[tuple[str, dict, dict | None]]:
    """(name, record, SKU) for every SKU of every row of this slice, and each grocery row with no
    pack size (``sku`` None draws the record's own drawing)."""
    out: list[tuple[str, dict, dict | None]] = []
    for (code, name), rec in _flavour_records().items():
        out += [(f"{code} {name} {s['pack_size']}", rec, s) for s in rec["skus"]]
        out.append((f"{code} {name} no pack", rec, None))
    out += [(pid, rec, None) for pid, rec in _authored().items()]
    return out


def test_each_row_draws_its_own_chocolate_shape() -> None:
    assert set(_flavour_records()) == set(FLAVOURS)
    assert set(_authored()) == set(AUTHORED)
    drawn = {
        **{k: r["drawing"] for k, r in _flavour_records().items()},
        **{k: r["drawing"] for k, r in _authored().items()},
    }
    got = {k: (d["shape"], (d.get("params") or {}).get("piece")) for k, d in drawn.items()}
    assert got == {**FLAVOURS, **AUTHORED}


def test_the_sweets_and_the_tablet_box_keep_their_packs() -> None:
    """The boiled sweets and the tablet gift box are no chocolate: their kinds draw as before."""
    assert decoy_rows.KINDS["sweets"].shape == "bag"
    assert decoy_rows.KINDS["chocolate_box"].shape == "box"


def test_every_pack_fills_half_its_product_area() -> None:
    cases = _cases()
    assert {"100g", "200g"} <= {s["pack_size"] for _, _, s in cases if s}
    under = {
        name: round(share, 3)
        for name, rec, sku in cases
        if (share := _fill(_parts(rec, sku))) < FLOOR
    }
    assert not under, f"{len(under)} under {FLOOR:.0%} of the product area: {under}"


def test_a_heavier_pack_of_cups_draws_larger() -> None:
    rec = _flavour_records()[("PNT", "Chocolate Peanut Butter Cups")]
    assert _fill(_parts(rec, pack_size="100g")) < _fill(_parts(rec, pack_size="200g")) - 0.04


@pytest.mark.parametrize(
    "name",
    [*(" ".join(k) for k in FLAVOURS), *AUTHORED],
    ids=lambda name: name.replace(" ", "-"),
)
def test_the_chocolate_shows_glossed(name: str) -> None:
    rec = next(r for n, r, s in _cases() if s is None and n.startswith(name))
    shape = rec["drawing"]["shape"]
    assert shape in LEAST, f"drawn as {shape}, not as its own chocolate"
    svg = "".join(_parts(rec))
    gloss = re.search(r'<linearGradient id="([^"]+)"', svg)
    assert gloss, "no gloss gradient"
    chocolate = re.findall(r'<g class="chocolate"[^>]*>(.*?)</g>', svg)
    assert len(chocolate) >= LEAST[rec["drawing"]["shape"]], len(chocolate)
    assert all(f"url(#{gloss[1]})" in g for g in chocolate)


def test_every_pack_draws_inside_its_sheet() -> None:
    """Every pack stays on the 400 x 400 sheet (gen#242), a pack of cups heavier than the full one
    too."""
    cups = _flavour_records()[("PNT", "Chocolate Peanut Butter Cups")]
    drawn = [(n, _parts(r, s)) for n, r, s in _cases()]
    drawn.append(("cups 400g", _parts(cups, pack_size="400g")))
    past = {
        name: round(over, 1)
        for name, parts in drawn
        if (over := sheet_extent.overrun(_svg(parts), 400.0)) > 0
    }
    assert not past, f"packs drawn past the sheet, by units: {past}"


def test_a_cup_is_cut_to_show_its_filling() -> None:
    svg = "".join(_parts(_flavour_records()[("PNT", "Chocolate Peanut Butter Cups")]))
    assert svg.count('class="cup"') == 3 and 'class="filling"' in svg


def test_the_advent_calendar_has_24_numbered_doors_two_open() -> None:
    svg = "".join(_parts(_authored()["BRD-SEAADV"]))
    assert svg.count('class="door"') == 22 and svg.count('class="door open"') == 2
    numbers = {int(n) for n in re.findall(r">(\d+)</text>", svg)}
    assert numbers == set(range(1, 25))


def test_each_cherry_has_its_stalk() -> None:
    svg = "".join(_parts(_authored()["PLT-DXQ42"]))
    stalks = svg.count('class="stalk"')
    assert stalks >= LEAST["chocolate_box"] and stalks == svg.count('class="cherry"')


@pytest.mark.parametrize(("pid", "fruit"), [("PLT-DXQ19", "strawberry"), ("PLT-DXQ39", "banana")])
def test_a_coated_fruit_bag_shows_its_fruit(pid: str, fruit: str) -> None:
    svg = "".join(_parts(_authored()[pid]))
    assert f'class="{fruit}"' in svg


def test_each_cups_and_peanuts_sku_draws_its_own_pack_size_unscaled() -> None:
    for rec in _flavour_records().values():
        for sku in rec["skus"]:
            spec = export.drawing_spec(rec, sku)
            assert spec.get("params", {}).get("pack_size") == sku["pack_size"], sku["sku"]
            assert "pack_scale" not in spec and "pack_count" not in spec, (sku["sku"], spec)
