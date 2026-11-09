"""A dress drawing shows the construction and the pattern its title names (gen#922).

"Petite Pinstripe Wrap Midi Dress" was drawn as the plain strap dress: no wrap front, no
pinstripe, so its image contradicted its own title on the result card.

* :data:`WORDS` is the vocabulary: each construction word (wrap, tiered, belted, ...) and pattern
  word (pinstripe, broderie, a named print) a dress title may carry, and what the release image
  must show for it: a drawn mark (``data-feature``) or the fill pattern of its color.
* :func:`apply` reads the words off each dress title and sets the drawing's ``features`` param, a
  space-separated list the shape draws. The fill comes from the SKU's color swatch
  (``image_release.colorway_drawing``), so a feature rides as a param, never in the color data.
* :func:`draw` is the marks themselves, original code-drawn art like the rest of the kit
  (``docs/drawings.md``): ``kit.dress`` and ``kit_garments.shirt_dress`` call it.
* :func:`unshown` is the check ``tests/test_dress_features_922.py`` runs over the generated dress
  rows: every word, with the rows whose image does not draw it.

A material (satin, lace trim, sequin, cable knit, crinkle) and a silhouette (skater, shift, slip,
tent) are not in it: the material is an attribute, and the silhouette is the style table's
(``style_table``, gen#511).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW_DETAIL,
    Fill,
    _line,
    _path,
    _shade,
    _tint,
)


@dataclass(frozen=True)
class Word:
    """A construction or pattern word, and what the release image must show for it."""

    word: str
    #: The word in a lowercased title.
    pattern: str
    #: The ``data-feature`` marks of which any one draws it.
    marks: tuple[str, ...] = ()
    #: The fill patterns (``kit.pattern_defs``) of which any one draws it.
    fills: tuple[str, ...] = ()
    #: The feature :func:`apply` sets for it; ``None`` when the color data draws it.
    feature: str | None = None


def _drawn(word: str, pattern: str, feature: str) -> Word:
    return Word(word, pattern, marks=(feature,), feature=feature)


WORDS: tuple[Word, ...] = (
    # Constructions: how the dress is cut and made up, drawn on its front.
    _drawn("wrap", r"\bwrap\b", "wrap"),
    _drawn("tiered", r"\btiered\b", "tiered"),
    _drawn("smocked", r"\bsmock(?:ed)?\b", "smocked"),
    _drawn("ruched", r"\bruched\b", "ruched"),
    _drawn("belted", r"\bbelted\b", "belted"),
    _drawn("button front", r"\bbutton[- ](?:front|through)\b", "button_front"),
    _drawn("pinafore", r"\bpinafore\b", "pinafore"),
    _drawn("pleated", r"\bpleated\b", "pleated"),
    _drawn("seamed", r"\bseamed\b", "seamed"),
    _drawn("slashed hem", r"\bslash(?:ed)? hem\b", "slashed_hem"),
    # Patterns: what the fabric carries, drawn over the fill or as the fill itself.
    _drawn("pinstripe", r"\bpin ?striped?\b", "pinstripe"),
    _drawn("broderie", r"\bbroderie\b", "broderie"),
    _drawn("roses", r"\broses\b", "rose_print"),
    _drawn("boat print", r"\bboat print\b", "boat_print"),
    Word("stripe", r"\bstriped?\b|\bstripes\b", marks=("pinstripe",), fills=("stripe",)),
    Word("spot", r"\b(?:polka|spots?|spotted|spotty|dots?|dotty)\b", fills=("polka",)),
    Word("check", r"\b(?:gingham|check|checked)\b", fills=("gingham", "tartan")),
    Word("tartan", r"\btartan\b", fills=("tartan",)),
    Word("leopard", r"\b(?:leopard|animal print)\b", fills=("leopard",)),
    Word("print", r"\b(?:print|printed|floral)\b", marks=("rose_print", "boat_print"),
         fills=("print",)),
)  # fmt: skip

#: The features each dress shape draws. A shirt dress draws its own belt and buttoned placket.
DRAWN: dict[str, frozenset[str]] = {
    "dress": frozenset(w.feature for w in WORDS if w.feature),
    "shirt_dress": frozenset({"pinstripe", "broderie", "rose_print", "boat_print", "pleated",
                              "seamed", "tiered"}),
}  # fmt: skip


def is_dress(rec: dict) -> bool:
    """A dress row: of the dress product type, or filed under a dresses node."""
    path = rec.get("category_path") or ()
    return rec.get("product_type") == "Dress" or any(p.endswith("Dresses") for p in path)


def words_of(title: str) -> list[str]:
    """The construction and pattern words ``title`` carries, in :data:`WORDS` order."""
    low = title.lower()
    return [w.word for w in WORDS if re.search(w.pattern, low)]


def apply(tpls: list[dict]) -> list[dict]:
    """``tpls`` with each dress drawing told the features its title names."""
    for tpl in tpls:
        drawing = tpl["drawing"]
        if not is_dress(tpl) or drawing["shape"] not in DRAWN:
            continue
        low = tpl["title"].lower()
        feats = sorted(
            w.feature for w in WORDS
            if w.feature in DRAWN[drawing["shape"]] and re.search(w.pattern, low)
        )  # fmt: skip
        if feats:
            drawing["params"] = {**(drawing.get("params") or {}), "features": " ".join(feats)}
    return tpls


def unshown(recs: list[dict], look: Callable[[dict], tuple[str, str]]) -> dict[str, list[str]]:
    """Each word a dress title names that its image does not draw, with the rows that name it.

    ``look`` gives a row's image: its fill pattern and its SVG. Every word of every row is read,
    so the report is the whole set, not the first word missing."""
    out: dict[str, list[str]] = {}
    for rec in recs:
        low = rec["title"].lower()
        words = [w for w in WORDS if re.search(w.pattern, low)]
        if not words:
            continue
        fill, svg = look(rec)
        marks = set(re.findall(r'data-feature="([a-z_]+)"', svg))
        for w in words:
            if fill not in w.fills and not marks & set(w.marks):
                out.setdefault(w.word, []).append(rec["product_id"])
    return out


# --------------------------------------------------------------------------
# The marks
# --------------------------------------------------------------------------

Point = tuple[float, float]
Curve = tuple[Point, Point, Point]


def _bez(c: Curve, t: float) -> Point:
    (x0, y0), (x1, y1), (x2, y2) = c
    u = 1 - t
    return u * u * x0 + 2 * u * t * x1 + t * t * x2, u * u * y0 + 2 * u * t * y1 + t * t * y2


def _lerp(p: Point, q: Point, v: float) -> Point:
    return p[0] + (q[0] - p[0]) * v, p[1] + (q[1] - p[1]) * v


def _pt(p: Point) -> str:
    return f"{p[0]:.1f},{p[1]:.1f}"


@dataclass(frozen=True)
class Frame:
    """A dress body's edges: the neckline edge, the waist, the hem (each left to right) and the
    skirt's left side (waist to hem). A point is ``(t, v)``: ``t`` across, ``v`` down."""

    top: Curve
    waist: Curve
    hem: Curve
    side: Curve

    def bodice(self, t: float, v: float) -> Point:
        return _lerp(_bez(self.top, t), _bez(self.waist, t), v)

    def skirt(self, t: float, v: float) -> Point:
        return _lerp(_bez(self.waist, t), _bez(self.hem, t), v)

    def on_side(self, s: float, right: bool = False) -> Point:
        x, y = _bez(self.side, s)
        return (400 - x, y) if right else (x, y)


