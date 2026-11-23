"""Health's feminine-care pieces (gen#1112, slice 1): the path, colors and a row helper.

Three types share them, each a spec under ``Health > Feminine Care``: ``type_specs/
sanitary_pads.py``, ``tampons.py`` and ``panty_liners.py``. Each is drawn by its shape in
:mod:`kit_health_feminine`. A style's SKUs are its pack counts (``piece_count``), and its title
shows two values the scaled build swaps (an absorbency and the wings, the applicator or the
scent; a pad's thickness too), so the build draws more packs than the templates. Each drawing
param is the lower-cased value of one of those attributes, so a derived style draws what it states
(gen#512). The rows are ``colorless``: the pack's color is the drawing's only. The brands are
Health's slice 2 brands (:data:`health_rows.OWNERS`), with the department's own labels on
derived styles (``department_rates/health.py``). Over the counter only, and no title or
description claims an effect (``docs/retail-health.md``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_health_feminine,  # noqa: F401 -- registers sanitary_pad_pack, tampon_box, liner_pack
)
from synthetic_ecommerce_data.domains.retail.health_rows import ROOT
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

FEMININE_CARE = (ROOT, "Feminine Care")

PINK = cw("Pink", "#d87a9a", "solid", "#ffffff")
PURPLE = cw("Purple", "#7a5aa8", "solid", "#ffffff")
TEAL = cw("Teal", "#2f8f8a", "solid", "#ffffff")
LILAC = cw("Lilac", "#b7a3d6", "solid", "#2a2a2e")


def row(code: str, title: str, brand: str, product_type: str, shape: str, description: str,
        attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        color: tuple = PINK) -> Row:  # fmt: skip
    """One feminine-care style under ``Health > Feminine Care > <product_type>``: its SKUs are its
    pack counts, and each attribute's lower-cased value is a drawing param of the same name less
    its type prefix (``pad_wings`` draws as ``wings``)."""
    params = tuple((k.split("_", 1)[-1] if "_" in k else k, str(v).lower()) for k, _n, v in attrs)
    return Row(code, title, brand, ROOT, (*FEMININE_CARE, product_type), product_type,
               sizes[0][1], shape, description, (color,), attrs, sizes, colorless=True,
               params=params, size_key="piece_count")  # fmt: skip
