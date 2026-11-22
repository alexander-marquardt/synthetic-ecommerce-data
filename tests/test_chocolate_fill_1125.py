"""A chocolate bar, box and sharing bag fill their picture and show their chocolate (gen#1125).

Before gen#1125 every chocolate bar was the grocery kit's generic ``bar``: a flat wrapper in the
flavour's color that covered about a fifth of the product area at 100g, with the chocolate seen
only in a torn corner. The ``chocolate_bar`` shape opens the wrapper over its foil to show the
segmented block, glossed, with broken pieces in front, and a multipack is a stack of bars. Fill
is the share of the product area the house style frames (``TURN_AREA``) the drawing paints,
measured by :mod:`sheet_cover` as gen#1111 measures produce; the ground shadow does not count.
A bar shows its weight itself (a 100g block is smaller than a 200g one), so no pack factor
shrinks it under the floor. Slice 2 does the same for the boxes (``chocolate_box``, opened on
its tray of chocolates) and the sharing bags (``chocolate_bag``, its buttons or bites in a
window and spilled in front).
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
    sheet_cover,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.grocery_families import chocolate_of
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import Fill
from synthetic_ecommerce_data.domains.retail.kit_chocolate import CHOCOLATE

FLOOR = 0.5
#: The families whose products are chocolate bars (a multipack is a pack of them).
BAR_FAMILIES = ("CHB", "CHO", "PNT", "PNH", "PNF", "CMP")


@functools.lru_cache(maxsize=1)
def _records() -> tuple[dict, ...]:
    codes = tuple(f"GRC-{c}-" for c in BAR_FAMILIES)
    return tuple(r for r in grocery.build(grocery.TARGET) if r["product_id"].startswith(codes))


def _packs() -> list[str]:
    return sorted({s["pack_size"] for r in _records() for s in r["skus"]})


def _flavors() -> dict[str, str]:
    """Each bar family's flavour name -> its color."""
    bars = (fam for fam in grocery.FAMILIES if fam.code in BAR_FAMILIES)
    return {f.name: f.hex for fam in bars for f in fam.flavors}


def _parts(base: str, pack_size: str | None) -> list[str]:
    fill = Fill("solid", base, "#ffffff")
    return kit.shapes()["chocolate_bar"](base, fill, "Chocolate Bar", pack_size=pack_size)


def _svg(parts: list[str]) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{"".join(parts)}</svg>'


def _fill(parts: list[str]) -> float:
    return sheet_cover.cover(_svg(parts), TURN_AREA, step=4.0, skip=("ground",))


def test_every_bar_family_draws_the_chocolate_bar() -> None:
    shapes = {r["product_id"][:7]: r["drawing"]["shape"] for r in _records()}
    assert set(shapes) == {f"GRC-{c}" for c in BAR_FAMILIES}
    assert set(shapes.values()) == {"chocolate_bar"}, shapes


def test_a_cereal_bar_keeps_the_generic_bar() -> None:
    assert next(f for f in grocery.FAMILIES if f.code == "CBR").shape == "bar"


@pytest.mark.parametrize("kind", ["dark_chocolate", "white_chocolate"])
def test_a_decoy_chocolate_bar_draws_the_chocolate_bar(kind: str) -> None:
    assert decoy_rows.KINDS[kind].shape == "chocolate_bar"


def test_every_pack_of_every_flavour_fills_half_its_product_area() -> None:
    packs = [*_packs(), None]  # None: a bar sold with no pack size (a decoy row)
    assert {"100g", "200g", "4 x 35g", "6 x 25g"} <= set(packs)
    under = {
        (name, pack): round(share, 3)
        for name, base in _flavors().items()
        for pack in packs
        if (share := _fill(_parts(base, pack))) < FLOOR
    }
    first = dict(list(under.items())[:6])
    assert not under, f"{len(under)} under {FLOOR:.0%} of the product area, first: {first}"


def test_every_pack_draws_inside_its_sheet() -> None:
    """The bar, its pieces and its shadow stay on the 400 x 400 sheet (gen#242) for every pack,
    a multipack and a bar heavier than the full one included."""
    packs = [*_packs(), None, "400g"]
    assert {"4 x 35g", "6 x 25g"} <= set(packs)
    past = {
        pack: round(over, 1)
        for pack in packs
        if (over := sheet_extent.overrun(_svg(_parts("#8a5a3c", pack)), 400.0)) > 0
    }
    assert not past, f"packs drawn past the sheet, by units: {past}"


def test_a_larger_bar_draws_larger() -> None:
    assert _fill(_parts("#8a5a3c", "100g")) < _fill(_parts("#8a5a3c", "200g")) - 0.04


