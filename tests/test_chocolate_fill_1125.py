"""A chocolate bar fills its picture and shows its chocolate (gen#1125, slice 1).

Before gen#1125 every chocolate bar was the grocery kit's generic ``bar``: a flat wrapper in the
flavour's color that covered about a fifth of the product area at 100g, with the chocolate seen
only in a torn corner. The ``chocolate_bar`` shape opens the wrapper over its foil to show the
segmented block, glossed, with broken pieces in front, and a multipack is a stack of bars. Fill
is the share of the product area the house style frames (``TURN_AREA``) the drawing paints,
measured by :mod:`sheet_cover` as gen#1111 measures produce; the ground shadow does not count.
A bar shows its weight itself (a 100g block is smaller than a 200g one), so no pack factor
shrinks it under the floor.
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
)
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import Fill

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
    return kit.SHAPES["chocolate_bar"](base, fill, "Chocolate Bar", pack_size=pack_size)


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
