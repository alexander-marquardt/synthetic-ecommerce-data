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
from collections.abc import Mapping, Sequence
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
        "product_type_label",
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
    "ft": "FOT",
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
    "Units per Pack": "C62",
    "Piece Count": "C62",
    "Max. RPM": "RPM",
    "Decimal Equivalent": "INH",
}

#: The size of one unit in its kind's canonical unit: millimetres, grams, degrees,
#: one, rpm, pound-force and millilitres. ``value_canonical = magnitude x size``.
CANONICAL_PER_UNIT: dict[str, Fraction] = {
    "INH": Fraction(127, 5),
    "FOT": Fraction(1524, 5),
    "MMT": Fraction(1),
    "DD": Fraction(1),
    "ONZ": Fraction(45359237, 1600000),
    "LBR": Fraction(45359237, 100000),
    "C62": Fraction(1),
    "RPM": Fraction(1),
    "C78": Fraction(1),
    # Retail (gen#125): centimetres, millilitres and grams. No percent (P1): prism
    # spells no such unit, so a percent is a plain number whose name says "(%)".
    "CMT": Fraction(10),
    "MLT": Fraction(1),
    "GRM": Fraction(1),
    # Retail breadth (gen#173): a tool's battery voltage, in volts.
    "VLT": Fraction(1),
    # Retail household (gen#200) and accessories (gen#207): a bin's or a pan's capacity
    # in litres, a bag's capacity in litres, an airer's drying length in metres.
    "LTR": Fraction(1000),
    "MTR": Fraction(1000),
    # Retail toys (gen#201): a ride-on's maximum rider weight, in kilograms.
    "KGM": Fraction(1000),
    # Retail lighting (gen#232): a light's color temperature, in kelvin.
    "KEL": Fraction(1),
}

#: Units that count something PER a size, so ``value_canonical = size / magnitude``.
#:
#: ``TPI`` is a LENGTH written as a count per inch (ruled on elastic/prism#9877):
#: ``32`` threads per inch is a 1/32 inch pitch, ``127/5 / 32 = 0.79375`` mm. The
#: entry keeps the count as its ``value`` and ``TPI`` as its unit, so the row a
#: shopper reads is still ``32 TPI``. The industrial deployment declares the same
#: reciprocal (``TPI: {reciprocal: "127/5"}`` under ``length``), which is what the
#: contract test reads its sizes from.
RECIPROCAL_PER_UNIT: dict[str, Fraction] = {
    "TPI": Fraction(127, 5),
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
    by ``bare_unit`` from the generator, which knows a metric tap's ``Thread Pitch`` is
    in millimetres (``MMT``) and an inch tap's ``Threads per Inch`` is a thread
    count (``TPI``), whose canonical is the pitch length. Anything else stays text.

    The mark decides the unit and nothing repairs it: an angle spelled with a
    length mark (``Point Angle = 2"``) would split as a length, and the one-kind
    guard (``tests/test_no_wrong_kind_values_404.py``) refuses it, because the
    generator writes no such value (#404).
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
    return {"value": magnitude, "unit_code": unit, "value_canonical": canonical(magnitude, unit)}


def canonical(magnitude: str, unit: str) -> float:
    """``value_canonical``: the exact magnitude in its kind's canonical unit, as a float.

    The arithmetic is exact (:class:`~fractions.Fraction`) and rounded to a float
    once, at the end, for every unit alike: ``3/8"`` is 9.525 mm and ``13`` TPI is
    the nearest float to 127/65 mm.
    """
    exact = _exact(magnitude)
    if unit in RECIPROCAL_PER_UNIT:
        return float(RECIPROCAL_PER_UNIT[unit] / exact)
    return float(exact * CANONICAL_PER_UNIT[unit])


def entry(
    name: str, published: str, bare_unit: str | None = None, key: str | None = None
) -> dict[str, Any]:
    """One nested entry: ``{key, name, value[, unit_code, value_canonical]}``.

    ``key`` is given only when the key must differ from the one the name derives: a
    roller chain's ``Pitch`` (link spacing) is keyed ``chain_pitch``, never the thread
    pitch a tap publishes as ``Thread Pitch`` (``thread_pitch``) (#36), though real catalogs
    label both pitches alike. Otherwise the key derives from the name.
    """
    return {
        "key": key if key is not None else entry_key(name),
        "name": name,
        **split(name, published, bare_unit),
    }


def flat_key(item: Mapping[str, Any]) -> str:
    """The flat ``facets`` key a nested entry's value sits under.

    The sanitised name, unless the entry carries a key set apart from its name
    (:func:`entry`), whose values the flat document files under that key so
    the two concepts stay two facets there too.
    """
    name = item["name"]
    # A row built by hand (a reader's own fixture) may carry no key at all.
    key = item.get("key")
    return sanitize(name) if key is None or key == entry_key(name) else key


def published(entries, facets: Mapping[str, Sequence[str]]) -> list[tuple[str, str]]:
    """``(name, published spelling)`` for each nested entry, read from flat ``facets``.

    A nested entry carries no spelling, because ``unit_code`` is the only place
    the unit lives (#42). A consumer that prints the published value -- a
    drawing's card stamp, a test comparing a title with its attributes -- reads
    it from the SKU's flat document instead, whose ``facets`` keep it unchanged.

    ``entries`` must be walked in emit order -- the line's, then the SKU's --
    which is the order ``facets`` was built in, so the n-th entry under a key is
    the n-th value under it. Raises :class:`LookupError` when ``facets`` holds
    no value for an entry: the flat document is not this SKU's.
    """
    taken: dict[str, int] = {}
    pairs: list[tuple[str, str]] = []
    for item in entries:
        name = item["name"]
        key = flat_key(item)
        index = taken.get(key, 0)
        values = facets.get(key, ())
        if index >= len(values):
            raise LookupError(f"flat facets carry no value #{index + 1} for {name!r} ({key})")
        pairs.append((name, values[index]))
        taken[key] = index + 1
    return pairs
