"""The visual encoding of a product line's published attributes.

One drawing per product line, and every difference between two drawings is a
difference between two records
--------------------------------------------------------------------------
A catalog of thousands of SKUs in 500 lines showing twelve drawings renders an Estrimore
K663 HSS AlTiN mill and a competitor's carbide TiCN mill identically. The fix
is not more shapes -- both of those really are square end mills, and the shape
is right -- it is to draw each line's own *published* values.

**Every channel here is a function of a published attribute.** None of them is
a function of the product id, the SKU, the series or the index. That rule is
the whole point, and it is not fussiness: a hash-driven palette would produce
exactly the same amount of variety and would be actively misleading, because a
reader who sees two mills in different colours will conclude the difference is
real. Driven by the record, that conclusion is correct -- the colour *is* the
brand, the tint *is* the coating, the hatch *is* the material.

The channels
------------
=========================  ==========================================
outline colour             ``brand``
fill tint                  the coating/finish attribute, under any of
                           its four published spellings
section hatch              the material attribute, under any of its
                           six published spellings
flutes drawn               ``Number of Flutes``
flute/thread hand          the direction attribute, under any of its
                           three published spellings
specification stamp        every published attribute, verbatim
=========================  ==========================================

Why the stamp carries *everything*
----------------------------------
The attribute sets are ragged: one line publishes ``Tap Material``, another
``Tap Finish``, another neither. An encoding built from the attributes common
to a product type collapses to almost nothing -- measured, it manufactures
about 226 false collisions where the records differ but the drawings do not.

The five geometric channels above are the legible ones, and they are also
finite: five channels cannot separate 500 lines whose difference is sometimes
nothing but a hardness class. Measured on a generated catalog, brand, finish,
material, flutes and standards alone leave 27 lines colliding. The stamp is
what closes that gap, and it closes it honestly: it is the record's own text,
set on the drawing, so a line that differs in any published value differs in
its drawing, and two lines that publish exactly the same values draw exactly
the same picture -- which is what the reader should conclude from seeing them.

What is deliberately NOT here
-----------------------------
*Rotation and tilt.* Considered and rejected: no product property maps to it,
so it would be variance that asserts nothing.

*A dimension.* No channel here reads a ``sku``-scope attribute. These are line
drawings shared by a line's 4 to 20 SKUs, whose dimensional spread has a median
of 5.5x, so a to-scale drawing would be wrong for most of the line. Everything
encoded here is a ``line``-scope attribute -- constant over the whole line and
therefore true of every SKU that shows the drawing.

*A default.* An unknown brand, coating or material raises rather than falling
back to a neutral. A drawing that quietly drew an unrecognised coating as bare
steel would be asserting something the record contradicts, and nothing
downstream could tell.
"""

from __future__ import annotations

import textwrap
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from ..catalog.brands import BRAND_BOOK, INKS
from .attrs import UnsupportedFeatureError

__all__ = [
    "BRAND_INK",
    "MIN_INK_SEPARATION",
    "DIRECTION_ATTRIBUTES",
    "FINISH_ATTRIBUTES",
    "FINISH_TINT",
    "MATERIAL_ATTRIBUTES",
    "MATERIAL_HATCH",
    "NEUTRAL",
    "Marking",
    "marking_for_line",
]

#: The outline colour of every line drawn on the part, by brand.
#:
#: From the brand book (:mod:`..catalog.brands`), where a brand's house style
#: is its ink AND its frame. Twelve inks over forty-five brands, so an ink alone
#: no longer names a brand; the (ink, frame) pair does, and
#: :func:`..drawing.style.brand_for_house_style` reads it back. The inks
#: themselves stay pairwise separated (``MIN_INK_SEPARATION``), so two brands
#: that share a frame never share a confusable ink.
BRAND_INK: dict[str, str] = {b.name: INKS[b.ink] for b in BRAND_BOOK}

#: How far apart two outline colours have to be for the channel to be
#: readable: no brand's colour may lie within this of any other brand's
#: colour blended towards the paper.
#:
#: The constraint is about BLENDS, not about the colours themselves, and that
#: is not fussiness. Every stroke on the page is antialiased, so a line drawn
#: in one brand's colour puts pixels all the way along the segment from that
#: colour to white -- and two brands 0.097 apart by this measure put sixteen
#: of one brand's pixels inside the other brand's colour on a single card.
#: Measured, that is exactly what the first palette here did.
MIN_INK_SEPARATION = 0.12

#: The fill tint of the part, by the coating or finish the record publishes.
#:
#: These are the colours the coatings actually are. TiN is gold, TiCN is
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

