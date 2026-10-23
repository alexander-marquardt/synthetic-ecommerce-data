"""The colors and attribute names a drawing reads off a record. Draws nothing.

The brand's ink, the fill tint of a coating, and the published spellings of
"what coats it" and "what it is made of". They are data, kept apart from the
drawing code so the generator's brand book and the drawing agree on them
without the one importing the other's picture-making.
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.brands import BRAND_BOOK, INKS

__all__ = [
    "BRAND_INK",
    "FINISH_ATTRIBUTES",
    "FINISH_TINT",
    "MATERIAL_ATTRIBUTES",
    "MIN_INK_SEPARATION",
]

#: From the brand book (:mod:`synthetic_ecommerce_data.core.brands`), where a brand's house style
#: is its ink AND its frame. Twelve inks over forty-five brands, so an ink alone
#: no longer names a brand; the (ink, frame) pair does, and
#: :func:`synthetic_ecommerce_data.core.drawing.style.brand_for_house_style` reads it back. The inks
#: themselves stay pairwise separated (``MIN_INK_SEPARATION``), so two brands
#: that share a frame never share a confusable ink.
BRAND_INK: dict[str, str] = {b.name: INKS[b.ink] for b in BRAND_BOOK}

#: How far apart two outline colors have to be for the channel to be
#: readable: no brand's color may lie within this of any other brand's
#: color blended towards the paper.
#:
#: The constraint is about BLENDS, not about the colors themselves, and that
#: is not fussiness. Every stroke on the page is antialiased, so a line drawn
#: in one brand's color puts pixels all the way along the segment from that
#: color to white -- and two brands 0.097 apart by this measure put sixteen
#: of one brand's pixels inside the other brand's color on a single sheet.
#: Measured, that is exactly what the first palette here did.
MIN_INK_SEPARATION = 0.12

#: The fill tint of the part, by the coating or finish the record publishes.
#:
#: These are the colors the coatings actually are. TiN is gold, TiCN is
#: blue-grey, TiAlN and AlTiN are violet-greys, black oxide is near-black,
#: bright steel is silver. So the channel is not a code to be looked up: a
#: machinist reads a gold-tinted mill as a TiN-coated mill without a legend,
#: because that is what a TiN-coated mill looks like.
#:
#: Every value is distinct, including the two violet-greys, so the channel
#: itself stays injective -- two different coatings never draw the same tint.
FINISH_TINT: dict[str, str] = {
    # Machining coatings.
    "AlTiN": "#cdc4dd",
    "TiAlN": "#bfb3d2",
    "TiCN": "#c0ccdb",
    "TiN": "#e8d59a",
    "nACo": "#a9a2bb",
    "Uncoated": "#f2f4f5",
    "Bright": "#e7ecef",
    # Drill and tap finishes.
    "Black Oxide": "#6f7275",
    "Bronze Oxide": "#c09a6b",
    "Steam Oxide": "#8f8b83",
    # Fastener finishes.
    "Plain": "#eceff1",
    "Zinc Plated": "#dbe6ec",
    "Zinc Yellow": "#ecdf8f",
    "Hot Dip Galvanized": "#c9d4cb",
    # Roller chain.
    "Nickel Plated": "#e3e6e2",
}

#: Every published spelling of "what coats it". The generator publishes the
#: census's generic ``Finish``; ``Finish - Machining`` is the census's minority
#: spelling on end mills, and a drawing has to read a record that uses it.
FINISH_ATTRIBUTES: tuple[str, ...] = (
    "Finish",
    "Finish - Machining",
)

#: Every published spelling of "what it is made of". ``Handle Material`` is
#: absent on purpose: it is the material of the handle, not of the part the
#: section hatch cuts through, and it is drawn on the handle instead.
#: ``Abrasive Material`` is the grain of an abrasive, which is what a flap
#: disc's section cuts through; a flap disc publishes no ``Material``.
MATERIAL_ATTRIBUTES: tuple[str, ...] = (
    "Material",
    "Material - Machining",
    "Abrasive Material",
)
