"""Neckline depth (gen#181): data only.

"womens boat neck top" must filter or boost the stored neckline and bury the other neck types.
The catalog could not show it: a handful of tops carried a neckline, two were boat and one
slash. This module gives the demo a list to rank.

* **Products.** Womens tops (Jersey Tops, Long Sleeve Tops) and dresses over the necklines the
  kit can draw, each a distinct product (a style; its colors times its sizes are its SKUs):
  boat and slash in depth (the policy's class), crew, round, v-neck, high (roll, funnel),
  square, halter and cowl for the neighbours there are to bury. A boat or slash neckline also
  sits on a few bodysuits and co-ord sets, near-miss types whose type must still win.
* **Words.** The title names the neckline on some of the boat and slash tops only ("Boat Neck
  Satin Top"); the rest carry it as the stored attribute and a neutral description ("a wide,
  shallow neckline"), so a text match finds part of them and the attribute finds all.
* **Decoys.** A title word that is not the neckline: a boat print, a slash pocket, slashed
  sleeves, a boathouse stripe. The stored neckline is true (crew, v-neck), so a policy on the
  attribute buries them.
* **Complete.** :func:`complete` gives every other top, dress, blouse and knit a neckline, read
  from what the style already states (its title, then its drawing), and the drawing of a top,
  jumper, cardigan or bodysuit is drawn again when the title's neckline differs from it.
  ``tests/test_retail_neckline_181.py`` pins that, for every carrier whose shape draws a
  neckline, :func:`pictured` equals the stored one or is a declared :data:`SAME_PICTURE` pair
  (round for crew, slash for boat, collared for the crew or v-neck drawn, tie-neck for a collar).

The rows are templates only: :func:`scale.derivable` leaves them out.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import re
import zlib
from dataclasses import dataclass

from breadth_rows import OWNERS
from class_model import BRAND_OWNER
from kit_garments import NECKLINES
from lowerbody_rows import LRow
from main_colors import MAIN_COLORS
from variants import cw

_BRANDS = ("Harbour & Pine", "Larkmoor", "Wrenfield", "Calderby & Lune")
OWNERS.update({b: BRAND_OWNER[b] for b in _BRANDS})
_C = "Clothing"
_TOPS = ("Womens", "Tops")
HEX = {
    **MAIN_COLORS, "White": "#ffffff", "Cream": "#efe4cf", "Navy": "#26365c", "Black": "#2a2a2e",
    "Rose": "#d98a96", "Camel": "#b5835a", "Oatmeal": "#d9ccb4", "Stone": "#bdb5a6",
}  # fmt: skip
_COLORS = ("Black", "White", "Navy", "Cream", "Red", "Rose", "Blue", "Green", "Camel", "Stone", "Oatmeal", "Yellow")


@dataclass(frozen=True)
class Neck:
    """A neckline: the stored value, the kit's drawing key and the words that state it."""

    value: str
    draw: str
    title: str  # the title phrase ("Boat Neck")
    desc: str  # the description when the title names it
    plain: str  # the description when the title does not (no neckline word)
    tops: int  # products over Womens tops
    dresses: int  # products over Womens dresses
    mention: float  # the share of its tops whose title names it


NECKS = (
    Neck("boat", "boat", "Boat Neck", "a wide boat neck from shoulder to shoulder", "a wide, shallow neckline across the collarbone", 26, 6, 0.6),
    Neck("slash", "boat", "Slash Neck", "a straight slash neck cut across the collarbone", "a straight, shallow neckline that skims the collarbone", 22, 4, 0.6),
    Neck("crew", "crew", "Crew Neck", "a classic crew neck", "a close, round neckline", 22, 10, 1.0),
    Neck("round", "scoop", "Scoop Neck", "a rounded scoop neck", "a soft, rounded neckline", 80, 36, 1.0),
    Neck("v-neck", "v_neck", "V Neck", "a V neck", "a V shaped neckline", 22, 10, 1.0),
    Neck("high", "roll_neck", "Funnel Neck", "a high funnel neck that sits close", "a high neckline that sits close", 46, 16, 1.0),
    Neck("square", "square", "Square Neck", "a square neck", "a square neckline", 30, 16, 1.0),
    Neck("halter", "halter", "Halter Neck", "a halter neck that ties behind the neck", "straps that rise to the neck", 20, 12, 1.0),
    Neck("cowl", "cowl", "Cowl Neck", "a draped cowl neck", "a soft, draped neckline", 20, 12, 1.0),
)  # fmt: skip
#: draw key -> the stored neckline the picture shows (``slash`` is drawn as a boat).
DRAWN = {"crew": "crew", "scoop": "round", "v_neck": "v-neck", "roll_neck": "high", "square": "square",
         "halter": "halter", "cowl": "cowl", "boat": "boat", "collar": "collared"}  # fmt: skip
