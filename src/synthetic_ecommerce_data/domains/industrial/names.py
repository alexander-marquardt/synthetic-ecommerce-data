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
2. **No product-type qualifier on a generic concept.** A name that contains
   one of the record's OWN product nouns -- a noun of its category path --
   anywhere, as a word (``End Mill Material`` on an end mill, ``Hex Nut
   Material`` on a nut, ``Cap Screw Type`` on a screw), is refused unless
   :data:`TYPE_SPECIFIC` lists it with census evidence that the concept really
   is type-specific. A noun naming a MATING or CONTAINED part is not a
   qualifier and is allowed: a washer's ``For Bolt Size`` (census 6), a tap's
   ``Drill Size`` (its tap-drill size; census 12), an indexable tool's ``Insert
   Screw`` (13) or ``Clamp Screw`` (5). Refusing those would steer a record to
   ``Size``, which is a different measurement. A name in the census's
   relational form, ``For <Part> ...``, is never a qualifier -- even when the
   part is the product's own root noun (a washer's ``For Fastener Sizes``,
   census 1).
   Membership alone would pass ``End Mill Material``: the census carries it on
   3 records, beside ``Material`` on 160. The census also carries
   ``Cap Screw Type``, ``Toggle Bolt Type`` and ``Machine Screw Head Type`` (1
   record each) and ``Drill Bit Size`` (4); each is a single-feed spelling
   beside a generic census name (``Type`` 52, ``Head Type`` 12, ``Size`` 109),
   so they are REFUSED, not allow-listed.
3. **No casing twin.** Keyword fields are case-sensitive, so ``Length Under
   Head`` and ``Length under Head`` are two facets. A name that differs from a
   census name only in case is refused -- use the census's casing -- and so
   are two names in one set that differ only in case.

