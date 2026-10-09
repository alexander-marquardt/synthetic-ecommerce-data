"""More deep-SKU templates for the scaled retail catalog (gen#125): data only.

:func:`scale.templates` builds these after the 328 authored styles
(:func:`build_preview4.samples`). They stay out of the round 4 preview, so its
pinned 328 samples and its generated files do not change. The rows use the
authored style classes (:class:`variants.JeanStyle`, :class:`variants.BraStyle`),
so their size runs and colorways follow the same rules.

Each row adds capacity to :mod:`scale` in one of two ways:

- a leaf's title-visible value it lacked: a mid rise skinny, a non-wired plunge.
  The leaf's other templates may then take it too (:func:`scale.value_pools`);
- a new leaf: cigarette, balloon, tapered, relaxed, mom, boyfriend and kick
  flare jeans (each a :data:`kit_garments.FITS` outline); push-up, longline,
  multiway, lace plunge, bralette, front fastening, sleep, racerback,
  halterneck, triangle, padded, demi cup, lace full cup, bandeau, smoothing,
  high apex, embroidered balcony, lace bralette, low back and post-surgery bras.

A :class:`Bra` row names its own straps and fastening in the description.

``Calderwick Denim`` is a third invented denim label: as a template brand it
joins the jeans brand pool only (:func:`scale.brand_pools`).
"""

from __future__ import annotations

from dataclasses import dataclass

from variants import WASHES, BraStyle, JeanStyle, cw, style_docs

#: :class:`variants.BraStyle`'s straps and fastening, as its description words them.
HOOK_BACK = "adjustable straps and a three-row hook and eye back"


