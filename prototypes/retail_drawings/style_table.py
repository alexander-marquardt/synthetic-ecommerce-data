"""The attributes a garment style word allows (gen#511).

A title that names a style ("Coat Dress", "Maxi Dress", "Camisole") promises a garment: a coat dress
is tailored, with a collar, lapels or a V neck, at knee or midi length, in wool, ponte or crepe; a
maxi dress is long. The generators draw neckline, length and material from their own pools, so a
clone of a boat-neck mini carrying a style word it contradicts read as no real product (#511: "Red
Coat Dress", boat neck, mini, crepe).

This module is the one table (:data:`STYLES`): per style word, the necklines, lengths, sleeves and
materials it allows. A field left ``None`` is unconstrained. :func:`violations` reads a catalog
document and names each attribute outside the table of a style word its title holds; the generators
that clone a style (:mod:`decoy_apparel`) draw only inside it (:func:`allows`), and
``tests/test_garment_style_table_511.py`` runs the check over the generated catalog.

Values are the catalog's own: a neckline is the ``neckline`` fact (``v-neck``, ``collared``,
``boat``, ``round`` for a scoop neck), a length the ``length`` or ``garment_length`` attribute, a
sleeve the ``sleeve_length`` attribute, a material or fabric a word one of whose keywords it holds.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

DRESS_TYPES = ("Dress", "Tea Dress")
#: The types a top or knitwear style word applies to.
TOP_TYPES = ("Top", "Knitted Top", "Jumper", "Cardigan", "T-Shirt", "Tee", "Polo Shirt", "Blouse",
             "Shirt", "Bodysuit")  # fmt: skip

LENGTH_WORDS = ("midi", "maxi", "mini")


@dataclass(frozen=True)
class Style:
    """One style word: where it applies, the title pattern that names it and what it allows."""

    word: str
    types: tuple[str, ...]
    pattern: str  # a regex over the lowercase title
    necklines: frozenset[str] | None = None
    lengths: frozenset[str] | None = None
    sleeves: frozenset[str] | None = None
    materials: tuple[str, ...] | None = None  # one keyword must be in the lowercase material


def _f(*values: str) -> frozenset[str]:
    return frozenset(values)


def _dress(word: str, **allowed) -> Style:
    """A dress style: the word sits straight before "dress" or before its length ("Wrap Midi
    Dress"); a hyphen or letter before it makes it another word ("T-Shirt" is not "Shirt")."""
    pat = rf"(?<![\w-]){re.escape(word)}(?: (?:midi|maxi|mini))? dress\b"
    return Style(word, DRESS_TYPES, pat, **allowed)


def _length(word: str) -> Style:
    return Style(word, DRESS_TYPES, rf"\b{word} dress\b", lengths=_f(word.title()))


_KNIT = ("knit", "merino", "wool", "cashmere", "cable", "rib")
STYLES: tuple[Style, ...] = (
    # A coat dress is tailored: collar, lapels or a V neck, knee or midi, a coating fabric.
    _dress("coat", necklines=_f("collared", "v-neck"), lengths=_f("Knee", "Midi"),
           materials=("wool", "ponte", "crepe", "tweed", "twill", "gabardine", "boucle")),
    _dress("blazer", necklines=_f("collared", "v-neck"),
           materials=("wool", "ponte", "crepe", "suiting", "tweed", "twill")),
    # A shirt dress buttons up to a collar, in a crisp woven fabric.
    _dress("shirt", necklines=_f("collared"),
           materials=("cotton", "poplin", "linen", "denim", "chambray", "oxford", "twill")),
    _dress("wrap", necklines=_f("v-neck")),
    _dress("tea", necklines=_f("v-neck", "square", "round", "crew", "collared"),
           lengths=_f("Knee", "Midi")),
    _dress("slip", necklines=_f("v-neck", "round", "square", "cowl"),
           lengths=_f("Mini", "Knee", "Midi", "Maxi"),
           materials=("satin", "silk", "crepe", "jersey", "viscose", "lace")),
    _dress("shift", necklines=_f("boat", "round", "square", "crew", "v-neck"),
           lengths=_f("Mini", "Knee", "Midi")),
    _dress("bodycon", necklines=_f("square", "round", "v-neck", "high", "crew", "halter"),
           lengths=_f("Mini", "Knee", "Midi"),
           materials=("jersey", "crepe", "scuba", "knit", "satin", "rib", "stretch")),
    _dress("jumper", necklines=_f("crew", "high", "v-neck", "boat"), materials=_KNIT),
    _dress("t-shirt", necklines=_f("crew"), materials=("jersey", "cotton", "modal")),
    _dress("hoodie", necklines=_f("crew", "high"),
           materials=("jersey", "cotton", "fleece", "loopback")),
    _dress("tunic", lengths=_f("Mini", "Knee", "Midi")),
    *(_length(w) for w in LENGTH_WORDS),
    # Tops and knitwear: a polo shirt has a collar, a roll or turtle neck is high, a camisole and
    # a vest top have no sleeves.
    Style("polo", TOP_TYPES, r"(?<![\w-])polo(?! neck)\b", necklines=_f("collared")),
    Style("roll neck", TOP_TYPES, r"\b(?:roll|turtle|polo|funnel) ?neck\b", necklines=_f("high")),
    Style("camisole", TOP_TYPES, r"\bcamisole\b", sleeves=_f("Sleeveless"),
          necklines=_f("v-neck", "round", "square")),
    Style("vest top", TOP_TYPES, r"\bvest top\b", sleeves=_f("Sleeveless")),
)  # fmt: skip

#: Sleeve words a title says, with the ``sleeve_length`` value each one means.
SLEEVE_TITLE = {
    "sleeveless": "Sleeveless", "short sleeve": "Short", "long sleeve": "Long",
    "three quarter sleeve": "Three quarter",
}  # fmt: skip
#: Neckline words a title says, with the ``neckline`` facts each one means.
NECK_TITLE = {
    "v neck": _f("v-neck"), "crew neck": _f("crew"), "boat neck": _f("boat"),
    "scoop neck": _f("round"), "square neck": _f("square"), "halter neck": _f("halter"),
    "cowl neck": _f("cowl"), "slash neck": _f("slash"),
}  # fmt: skip


def attr(doc: dict, *keys: str) -> str | None:
    """The first of the document's attributes named ``keys``, as its value."""
    for k in keys:
        for a in doc.get("attributes", ()):
            if a["key"] == k:
                return a["value"]
    return None


def length_of(doc: dict) -> str | None:
    return attr(doc, "garment_length", "length")


def material_of(doc: dict) -> str | None:
    return attr(doc, "material", "fabric")


def styles_of(title: str, product_type: str) -> list[Style]:
    """The styles whose word the title names, for a garment of ``product_type``."""
    low = title.lower()
    return [s for s in STYLES if product_type in s.types and re.search(s.pattern, low)]


def mismatch(style: Style, doc: dict) -> list[str]:
    """What the document holds outside ``style``'s table: one note per attribute."""
    out = []
    neck = doc.get("neckline")
    if style.necklines is not None and neck is not None and neck not in style.necklines:
        out.append(f"neckline {neck}")
    length = length_of(doc)
    if style.lengths is not None and length is not None and length not in style.lengths:
        out.append(f"length {length}")
    sleeve = attr(doc, "sleeve_length")
    if style.sleeves is not None and sleeve is not None and sleeve not in style.sleeves:
        out.append(f"sleeve {sleeve}")
    material = (material_of(doc) or "").lower()
    if style.materials and material and not any(k in material for k in style.materials):
        out.append(f"material {material}")
    return out


def title_fits(title: str, doc: dict) -> bool:
    """Whether ``doc``, retitled ``title``, stays inside the table of each style the title names.
    The decoy generator asks it of each exemplar before it clones one under a style word."""
    return not any(mismatch(s, doc) for s in styles_of(title, doc["product_type"]))


def necklines_for(title: str, product_type: str) -> frozenset[str] | None:
    """The necklines every style word of the title allows together, or ``None`` when no style
    of the title limits the neckline."""
    sets = [s.necklines for s in styles_of(title, product_type) if s.necklines is not None]
    return frozenset.intersection(*sets) if sets else None


def complete_lengths(body: list[dict]) -> list[dict]:
    """Give each dress whose title names a length ("Midi Dress") that length when it states
    none, so a filter on Garment length finds it. Nothing already stated is changed, and a
    record is copied, never edited in place (the authored samples share the records)."""
    from variants import attr as make_attr

    out = []
    for d in body:
        low = d["title"].lower()
        word = next((w for w in LENGTH_WORDS if re.search(rf"\b{w} dress\b", low)), None)
        if d["product_type"] in DRESS_TYPES and word and length_of(d) is None:
            d = {**d, "attributes": [*d["attributes"], make_attr("length", "Length", word.title())]}
        out.append(d)
    return out


def violations(doc: dict) -> list[str]:
    """Each style word the title names whose table the document's attributes leave, as
    ``"<word>: <what>"``; also a length word with no length attribute, and a neckline or sleeve
    word of the title the attributes contradict."""
    low = doc["title"].lower()
    ptype = doc["product_type"]
    out = [f"{s.word}: {m}" for s in styles_of(doc["title"], ptype) for m in mismatch(s, doc)]
    if ptype in DRESS_TYPES:
        for w in LENGTH_WORDS:
            if re.search(rf"\b{w} dress\b", low) and length_of(doc) is None:
                out.append(f"{w}: no length attribute")
    neck = doc.get("neckline")
    for phrase, facts in NECK_TITLE.items():
        if phrase in low and neck is not None and neck not in facts:
            out.append(f"{phrase}: neckline {neck}")
    sleeve = attr(doc, "sleeve_length")
    for phrase, value in SLEEVE_TITLE.items():
        if phrase in low and sleeve is not None and sleeve != value:
            out.append(f"{phrase}: sleeve {sleeve}")
    return out