_FABRICS = ("Cotton Jersey", "Ribbed Cotton", "Modal", "Satin", "Linen Blend", "Crepe", "Stretch Jersey", "Slub Cotton")
_MATERIAL = {"Cotton Jersey": "Cotton", "Ribbed Cotton": "Cotton", "Modal": "Modal", "Satin": "Satin",
             "Linen Blend": "Linen blend", "Crepe": "Crepe", "Stretch Jersey": "Cotton blend", "Slub Cotton": "Cotton"}  # fmt: skip
_SLEEVES = (("sleeveless", "Sleeveless", "Sleeveless"), ("short", "Short Sleeve", "Short"),
            ("three_quarter", "Three Quarter Sleeve", "Three quarter"), ("long", "Long Sleeve", "Long"))  # fmt: skip
_FITS = ("Fitted", "Relaxed", "Cropped", "Boxy")
_LINES = ("Everyday", "Essential", "Weekend", "Classic", "Soft Touch", "Easy")
_DRESS_FABRICS = ("Jersey", "Linen Blend", "Satin", "Crepe", "Cotton Poplin", "Viscose", "Broderie")
_LENGTHS = ("Mini", "Midi", "Maxi")
_BODY_FABRICS = ("Ribbed", "Cotton", "Modal")
_SIZES = ("XS", "S", "M", "L", "XL")


def _digest(*parts) -> int:
    return zlib.crc32("|".join(map(str, parts)).encode())