@pytest.mark.parametrize(("pack", "n"), [("4 x 35g", 4), ("6 x 25g", 6), ("100g", 1)])
def test_a_multipack_draws_each_of_its_bars(pack: str, n: int) -> None:
    assert "".join(_parts("#8a5a3c", pack)).count('class="bar"') == n


def test_the_chocolate_shows_with_a_highlight_and_a_shade() -> None:
    svg = "".join(_parts("#3b2416", "200g"))
    gloss = re.search(r'<linearGradient id="([^"]+)"', svg)
    assert gloss, "no gloss gradient"
    gradient = svg[gloss.start() : svg.index("</linearGradient>")]
    stops = re.findall(r'stop-color="(#[0-9a-f]{6})"', gradient)
    assert {"#ffffff", "#000000"} <= set(stops)  # a highlight and a shade
    chocolate = re.findall(r'<g class="chocolate"[^>]*>(.*?)</g>', svg)
    assert len(chocolate) >= 2  # the opened block and a broken piece in front
    assert all(f"url(#{gloss[1]})" in g for g in chocolate)


def _luminance(color: str) -> float:
    def channel(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _wrapper(parts: list[str]) -> str | None:
    found = re.search(r'class="wrapper"[^>]*fill="(#[0-9a-f]{6})"', "".join(parts))
    return found[1] if found else None


@pytest.mark.parametrize("name", sorted(_flavors()))
def test_every_wrapper_stands_out_on_white_paper(name: str) -> None:
    wrapper = _wrapper(_parts(_flavors()[name], "100g"))
    assert wrapper is not None, "no wrapper"
    assert _contrast(wrapper, "#ffffff") >= 3.0, (name, wrapper)
    assert _contrast(wrapper, kit.PAPER) >= 3.0, (name, wrapper)


def test_each_sku_draws_its_own_pack_size_unscaled() -> None:
    for rec in _records():
        for sku in rec["skus"]:
            spec = export.drawing_spec(rec, sku)
            assert spec.get("params", {}).get("pack_size") == sku["pack_size"], sku["sku"]
            assert "pack_scale" not in spec and "pack_count" not in spec, (sku["sku"], spec)


def _chocolate_fills(parts: list[str]) -> set[str]:
    groups = re.findall(r'<g class="chocolate"[^>]*>(.*?)</g>', "".join(parts))
    return {c for g in groups for c in re.findall(r'fill="(#[0-9a-f]{6})"', g)}


def test_a_mint_dark_bar_is_dark_chocolate_in_a_green_wrapper() -> None:
    green = "#2f6b52"
    fill = Fill("solid", green, "#ffffff")
    parts = kit.shapes()["chocolate_bar"](
        green, fill, "Mint Dark", pack_size="100g", chocolate="dark"
    )
    assert CHOCOLATE["dark"] in _chocolate_fills(parts)
    assert green not in _chocolate_fills(parts)
    assert _wrapper(parts) == green


def test_every_bar_style_draws_the_chocolate_its_flavour_is_made_of() -> None:
    for rec in _records():
        params = rec["drawing"].get("params", {})
        assert params.get("chocolate") in CHOCOLATE, (rec["product_id"], params)


@pytest.mark.parametrize(
    ("kind", "chocolate"), [("dark_chocolate", "dark"), ("white_chocolate", "white")]
)
def test_a_decoy_bar_names_its_chocolate(kind: str, chocolate: str) -> None:
    assert dict(decoy_rows.KINDS[kind].params)["chocolate"] == chocolate


#: The box and bag families, and the shape each draws.
PACK_SHAPES = {"CHX": "chocolate_box", "CSB": "chocolate_bag"}


@functools.lru_cache(maxsize=1)
def _pack_records() -> tuple[dict, ...]:
    codes = tuple(f"GRC-{c}-" for c in PACK_SHAPES)
    return tuple(r for r in grocery.build(grocery.TARGET) if r["product_id"].startswith(codes))


def _pack_cases() -> list[tuple[str, str, str, str | None]]:
    """(family, flavour, color, pack size) for every flavour of a box or bag family, at every
    pack size its family sells and with none."""
    out = []
    for fam in grocery.FAMILIES:
        if fam.code in PACK_SHAPES:
            out += [(fam.code, f.name, f.hex, p) for f in fam.flavors for p in (*fam.packs, None)]
    return out


def _pack_parts(code: str, flavor: str, base: str, pack_size: str | None) -> list[str]:
    """The family's shape drawn as the build asks: its own pack size, chocolate and piece."""
    params: dict = {
        "pack_size": pack_size,
        "chocolate": chocolate_of(grocery_families_flavor(code, flavor)),
    }
    if code == "CSB":
        params["piece"] = "buttons" if "Buttons" in flavor else "bites"
    return kit.shapes()[PACK_SHAPES[code]](
        base, Fill("solid", base, "#ffffff"), "Chocolates", **params
    )


def grocery_families_flavor(code: str, name: str):
    fam = next(f for f in grocery.FAMILIES if f.code == code)
    return next(f for f in fam.flavors if f.name == name)


def test_every_box_and_bag_family_draws_its_chocolate_shape() -> None:
    shapes = {r["product_id"][4:7]: r["drawing"]["shape"] for r in _pack_records()}
    assert shapes == PACK_SHAPES


def test_every_box_and_bag_fills_half_its_product_area() -> None:
    cases = _pack_cases()
    assert {("CHX", "150g"), ("CHX", "400g"), ("CSB", "150g")} <= {(c, p) for c, _, _, p in cases}
    under = {
        (code, name, pack): round(share, 3)
        for code, name, base, pack in cases
        if (share := _fill(_pack_parts(code, name, base, pack))) < FLOOR
    }
    first = dict(list(under.items())[:6])
    assert not under, f"{len(under)} under {FLOOR:.0%} of the product area, first: {first}"


@pytest.mark.parametrize(
    ("code", "small", "big"), [("CHX", "150g", "400g"), ("CSB", "150g", "250g")]
)
def test_a_heavier_box_or_bag_draws_larger(code: str, small: str, big: str) -> None:
    name = "Classic Milk" if code == "CHX" else "Milk Chocolate Buttons"
    base = grocery_families_flavor(code, name).hex
    assert (
        _fill(_pack_parts(code, name, base, small))
        < _fill(_pack_parts(code, name, base, big)) - 0.04
    )


def test_every_box_and_bag_draws_inside_its_sheet() -> None:
    past = {
        (code, pack): round(over, 1)
        for code, name, base, pack in _pack_cases()
        if (over := sheet_extent.overrun(_svg(_pack_parts(code, name, base, pack)), 400.0)) > 0
    }
    assert not past, f"packs drawn past the sheet, by units: {past}"


GLOSSED = [
    ("CHX", "Dark Truffle", 12),
    ("CSB", "Milk Chocolate Buttons", 10),
    ("CSB", "Caramel Milk Chocolate Bites", 10),
]


@pytest.mark.parametrize(("code", "name", "least"), GLOSSED)
def test_the_box_and_bag_show_their_chocolates_glossed(code: str, name: str, least: int) -> None:
    svg = "".join(_pack_parts(code, name, grocery_families_flavor(code, name).hex, "150g"))
    gloss = re.search(r'<linearGradient id="([^"]+)"', svg)
    assert gloss, "no gloss gradient"
    chocolate = re.findall(r'<g class="chocolate"[^>]*>(.*?)</g>', svg)
    assert len(chocolate) >= least, len(chocolate)
    assert all(f"url(#{gloss[1]})" in g for g in chocolate)


def test_a_larger_box_holds_more_chocolates() -> None:
    def count(pack: str) -> int:
        svg = "".join(_pack_parts("CHX", "Praline", "#9a6a44", pack))
        return svg.count('<g class="chocolate"')

    assert count("150g") < count("250g") < count("400g")


def test_a_box_draws_its_own_chocolate_and_a_second_one() -> None:
    fills = _chocolate_fills(_pack_parts("CHX", "Dark Truffle", "#3b2416", "400g"))
    assert {CHOCOLATE["dark"], CHOCOLATE["milk"]} <= fills


def test_a_sharing_bag_draws_the_pieces_its_flavour_names() -> None:
    pieces = {
        r["drawing"]["params"].get("piece")
        for r in _pack_records()
        if r["product_id"].startswith("GRC-CSB")
    }
    assert pieces == {"buttons", "bites"}
    buttons = _pack_parts("CSB", "Milk Chocolate Buttons", "#8a5a3c", "250g")
    bites = _pack_parts("CSB", "Caramel Milk Chocolate Bites", "#8a5a3c", "250g")
    assert buttons != bites


@pytest.mark.parametrize(
    ("code", "name", "base"), [(c, n, b) for c, n, b, p in _pack_cases() if p == "150g"]
)
def test_every_box_and_bag_stands_out_on_white_paper(code: str, name: str, base: str) -> None:
    wrapper = _wrapper(_pack_parts(code, name, base, "150g"))
    assert wrapper is not None, "no wrapper"
    assert _contrast(wrapper, "#ffffff") >= 3.0, (name, wrapper)
    assert _contrast(wrapper, kit.PAPER) >= 3.0, (name, wrapper)


def test_each_box_and_bag_sku_draws_its_own_pack_size_unscaled() -> None:
    for rec in _pack_records():
        for sku in rec["skus"]:
            spec = export.drawing_spec(rec, sku)
            assert spec.get("params", {}).get("pack_size") == sku["pack_size"], sku["sku"]
            assert "pack_scale" not in spec and "pack_count" not in spec, (sku["sku"], spec)
