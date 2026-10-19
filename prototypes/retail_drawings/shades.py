"""Complexion shades (gen#345): a foundation is sold by shade, never by colour.

A foundation, a concealer and a tinted moisturiser are asked for by the skin they match
("foundation for medium skin, warm undertone", "6N"), never by a colour ("red foundation"). So
the export writes the shade to three entries and none to ``color``, which clothing queries read:

==============  ==========================================================================
``shade``       the code or name as sold: ``6N``, ``Porcelain``
``shade_depth`` fair, light, medium, tan or deep, from the code's depth (``6`` is medium)
``undertone``   cool, neutral or warm, from the code's letter (``C``, ``N``, ``W``)
==============  ==========================================================================

A shade that is a name, not a code, states its depth and undertone in :data:`NAMED`: nothing is
guessed from a word. The authored record keeps the shade under its ``color`` key (the swatch the
drawing and the image id read); :mod:`export` writes it as the three entries above for each type
of :data:`SOLD_BY_SHADE`.
"""

from __future__ import annotations

import re

#: A shade code: depth 1-14 and an undertone letter ("6N"). No ``color`` value matches it.
SHADE_CODE = re.compile(r"^(\d{1,2})([CNW])$")

#: The product types sold by shade. Each is also a declared exception to the six main colors
#: (``main_colors.EXCEPTIONS``): no red foundation. A moisturiser carries a shade only when it is
#: tinted; the untinted ones carry no colour either.
SOLD_BY_SHADE = frozenset({"Foundation", "Concealer", "Moisturiser"})

DEPTHS = ("fair", "light", "medium", "tan", "deep")
UNDERTONES = {"C": "cool", "N": "neutral", "W": "warm"}

#: The first code depth of each :data:`DEPTHS` band: 1-2 fair, 3-5 light, 6-8 medium, 9-11 tan,
#: 12 and deeper deep.
_BAND_START = (1, 3, 6, 9, 12)

#: A named shade -> (depth, undertone). A name not here is refused (:func:`classify`).
NAMED = {
    "Porcelain": ("fair", "neutral"),
    "Caramel": ("tan", "warm"),
    "Toffee": ("tan", "warm"),
    "Espresso": ("deep", "neutral"),
}


def classify(shade: str) -> tuple[str, str]:
    """``(shade_depth, undertone)`` of a shade code or of a name in :data:`NAMED`."""
    match = SHADE_CODE.match(shade)
    if match is None:
        if shade not in NAMED:
            raise KeyError(f"shade {shade!r} is neither a code like 6N nor a name in NAMED")
        return NAMED[shade]
    depth = int(match.group(1))
    band = max(i for i, start in enumerate(_BAND_START) if depth >= start)
    return DEPTHS[band], UNDERTONES[match.group(2)]