Realistic minority spellings (``Material - Machining`` beside ``Material``) are
deliberately NOT emitted yet: they wait for the Engine's multi-name source
(elastic/prism#9406), then return as a deliberate demo.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

#: Nouns that name a product TYPE in this catalog. A name led by one of these
#: is a type-qualified spelling. ``tests/test_attribute_names.py`` asserts that
#: every category leaf contains one, so a new type cannot arrive without its
#: noun and slip its own ``<Type> Material`` past the gate.
PRODUCT_NOUNS: tuple[str, ...] = (
    "End Mill",
    "Drill Bit",
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
    "Kit",
    # The breadth categories' own nouns (alexander-marquardt/synthetic-ecommerce-data#34):
    # every one of ~50 new category leaves needs its head noun registered here
    # too, or the qualifier check above is silently disabled for that type
    # (``test_every_category_leaf_ends_in_its_own_product_noun``). Checked
    # against every VOCAB name, old and new, before landing: none collides.
    "Ball",
    "Bar",
    "Rod",
    "Stud",
    "Anchor",
    "Rivet",
    "Pin",
    "Ring",
    "Spring",
    "Fitting",
    "Clamp",
    "Nipple",
    "Valve",
    "Caster",
    "Bushing",
    "Collar",
    "Coupling",
    "Belt",
    "Chain",
    "Turnbuckle",
    "Shackle",
    "Sprocket",
    "Link",
    "Pulley",
    "Seal",
    "Gasket",
    "Glove",
    "Glass",
    "Plug",
    "File",
    "Punch",
    "Chisel",
    "Wrench",
    "Socket",
    "Vise",
    "Gage",
    "Collet",
    # The text-match decoys' head nouns (alexander-marquardt/synthetic-ecommerce-data#462).
    # "Handle" stays unregistered: it is the negative control of
    # ``test_the_head_noun_rule_bites``.
    "Plier",
    "Set",
    "Driver",
    "Splitter",
    "Holder",
    "Extractor",
    "Puller",
    "Breaker",
    "Lubricant",
    "Tensioner",
    "Guard",
    "Heater",
    "Laser",
    "Padlock",
    "Fluted Dowel",
    "Threadlocker",
    "Counterbore",
    "Fixture",
    "Case",
    "Rack",
    "Sharpener",
    "Fluid",
    "Pad",
    "Mandrel",
    "Wedge",
    "Holster",
    "Organizer",
    "Slide",
    "Blade",
    "Dispenser",
    "Cutter",
    "Tool",
    "Compound",
    "Grease",
    "Chaser",
)

#: Type-qualified names that ARE type-specific in the evidence, with it.
TYPE_SPECIFIC: dict[str, str] = {
    "End Mill Style": "census 132 of 496 records, 75% of census end mills",
    "End Mill Application": "census 67 records, all end mills",
    "Tap Style": "census 18 records, 17 of the 24 census taps",
    "Tap Chamfer": "census 3; a tap's chamfer class (Plug, Bottoming, Taper)",
    "Bearing Number": "reference spec table (ball bearings): the designation",
    "Wheel Dia.": "label ruling 2026-10-07: a diameter is named by what it measures",
    "Pin Dia.": "label ruling 2026-10-07: a cotter pin diameter is named by what it measures",
}

#: Names in neither the census nor the reference list, and why each is kept.
#: The census has no hammer and no abrasive family, so these are unknown there,
#: not contradicted by it.
NAME_EXCEPTIONS: dict[str, str] = {
    "Wheel Dia.": "a grinding wheel face diameter; the census carries no abrasive family",
    "Pin Dia.": "a cotter pin diameter; the census carries no cotter pin family",
    # Not in TYPE_SPECIFIC: "Dowel" is not a qualifying noun, so only the census gate applies.
    "Dowel Dia. (in)": "a dowel pin diameter, inch; the census carries no dowel pin family",
    "Dowel Dia. (mm)": "a dowel pin diameter, metric; the census carries no dowel pin family",
    "Backing Material": "component material: a flap disc's backing plate",
    "Handle Grip Material": "component material: a hammer's grip, beside Handle Material",
    "Face Type": "hammer striking-face form; the census carries no hammer family",
    "Face Dia.": "hammer striking-face diameter; the census carries no hammer family",
    "Handle Length": "hammer handle length, a distinct measurement from Overall Length",
    "Take Up": "how far a turnbuckle draws its ends together; no turnbuckle in the census",
    "Closed Length": "a turnbuckle end to end, fully taken up; no turnbuckle in the census",
    "Head Weight": "hammer head weight; the census carries no hammer family",
    "Base to Center Height": (
        "a pillow block's mounting face to its shaft centre; the census has Height and"
        " Overall Height, which are other measurements"
    ),
    "For Shaft Diameter": (
        "the shaft a retaining ring fits, in the census's relational form;"
        " the census carries no retaining ring family"
    ),
    "Groove Diameter": "the shaft groove a retaining ring sits in; no retaining ring in the census",
    "Groove Width": "the shaft groove a retaining ring sits in; no retaining ring in the census",
    "Square Size": "a tap's drive square; declared, never emitted (issue #3)",
    "Dash Number": "an O-ring's SAE AS568 size designation; the census carries no O-ring family",
    "Width Tolerance": (
        "an O-ring's cross-section tolerance from the AS568 table, beside the census's"
        " Inside Dia. Tolerance"
    ),
    "Thread Pitch": (
        "a metric tap's millimetres between threads; the census's bare Pitch is also a"
        " roller chain's link spacing, a different quantity, so the thread qualifies it (#113)"
    ),
    "Threads per Inch": (
        "an inch tap's thread count, a different quantity from a metric tap's Thread Pitch"
        " (#42); cased like the census's Teeth per Inch"
    ),
    "Roller Dia.": (
        "a roller chain's ASME B29.1 roller diameter; the census carries no chain"
        " dimensions, and the bare Dia. would read as the chain's own diameter"
    ),
    "Hub Diameter": "a sprocket's hub, beside its Outside Dia.; no sprocket hub in the census",
    "Length Through Bore": "a sprocket's width along the shaft; no sprocket hub in the census",
    "Fit": (
        "key stock's oversized or undersized bar, the name distributors facet it"
        " by; the census carries no key stock, and its Class is another concept"
    ),
}


def own_nouns(category: tuple[str, ...]) -> tuple[str, ...]:
    """The product nouns a category path names: the record's own type words."""
    joined = " ".join(category)
    return tuple(
        noun
        for noun in PRODUCT_NOUNS
        if re.search(rf"\b{re.escape(noun)}(e?s)?\b", joined, flags=re.IGNORECASE)
    )


def qualifying_noun(name: str, nouns: tuple[str, ...] = PRODUCT_NOUNS) -> str | None:
    """The noun from ``nouns`` that ``name`` contains as a word (singular or plural), if any."""
    for noun in nouns:
        if re.search(rf"\b{re.escape(noun)}(e?s)?\b", name, flags=re.IGNORECASE):
            return noun
    return None


def name_problems(
    names: Iterable[str],
    observed: frozenset[str],
    census: frozenset[str] = frozenset(),
    nouns: tuple[str, ...] = PRODUCT_NOUNS,
) -> list[str]:
    """Every reason a name set fails the gate, one line per name; empty when it passes.

    ``observed`` is the census names plus the reference spec-table names;
    ``census`` is the census alone, whose casing wins; ``nouns`` are the nouns
    that qualify a name for THIS product type (:func:`own_nouns`). The default,
    every registered noun, is the strict form for a name set with no type.
    """
    problems: list[str] = []
    wanted = sorted(set(names))
    by_fold: dict[str, list[str]] = {}
    for name in wanted:
        by_fold.setdefault(name.casefold(), []).append(name)
    for twins in by_fold.values():
        if len(twins) > 1:
            problems.append(f"{twins!r} differ only in case: one concept, two facets")
    census_casing = {name.casefold(): name for name in census}
    for name in wanted:
        canonical = census_casing.get(name.casefold())
        if canonical is not None and canonical != name:
            problems.append(f"{name!r} is the census's {canonical!r} in another casing")
            continue
        if name not in observed and name not in NAME_EXCEPTIONS:
            problems.append(
                f"{name!r} is in neither the census, the reference spec-table list, "
                "nor NAME_EXCEPTIONS -- use the census name for the concept, or add "
                "the name with the reason it is needed"
            )
            continue
        # A "For <part> ..." name is relational by its own grammar: it names
        # what the product MATES with (``For Bolt Size``, ``For Fastener
        # Sizes``), so the product's own noun in it is not a qualifier.
        relational = name.casefold().startswith("for ")
        noun = None if relational else qualifying_noun(name, nouns)
        if noun is not None and name not in TYPE_SPECIFIC:
            problems.append(
                f"{name!r} qualifies a concept with this product's own noun {noun!r} -- "
                "if it is this product's own property, publish the generic name the "
                "census uses (Material, Finish, Type, Size, ...); if it names a part "
                "this product mates with, use the census's relational form "
                "('For <Part> Size'); if the census shows the concept is genuinely "
                "type-specific, list it in TYPE_SPECIFIC with that evidence"
            )
    return problems
