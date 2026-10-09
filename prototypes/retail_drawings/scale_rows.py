"""More deep-SKU templates for the scaled retail catalog (gen#125): data only.

:func:`scale.templates` builds these after the 328 authored styles
(:func:`build_preview4.samples`). They stay out of the round 4 preview, so its
pinned 328 samples and its generated files do not change. The rows use the
authored style classes (:class:`variants.JeanStyle`, :class:`variants.BraStyle`),
so their size runs and colorways follow the same rules.

Each row adds capacity to :mod:`scale` in one of two ways:

- a leaf's title-visible value it lacked: a mid rise skinny, a non-wired plunge.
  The leaf's other templates may then take it too (:func:`scale.value_pools`);
- a new leaf: cigarette and balloon jeans, push-up, longline, multiway and lace
  plunge bras.

``Calderwick Denim`` is a third invented denim label: as a template brand it
joins the jeans brand pool only (:func:`scale.brand_pools`).
"""

from __future__ import annotations

from variants import WASHES, BraStyle, JeanStyle, cw, style_docs

_W = tuple(WASHES)
_BLACK, _WHITE, _NUDE = cw("Black", "#2a2a2e"), cw("White", "#ffffff"), cw("Almond", "#d9b79a")
_W_LEGS = ("Petite", "Regular", "Long")
_M_LEGS = ("Short", "Regular", "Long")

JEANS = (
    JeanStyle("WINSCAR", "Winscar", "Calderwick Denim", "Womens", "Skinny", "Mid", _W[:6],
              _W_LEGS, 6, 22, 30.0),
    JeanStyle("HOLTBY", "Holtby", "Ferrowick Denim", "Mens", "Straight", "Low",
              ("Rinse", "Indigo", "Mid Wash", "Black", "Grey"), _M_LEGS, 28, 40, 36.0),
    JeanStyle("ELLERBY", "Ellerby", "Calderwick Denim", "Womens", "Wide Leg", "Mid",
              ("Indigo", "Mid Wash", "Light Wash", "Black", "Ecru"), _W_LEGS, 6, 24, 38.0),
    JeanStyle("GARSDALE", "Garsdale", "Ottery Denim", "Womens", "Bootcut", "High",
              ("Rinse", "Indigo", "Mid Wash", "Black"), (*_W_LEGS, "Extra Long"), 6, 22, 34.0),
    JeanStyle("MUNSLOW", "Munslow", "Calderwick Denim", "Womens", "Barrel", "Mid",
              ("Mid Wash", "Light Wash", "Ecru", "Washed Black"), ("Regular", "Long"),
              6, 18, 44.0, "100% Cotton"),
    JeanStyle("STAINBY", "Stainby", "Ottery Denim", "Womens", "Slim", "High",
              ("Dark Indigo", "Indigo", "Vintage Blue", "Black", "Grey"), _W_LEGS, 6, 22, 29.0),
    JeanStyle("TARNSIDE", "Tarnside", "Ferrowick Denim", "Womens", "Flared", "Mid",
              ("Indigo", "Mid Wash", "Black", "White"), ("Regular", "Long", "Extra Long"),
              8, 20, 40.0),
    JeanStyle("KESWOLD", "Keswold", "Calderwick Denim", "Womens", "Carrot", "High",
              ("Mid Wash", "Light Wash", "Bleach Wash", "Ecru"), _W_LEGS, 6, 20, 42.0,
              "100% Cotton"),
    JeanStyle("RAVELIN", "Ravelin", "Ottery Denim", "Womens", "Cigarette", "High",
              ("Rinse", "Dark Indigo", "Black", "Ecru"), _W_LEGS, 6, 20, 36.0),
    JeanStyle("BROCKHURST", "Brockhurst", "Ferrowick Denim", "Womens", "Cigarette", "Mid",
              ("Indigo", "Mid Wash", "Washed Black"), ("Petite", "Regular"), 6, 18, 34.0),
    JeanStyle("PENNARD", "Pennard", "Calderwick Denim", "Womens", "Balloon", "High",
              ("Mid Wash", "Light Wash", "Ecru"), ("Regular", "Long"), 6, 18, 46.0,
              "100% Cotton"),
    JeanStyle("HADDOW", "Haddow", "Ferrowick Denim", "Mens", "Slim", "Low",
              ("Rinse", "Dark Indigo", "Mid Wash", "Black", "Grey", "Ecru"), _M_LEGS,
              28, 38, 35.0),
)  # fmt: skip

BRAS = (
    BraStyle("WENSLEY", "Wensley", "Bramblewood", "Plunge", (30, 40), ("A", "E"),
             (_BLACK, _NUDE, cw("Rose", "#d98a96")), 20.0, wired=False),
    BraStyle("COVERACK", "Coverack", "Saltmarsh", "T-Shirt", (30, 42), ("A", "F"),
             (_BLACK, _WHITE, _NUDE, cw("Grey Marl", "#9a9ca0")), 18.0, wired=False),
    BraStyle("ASHWELL", "Ashwell", "Saltmarsh", "Full Cup", (32, 46), ("B", "H"),
             (_BLACK, _WHITE, _NUDE), 24.0, wired=False, fabric="Cotton, Elastane"),
    BraStyle("DUNHOLME", "Dunholme", "Bramblewood", "Balcony", (30, 40), ("A", "E"),
             (_BLACK, _NUDE, cw("Claret", "#7a1f35")), 22.0, wired=False),
    BraStyle("FENBRIDGE", "Fenbridge", "Saltmarsh", "Minimiser", (34, 46), ("C", "G"),
             (_BLACK, _NUDE), 24.0, wired=False),
    BraStyle("KELSALL", "Kelsall", "Bramblewood", "Push-Up", (30, 38), ("A", "D"),
             (_BLACK, _WHITE, _NUDE, cw("Scarlet", "#b3202c")), 26.0),
    BraStyle("MORVAH", "Morvah", "Bramblewood", "Longline", (30, 40), ("A", "F"),
             (_BLACK, cw("Ivory", "#f3ecd9")), 30.0),
    BraStyle("THIRLBY", "Thirlby", "Saltmarsh", "Multiway", (30, 40), ("A", "F"),
             (_BLACK, _WHITE, _NUDE), 26.0),
    BraStyle("HAVERIGG", "Haverigg", "Bramblewood", "Lace Plunge", (28, 38), ("AA", "F"),
             (_BLACK, _WHITE, cw("Wine", "#5e1a2c")), 25.0),
    BraStyle("RUDSTON", "Rudston", "Saltmarsh", "Sports", (30, 42), ("B", "G"),
             (_BLACK, cw("Navy", "#26365c")), 32.0, fabric="Recycled Polyester, Elastane"),
)  # fmt: skip

#: family -> its scale-only styles, in build order.
FAMILIES: dict[str, tuple] = {"Jeans": JEANS, "Bras": BRAS}


def docs() -> list[dict]:
    """Every scale-only style's document, after the authored ones in :func:`scale.templates`."""
    return [d for fam, styles in FAMILIES.items() for s in styles for d in style_docs(fam, s)]