def _colors(code: str, base: float):
    """Two or three colors, a main color among them (``main_colors.complete`` adds the rest)."""
    n = _digest(code, "c")
    picks: list[str] = []
    for i in range(2 + n % 2):
        c = _COLORS[(n // 7 + 5 * i + (3 * i * n) % 4) % len(_COLORS)]
        while c in picks:
            c = _COLORS[(_COLORS.index(c) + 1) % len(_COLORS)]
        picks.append(c)
    return tuple(cw(c, HEX[c]) for c in picks)


def _row(code, title, brand, path, ptype, shape, desc, neck: Neck, *, price, params, attrs=(), extra=()) -> LRow:
    return LRow(
        code, title, brand, _C, path, ptype, price, shape, desc, _colors(code, price),
        attrs=attrs, sizes=tuple((s, price) for s in _SIZES), params=params, size_key="size",
        facts=(("neckline", neck.value), ("size_range", ["regular"]), *extra),
    )  # fmt: skip


def _tops() -> list[LRow]:
    rows: list[LRow] = []
    seen: set[str] = set()
    for ni, nk in enumerate(NECKS):
        for n in range(nk.tops):
            named = (_digest(nk.value, n, "m") % 100) < int(nk.mention * 100)
            if nk.mention < 1.0:  # an even spread: the first 3 of each 5 are named
                named = n % 5 < round(nk.mention * 5)
            k = n
            while True:
                fab = _FABRICS[(k + ni) % len(_FABRICS)]
                sleeves = _SLEEVES[:1] if nk.value == "halter" else _SLEEVES
                sl = sleeves[(k // len(_FABRICS) + ni) % len(sleeves)]
                fit = _FITS[(k // 3 + ni) % len(_FITS)]
                line = _LINES[(k // 2 + 3 * ni) % len(_LINES)]
                title = f"Womens {nk.title + ' ' if named else ''}{line} {fab} {fit} {sl[1]} Top"
                if title not in seen:
                    break
                k += 17
            seen.add(title)
            code = f"NK{ni}T{n:02d}"
            leaf = "Long Sleeve Tops" if sl[0] == "long" else "Jersey Tops"
            desc = f"A {fit.lower()} {sl[2].lower()} sleeve top in {_MATERIAL[fab].lower()} with {nk.desc if named else nk.plain}."
            if sl[0] == "sleeveless":
                desc = f"A {fit.lower()} sleeveless top in {_MATERIAL[fab].lower()} with {nk.desc if named else nk.plain}."
            rows.append(_row(code, title, _BRANDS[(n + ni) % 4], (*_TOPS, leaf), "Top", "top", desc, nk,
                             price=round(14.0 + 2.0 * ((k + ni) % 9), 2),
                             params=(("neckline", nk.draw), ("sleeve", sl[0]), ("kind", "tee")),
                             attrs=(("material", "Material", _MATERIAL[fab]), ("fit", "Fit", fit),
                                    ("sleeve_length", "Sleeve length", sl[2]))))  # fmt: skip
    return rows


def _dresses() -> list[LRow]:
    rows: list[LRow] = []
    seen: set[str] = set()
    for ni, nk in enumerate(NECKS):
        for n in range(nk.dresses):
            k = n
            while True:
                fab = _DRESS_FABRICS[(k + ni) % len(_DRESS_FABRICS)]
                length = _LENGTHS[(k // len(_DRESS_FABRICS) + ni) % 3]
                line = _LINES[(k // 3 + ni) % len(_LINES)]
                title = f"Womens {nk.title} {line} {fab} {length} Dress"
                if title not in seen:
                    break
                k += 11
            seen.add(title)
            desc = f"A {length.lower()} dress in {fab.lower()} with {nk.desc} and a flared skirt."
            rows.append(_row(f"NK{ni}D{n:02d}", title, _BRANDS[(n + ni + 1) % 4], ("Womens", "Dresses", f"{length} Dresses"),
                             "Dress", "dress", desc, nk, price=round(26.0 + 3.0 * ((k + ni) % 9), 2),
                             params=(("neckline", nk.draw),),
                             attrs=(("material", "Material", {"Broderie": "Cotton", "Linen Blend": "Linen blend"}.get(fab, fab)),
                                    ("length", "Length", length))))  # fmt: skip
    return rows


def _near_misses() -> list[LRow]:
    """Bodysuits and co-ord sets with a boat or slash neckline: the type must still win."""
    rows: list[LRow] = []
    for ni, nk in enumerate(NECKS[:2]):
        for n in range(3):
            fab = _BODY_FABRICS[(n + ni) % 3]
            sl = _SLEEVES[(n + 2 * ni) % 4]
            t_b = f"Womens {nk.title} {fab} {sl[1]} Bodysuit"
            rows.append(_row(f"NK{ni}B{n:02d}", t_b, _BRANDS[(n + ni) % 4], (*_TOPS, "Bodysuits"), "Bodysuit", "bodysuit",
                             f"A {fab.lower()} bodysuit with {nk.desc} and a popper fastening.", nk, price=18.0 + 2 * n,
                             params=(("neckline", nk.draw), ("sleeve", sl[0]))))  # fmt: skip
            col = _colors(f"NK{ni}S{n:02d}", 40.0)[0]
            rows.append(LRow(f"NK{ni}S{n:02d}", f"Womens {nk.title} Top and Trousers Set {n + 1}", _BRANDS[(n + ni) % 4], _C,
                             ("Womens", "Co-ords", "Sets"), "Co-ord Set", 44.0 + 2 * n, "outfit_set",
                             f"A womens co-ord: a top with {nk.desc} and matching wide trousers.", (col,),
                             sizes=tuple((s, 44.0 + 2 * n) for s in _SIZES), params=(("tee", HEX[col[0]]),),
                             facts=(("neckline", nk.value), ("size_range", ["regular"]))))  # fmt: skip
    return rows


#: (code, title, description, true neckline, draw key, sleeve, class): a title word that is not the neckline.
_DECOYS = (
    ("DBOAT", "Womens Boat Print Cotton Jersey Top", "A crew neck top in cotton jersey with a small sailing boat print on the chest.", "crew", "crew", "short", "Top"),
    ("DSLPK", "Womens Slash Pocket Slub Cotton Top", "A relaxed top in slub cotton with a V neck and slash pockets at the hem.", "v-neck", "v_neck", "long", "Top"),
    ("DSLSL", "Womens Slashed Sleeve Ribbed Cotton Top", "A fitted ribbed top with a scoop neck and slashed sleeves that open at the wrist.", "round", "scoop", "long", "Top"),
    ("DBTHS", "Womens Boathouse Stripe Modal Top", "A modal top with a square neck, named for the painted boathouses it is printed after.", "square", "square", "short", "Top"),
    ("DCREW", "Womens Rowing Crew Slogan Cotton Top", "A V neck cotton top with a rowing club slogan across the chest.", "v-neck", "v_neck", "short", "Top"),
    ("DBOAD", "Womens Boat Print Linen Blend Midi Dress", "A linen blend midi dress with a square neck and a small sailing boat print.", "square", "square", "", "Dress"),
    ("DSLSD", "Womens Slashed Hem Crepe Midi Dress", "A crepe midi dress with a crew neck and a slashed hem that opens over the knee.", "crew", "crew", "", "Dress"),
)  # fmt: skip


def _decoys() -> list[LRow]:
    rows = []
    for i, (code, title, desc, value, draw, sleeve, ptype) in enumerate(_DECOYS):
        nk = Neck(value, draw, "", "", "", 0, 0, 0)
        if ptype == "Top":
            rows.append(_row(f"NKX{code}", title, _BRANDS[i % 4], (*_TOPS, "Long Sleeve Tops" if sleeve == "long" else "Jersey Tops"),
                             "Top", "top", desc, nk, price=16.0 + i, params=(("neckline", draw), ("sleeve", sleeve), ("kind", "tee"))))  # fmt: skip
        else:
            rows.append(_row(f"NKX{code}", title, _BRANDS[i % 4], ("Womens", "Dresses", "Midi Dresses"), "Dress", "dress",
                             desc, nk, price=30.0 + i, params=(("neckline", draw),)))  # fmt: skip
    return rows


ROWS: tuple[LRow, ...] = (*_tops(), *_dresses(), *_near_misses(), *_decoys())
DECOY_CODES = tuple(f"NKX{d[0]}" for d in _DECOYS)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: a color completion leaves them as authored."""
    return frozenset(f"BRD-{c}" for c in DECOY_CODES)


# --------------------------------------------------------------------------
# Completing the styles authored before this module
# --------------------------------------------------------------------------

#: Product types that carry a neckline: a top, a dress, a blouse or a knit.
NECK_TYPES = frozenset({"Top", "Dress", "Tea Dress", "Blouse", "Jumper", "Cardigan", "Knitted Top",
                        "T-Shirt", "Shirt", "Bodysuit", "Co-ord Set", "Polo Shirt"})  # fmt: skip
DRESS_TYPES = frozenset({"Dress", "Tea Dress"})
#: Title phrase -> stored neckline, in the order they are tried.
TITLE_WORDS = (
    (r"\bboat neck\b", "boat"), (r"\bslash neck\b", "slash"), (r"\bv[- ]neck\b", "v-neck"),
    (r"\b(?:crew|round) neck\b", "crew"), (r"\bscoop neck\b", "round"), (r"\bsquare neck\b", "square"),
    (r"\bhalter(?: neck)?\b", "halter"), (r"\bcowl neck\b", "cowl"), (r"\btie neck\b", "tie-neck"),
    (r"\b(?:roll|turtle|funnel|high|polo) neck\b", "high"), (r"\b(?:shawl|band|revere) collar\b", "collared"),
)  # fmt: skip
#: Words that state a neckline on a dress only ("Wrap Dress", "Shirt Dress").
DRESS_WORDS = ((r"\bshirt dress\b", "collared"), (r"\bwrap\b", "v-neck"))
#: A drawing shape with no neckline param -> the neckline it draws.
_BY_SHAPE = {"sweatshirt": "crew", "tshirt": "crew", "blouse": "collared", "cardigan": "v-neck", "top": "crew"}
#: A dress that states no neckline: one of these, by its id (and its picture is drawn to match).
_DRESS_CHOICE = ("round", "v-neck", "square", "crew", "high", "round")


def stated(rec: dict) -> str | None:
    """The neckline a style's title states, or None."""
    title = f"{rec['title']} {rec.get('description', '')}".lower()  # the text the standard reads
    words = TITLE_WORDS + (DRESS_WORDS if rec["product_type"] in DRESS_TYPES else ())
    return next((value for pat, value in words if re.search(pat, title)), None)


#: (stated neckline, pictured neckline) pairs the drawing may differ by: the picture is the same
#: garment. Every other difference is a contradiction (``tests/test_retail_neckline_181.py``).
#: round/crew: a round neck is drawn as the crew (a scoop is drawn, but the crew stands for it);
#: slash/boat: a slash neck is drawn as the boat; collared/crew: the crew drawing stands for the
#: collar of the shirts drawn beneath it (authored before this); tie-neck/collared: a tie neck is
#: drawn as the blouse's collar, with no drawing of its own; collared/v-neck: a shawl-collar
#: cardigan is drawn open at the v, the cardigan having no collar to draw.
SAME_PICTURE = frozenset({("round", "crew"), ("slash", "boat"), ("collared", "crew"),
                          ("tie-neck", "collared"), ("collared", "v-neck")})  # fmt: skip


def agrees(rec: dict) -> bool:
    """True when the drawing shows the stored neckline (or a declared :data:`SAME_PICTURE`), or
    its shape draws no neckline."""
    shown = pictured(rec)
    return shown is None or rec.get("neckline") == shown or (rec.get("neckline"), shown) in SAME_PICTURE


def pictured(rec: dict) -> str | None:
    """The neckline a style's drawing shows, or None when its shape draws none."""
    d = rec.get("drawing") or {}
    params = d.get("params") or {}
    if "neckline" in params:
        return DRAWN.get(params["neckline"])
    return _BY_SHAPE.get(d.get("shape"))


#: The shapes that take a ``neckline`` param drawn from :data:`kit_garments.NECKLINES`.
_REDRAWN = frozenset({"top", "sweatshirt", "cardigan", "bodysuit"})


def _drawn_to_match(r: dict) -> dict:
    """``r`` with its drawing re-drawn to show its stored neckline, when it contradicts it, its
    shape takes a neckline param and the kit draws that neckline; else ``r`` as it is."""
    d = r.get("drawing") or {}
    if agrees(r) or d.get("shape") not in _REDRAWN:
        return r
    key = next((k for k, v in DRAWN.items() if v == r["neckline"] and k in NECKLINES), None)
    if key is None:  # collared, slash, tie-neck: no drawing of its own (see SAME_PICTURE)
        return r
    return {**r, "drawing": {**d, "params": {**(d.get("params") or {}), "neckline": key}}}


def complete(tpls: list[dict]) -> list[dict]:
    """Give each top, dress, blouse and knit without a neckline one: the title's, else the
    drawing's, else (a dress only) one drawn to match. Nothing already stated is changed.

    The title's neckline is the shopper truth, so a style whose drawing contradicts it is drawn
    again to show it (a dress, a top, a jumper, a cardigan, a bodysuit); one the kit has no
    drawing for stays as drawn when the pair is declared in :data:`SAME_PICTURE`.

    The records are shared with the authored samples (``build_preview4.samples``), which the image
    release draws too: a completed record is a copy, never the shared one edited in place."""
    out = []
    for r in tpls:
        if r["product_type"] not in NECK_TYPES or r.get("neckline"):
            out.append(r)
            continue
        r = {**r}
        d = r.get("drawing") or {}
        if r["product_type"] in DRESS_TYPES and d.get("shape") == "dress":
            r["neckline"] = stated(r) or _DRESS_CHOICE[_digest(r["product_id"], "neck") % len(_DRESS_CHOICE)]
            key = next((k for k, v in DRAWN.items() if v == r["neckline"]), None)
            if key:  # the picture shows what the fact says (a tie neck has no drawing yet)
                r["drawing"] = {**d, "params": {**(d.get("params") or {}), "neckline": key}}
        else:
            r["neckline"] = stated(r) or pictured(r) or "crew"
            r = _drawn_to_match(r)
        out.append(r)
    return out
