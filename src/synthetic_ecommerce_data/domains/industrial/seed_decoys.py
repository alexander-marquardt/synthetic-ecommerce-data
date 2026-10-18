"""Which text-match decoys serve which industrial seed query (#462).

A seed query is one the Combined demo runs on its industrial half (the Fasteners, Motion Control,
Fluid Power and Fittings, and Tools and Raw Materials sections, plus the item nouns). A decoy for
it is a real product whose TITLE holds the seed's words but whose category path does not name the
seed's own category, so a category policy has something visible to remove. Each decoy is one type
module under ``product_types/decoys/``; ``tests/test_industrial_seed_decoys_462.py`` holds the
rule.

* :data:`SEED_TERMS` maps a query to ``(terms, forbidden)``. ``terms`` are the words a decoy's
  title must hold, all in one SKU's title; a term matches as a whole word with an optional plural
  ending, so ``screw`` never matches ``Screwdriver``. ``forbidden`` are the phrases the decoy's
  category path must not hold: the seed's own category, a plural leaf by the catalogue's leaf rule.
* :data:`SEED_DECOYS` maps a query to the type keys that serve it.
* :data:`SECTIONS` groups the queries the way the issue's four tables do.
"""

from __future__ import annotations

#: query -> (terms the title holds, phrases the category path must not hold)
SEED_TERMS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    # Fasteners
    "hex nuts": (("hex nut",), ("hex nuts",)),
    "lock nuts": (("lock nut",), ("lock nuts",)),
    "m10 washers": (("m10", "washer"), ("washers",)),
    "stainless steel hex bolts": (("stainless steel", "hex bolt"), ("hex bolts",)),
    "7/16-14 hex head bolts": (("7/16-14", "hex head bolt"), ("hex head bolts",)),
    "m12x1.75 socket cap screws": (("m12x1.75", "socket cap screw"), ("socket cap screws",)),
    "m6x1 set screws": (("m6x1", "set screw"), ("set screws",)),
    "1/4-20 screws": (("1/4-20", "screw"), ("screws",)),
    "dowel pins": (("dowel pin",), ("dowel pins",)),
    "retaining rings": (("retaining ring",), ("retaining rings",)),
    # Motion Control, Fluid Power and Fittings
    "ball bearings": (("ball bearing",), ("ball bearings",)),
    "6203 bearing": (("6203", "bearing"), ("bearings",)),
    "roller chain": (("roller chain",), ("roller chain",)),
    "sprockets": (("sprocket",), ("sprockets",)),
    "shackles": (("shackle",), ("shackles",)),
    # Tools and Raw Materials
    "1/2 endmill": (("1/2", "end mill"), ("end mills",)),
    "3/8 square endmill": (("3/8", "square end mill"), ("square end mills",)),
    "2.5mm end mill": (("2.5 mm", "end mill"), ("end mills",)),
    "25mm end mill": (("25 mm", "end mill"), ("end mills",)),
    "3/8 inch drill bit": (("3/8", "drill bit"), ("drill bits",)),
    "carbide drill bit": (("carbide", "drill bit"), ("drill bits",)),
    "spiral flute tap": (("spiral flute tap",), ("spiral flute taps",)),
    "flap discs": (("flap disc",), ("flap discs",)),
    "cut-off wheels": (("cut-off wheel",), ("cut-off wheels",)),
    "hammers": (("hammer",), ("hammers",)),
    "screwdrivers": (("screwdriver",), ("screwdrivers",)),
    "hex keys": (("hex key",), ("hex keys",)),
    "bar stock": (("bar stock",), ("bar stock",)),
    # Item nouns
    "o-rings": (("o-ring",), ("o-rings",)),
    "screws": (("screw",), ("screws",)),
    "bolts": (("bolt",), ("bolts",)),
    "washers": (("washer",), ("washers",)),
    "nuts": (("nut",), ("nuts",)),
}

#: query -> the type keys (modules under ``product_types/decoys/``) that serve it
SEED_DECOYS: dict[str, tuple[str, ...]] = {query: () for query in SEED_TERMS}

#: section -> its queries, the four tables of the issue
SECTIONS: dict[str, tuple[str, ...]] = {
    "Fasteners": (
        "hex nuts",
        "lock nuts",
        "m10 washers",
        "stainless steel hex bolts",
        "7/16-14 hex head bolts",
        "m12x1.75 socket cap screws",
        "m6x1 set screws",
        "1/4-20 screws",
        "dowel pins",
        "retaining rings",
    ),
    "Motion Control, Fluid Power and Fittings": (
        "ball bearings",
        "6203 bearing",
        "roller chain",
        "sprockets",
        "shackles",
    ),
    "Tools and Raw Materials": (
        "1/2 endmill",
        "3/8 square endmill",
        "2.5mm end mill",
        "25mm end mill",
        "3/8 inch drill bit",
        "carbide drill bit",
        "spiral flute tap",
        "flap discs",
        "cut-off wheels",
        "hammers",
        "screwdrivers",
        "hex keys",
        "bar stock",
    ),
    "Item nouns": ("o-rings", "screws", "bolts", "washers", "nuts"),
}
