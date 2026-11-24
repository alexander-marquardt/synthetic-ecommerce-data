"""Brownie Tin (gen#1119, slice 3): Home > Kitchen & Dining > Bakeware > Brownie Tins.

The half of ``How to Make Brownies`` a shopper bakes in. Each title names what the tin shows: its
outline, a loose base, its twelve cells, its depth, its enamel or its lid
(:func:`kit_baking.brownie_tin`). Each SKU is a length in centimeters. Templates only: the set is
sized to the collision, so the scaled build draws no more of it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baking_rows import TINS, row
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec, a
from synthetic_ecommerce_data.domains.retail.variants import cw

HEARTH, LANTERNBY, CALDERBY, BRACKENMERE = (
    "Hearth & Table", "Lanternby", "Calderby & Lune", "Brackenmere Home")  # fmt: skip
#: Who makes each brand, as :data:`breadth_row.OWNERS` states it.
OWNERS = (
    (HEARTH, "own"), (LANTERNBY, "third_party"), (CALDERBY, "third_party"), (BRACKENMERE, "own"),
)  # fmt: skip
CHARCOAL = cw("Charcoal", "#4a4d52", "solid", "#ffffff")
GREY = cw("Grey", "#8c9196", "solid", "#2a2a2e")
SILVER = cw("Silver", "#c3c8cc", "solid", "#2a2a2e")
CREAM = cw("Cream", "#efe6d0", "solid", "#2a2a2e")
GOLD = cw("Gold", "#c9a65a", "solid", "#2a2a2e")


def _cm(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A tin's lengths in centimeters as its SKU sizes, at the price of each."""
    return tuple((str(cm), p) for cm, p in pairs)


def _row(code: str, title: str, brand: str, desc: str, material: str, coating: str, outline: str,
         sizes: tuple[tuple[str, float], ...], color: tuple, **params: str) -> object:  # fmt: skip
    return row(code, title, brand, TINS, "Brownie Tin", "brownie_tin", desc,
               (a("material", "Material", material), a("coating", "Coating", coating)),
               sizes, "length_cm", color, (("outline", outline), *sorted(params.items())))  # fmt: skip


ROWS = (
    _row("BRTSQN", "Square Non-Stick Brownie Tin", LANTERNBY,
         "A square carbon steel tin with rolled edges and a non-stick coating.",
         "Carbon Steel", "Non-Stick", "square", _cm((18, 6.0), (20, 7.0), (23, 8.5), (25, 10.0)), CHARCOAL),
    _row("BRTRCN", "Rectangular Non-Stick Brownie Tin", HEARTH,
         "A rectangular carbon steel tin with a non-stick coating, for a full tray to cut up.",
         "Carbon Steel", "Non-Stick", "rectangular", _cm((27, 8.0), (30, 9.5), (33, 11.0)), GREY),
    _row("BRTSQL", "Loose Base Square Brownie Tin", CALDERBY,
         "A square tin with a base that pushes up, so the bake lifts out in one piece.",
         "Anodized Aluminum", "Uncoated", "square", _cm((18, 13.0), (20, 15.0), (23, 18.0), (25, 21.0)), SILVER, base="loose"),
    _row("BRTCEL", "Divided Brownie Tin for 12 Brownies", BRACKENMERE,
         "A rectangular non-stick tin with twelve cells, so every square has four crisp edges.",
         "Carbon Steel", "Non-Stick", "rectangular", _cm((30, 14.0), (33, 17.0)), CHARCOAL, cells="12"),
    _row("BRTDPS", "Deep Square Brownie Tin", CALDERBY,
         "A deep square tin with straight sides, for a tall bake.",
         "Anodized Aluminum", "Uncoated", "square", _cm((18, 12.0), (20, 14.0), (23, 17.0), (25, 20.0)), SILVER, depth="deep"),
    _row("BRTENM", "Rectangular Enamel Brownie Tin", BRACKENMERE,
         "A steel tin with a speckled cream enamel and a dark rim, to bake in and serve from.",
         "Steel", "Enamel", "rectangular", _cm((25, 12.0), (30, 15.0), (35, 18.0)), CREAM, finish="speckled"),
    _row("BRTLID", "Rectangular Brownie Tin with Lid", LANTERNBY,
         "A non-stick tin with a lid that clips on, to bake, carry and store in.",
         "Carbon Steel", "Non-Stick", "rectangular", _cm((27, 13.0), (30, 15.0), (33, 17.0)), GREY, lid="yes"),
    _row("BRTGLD", "Loose Base Rectangular Brownie Tin", HEARTH,
         "A gold non-stick tin with a base that pushes up, for clean corners.",
         "Carbon Steel", "Non-Stick", "rectangular", _cm((27, 14.0), (30, 16.0), (33, 18.0)), GOLD, base="loose"),
)  # fmt: skip

SPEC = TypeSpec(
    key="brownie_tin",
    department="Home",
    product_type="Brownie Tin",
    owners=OWNERS,
    rows=ROWS,
)
