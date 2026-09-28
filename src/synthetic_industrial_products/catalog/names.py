"""Which attribute names the generator may publish: the census gate.

The catalog used to be built on the opposite rule. ``vocab.py`` declared its
vocabularies "deliberately disjoint", and its allow-list said every other name
"must be unique to its type". That rule forced a new name per product type for
one concept -- ``Fastener Material``, ``Drill Bit Material``, ``Tap Material``,
``End Mill Material`` -- where the reference census names the concept
``Material`` (160 of 496 records) and carries ``Fastener Material`` on none.
Measured by the audit on elastic/prism-industrial-products#103: 21 of 77
emitted names were type-prefixed variants of a generically named concept. On a
nested key/value index every such name is its own facet, so the rule grew the
field count with the type count, which is exactly the explosion nested storage
must not be used to hide.

The gate that replaces it has two parts, and both are needed:

1. **Membership.** Every name is verbatim in the census, or in the names-only
   reference spec-table list, or in :data:`NAME_EXCEPTIONS` with the reason it
   is neither. A name nobody observed (``Widget Material``) is refused.
2. **No product-type qualifier on a generic concept.** A name that starts with
   a product noun (``End Mill ...``, ``Fastener ...``, ``Drill ...``) is
   refused unless :data:`TYPE_SPECIFIC` lists it with census evidence that the
   concept really is type-specific. Membership alone would pass ``End Mill
   Material``: the census carries it on 3 records, beside ``Material`` on 160.

Realistic minority spellings (``Material - Machining`` beside ``Material``) are
deliberately NOT emitted yet: they wait for the Engine's multi-name source
(elastic/prism#9406), then return as a deliberate demo.
"""

from __future__ import annotations

from collections.abc import Iterable

#: Nouns that name a product TYPE in this catalog. A name led by one of these
#: is a type-qualified spelling. ``tests/test_attribute_names.py`` asserts that
#: every category leaf contains one, so a new type cannot arrive without its
#: noun and slip its own ``<Type> Material`` past the gate.
PRODUCT_NOUNS: tuple[str, ...] = (
    "End Mill",
    "Drill",
    "Tap",
    "Fastener",
    "Screw",
    "Bolt",
    "Washer",
    "Hammer",
    "Disc",
    "Nut",
    "Bearing",
    "Wheel",
    "Key",
)

#: Type-qualified names that ARE type-specific in the evidence, with it.
TYPE_SPECIFIC: dict[str, str] = {
    "End Mill Style": "census 132 of 496 records, 75% of census end mills",
    "End Mill Application": "census 67 records, all end mills",
    "Tap Style": "census 18 records, 17 of the 24 census taps",
    "Tap Chamfer": "census 3; a tap's chamfer class (Plug, Bottoming, Taper)",
    "Bearing Number": "reference spec table (ball bearings): the designation",
}

#: Names in neither the census nor the reference list, and why each is kept.
#: The census has no hammer and no abrasive family, so these are unknown there,
#: not contradicted by it.
NAME_EXCEPTIONS: dict[str, str] = {
    "Backing Material": "component material: a flap disc's backing plate",
    "Handle Grip Material": "component material: a hammer's grip, beside Handle Material",
    "Face Type": "hammer striking-face form; the census carries no hammer family",
    "Face Dia.": "hammer striking-face diameter; the census carries no hammer family",
    "Handle Length": "hammer handle length, a distinct measurement from Overall Length",
    "Head Weight": "hammer head weight; the census carries no hammer family",
    "Square Size": "a tap's drive square; declared, never emitted (issue #3)",
}


def qualifying_noun(name: str) -> str | None:
    """The product noun ``name`` starts with, if any."""
    lowered = name.lower()
    for noun in PRODUCT_NOUNS:
        n = noun.lower()
        if lowered == n or lowered.startswith(n + " ") or lowered.startswith(n + "s "):
            return noun
    return None


def name_problems(names: Iterable[str], observed: frozenset[str]) -> list[str]:
    """Every reason a name set fails the gate, one line per name; empty when it passes.

    ``observed`` is the census names plus the reference spec-table names.
    """
    problems: list[str] = []
    for name in sorted(set(names)):
        if name not in observed and name not in NAME_EXCEPTIONS:
            problems.append(
                f"{name!r} is in neither the census, the reference spec-table list, "
                "nor NAME_EXCEPTIONS -- use the census name for the concept, or add "
                "the name with the reason it is needed"
            )
            continue
        noun = qualifying_noun(name)
        if noun is not None and name not in TYPE_SPECIFIC:
            problems.append(
                f"{name!r} qualifies a concept with the product noun {noun!r} -- "
                "publish the generic name the census uses (Material, Finish, Type, "
                "Size, Diameter, ...), or list it in TYPE_SPECIFIC with census evidence"
            )
    return problems