@dataclass(frozen=True)
class Bra(BraStyle):
    """A :class:`variants.BraStyle` whose description names its own straps and fastening:
    a front-fastening, sleep or bandeau bra has no three-row hook and eye back."""

    fitting: str = HOOK_BACK

    def doc(self) -> dict:
        rec = super().doc()
        return {**rec, "description": rec["description"].replace(HOOK_BACK, self.fitting)}



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
    # A rise the leaf lacked.
    JeanStyle("ASKERN", "Askern", "Ottery Denim", "Womens", "Bootcut", "Low",
              ("Dark Indigo", "Mid Wash", "Vintage Blue", "Black"), (*_W_LEGS, "Extra Long"),
              6, 20, 32.0),
    JeanStyle("LUMLEY", "Lumley", "Calderwick Denim", "Womens", "Flared", "Low",
              ("Rinse", "Mid Wash", "Light Wash", "Washed Black"),
              ("Regular", "Long", "Extra Long"), 6, 18, 39.0),
    JeanStyle("COTHERSTONE", "Cotherstone", "Ferrowick Denim", "Womens", "Wide Leg", "Low",
              ("Light Wash", "Bleach Wash", "Ecru", "Black"), ("Regular", "Long"), 6, 20, 37.0),
    JeanStyle("RIPLEY", "Ripley", "Ottery Denim", "Womens", "Balloon", "Mid",
              ("Vintage Blue", "Ecru", "Washed Black"), ("Petite", "Regular"), 6, 18, 42.0,
              "100% Cotton"),
    # A new leaf (a new kit_garments.FITS key).
    JeanStyle("COXWOLD", "Coxwold", "Ferrowick Denim", "Mens", "Tapered", "Mid",
              ("Rinse", "Dark Indigo", "Mid Wash", "Washed Black", "Grey"), _M_LEGS, 28, 40, 38.0),
    JeanStyle("HUTTON", "Hutton", "Calderwick Denim", "Womens", "Tapered", "High",
              ("Indigo", "Mid Wash", "Black", "Ecru"), _W_LEGS, 6, 22, 33.0),
    JeanStyle("BAINBRIDGE", "Bainbridge", "Ottery Denim", "Mens", "Tapered", "Low",
              ("Dark Indigo", "Vintage Blue", "Black"), _M_LEGS, 28, 38, 34.0),
    JeanStyle("KETTLEWELL", "Kettlewell", "Ottery Denim", "Mens", "Relaxed", "Mid",
              ("Rinse", "Indigo", "Mid Wash", "Light Wash", "Black"), (*_M_LEGS, "Extra Long"),
              30, 42, 40.0, "100% Cotton"),
    JeanStyle("GRASSINGTON", "Grassington", "Ferrowick Denim", "Womens", "Relaxed", "High",
              ("Mid Wash", "Vintage Blue", "Light Wash", "Ecru"), _W_LEGS, 6, 24, 36.0),
    JeanStyle("HAWES", "Hawes", "Ottery Denim", "Womens", "Mom", "High",
              ("Vintage Blue", "Mid Wash", "Light Wash", "Bleach Wash", "Black"), _W_LEGS,
              6, 22, 35.0, "100% Cotton"),
    JeanStyle("REETH", "Reeth", "Calderwick Denim", "Womens", "Mom", "Mid",
              ("Indigo", "Mid Wash", "Washed Black"), ("Regular", "Long"), 6, 20, 30.0),
    JeanStyle("MUKER", "Muker", "Ferrowick Denim", "Womens", "Boyfriend", "Mid",
              ("Light Wash", "Mid Wash", "Vintage Blue", "Grey"), _W_LEGS, 6, 22, 34.0,
              "100% Cotton"),
    JeanStyle("THWAITE", "Thwaite", "Ottery Denim", "Womens", "Boyfriend", "Low",
              ("Bleach Wash", "Light Wash", "Black"), ("Petite", "Regular"), 6, 18, 31.0,
              "100% Cotton"),
    JeanStyle("ASKRIGG", "Askrigg", "Calderwick Denim", "Womens", "Kick Flare", "High",
              ("Rinse", "Indigo", "Mid Wash", "Black", "White"), _W_LEGS, 6, 22, 38.0),
    JeanStyle("MALHAM", "Malham", "Ferrowick Denim", "Womens", "Kick Flare", "Mid",
              ("Dark Indigo", "Vintage Blue", "Ecru"), _W_LEGS, 6, 20, 36.0),
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
    # A wiring the leaf lacked.
    Bra("ORMESBY", "Ormesby", "Saltmarsh", "Push-Up", (30, 38), ("A", "E"),
        (_NUDE, _BLACK, _WHITE, cw("Berry", "#8c2a4f")), 22.0, wired=False),
    Bra("CARNBREA", "Carnbrea", "Saltmarsh", "Longline", (30, 40), ("A", "F"),
        (cw("Sage", "#9bb08f"), _BLACK, _NUDE, cw("Oat", "#d8ccb4")), 24.0, wired=False),
    Bra("LINDALE", "Lindale", "Bramblewood", "Lace Plunge", (28, 38), ("AA", "E"),
        (cw("Blush", "#e8b9b3"), _BLACK, _WHITE, cw("Midnight", "#1f2440")), 21.0, wired=False),
    Bra("WYNCOTE", "Wyncote", "Saltmarsh", "Lace Balcony", (30, 38), ("A", "F"),
        (cw("Ivory", "#f3ecd9"), _BLACK, cw("Forest", "#2f4a3a")), 23.0, wired=False),
    # A new leaf.
    Bra("FERNLEA", "Fernlea", "Bramblewood", "Bralette", (30, 40), ("A", "F"),
        (_BLACK, cw("Ivory", "#f3ecd9"), cw("Dusty Rose", "#c99a9a"), cw("Sage", "#9bb08f"),
         cw("Lavender", "#b8a9d6")), 18.0, wired=False,
        fitting="adjustable straps and a two-row hook and eye back"),
    Bra("HESKETH", "Hesketh", "Saltmarsh", "Front Fastening", (32, 44), ("B", "G"),
        (_WHITE, _BLACK, _NUDE), 26.0, fitting="adjustable straps and a front clasp"),
    Bra("TREGONY", "Tregony", "Bramblewood", "Front Fastening", (32, 46), ("B", "H"),
        (_NUDE, _BLACK, cw("Navy", "#26365c")), 22.0, wired=False, fabric="Cotton, Elastane",
        fitting="adjustable straps and a front clasp"),
    Bra("MOSSLEY", "Mossley", "Saltmarsh", "Sleep", (32, 44), ("A", "G"),
        (cw("Grey Marl", "#9a9ca0"), _BLACK, cw("Blush", "#e8b9b3"), cw("Navy", "#26365c")),
        15.0, wired=False, fabric="Modal, Elastane",
        fitting="wide soft straps and a pull-on fit with no fastening"),
    Bra("CRANWELL", "Cranwell", "Bramblewood", "Racerback", (30, 40), ("A", "G"),
        (_BLACK, _NUDE, _WHITE), 24.0,
        fitting="straps that clip into a racerback and a two-row hook and eye back"),
    Bra("DINSDALE", "Dinsdale", "Saltmarsh", "Racerback", (30, 40), ("A", "E"),
        (cw("Grey Marl", "#9a9ca0"), _BLACK, cw("Teal", "#2e7d7a")), 20.0, wired=False,
        fabric="Cotton, Elastane",
        fitting="straps that clip into a racerback and a two-row hook and eye back"),
    Bra("POLWENNA", "Polwenna", "Bramblewood", "Halterneck", (30, 38), ("A", "F"),
        (_BLACK, cw("Champagne", "#e6d3b3"), cw("Emerald", "#1f6b4f")), 27.0,
        fitting="a halterneck strap that fastens at the neck and a three-row hook and eye "
                "back"),
    Bra("IVELET", "Ivelet", "Bramblewood", "Triangle", (28, 36), ("AA", "D"),
        (cw("Coral", "#ef7b62"), _BLACK, _WHITE, cw("Lilac", "#b9a3d0")), 16.0, wired=False,
        fitting="thin adjustable straps and a two-row hook and eye back"),
    Bra("KIRKHAM", "Kirkham", "Saltmarsh", "Padded", (30, 40), ("A", "E"),
        (cw("Mocha", "#7b5a45"), _BLACK, _NUDE, _WHITE), 22.0),
    Bra("LOWTHER", "Lowther", "Bramblewood", "Padded", (30, 40), ("A", "E"),
        (cw("Rose", "#d98a96"), _BLACK, _NUDE), 19.0, wired=False),
    Bra("RYDAL", "Rydal", "Bramblewood", "Demi Cup", (30, 38), ("A", "F"),
        (cw("Wine", "#5e1a2c"), _BLACK, cw("Ivory", "#f3ecd9")), 25.0),
    Bra("WHARRAM", "Wharram", "Saltmarsh", "Lace Full Cup", (32, 46), ("B", "J"),
        (cw("Ivory", "#f3ecd9"), _BLACK, cw("Navy", "#26365c"), cw("Plum", "#6b3a5a")), 29.0),
    Bra("HAWKRIDGE", "Hawkridge", "Bramblewood", "Lace Full Cup", (32, 44), ("B", "G"),
        (_BLACK, _WHITE, cw("Fawn", "#c4a484")), 25.0, wired=False),
    Bra("TREEN", "Treen", "Bramblewood", "Bandeau", (30, 38), ("A", "E"),
        (_NUDE, _BLACK, _WHITE), 17.0, wired=False,
        fitting="a strapless band with a silicone grip and a three-row hook and eye back"),
    Bra("SKELWITH", "Skelwith", "Saltmarsh", "Smoothing", (32, 44), ("B", "H"),
        (cw("Latte", "#c8a98a"), _BLACK, _WHITE), 28.0,
        fitting="wide adjustable straps and a four-row hook and eye back"),
    Bra("NETHERCOTE", "Nethercote", "Bramblewood", "High Apex", (30, 40), ("C", "HH"),
        (_BLACK, cw("Claret", "#7a1f35"), _NUDE, cw("Petrol", "#1f4f5a")), 30.0),
    Bra("ALDBROUGH", "Aldbrough", "Bramblewood", "Embroidered Balcony", (30, 40), ("A", "G"),
        (cw("Teal", "#2e7d7a"), _BLACK, cw("Ivory", "#f3ecd9"), cw("Blush", "#e8b9b3")), 28.0),
    Bra("GLAISDALE", "Glaisdale", "Saltmarsh", "Lace Bralette", (30, 38), ("A", "E"),
        (cw("Burgundy", "#6e1f2f"), _BLACK, _WHITE, cw("Sky", "#a9c8e6")), 17.0, wired=False,
        fitting="adjustable straps and a two-row hook and eye back"),
    Bra("SANDSEND", "Sandsend", "Saltmarsh", "Low Back", (30, 38), ("A", "F"),
        (cw("Caramel", "#b07a45"), _BLACK, _WHITE), 27.0,
        fitting="adjustable straps and a low back band with a two-row hook and eye"),
    Bra("RUNSWICK", "Runswick", "Saltmarsh", "Strapless", (30, 38), ("A", "D"),
        (cw("Latte", "#c8a98a"), _BLACK, _WHITE), 20.0, wired=False,
        fitting="a silicone-gripped band, detachable straps and a three-row hook and eye back"),
    Bra("STAITHES", "Staithes", "Saltmarsh", "Post-Surgery", (32, 44), ("A", "F"),
        (cw("Soft Grey", "#b9bbbe"), _NUDE, _BLACK), 22.0, wired=False, fabric="Cotton, Elastane",
        fitting="soft wide straps, a front hook and eye fastening and pocketed cups"),
)  # fmt: skip

#: family -> its scale-only styles, in build order.
FAMILIES: dict[str, tuple] = {"Jeans": JEANS, "Bras": BRAS}


def docs() -> list[dict]:
    """Every scale-only style's document, after the authored ones in :func:`scale.templates`."""
    return [d for fam, styles in FAMILIES.items() for s in styles for d in style_docs(fam, s)]
