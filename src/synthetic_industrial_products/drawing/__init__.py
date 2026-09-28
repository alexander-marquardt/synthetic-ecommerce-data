"""One text-free drawing per SKU, drawn from that SKU's own published values.

Rulings this implements (elastic/prism-industrial-products#103, 2026-09-26 to
2026-09-28):

* **One image per SKU**, so selecting a variant can switch the picture once a
  grouped view exists, and so two SKUs that differ in a visible specification
  look different today.
* **No text of any kind** in a drawing (:func:`svg_problems` is the gate):
  no dimension, callout, label, brand name, caption or SKU. The drawing
  reflects the specifications visually --
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

import re
import xml.etree.ElementTree as ET
from collections.abc import Mapping

from ..render.marking import FINISH_ATTRIBUTES, MATERIAL_ATTRIBUTES
from .figures import FIGURES
from .sheet import paint
from .style import house_style, material_hatch, part_fill

__all__ = ["FIGURES", "draw_sku", "svg_problems", "UnknownTypeError"]

#: THE ALLOW-LIST a drawing is checked against. A blacklist of text forms
#: (``<text>``, ``font-family``, one font's glyph ids) misses most of them --
#: ``<title>``, ``<desc>``, ``aria-label``, a comment, ``<metadata>``,
#: ``<foreignObject>``, an embedded raster, ``@font-face`` in a ``<style>``, a
#: glyph path from any other font. So the check is the other way round: every
#: element and attribute must be one the figures emit, no element may carry
#: character data, and nothing but elements may appear (no comment, processing
#: instruction, declaration or doctype).
ALLOWED_ELEMENTS: frozenset[str] = frozenset(
    {"svg", "rect", "defs", "pattern", "g", "path", "circle"}
)
ALLOWED_ATTRIBUTES: frozenset[str] = frozenset(
    {
        "viewBox", "width", "height", "x", "y", "rx", "cx", "cy", "r", "d",
        "fill", "stroke", "stroke-width", "stroke-opacity", "stroke-linejoin",
        "opacity", "transform", "id", "patternUnits",
    }
)  # fmt: skip
#: Ids are the hatch patterns' own (``h45s5<ink>``): a font's glyph ids
#: (``DejaVuSans-31``) and anything else are refused.
_ID = re.compile(r"^h[0-9-]*s[0-9.]+d?[0-9a-f]{6}$")
_SVG_NS = "{http://www.w3.org/2000/svg}"


def svg_problems(svg: bytes) -> list[str]:
    """Every way ``svg`` departs from the allow-list; empty for a clean drawing."""
    problems: list[str] = []
    if b"<!" in svg or b"<?" in svg:
        problems.append("a comment, declaration, doctype or processing instruction")
    builder = ET.TreeBuilder(insert_comments=True, insert_pis=True)
    parser = ET.XMLParser(target=builder)
    try:
        parser.feed(svg)
        root = parser.close()
    except ET.ParseError as exc:
        return [f"not well-formed XML: {exc}"]
    for element in root.iter():
        tag = element.tag
        if not isinstance(tag, str):
            problems.append("a comment or processing instruction")
            continue
        local = tag[len(_SVG_NS) :] if tag.startswith(_SVG_NS) else tag
        if not tag.startswith(_SVG_NS):
            problems.append(f"element {tag!r} is outside the SVG namespace")
        if local not in ALLOWED_ELEMENTS:
            problems.append(f"element <{local}> is not allowed")
        for name, value in element.attrib.items():
            if name not in ALLOWED_ATTRIBUTES:
                problems.append(f"attribute {name!r} on <{local}> is not allowed")
            elif name == "id" and not _ID.match(value):
                problems.append(f"id {value!r} is not a hatch pattern id")
        for text in (element.text, element.tail):
            if text is not None and text.strip():
                problems.append(f"character data {text.strip()[:20]!r} in <{local}>")
    return problems


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
