"""One text-free drawing per SKU, drawn from that SKU's own published values.

Rulings this implements (elastic/prism-industrial-products#103, 2026-09-26 to
2026-09-28):

* **One image per SKU**, so selecting a variant can switch the picture once a
  grouped view exists, and so two SKUs that differ in a visible specification
  look different today.
* **No text of any kind** in a drawing: no dimension, callout, label, brand
  name, caption or SKU. The drawing reflects the specifications visually --
  proportions, geometry, flute count, head style, thread density -- and the
  words stay on the record, where they can change without re-rendering.
* **Brands visibly different**, by house style (:mod:`.style`), never by chance.
* **Small SVG**, a few hundred bytes to a couple of KB.

The drawing is a pure function of ``(product_type, brand, attributes)``. It
does not read the SKU, the product id or the title, so two SKUs publishing the
same drawn values draw the same bytes, which is the correct answer: the
picture has nothing to tell them apart with.
"""

from __future__ import annotations

from collections.abc import Mapping

from ..render.marking import FINISH_ATTRIBUTES, MATERIAL_ATTRIBUTES
from .figures import FIGURES
from .sheet import paint
from .style import house_style, material_hatch, part_fill

__all__ = ["FIGURES", "draw_sku", "text_in", "UnknownTypeError"]

#: What text looks like inside an SVG, however it got there: a text element, a
#: text span, a font declaration, or the glyph outlines a figure library emits
#: when it converts text to paths (matplotlib names them after the font).
_TEXT_MARKERS = (b"<text", b"<tspan", b"font-family", b"font:", b"<font", b"DejaVu", b"glyph")


def text_in(svg: bytes) -> list[str]:
    """Every text marker found in ``svg``; empty for a drawing with no text."""
    lowered = svg.lower()
    return [marker.decode() for marker in _TEXT_MARKERS if marker.lower() in lowered]


class UnknownTypeError(KeyError):
    """No figure is defined for this product type."""


def _first(record: Mapping[str, str], names) -> str | None:
    for name in names:
        value = record.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def draw_sku(product_type: str, brand: str, record: Mapping[str, str]) -> tuple[bytes, str]:
    """``(svg_bytes, source)`` for one SKU. ``record`` maps attribute name to value.

    ``source`` is ``record``, ``partial`` or ``nominal`` -- see
    :mod:`.figures` for what each means.
    """
    try:
        figure_fn, size_range = FIGURES[product_type]
    except KeyError as exc:
        raise UnknownTypeError(f"no figure for product type {product_type!r}") from exc
    drawn = figure_fn(dict(record))
    material = _first(record, MATERIAL_ATTRIBUTES)
    finish = _first(record, FINISH_ATTRIBUTES)
    data = paint(
        drawn.figure,
        house_style(brand),
        part_fill(finish, material),
        material_hatch(material),
        size_range,
    )
    return data, drawn.source