#: The section hatch of the part, by material.
#:
#: Hatching a section by material is already how an engineering drawing says
#: what something is made of, so this channel is the one convention here that
#: the reader may already know. Cemented carbide gets the cross-hatch, powdered
#: metal the stipple that denotes a sintered powder, the steels the plain
#: diagonals they are conventionally given, and the non-metals a coarser
#: pattern.
#:
#: Distinct across the whole catalog rather than only within a product type.
#: The vocabularies are disjoint by type, so per-type uniqueness would be
#: enough today -- and would silently stop being enough the first time a
#: material name was shared.
#:
#: Each pattern is written at its SPARSEST spelling -- one ``/``, not three.
#: Repeating a hatch character in matplotlib multiplies its density, and a
#: dense hatch over a whole elevation both buries the part and triples the
#: compressed size of the file: measured, the same detail sheet is 42 KB at
#: three repeats and 20 KB at one.
MATERIAL_HATCH: dict[str, str] = {
    # Cutting-tool materials.
    "High Speed Steel": "/",
    "Cobalt": "\\",
    "Solid Carbide": "x",
    "Powdered Metal": ".",
    # Fastener materials.
    "Steel": "-",
    "Alloy Steel": "|",
    "Grade 12.9 Alloy Steel": "+",
    "18-8 Stainless Steel": "/.",
    "Nylon": "o",
    "316 Stainless Steel": "|.",
    "Brass": "+.",
    # Hammer head.
    "Forged Steel": "\\.",
    # Abrasives.
    "Zirconia Alumina": "*",
    "Ceramic": "O",
    "Aluminum Oxide": "\\-",
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

#: Every published spelling of "which way it turns".
DIRECTION_ATTRIBUTES: tuple[str, ...] = (
    "Cutting Direction",
    "Thread Direction",
)

#: The attribute whose value is drawn as a count of flutes.
FLUTES_ATTRIBUTE = "Number of Flutes"

#: Values the direction attributes take, and which way each leans.
_HAND: dict[str, int] = {"Right Hand": 1, "Left Hand": -1}

#: Flute counts a drawing can actually show as separate flutes. A count
#: outside it is refused rather than drawn as the nearest one it can manage.
MIN_FLUTES, MAX_FLUTES = 2, 8

#: Characters of stamp text one line of the card holds at its stamp size.
_CARD_STAMP_COLUMNS = 58
#: Lines of stamp the card has room for under the drawing.
_CARD_STAMP_LINES = 4


def _lookup(table: Mapping[str, str], value: str, channel: str, names: Sequence[str]) -> str:
    try:
        return table[value]
    except KeyError as exc:
        raise UnsupportedFeatureError(
            f"{value!r} is published as {' / '.join(names)} and the {channel} "
            f"channel has no entry for it. Add one: a drawing that fell back to "
            "a neutral would be showing a property the record contradicts."
        ) from exc


@dataclass(frozen=True)
class Marking:
    """What one product line's published attributes make its drawing look like.

    Built by :func:`marking_for_line` and passed to every drawing function.
    Frozen, so a drawing cannot quietly acquire a property on the way through.
    """

    #: The brand, kept beside its colour so a caller need not invert the map.
    brand: str
    #: Outline colour of the part.
    ink: str
    #: Fill colour of the part, or ``None`` when the record publishes no
    #: finish -- in which case the drawing is left unfilled rather than filled
    #: with a guess.
    tint: str | None
    #: Section hatch, or ``None`` when the record publishes no material.
    hatch: str | None
    #: How many flutes to draw, or ``None`` when the record does not say.
    flutes: int | None
    #: Which way flutes and threads lean: +1 right hand, -1 left hand, and
    #: ``None`` when the record publishes no direction.
    hand: int | None
    #: Every published attribute, in the order the record published it. This
    #: is what the stamp sets, and it is the whole record's line-scope half.
    rows: tuple[tuple[str, str], ...]

    @property
    def lean(self) -> int:
        """The direction to lean a flute when the record does not say.

        Right hand, because a drawing has to lean it somewhere. The stamp is
        where the reader finds out whether the record said so -- an unpublished
        direction has no row there, and the absence is the disclosure.
        """
        return 1 if self.hand is None else self.hand

    def stamp_lines(self, columns: int = _CARD_STAMP_COLUMNS, limit: int = _CARD_STAMP_LINES):
        """The card's stamp: every published value, wrapped to the card's width.

        Values only, without their attribute names. The card is 150 CSS pixels
        wide and a name-and-value table does not fit in one; the detail profile
        sets the full table, names included. Nothing is dropped to make it fit
        -- if the values run past ``limit`` lines the text is returned in full
        and the caller sets it smaller, because a stamp that silently stopped
        part-way would be a drawing claiming to show a record it was showing
        half of.

        ``break_on_hyphens=False`` because a published VALUE is a token and
        not prose. ``textwrap`` defaults to breaking at an internal hyphen, so
        ``Non-Coolant Through`` was set as ``Non-`` at the end of one line and
        ``Coolant Through`` on the next -- and ``18-8 Stainless Steel``,
        ``7/16-14`` and ``Roughing/Finishing`` are all the same shape. Read
        back, the stamp then said ``Non- Coolant Through``, which is not a
        value the record publishes.
        """
        del limit
        text = " · ".join(value for _, value in self.rows)
        return tuple(textwrap.wrap(text, width=columns, break_on_hyphens=False)) if text else ()


#: The marking for a drawing that is not of any one line: plain black line
#: work, no fill, no hatch, no stamp.
#:
#: This is what ``sip-render generics`` draws -- the twelve shapes as shapes,
#: which is a statement about a product TYPE and carries no line's values
#: because it is not a drawing of a line. Every catalog image goes through
#: :func:`marking_for_line` instead.
NEUTRAL = Marking(
    brand="",
    ink="#1b1b1b",
    tint=None,
    hatch=None,
    flutes=None,
    hand=None,
    rows=(),
)


def _first_published(
    attributes: Sequence[tuple[str, str]], names: Iterable[str]
) -> tuple[str, str] | None:
    wanted = set(names)
    for name, value in attributes:
        if name in wanted and str(value).strip():
            return name, str(value).strip()
    return None


def _flute_count(raw: str, names: Sequence[str]) -> int:
    try:
        count = int(str(raw).strip())
    except ValueError as exc:
        raise UnsupportedFeatureError(
            f"{FLUTES_ATTRIBUTE} is published as {raw!r}, which is not a count "
            "of flutes, so no number of flutes can be drawn"
        ) from exc
    if not MIN_FLUTES <= count <= MAX_FLUTES:
        raise UnsupportedFeatureError(
            f"{FLUTES_ATTRIBUTE} is published as {raw!r}; the drawing shows "
            f"{MIN_FLUTES} to {MAX_FLUTES} flutes and will not draw a count it "
            "cannot draw as separate flutes"
        )
    del names
    return count


def attribute_pairs(attributes) -> tuple[tuple[str, str], ...]:
    """``(name, value)`` for every entry, multi-valued attributes expanded.

    Accepts what the catalog's nested document carries -- a list of
    ``{"name": ..., "value": ...}`` -- and what a flat record carries, a plain
    mapping. One reader for both, so the two shapes cannot come to be marked
    differently.
    """
    if isinstance(attributes, Mapping):
        return tuple(
            (str(name), str(value))
            for name, value in attributes.items()
            if name != "sku" and str(value).strip()
        )
    pairs: list[tuple[str, str]] = []
    for entry in attributes:
        name = str(entry["name"])
        for value in entry.get("values") or [entry.get("value")]:
            if value is not None and str(value).strip():
                pairs.append((name, str(value).strip()))
    return tuple(pairs)


def marking_for_line(brand: str, attributes) -> Marking:
    """The marking for a line with ``brand`` and these published attributes.

    ``attributes`` is the line's own attribute entries -- its ``line``-scope
    half, constant over every SKU beneath it. Passing a SKU's dimensions here
    would put a dimension in the drawing, which is exactly what one drawing
    shared by a 5.5x spread of sizes must not do.
    """
    pairs = attribute_pairs(attributes)

    ink = _lookup(BRAND_INK, str(brand).strip(), "outline-colour", ("brand",))

    tint = None
    found = _first_published(pairs, FINISH_ATTRIBUTES)
    if found is not None:
        tint = _lookup(FINISH_TINT, found[1], "fill-tint", FINISH_ATTRIBUTES)

    hatch = None
    found = _first_published(pairs, MATERIAL_ATTRIBUTES)
    if found is not None:
        hatch = _lookup(MATERIAL_HATCH, found[1], "section-hatch", MATERIAL_ATTRIBUTES)

    flutes = None
    found = _first_published(pairs, (FLUTES_ATTRIBUTE,))
    if found is not None:
        flutes = _flute_count(found[1], (FLUTES_ATTRIBUTE,))

    hand = None
    found = _first_published(pairs, DIRECTION_ATTRIBUTES)
    if found is not None:
        hand = _HAND.get(found[1])
        if hand is None:
            raise UnsupportedFeatureError(
                f"{found[0]} is published as {found[1]!r}, which names no hand; "
                f"the drawing leans a flute one of {sorted(_HAND)}"
            )

    return Marking(
        brand=str(brand).strip(),
        ink=ink,
        tint=tint,
        hatch=hatch,
        flutes=flutes,
        hand=hand,
        rows=pairs,
    )
