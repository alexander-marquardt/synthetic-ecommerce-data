"""One drawing per SKU, drawn from that SKU's own published values.

Rulings this implements (elastic/prism-industrial-products#103, 2026-09-26 to
2026-09-28; synthetic-ecommerce-data#132, 2026-10-08):

* **One image per SKU**, so selecting a variant can switch the picture once a
  grouped view exists, and so two SKUs that differ in a visible specification
  look different today.
* **No text but the brand's wordmark** (:func:`svg_problems` is the gate): no
  dimension, callout, label, caption or SKU. The drawing reflects the
  specifications visually -- proportions, geometry, flute count, head style,
  thread density -- and the words stay on the record, where they can change
  without re-rendering. The one exception (#132) is the brand plate under
  the figure: the brand's mark and its full name, whose capitals render at
  least 10 px tall at the Studio tile (:data:`.sheet.MIN_NAME_PX`).
* **Brands visibly different**, by house style (:mod:`.style`) and by the
  brand's mark (:mod:`...domains.industrial.drawing.brand_marks`), never by
  chance.
* **Small SVG**, a few hundred bytes to a couple of KB.

The drawing is a pure function of ``(product_type, brand, attributes)``. It
does not read the SKU, the product id or the title, so two SKUs publishing the
same drawn values draw the same bytes, which is the correct answer: the
picture has nothing to tell them apart with.
"""

from __future__ import annotations

import functools
import re
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.drawing import brand_mark
from synthetic_ecommerce_data.core.drawing.sheet import magnifier, paint, type_scale, wordmark_of
from synthetic_ecommerce_data.core.drawing.style import house_style, material_hatch, part_fill
from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES
from synthetic_ecommerce_data.domains.industrial.render.marking import (
    FINISH_ATTRIBUTES,
    MATERIAL_ATTRIBUTES,
)

__all__ = [
    "FIGURES",
    "draw_product",
    "draw_sku",
    "magnifier",
    "product_scale_for",
    "svg_problems",
    "UnknownTypeError",
]

#: THE ALLOW-LIST a drawing is checked against. A blacklist of text forms
#: (``<text>``, ``font-family``, one font's glyph ids) misses most of them --
#: ``<title>``, ``<desc>``, ``aria-label``, a comment, ``<metadata>``,
#: ``<foreignObject>``, an embedded raster, ``@font-face`` in a ``<style>``, a
#: glyph path from any other font. So the check is the other way round: every
#: element and attribute must be one the figures emit, no element may carry
#: character data, and nothing but elements may appear (no comment, processing
#: instruction, declaration or doctype).
#:
#: THE ONE TEXT ALLOWED (#132, revising the no-text ruling for the brand mark
#: only): ``<text>`` elements whose words, joined by a space, are one brand's
#: wordmark (:func:`.sheet.wordmark_of`: its full name, on one line or two).
#: Its face, weight and width adjustment are fixed values; any
#: other character data, and any ``<text>`` that spells something else, is
#: refused. Which brand's wordmark a drawing carries is the drawing tests'
#: check (``tests/test_brand_marks.py``): the gate does not know the brand.
ALLOWED_ELEMENTS: frozenset[str] = frozenset(
    {"svg", "rect", "defs", "pattern", "g", "path", "circle", "text"}
)
ALLOWED_ATTRIBUTES: frozenset[str] = frozenset(
    {
        "viewBox", "width", "height", "x", "y", "rx", "cx", "cy", "r", "d",
        "fill", "stroke", "stroke-width", "stroke-opacity", "stroke-linejoin",
        "opacity", "transform", "id", "patternUnits", "stroke-linecap", "stroke-dasharray",
        "font-family", "font-size", "font-weight", "textLength", "lengthAdjust",
    }
)  # fmt: skip
#: Attributes only the wordmark's ``<text>`` may carry.
_TEXT_ONLY = frozenset({"font-family", "font-size", "font-weight", "textLength", "lengthAdjust"})
#: Ids are the hatch patterns' own (``h45s5<ink>``) and the textures' (``tgrid<ink>``,
#: ``tdot<ink>``): a font's glyph ids (``DejaVuSans-31``) and anything else are refused.
_ID = re.compile(r"^(?:h[0-9-]*s[0-9.]+d?|tgrid|tdot)[0-9a-f]{6}$")