#: The body paths of ``kit.dress`` and ``kit_garments.shirt_dress``, as frames.
FRAMES = {
    "dress": Frame(((158, 112), (200, 128), (242, 112)), ((164, 196), (200, 206), (236, 196)),
                   ((66, 352), (200, 378), (334, 352)), ((164, 196), (110, 270), (66, 352))),
    "shirt_dress": Frame(((158, 66), (200, 66), (242, 66)), ((148, 172), (200, 172), (252, 172)),
                         ((94, 358), (200, 376), (306, 358)), ((148, 172), (121, 265), (94, 358))),
}  # fmt: skip


def _luma(base: str) -> float:
    r, g, b = (int(base.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


def _g(feature: str, parts: list[str], fill: Fill) -> str:
    """The feature's marks, grouped and named. On a dark fill the kit's ink would vanish, so
    the marks draw in a light tint of the fill instead."""
    body = "".join(parts)
    if _luma(fill.base) < 70:
        light = _tint(fill.base, 0.55)
        body = body.replace(f'stroke="{INK}"', f'stroke="{light}"')
        body = body.replace(f'fill="{INK}"', f'fill="{light}"')
    return f'<g data-feature="{feature}">{body}</g>'


def _on(base: str) -> str:
    """A line color that reads on ``base``: darker on a light fill, lighter on a dark one."""
    return _shade(base, 0.45) if _luma(base) > 150 else _tint(base, 0.6)


def _pinstripe(f: Frame, fill: Fill) -> list[str]:
    n = 13
    d = " ".join(
        f"M{_pt(_bez(f.top, k / n))} L{_pt(_bez(f.waist, k / n))} L{_pt(_bez(f.hem, k / n))}"
        for k in range(1, n)
    )
    return [_line(d, 1.1, ' stroke-opacity=".9"', _on(fill.base))]


def _scatter(f: Frame) -> list[Point]:
    """Spots spread over the body for a print: two on the bodice, six on the skirt."""
    return [f.bodice(0.32, 0.55), f.bodice(0.7, 0.35),
            *(f.skirt(t, v) for t, v in ((0.2, 0.3), (0.58, 0.22), (0.4, 0.58), (0.8, 0.6),
                                         (0.24, 0.86), (0.64, 0.9)))]  # fmt: skip


def _broderie(f: Frame, fill: Fill) -> list[str]:
    """Broderie anglaise: rows of eyelet flowers, a hole with four petals round it."""
    spots = [f.bodice(t, 0.5) for t in (0.25, 0.5, 0.75)]
    for i, v in enumerate((0.16, 0.4, 0.64, 0.88)):
        ts = (0.12, 0.31, 0.5, 0.69, 0.88) if i % 2 == 0 else (0.215, 0.405, 0.595, 0.785)
        spots += [f.skirt(t, v) for t in ts]
    ring = f'fill="#ffffff" stroke="{INK}" stroke-width=".8"'
    out = []
    for x, y in spots:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" {ring}/>')
        out += [f'<ellipse cx="{x + dx:.1f}" cy="{y + dy:.1f}" rx="1.6" ry="1.6" {ring}/>'
                for dx, dy in ((5, 0), (-5, 0), (0, 5), (0, -5))]  # fmt: skip
    return out


def _roses(f: Frame, fill: Fill) -> list[str]:
    out = []
    for x, y in _scatter(f):
        out += [
            f'<ellipse cx="{x - 8:.1f}" cy="{y + 5:.1f}" rx="5" ry="2.6" fill="#3d6b35" '
            f'transform="rotate(-25 {x - 8:.1f} {y + 5:.1f})"/>',
            f'<ellipse cx="{x + 8:.1f}" cy="{y + 5:.1f}" rx="5" ry="2.6" fill="#3d6b35" '
            f'transform="rotate(25 {x + 8:.1f} {y + 5:.1f})"/>',
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#9b111e"/>',
            _line(
                f"M{x:.1f},{y:.1f} q3,-3 0,-4.5 q-5,0 -4.5,4.5 q1,6 7,3.5 q4,-3 1.5,-8",
                1.1,
                stroke="#5e0a12",
            ),
        ]
    return out


def _boats(f: Frame, fill: Fill) -> list[str]:
    out = []
    for x, y in _scatter(f):
        out += [
            _path(f"M{x - 9:.1f},{y + 3:.1f} L{x + 9:.1f},{y + 3:.1f} L{x + 5:.1f},{y + 8:.1f} "
                  f"L{x - 5:.1f},{y + 8:.1f} Z", INK, 0.8),
            _line(f"M{x:.1f},{y + 3:.1f} L{x:.1f},{y - 11:.1f}", 1.1),
            _path(f"M{x + 1.5:.1f},{y - 10:.1f} L{x + 9:.1f},{y + 1:.1f} L{x + 1.5:.1f},"
                  f"{y + 1:.1f} Z", "#ffffff", 0.8),
        ]  # fmt: skip
    return out


def _tiered(f: Frame, fill: Fill) -> list[str]:
    """Two gathered seams across the skirt, with the gathers ticked under each."""
    out = []
    for s in (0.36, 0.68):
        left, right = f.on_side(s), f.on_side(s, right=True)
        seam: Curve = (left, (200, left[1] + 14 + 20 * s), right)
        ticks = " ".join(f"M{_pt(p)} l0,9" for p in (_bez(seam, k / 12) for k in range(1, 12)))
        out += [_line(f"M{_pt(left)} Q{_pt(seam[1])} {_pt(right)}", 2.2),
                _line(ticks, 1.1, ' stroke-opacity=".7"')]  # fmt: skip
    return out


def _pleated(f: Frame, fill: Fill) -> list[str]:
    d = " ".join(f"M{_pt(_bez(f.waist, k / 8))} L{_pt(_bez(f.hem, k / 8))}" for k in range(1, 8))
    return [_line(d, 1.3)]


def _seamed(f: Frame, fill: Fill) -> list[str]:
    """Princess seams from the bust to the hem, top-stitched beside each."""
    out = []
    for t in (0.3, 0.7):
        d = (
            f"M{_pt(f.bodice(t, 0.08))} L{_pt(_bez(f.waist, t + (0.03 if t < 0.5 else -0.03)))} "
            f"Q{_pt(f.skirt(t, 0.5))} {_pt(_bez(f.hem, t - (0.06 if t < 0.5 else -0.06)))}"
        )
        shift = f' stroke-dasharray="3 3" transform="translate({4 if t < 0.5 else -4} 0)"'
        out += [_line(d, 1.5), _line(d, 0.9, shift)]
    return out


def _smocked(f: Frame, fill: Fill) -> list[str]:
    """Rows of zigzag smocking stitch across the bodice."""
    rows = []
    for v in (0.3, 0.45, 0.6, 0.75):
        pts = [f.bodice(0.06 + 0.88 * k / 14, v) for k in range(15)]
        zig = (_pt((x, y + (3 if k % 2 else -3))) for k, (x, y) in enumerate(pts))
        rows.append("M" + " L".join(zig))
    return [_line(" ".join(rows), 1.2)]


def _ruched(f: Frame, fill: Fill) -> list[str]:
    """Gathers pulled in along both side seams, down the bodice and the top of the skirt."""
    d = []
    for v in (0.15, 0.4, 0.65, 0.9):
        for t0, t1 in ((0.02, 0.26), (0.98, 0.74)):
            a, c, b = f.bodice(t0, v), f.bodice((t0 + t1) / 2, v - 0.1), f.bodice(t1, v + 0.06)
            d.append(f"M{_pt(a)} Q{_pt(c)} {_pt(b)}")
    for v in (0.1, 0.24, 0.38):
        for t0, t1 in ((0.04, 0.24), (0.96, 0.76)):
            a, c, b = f.skirt(t0, v), f.skirt((t0 + t1) / 2, v - 0.05), f.skirt(t1, v + 0.03)
            d.append(f"M{_pt(a)} Q{_pt(c)} {_pt(b)}")
    return [_line(" ".join(d), 1.2)]


def _belted(f: Frame, fill: Fill) -> list[str]:
    tl, tr = f.bodice(0.0, 0.9), f.bodice(1.0, 0.9)
    bl, br = f.on_side(0.06), f.on_side(0.06, right=True)
    band = (
        f"M{_pt(tl)} Q200,{tl[1] + 12:.1f} {_pt(tr)} L{_pt(br)} Q200,{bl[1] + 12:.1f} {_pt(bl)} Z"
    )
    mid = (tl[1] + bl[1]) / 2 + 6
    return [
        _path(band, _shade(fill.base, 0.28), LW_DETAIL),
        f'<rect x="189" y="{mid - 11:.1f}" width="22" height="22" rx="3" fill="none" '
        f'stroke="{INK}" stroke-width="2"/>',
        _line(f"M200,{mid - 6:.1f} L200,{mid + 6:.1f}", 1.6),
    ]


def _button_front(f: Frame, fill: Fill) -> list[str]:
    top = _bez(f.top, 0.5)
    spots = [f.bodice(0.5, v) for v in (0.3, 0.6)] + [f.skirt(0.5, v) for v in (0.2, 0.45, 0.7)]
    return [
        _line(f"M{_pt(top)} L{_pt(_bez(f.hem, 0.5))}"),
        *(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="#ffffff" stroke="{INK}" '
          f'stroke-width="1.2"/>' for x, y in spots),
    ]  # fmt: skip


def _pinafore(f: Frame, fill: Fill, paint: str) -> list[str]:
    """Broad straps, a square bib with a button at each strap, and a patch pocket."""
    strap = "M158,114 L164,48 L184,48 L180,114 Z"
    px, py = f.skirt(0.5, 0.3)
    return [
        _path(strap, paint),
        _path("M242,114 L236,48 L216,48 L220,114 Z", paint),
        _line("M170,120 L230,120 L232,192 L168,192 Z"),
        *(f'<circle cx="{x}" cy="128" r="4" fill="#d6b56a" stroke="{INK}" stroke-width="1.2"/>'
          for x in (176, 224)),
        _path(f"M{px - 22:.1f},{py - 14:.1f} L{px + 22:.1f},{py - 14:.1f} L{px + 22:.1f},"
              f"{py + 12:.1f} Q{px:.1f},{py + 20:.1f} {px - 22:.1f},{py + 12:.1f} Z", paint,
              LW_DETAIL),
    ]  # fmt: skip


def _slashed_hem(f: Frame, fill: Fill) -> list[str]:
    """A slit cut up from the hem, the lining dark inside it."""
    a, b = _bez(f.hem, 0.63), _bez(f.hem, 0.69)
    top = f.skirt(0.655, 0.7)
    return [_path(f"M{_pt(a)} L{_pt(top)} L{_pt(b)} Z", _shade(fill.base, 0.45), LW_DETAIL)]


def _wrap(f: Frame, fill: Fill) -> list[str]:
    """The front panel crossing from the left shoulder to the right waist, the under panel's
    edge showing above it, the overlap running on down the skirt, and a tie at the left waist."""
    knot = _bez(f.waist, 0.06)
    tail = _shade(fill.base, 0.12)
    tails = (
        f"M{_pt(knot)} q-14,20 -10,48 M{_pt(knot)} q2,24 8,44 "
        f"M{_pt(knot)} q-16,-10 -18,2 q4,8 18,-2 M{_pt(knot)} q-8,14 -18,10 q0,-10 18,-10"
    )
    return [
        _line(f"M{_pt(_bez(f.top, 0.93))} L{_pt(f.bodice(0.62, 0.42))}", 1.6,
              ' stroke-opacity=".7"'),
        _line(f"M{_pt(_bez(f.top, 0.07))} Q{_pt(f.bodice(0.55, 0.35))} "
              f"{_pt(_bez(f.waist, 0.93))}", 2.4),
        _line(f"M{_pt(_bez(f.waist, 0.93))} Q{_pt(f.skirt(0.86, 0.5))} {_pt(_bez(f.hem, 0.74))}",
              2.0),
        _line(tails, 6),
        _line(tails, 3.4, stroke=tail),
        f'<circle cx="{knot[0]:.1f}" cy="{knot[1]:.1f}" r="5" fill="{tail}" stroke="{INK}" '
        f'stroke-width="1.6"/>',
    ]  # fmt: skip


#: Drawn over the fill, under the dress's own seams.
_PATTERNS = {"pinstripe": _pinstripe, "broderie": _broderie, "rose_print": _roses,
             "boat_print": _boats}  # fmt: skip
#: Drawn over everything, in this order.
_CONSTRUCTIONS = {"tiered": _tiered, "pleated": _pleated, "seamed": _seamed, "smocked": _smocked,
                  "ruched": _ruched, "slashed_hem": _slashed_hem, "wrap": _wrap,
                  "belted": _belted, "button_front": _button_front}  # fmt: skip


def draw(shape: str, features: str, paint: str, fill: Fill) -> tuple[list[str], list[str]]:
    """The marks of ``features`` on ``shape``: (those over the fill, those over the seams)."""
    wanted = set(features.split())
    unknown = wanted - DRAWN[shape]
    if unknown:
        raise ValueError(f"{shape} draws no {sorted(unknown)}")
    f = FRAMES[shape]
    under = [_g(k, fn(f, fill), fill) for k, fn in _PATTERNS.items() if k in wanted]
    over = [_g(k, fn(f, fill), fill) for k, fn in _CONSTRUCTIONS.items() if k in wanted]
    if "pinafore" in wanted:
        over.insert(0, _g("pinafore", _pinafore(f, fill, paint), fill))
    return under, over
