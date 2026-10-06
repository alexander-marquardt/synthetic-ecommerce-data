"""One nested attribute entry: its machine key, and its value split into parts.

The data contract is elastic/prism#9935's ruling (tracked here as #42):

* every entry carries a REQUIRED machine ``key`` beside its display ``name``. The
  Engine discovers attributes from that key;
* a MEASURED value is fully split. ``value`` is the bare magnitude (``1/2``),
  ``unit_code`` is the only place the unit lives, and ``value_canonical`` is
  derived from the pair. A count is measured too (``C62``);
* a composite designator (``1/4-20``, ``M10x1.5``) stays unitless text.

The split reads the PUBLISHED string, for the reason :mod:`.model` gives for
``value_num``: a number computed from the generator's own magnitude can disagree
with the string actually published, and one read back out of it cannot.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

_NON_WORD = re.compile(r"[^a-z0-9]+")

#: PRISM canonical names taken by the document's first-class columns. An attribute
#: that sanitises onto one of these is NAMESPACED rather than dropped or refused:
#: see :func:`canonical_name`.
STRUCTURAL_NAMES = frozenset(
    {
        "id",
        "sku",
        "product_id",
        "product_type",
        "title",
        "description",
        "parent_title",
        "brand",
        "brand_search",
        "series",
        "series_search",
        "categories",
        "category_path_joined",
        "category_leaf",
        "dimension_provenance",
        "spec_quality",
        "price",
        "stock",
        "attribute_names",
        "fulltext",
    }
)

#: The prefix an attribute's canonical name takes when its sanitised key is a
#: structural field's name.
ATTRIBUTE_PREFIX = "attr_"

#: A published unit marker, and the UN/CEFACT code it means.
UNIT_FOR_SUFFIX: dict[str, str] = {
    '"': "INH",
    "in": "INH",
    "in.": "INH",
    "mm": "MMT",
    "Degrees": "DD",
    "oz": "ONZ",
    "lbf": "C78",
    "lb": "LBR",
}

#: Attributes published as a bare number, and the unit that number is in. A count
#: is measured in ``C62`` (one), so it ranges like any other measurement.
UNIT_FOR_BARE_NAME: dict[str, str] = {
    "Number of Flutes": "C62",
    "Grit": "C62",
    "Package Quantity": "C62",
    "Number of Pieces": "C62",
    "Max. RPM": "RPM",
    "Decimal Equivalent": "INH",
}

#: The size of one unit in its kind's canonical unit: millimetres, grams, degrees,
#: one, rpm and pound-force, the canonical units the industrial deployment declares.
CANONICAL_PER_UNIT: dict[str, Fraction] = {
    "INH": Fraction(127, 5),
    "MMT": Fraction(1),
    "DD": Fraction(1),
    "ONZ": Fraction(45359237, 1600000),
    "LBR": Fraction(45359237, 100000),
    "C62": Fraction(1),
    "RPM": Fraction(1),
    "C78": Fraction(1),
}

#: A published number: a mixed number, a fraction, a thousands-separated or plain
#: decimal, or a leading-dot decimal.
_NUMBER = (
    r"(?:[0-9]+[ -][0-9]+/[0-9]+|[0-9]+/[0-9]+"
    r"|[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?|\.[0-9]+)"
)
# Longest suffix first, so ``lbf`` is not read as ``lb`` and ``in.`` not as ``in``.
_SUFFIXES = "|".join(re.escape(s) for s in sorted(UNIT_FOR_SUFFIX, key=len, reverse=True))
_WITH_UNIT = re.compile(rf"^\s*(?P<number>{_NUMBER})\s*(?P<suffix>{_SUFFIXES})\s*$")
_BARE = re.compile(rf"^\s*(?P<number>{_NUMBER})\s*$")


def sanitize(name: str) -> str:
    """``Milling Dia.`` -> ``milling_dia``: a usable field name.

    Attribute names as published contain dots, slashes and trailing
    punctuation. A dot is a path separator in Elasticsearch and a trailing one
    is simply invalid, so a published name cannot be used as a field name
    as-is.
    """
    return _NON_WORD.sub("_", name.strip().lower()).strip("_")


def canonical_name(key: str) -> str:
    """An attribute's canonical name: its sanitised key, namespaced on a collision.

    THE GENERAL RULE, not a one-off. Supplier feeds publish attribute names
    that are also the names of a catalog's own columns -- the reference census
    carries ``Series`` (25 records), ``Product Type`` (15) and ``Brand`` (1) as
    ATTRIBUTE names -- and a bearing's ``Series`` (``62``) is not its product
    line's ``series`` column. Dropping the attribute loses data; refusing the
    whole catalog is worse. So the attribute is named ``attr_series``, both as
    a nested entry's ``key`` and as the flat field map's entry name; one rule
    serves both so the two cannot drift.
    """
    return f"{ATTRIBUTE_PREFIX}{key}" if key in STRUCTURAL_NAMES else key


def entry_key(name: str) -> str:
    """The machine ``key`` a nested entry carries for a published attribute name."""
    return canonical_name(sanitize(name))


def _magnitude(number: str) -> str:
    """The bare magnitude: thousands separators dropped, a mixed number hyphenated."""
    number = number.replace(",", "")
    return re.sub(r"^([0-9]+) ([0-9]+/[0-9]+)$", r"\1-\2", number)


def _exact(magnitude: str) -> Fraction:
    if "-" in magnitude:
        whole, frac = magnitude.split("-")
        return int(whole) + Fraction(frac)
    return Fraction(magnitude)


def split(name: str, published: str, bare_unit: str | None = None) -> dict[str, Any]:
    """The value parts of one entry: ``value``, and when measured the unit and canonical.

    A unit marker in the string decides the unit. A bare number takes one only
    when its attribute is known to be published bare in a unit -- by name, or
    by ``bare_unit`` from the generator, which knows a metric tap's pitch is in
    millimetres and an inch tap's is a thread count. Anything else stays text.

    A defective spelling such as ``Helix Angle = 42"`` splits as written: the
    bad value is kept and the bad spelling is dropped (#9284).
    """
    unit: str | None = None
    match = _WITH_UNIT.fullmatch(published)
    if match is not None:
        unit = UNIT_FOR_SUFFIX[match["suffix"]]
    else:
        match = _BARE.fullmatch(published)
        if match is not None:
            unit = bare_unit or UNIT_FOR_BARE_NAME.get(name)
    if match is None or unit is None:
        return {"value": published}
    magnitude = _magnitude(match["number"])
    canonical = float(_exact(magnitude) * CANONICAL_PER_UNIT[unit])
    return {"value": magnitude, "unit_code": unit, "value_canonical": canonical}


def entry(name: str, published: str, bare_unit: str | None = None) -> dict[str, Any]:
    """One nested entry: ``{key, name, value[, unit_code, value_canonical]}``."""
    return {"key": entry_key(name), "name": name, **split(name, published, bare_unit)}