#: Attribute VALUES, as the figures write them. A value grammar closes the
#: paint-server route: ``fill="url(data:...)"`` or ``url(https://...#p)`` would
#: pull in an external paint server -- the one way to render text from inside
#: an allowed attribute when the file is opened directly rather than in an
#: ``<img>``. A paint may only reference a hatch pattern in the same file.
#: WHAT NO STRUCTURAL CHECK CAN CATCH, stated rather than implied: a glyph's
#: outline drawn as a plain ``<path d="...">`` is indistinguishable from any
#: other outline; only the figures' own code keeps letters out of a path.
_NUMBER = r"-?(?:\d+\.?\d*|\.\d+)"
_COLOR = r"#[0-9a-f]{6}"
_VALUE_GRAMMAR: dict[str, re.Pattern[str]] = {
    "fill": re.compile(
        rf"^(?:{_COLOR}|none|url\(#(?:h[0-9-]*s[0-9.]+d?|tgrid|tdot)[0-9a-f]{{6}}\))$"
    ),
    # The brand book's dash arrays (``brands.DASHES``), nothing else.
    "stroke-dasharray": re.compile(
        "^(?:" + "|".join(re.escape(d) for d in brands.DASHES if d) + ")$"
    ),
    "stroke": re.compile(rf"^{_COLOR}$"),
    "d": re.compile(r"^[MLHVZlhvz0-9 .\-]+$"),
    "transform": re.compile(rf"^rotate\({_NUMBER} {_NUMBER} {_NUMBER}\)$"),
    "viewBox": re.compile(rf"^{_NUMBER} {_NUMBER} {_NUMBER} {_NUMBER}$"),
    "patternUnits": re.compile(r"^userSpaceOnUse$"),
    "stroke-linejoin": re.compile(r"^round$"),
    # The magnifier glyph's round caps (the icon's own); nothing else.
    "stroke-linecap": re.compile(r"^round$"),
    "font-family": re.compile(rf"^{re.escape(brand_mark.FONT_FAMILY)}$"),
    "font-weight": re.compile(rf"^{brand_mark.FONT_WEIGHT}$"),
    "lengthAdjust": re.compile(r"^spacingAndGlyphs$"),
}
_NUMERIC = re.compile(rf"^{_NUMBER}$")
_SVG_NS = "{http://www.w3.org/2000/svg}"


@functools.cache
def _wordmarks() -> frozenset[str]:
    """Every brand's wordmark, as its ``<text>`` elements' words join."""
    return frozenset(wordmark_of(brand) for brand in brands.BY_NAME)


def svg_problems(svg: bytes) -> list[str]:
    """Every way ``svg`` departs from the allow-list; empty for a clean drawing."""
    problems: list[str] = []
    if b"<!" in svg or b"<?" in svg:
        problems.append("a comment, declaration, doctype or processing instruction")
    if b"&" in svg.replace(b"&amp;", b""):
        # The figures write no entity or character reference but the escaped
        # ampersand of a brand name ("Lark &amp; Lathe"); any other in a value
        # could spell a color the grammar then accepts, or anything else.
        problems.append("an entity or character reference")
    builder = ET.TreeBuilder(insert_comments=True, insert_pis=True)
    parser = ET.XMLParser(target=builder)
    try:
        parser.feed(svg)
        root = parser.close()
    except ET.ParseError as exc:
        return [f"not well-formed XML: {exc}"]
    words: list[str] = []
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
        if local == "svg" and element is not root:
            problems.append("a nested <svg> is not allowed")
        if local == "text":
            if len(element):
                problems.append("a <text> with child elements")
            words.append(element.text or "")
        for name, value in element.attrib.items():
            if name not in ALLOWED_ATTRIBUTES or (name in _TEXT_ONLY and local != "text"):
                problems.append(f"attribute {name!r} on <{local}> is not allowed")
            elif name == "id" and not _ID.match(value):
                problems.append(f"id {value!r} is not a hatch pattern id")
            elif name != "id" and not (_VALUE_GRAMMAR.get(name) or _NUMERIC).match(value):
                problems.append(f"{name}={value[:40]!r} on <{local}> is not a value it may take")
        for text in (element.tail,) if local == "text" else (element.text, element.tail):
            if text is not None and text.strip():
                problems.append(f"character data {text.strip()[:20]!r} in <{local}>")
    if words and " ".join(words) not in _wordmarks():
        problems.append(f"text {' '.join(words)[:40]!r} is not a brand's wordmark")
    return problems


class UnknownTypeError(KeyError):
    """No figure is defined for this product type."""


def _first(record: Mapping[str, str], names) -> str | None:
    for name in names:
        value = record.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def product_scale_for(product_type: str, records: Sequence[Mapping[str, str]]) -> float:
    """The scale every SKU of a product is drawn at (sheet units per inch): its TYPE's.

    One constant per type, so siblings draw a head, a thread or a bore they
    share identically and every part of a type is in true proportion. A part
    too small to read gets the magnifier (:func:`.sheet.magnifier`) rather than
    a larger scale. ``records`` is accepted so a caller need not know that no
    record changes the answer.
    """
    del records
    _, extent = _figure(product_type)
    return type_scale(extent)


def draw_product(
    product_type: str, brand: str, records: Sequence[Mapping[str, str]]
) -> list[tuple[bytes, str]]:
    """``(svg_bytes, source)`` for each SKU of one product, all at the product's one scale."""
    scale = product_scale_for(product_type, records)
    return [_draw(product_type, brand, record, scale) for record in records]


def draw_sku(product_type: str, brand: str, record: Mapping[str, str]) -> tuple[bytes, str]:
    """``(svg_bytes, source)`` for a SKU drawn on its own -- a product of one variant.

    ``source`` is ``record``, ``partial`` or ``nominal`` -- see
    :mod:`.figures` for what each means.
    """
    return draw_product(product_type, brand, [record])[0]


def _figure(product_type: str):
    try:
        return FIGURES[product_type]
    except KeyError as exc:
        raise UnknownTypeError(f"no figure for product type {product_type!r}") from exc


def _draw(
    product_type: str, brand: str, record: Mapping[str, str], scale: float
) -> tuple[bytes, str]:
    figure_fn, _ = _figure(product_type)
    drawn = figure_fn(dict(record))
    material = _first(record, MATERIAL_ATTRIBUTES)
    finish = _first(record, FINISH_ATTRIBUTES)
    data = paint(
        drawn.figure,
        house_style(brand),
        part_fill(finish, material),
        material_hatch(material),
        scale,
    )
    return data, drawn.source
