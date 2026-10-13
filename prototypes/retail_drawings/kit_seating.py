"""Living-room seating (gen#196): sofas by seat count and form, sofa beds, armchairs, footstools.

Each piece is drawn from in front and a little above, in a light oblique projection (a unit
of depth moves the drawing left by :data:`KX` and up by :data:`KY`), so a seat's top, its
front and its left side all show: a three-seater visibly has three seat cushions, a corner
sofa its return, a sofa bed its mattress. Upholstery takes the record's fill (color and
pattern); the legs take their finish.

==============  ===============================================  ===============================
shape           draws                                            params
==============  ===============================================  ===============================
sofa_seats      a straight sofa, one seat and back cushion       seats (2, 2.5, 3, 4), arms,
                per seat (2.5 draws two wide ones)               legs
corner_sofa     a sofa and its return, the return with its own   seats (main run), side (left,
                back and seats; ``u`` returns on both sides      right, u), arms, legs
chaise_sofa     a sofa whose end seat runs forward as a chaise,  seats, side (left, right),
                no back over the chaise                          arms, legs
modular_sofa    separate modules with a gap between each,        pieces, layout (straight,
                armless in the middle; an ottoman in front       corner), ottoman (yes, no)
recliner_sofa   a sofa of separate padded seats, each with its   seats, legs
                footrest raised in front
sofa_bed        a sofa and the bed it makes: a pulled-out or     mechanism (pull_out,
                folded-out mattress, or a click-clack laid flat  click_clack, fold_out), seats
armchair        one seat, by style: a slim accent chair, a       style (accent, wingback, tub,
                winged back, a tub, a swivel pedestal, a high    swivel, nursing, recliner),
                armless nursing chair, a recliner                legs
footstool       a padded stool on legs, buttoned on top; a       form (round, rectangular),
                storage stool shows its lid line                 storage (yes, no), legs
==============  ===============================================  ===============================

``arms`` is ``track`` (square), ``rolled`` (a rounded scroll) or ``slim`` (narrow and low).
``legs`` names a finish in :data:`LEG_FINISHES`. Every params value is a string, as a style
row's ``params`` carry it.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import dataclass

from kit import INK, LW, LW_DETAIL, Fill, _path, _shade, _tint, register

#: A unit of depth moves the drawing this far left (KX) and up (KY): the left side shows,
#: and the right side, which :func:`_box` does not draw, hides behind the front and top.
KX, KY = 0.34, 0.46

#: Leg finish -> its paint.
LEG_FINISHES = {
    "oak": "#c8a06a",
    "walnut": "#6b4a2e",
    "black_metal": "#2e2e33",
    "chrome": "#c9ccd1",
}
#: A mattress's ticking, and a metal bed frame.
TICKING = "#f3f0e8"
FRAME = "#55575e"

#: The sheet area a drawing is fitted into: (left, top, right, bottom).
FIT = (34.0, 78.0, 366.0, 336.0)


@dataclass(frozen=True)
class Box:
    """An axis-aligned block in drawing units: x across, y up, z back from the front."""

    x0: float
    x1: float
    y0: float
    y1: float
    z0: float
    z1: float
    paint: str  # "fill" (the upholstery), "accent", or a color
    rolled: bool = False  # a rolled arm's rounded top
    tufted: bool = False  # buttons on the top face
    front: float = 0.0  # a shadow over the front face (a base under its cushions)


class _Sheet:
    """The projection, fitted to :data:`FIT` over every box it will draw."""

    def __init__(self, boxes: list[Box]) -> None:
        pts = [self._raw(x, y, z) for b in boxes for x in (b.x0, b.x1) for y in (b.y0, b.y1) for z in (b.z0, b.z1)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        left, top, right, bottom = FIT
        self.s = min((right - left) / (max(xs) - min(xs)), (bottom - top) / (max(ys) - min(ys)))
        self.ox = (left + right) / 2 - self.s * (max(xs) + min(xs)) / 2
        self.oy = (top + bottom) / 2 - self.s * (max(ys) + min(ys)) / 2

    @staticmethod
    def _raw(x: float, y: float, z: float) -> tuple[float, float]:
        return x - KX * z, -y - KY * z

    def p(self, x: float, y: float, z: float) -> str:
        rx, ry = self._raw(x, y, z)
        return f"{self.ox + self.s * rx:.1f},{self.oy + self.s * ry:.1f}"

    def poly(self, *pts: tuple[float, float, float]) -> str:
        head, *rest = (self.p(*q) for q in pts)
        return f"M{head} " + " ".join(f"L{q}" for q in rest) + " Z"


def _color(box: Box, paint: str, fill: Fill) -> str:
    return {"fill": paint, "accent": fill.accent}.get(box.paint, box.paint)


def _box(sheet: _Sheet, b: Box, paint: str, fill: Fill) -> list[str]:
    """One block's left side, top and front, each outlined, the side and top shaded."""
    color = _color(b, paint, fill)
    width = LW if b.paint in ("fill", "accent") else LW_DETAIL
    x0, x1, y0, y1, z0, z1 = b.x0, b.x1, b.y0, b.y1, b.z0, b.z1
    r = (x1 - x0) / 2 if b.rolled else 0.0
    yt = y1 - r
    side = sheet.poly((x0, y0, z0), (x0, yt, z0), (x0, yt, z1), (x0, y0, z1))
    out = [_path(side, color, width), _shade_over(side, 0.22)]
    if b.rolled:
        rr = r * sheet.s
        f0, f1 = sheet.p(x0, yt, z0), sheet.p(x1, yt, z0)
        k0, k1 = sheet.p(x0, yt, z1), sheet.p(x1, yt, z1)
        top = f"M{f0} A{rr:.1f},{rr:.1f} 0 0 1 {f1} L{k1} A{rr:.1f},{rr:.1f} 0 0 0 {k0} Z"
        front = f"M{sheet.p(x0, y0, z0)} L{f0} A{rr:.1f},{rr:.1f} 0 0 1 {f1} L{sheet.p(x1, y0, z0)} Z"
        out += [_path(top, color, width), _lift(top, 0.14), _path(front, color, width)]
        out.append(_path(f"M{sheet.p(x0 + r * 0.45, yt, z0)} A{rr * 0.55:.1f},{rr * 0.55:.1f} 0 0 1 {sheet.p(x1 - r * 0.45, yt, z0)}", "none", LW_DETAIL))
        return out
    top = sheet.poly((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1))
    front = sheet.poly((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))
    out += [_path(top, color, width), _lift(top, 0.14), _path(front, color, width)]
    if b.front:
        out.append(_shade_over(front, b.front))
    if b.tufted:
        for i in (1, 2, 3):
            for j in (1, 2):
                x = x0 + (x1 - x0) * i / 4
                z = z0 + (z1 - z0) * j / 3
                cx, cy = sheet.p(x, y1, z).split(",")
                out.append(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{_shade(fill.base, 0.35)}" stroke="{INK}" stroke-width="0.8"/>')
    return out


def _shade_over(d: str, opacity: float) -> str:
    return f'<path d="{d}" fill="#000000" fill-opacity="{opacity:g}" stroke="none"/>'


def _lift(d: str, opacity: float) -> str:
    return f'<path d="{d}" fill="#ffffff" fill-opacity="{opacity:g}" stroke="none"/>'


def _outline(b: Box) -> list[tuple[float, float]]:
    """The block's silhouette on the sheet (unscaled): the convex hull of its eight corners."""
    pts = sorted({_Sheet._raw(x, y, z) for x in (b.x0, b.x1) for y in (b.y0, b.y1) for z in (b.z0, b.z1)})

    def half(seq: list[tuple[float, float]]) -> list[tuple[float, float]]:
        out: list[tuple[float, float]] = []
        for q in seq:
            while len(out) > 1 and (out[-1][0] - out[-2][0]) * (q[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(q)
        return out[:-1]

    return half(pts) + half(pts[::-1])


def _overlap(a: Box, b: Box) -> bool:
    """Whether the two silhouettes share area (touching edges do not count)."""
    pa, pb = _outline(a), _outline(b)
    for poly in (pa, pb):
        for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1], strict=True):
            nx, ny = y0 - y1, x1 - x0
            da, db = [nx * x + ny * y for x, y in pa], [nx * x + ny * y for x, y in pb]
            if max(da) <= min(db) + 1e-6 or max(db) <= min(da) + 1e-6:
                return False
    return True


def _before(a: Box, b: Box) -> bool | None:
    """Whether ``a`` draws before ``b``: the one below, behind or to the right goes first (the
    viewer is above, in front and to the left). None when neither hides the other: their
    silhouettes do not overlap, which keeps a far-apart pair from forcing an order that
    contradicts the pairs between them."""
    if not _overlap(a, b):
        return None
    if a.y1 <= b.y0 or b.y1 <= a.y0:
        return a.y1 <= b.y0
    if a.z1 <= b.z0 or b.z1 <= a.z0:
        return a.z0 >= b.z1
    if a.x1 <= b.x0 or b.x1 <= a.x0:
        return a.x0 >= b.x1
    return None


def _order(boxes: list[Box]) -> list[Box]:
    """``boxes`` in painter's order (:func:`_before`), the authored order breaking ties."""
    after = {i: {j for j, b in enumerate(boxes) if j != i and _before(a, b)} for i, a in enumerate(boxes)}
    waiting = {i: sum(i in after[j] for j in after) for i in after}
    out: list[Box] = []
    while waiting:
        ready = [i for i, n in waiting.items() if n == 0] or [min(waiting)]
        i = min(ready)
        out.append(boxes[i])
        del waiting[i]
        for j in after[i]:
            if j in waiting:
                waiting[j] -= 1
    return out


def _draw(boxes: list[Box], paint: str, fill: Fill, extra=None) -> list[str]:
    """Every box in painter's order (:func:`_order`), on one fitted sheet; ``extra`` adds marks
    after."""
    sheet = _Sheet(boxes)
    out = [part for b in _order(boxes) for part in _box(sheet, b, paint, fill)]
    if extra is not None:
        out += extra(sheet)
    return out


# --------------------------------------------------------------------------
# The parts of a sofa, in drawing units (about a centimetre each)
# --------------------------------------------------------------------------

DEPTH = 92.0  # a sofa's depth, front to back
SEAT = 60.0  # one seat's width
LEG, BASE, CUSHION, BACK = 12.0, 30.0, 46.0, 84.0  # heights: leg top, base top, seat top, back top

#: arm style -> (width, height)
ARMS = {"track": (20.0, 62.0), "rolled": (24.0, 66.0), "slim": (9.0, 58.0)}


def _legs(x0: float, x1: float, z0: float, z1: float, finish: str) -> list[Box]:
    """The two front legs under a footprint (the back two hide behind it): blocks in wood,
    slim ones in metal."""
    color = LEG_FINISHES[finish]
    w = 7.0 if finish in ("oak", "walnut") else 4.0
    return [Box(x, x + w, 0.0, LEG, z0 + 3, z0 + 3 + w, color) for x in (x1 - w - 4, x0 + 4)]


def _cushions(x0: float, x1: float, n: int, y0: float, y1: float, z0: float, z1: float, paint: str = "fill") -> list[Box]:
    """``n`` cushions across ``x0..x1``, right to left (the drawing order), a small gap apart."""
    w = (x1 - x0) / n
    return [Box(x0 + i * w + 1, x0 + (i + 1) * w - 1, y0, y1, z0, z1, paint) for i in reversed(range(n))]


def _run(x0: float, x1: float, n: int, z0: float = 0.0, back: bool = True) -> list[Box]:
    """A seating run from ``x0`` to ``x1``: back frame and cushions, base, ``n`` seat cushions."""
    out: list[Box] = []
    if back:
        out.append(Box(x0, x1, BASE, BACK - 6, DEPTH - 14 + z0, DEPTH + z0, "fill"))
        out += _cushions(x0, x1, n, CUSHION - 2, BACK, DEPTH - 32 + z0, DEPTH - 14 + z0)
    out.append(Box(x0, x1, LEG, BASE, z0, (DEPTH if back else DEPTH - 14) + z0, "fill"))
    out += _cushions(x0, x1, n, BASE, CUSHION, z0, DEPTH - 32 + z0 + (0 if back else 18))
    return out


def _seats(seats: str) -> tuple[int, float]:
    """``seats`` -> (cushions drawn, run width): 2.5 seats are two wide cushions."""
    n = float(seats)
    return max(1, int(n)), SEAT * n


def _arm(x0: float, style: str, z0: float = 0.0, z1: float = DEPTH) -> Box:
    w, h = ARMS[style]
    return Box(x0, x0 + w, LEG, h, z0, z1, "fill", rolled=style == "rolled")


def _straight(seats: str, arms: str, legs: str) -> list[Box]:
    n, width = _seats(seats)
    aw = ARMS[arms][0]
    return [
        *_legs(-aw, width + aw, 0.0, DEPTH, legs),
        *_run(0.0, width, n)[: 1 + n],
        Box(0.0, width, LEG, BASE, 0.0, DEPTH, "fill", front=0.14),
        _arm(width, arms),
        *_cushions(0.0, width, n, BASE, CUSHION, 0.0, DEPTH - 32),
        _arm(-aw, arms),
    ]


def _mirrored(boxes: list[Box]) -> list[Box]:
    """The drawing flipped left to right (the painter's order is recomputed when drawn)."""
    return [Box(-b.x1, -b.x0, b.y0, b.y1, b.z0, b.z1, b.paint, b.rolled, b.tufted, b.front) for b in boxes]


def sofa_seats(paint: str, fill: Fill, label: str | None, seats: str = "3", arms: str = "track", legs: str = "walnut") -> list[str]:
    """A straight sofa: one seat cushion and one back cushion per seat, its arms and legs."""
    return _draw(_straight(seats, arms, legs), paint, fill)


def corner_sofa(paint: str, fill: Fill, label: str | None, seats: str = "3", side: str = "left", arms: str = "track", legs: str = "black_metal") -> list[str]:
    """A main run of ``seats`` and a two-seat return coming forward on ``side`` (both for ``u``).

    The return has its own back along its outer edge and its own seat cushions; the corner seat
    joins the two, and an arm closes any end with no return.
    """
    n, width = _seats(seats)
    aw = ARMS[arms][0]
    d, ret = DEPTH, 2 * SEAT
    left = side in ("left", "right", "u")  # a right-hand sofa is the left-hand one flipped
    right = side == "u"
    x0 = -d if left else -aw
    x1 = width + d if right else width + aw
    boxes = [
        *_legs(x0, 0.0, -ret, d, legs)[1:],
        *(_legs(width, x1, -ret, d, legs)[:1] if right else _legs(0.0, x1, 0.0, d, legs)[:1]),
        Box(x0, x1, BASE, BACK - 6, d - 14, d, "fill"),
        *_cushions(x0 + 32 if left else 0.0, x1 - 32 if right else width, n + left + right, CUSHION - 2, BACK, d - 32, d - 14),
        Box(x0 if left else 0.0, x1 if right else width, LEG, BASE, 0.0, d - 14, "fill", front=0.14),
        *_cushions(x0 + 32 if left else 0.0, x1 - 32 if right else width, n + left + right, BASE, CUSHION, 0.0, d - 32),
    ]
    if not right:
        boxes.append(_arm(width, arms))
    for flip in (False, True)[: 1 + right]:
        # the return: a back along its outer edge, two seats facing in, from z=-ret to the run
        ret_boxes = [
            Box(-d, -d + 14, BASE, BACK - 6, -ret, d - 14, "fill"),
            *[Box(-d + 14, -d + 32, BASE, BACK, z, z + SEAT - 2, "fill") for z in (1.0, -SEAT + 1)],
            Box(-d, 0.0, LEG, BASE, -ret, 0.0, "fill", front=0.14),
            *[Box(-d + 32, -1.0, BASE, CUSHION, z, z + SEAT - 2, "fill") for z in (-SEAT + 1, -ret + 1)],
        ]
        if flip:
            ret_boxes = [Box(width - b.x1, width - b.x0, b.y0, b.y1, b.z0, b.z1, b.paint, front=b.front) for b in ret_boxes]
        boxes += ret_boxes
    if side == "right":
        boxes = _mirrored(boxes)
    return _draw(boxes, paint, fill)


def chaise_sofa(paint: str, fill: Fill, label: str | None, seats: str = "3", side: str = "left", arms: str = "track", legs: str = "oak") -> list[str]:
    """A straight sofa whose end seat on ``side`` runs forward as a chaise, with no back over it."""
    n, width = _seats(seats)
    aw = ARMS[arms][0]
    reach = 70.0  # how far the chaise comes forward of the seats
    boxes = [
        *_legs(-aw, SEAT, -reach, DEPTH, legs)[1:],
        *_legs(SEAT, width + aw, 0.0, DEPTH, legs)[:1],
        Box(0.0, width, BASE, BACK - 6, DEPTH - 14, DEPTH, "fill"),
        *_cushions(0.0, width, n, CUSHION - 2, BACK, DEPTH - 32, DEPTH - 14),
        Box(SEAT, width, LEG, BASE, 0.0, DEPTH, "fill", front=0.14),
        _arm(width, arms),
        *_cushions(SEAT, width, n - 1, BASE, CUSHION, 0.0, DEPTH - 32),
        Box(0.0, SEAT, LEG, BASE, -reach, DEPTH, "fill", front=0.14),
        Box(1.0, SEAT - 1, BASE, CUSHION, -reach, DEPTH - 32, "fill"),
        _arm(-aw, arms, -reach, DEPTH),
    ]
    if side == "right":
        boxes = _mirrored(boxes)
    return _draw(boxes, paint, fill)


def modular_sofa(paint: str, fill: Fill, label: str | None, pieces: str = "4", layout: str = "straight", ottoman: str = "no", legs: str = "black_metal") -> list[str]:
    """``pieces`` modules: a gap between each, arms only on the end modules, armless ones between.

    ``layout`` ``corner`` turns the left end module into a corner (a back on two sides) with a
    module in front of it; ``ottoman`` ``yes`` counts a loose ottoman among the pieces, drawn in
    front of the seats.
    """
    total = int(pieces)
    seats = total - (1 if ottoman == "yes" else 0)
    forward = 1 if layout == "corner" else 0
    across = seats - forward
    gap, aw = 4.0, 16.0
    mods: list[Box] = []
    xs = [i * (SEAT + gap) for i in range(across)]
    for i in reversed(range(across)):
        x0 = xs[i]
        x1 = x0 + SEAT
        end_r, end_l = i == across - 1, i == 0
        lo, hi = x0 + (aw if end_l and not forward else 0), x1 - (aw if end_r else 0)
        mods += [
            *_legs(x0, x1, 0.0, DEPTH, legs),
            Box(x0, x1, BASE, BACK - 6, DEPTH - 14, DEPTH, "fill"),
            Box(lo + 1, hi - 1, CUSHION - 2, BACK, DEPTH - 32, DEPTH - 14, "fill"),
            Box(x0, x1, LEG, BASE, 0.0, DEPTH, "fill", front=0.14),
        ]
        if end_r:
            mods.append(Box(x1 - aw, x1, LEG, ARMS["track"][1], 0.0, DEPTH, "fill"))
        mods.append(Box(lo + 1, hi - 1, BASE, CUSHION, 0.0, DEPTH - 32, "fill"))
        if end_l and not forward:
            mods.append(Box(x0, x0 + aw, LEG, ARMS["track"][1], 0.0, DEPTH, "fill"))
    if forward:
        # the corner: a back along the left side of the first module, a module in front of it
        x0 = xs[0]
        z0 = -(SEAT + gap)
        mods = [Box(x0, x0 + 14, BASE, BACK - 6, 0.0, DEPTH, "fill"), *mods]
        mods += [
            *_legs(x0, x0 + DEPTH, z0, z0 + SEAT, legs),
            Box(x0, x0 + 14, BASE, BACK - 6, z0, z0 + SEAT, "fill"),
            Box(x0 + 14, x0 + 32, BASE, BACK, z0 + 1, z0 + SEAT - 1, "fill"),
            Box(x0, x0 + DEPTH, LEG, BASE, z0, z0 + SEAT, "fill", front=0.14),
            Box(x0 + 32, x0 + DEPTH - 1, BASE, CUSHION, z0 + 1, z0 + SEAT - 1, "fill"),
        ]
    if ottoman == "yes":
        mid = xs[-1] - SEAT * 0.3 if forward else (xs[0] + xs[-1] + SEAT) / 2 - SEAT / 2
        z = -SEAT - 30 if not forward else -SEAT * 0.9
        mods += [*_legs(mid, mid + SEAT, z, z + SEAT * 0.8, legs), Box(mid, mid + SEAT, LEG, CUSHION - 4, z, z + SEAT * 0.8, "fill", tufted=True)]
    return _draw(mods, paint, fill)


def recliner_sofa(paint: str, fill: Fill, label: str | None, seats: str = "3", legs: str = "black_metal") -> list[str]:
    """Separate padded seats, a pillow back on each, every footrest raised in front of its seat."""
    n, width = _seats(seats)
    aw = 26.0
    boxes = [
        *_legs(-aw, width + aw, 0.0, DEPTH, legs),
        Box(0.0, width, BASE, BACK - 2, DEPTH - 14, DEPTH, "fill"),
        *_cushions(0.0, width, n, CUSHION - 2, BACK + 4, DEPTH - 34, DEPTH - 14),
        Box(0.0, width, LEG, BASE, 0.0, DEPTH, "fill", front=0.14),
        Box(width, width + aw, LEG, 60.0, 0.0, DEPTH, "fill"),
        *_cushions(0.0, width, n, BASE, CUSHION + 2, 0.0, DEPTH - 34),
        Box(-aw, 0.0, LEG, 60.0, 0.0, DEPTH, "fill"),
    ]
    w = width / n
    for i in reversed(range(n)):
        x0 = i * w + 6
        boxes.append(Box(x0, x0 + w - 12, 22.0, 34.0, -46.0, -4.0, "fill"))

    def struts(sheet: _Sheet) -> list[str]:
        out = []
        for i in range(n):
            x = i * w + w / 2
            out.append(_path(f"M{sheet.p(x - 10, 22.0, -30.0)} L{sheet.p(x - 4, LEG + 2, -2.0)} M{sheet.p(x + 10, 22.0, -30.0)} L{sheet.p(x + 4, LEG + 2, -2.0)}", "none", LW_DETAIL, stroke=FRAME))
        return out

    return _draw(boxes, paint, fill, struts)


def sofa_bed(paint: str, fill: Fill, label: str | None, mechanism: str = "pull_out", seats: str = "3") -> list[str]:
    """The bed a sofa bed makes: its mattress pulled or folded out in front, or a click-clack laid flat.

    ``pull_out`` slides one deep mattress out on a low base; ``fold_out`` unfolds a thinner
    three-part mattress on a metal frame (two fold seams across it); ``click_clack`` has no arms,
    its back lowered flat beside the seat into one sleeping surface with a hinge line.
    """
    n, width = _seats(seats)
    if mechanism == "click_clack":
        boxes = [
            *_legs(0.0, width, 0.0, DEPTH * 2, "black_metal"),
            Box(0.0, width, LEG, LEG + 8, 0.0, DEPTH * 2, FRAME),
            Box(1.0, width - 1, LEG + 8, LEG + 26, DEPTH, DEPTH * 2, "fill"),
            Box(1.0, width - 1, LEG + 8, LEG + 26, 0.0, DEPTH - 2, "fill"),
        ]

        def hinge(sheet: _Sheet) -> list[str]:
            return [_path(f"M{sheet.p(1.0, LEG + 26, DEPTH - 1)} L{sheet.p(width - 1, LEG + 26, DEPTH - 1)}", "none", 2.2)]

        return _draw(boxes, paint, fill, hinge)
    aw = ARMS["track"][0]
    reach = 150.0 if mechanism == "fold_out" else 120.0
    boxes = [
        *_legs(-aw, width + aw, 0.0, DEPTH, "walnut"),
        Box(0.0, width, BASE, BACK - 6, DEPTH - 14, DEPTH, "fill"),
        *_cushions(0.0, width, n, CUSHION - 2, BACK, DEPTH - 32, DEPTH - 14),
        Box(0.0, width, LEG, BASE, 0.0, DEPTH, "fill", front=0.14),
        _arm(width, "track"),
    ]
    if mechanism == "fold_out":
        thick = 8.0
        boxes += [Box(4.0, width - 4, 30.0, 30.0 + thick, -reach, DEPTH - 32, TICKING)]
        boxes += [Box(x, x + 3, 0.0, 30.0, z, z + 3, FRAME) for z in (-reach + 4, -reach / 2) for x in (width - 10, 8.0)]
        seams = (-reach / 3, -reach * 2 / 3 + 20)
    else:
        boxes += [Box(4.0, width - 4, LEG, LEG + 8, -reach, 0.0, "fill")]
        boxes += [Box(6.0, width - 6, LEG + 8, LEG + 24, -reach + 2, -2.0, TICKING)]
        seams = ()
    boxes.append(_arm(-aw, "track"))

    def quilt(sheet: _Sheet) -> list[str]:
        y = 30.0 + 8.0 if mechanism == "fold_out" else LEG + 24
        out = [_path(f"M{sheet.p(4.0, y, z)} L{sheet.p(width - 4, y, z)}", "none", 2.2) for z in seams]
        for x in (width * 0.25, width * 0.5, width * 0.75):
            out.append(_path(f"M{sheet.p(x, y, -reach + 10)} L{sheet.p(x, y, -12.0)}", "none", 0.9, ' stroke-dasharray="4 4" stroke-opacity=".5"'))
        return out

    return _draw(boxes, paint, fill, quilt)


def armchair(paint: str, fill: Fill, label: str | None, style: str = "accent", legs: str = "oak") -> list[str]:
    """One seat in its style's silhouette.

    ``accent``: slim low arms on tall legs. ``wingback``: a tall back with wings above rolled
    arms. ``tub``: arms as high as the back, wrapping it, on short legs. ``swivel``: a tub on
    a round pedestal. ``nursing``: a high armless back. ``recliner``: chunky arms, its footrest
    raised.
    """
    w, d = SEAT + 8, DEPTH - 6
    leg_h = {"accent": 22.0, "nursing": 18.0, "swivel": 28.0}.get(style, LEG)
    lift = leg_h - LEG
    arm_h = {"accent": 56.0, "wingback": 64.0, "tub": 76.0, "swivel": 76.0, "nursing": 0.0, "recliner": 62.0}[style]
    back_h = {"wingback": 112.0, "nursing": 108.0, "tub": 80.0, "swivel": 80.0}.get(style, 92.0) + lift
    aw = {"accent": 9.0, "recliner": 26.0, "tub": 14.0, "swivel": 14.0}.get(style, 22.0)
    boxes: list[Box] = []
    if style == "swivel":
        boxes.append(Box(w / 2 - 5, w / 2 + 5, 2.0, leg_h, d / 2 - 5, d / 2 + 5, LEG_FINISHES["chrome"]))
    else:
        reach = aw if arm_h else 0.0  # an armless chair stands on legs under its seat
        boxes += [Box(b.x0, b.x1, 0.0, leg_h, b.z0, b.z1, b.paint) for b in _legs(-reach, w + reach, 0.0, d, legs)]
    boxes += [
        Box(0.0, w, BASE + lift, back_h - 6, d - 14, d, "fill"),
        Box(1.0, w - 1, CUSHION + lift - 2, back_h, d - 30, d - 14, "fill"),
    ]
    if style == "wingback":
        boxes += [Box(w - 10, w, 60.0 + lift, back_h - 4, d - 40, d - 10, "fill")]
    boxes += [Box(0.0, w, leg_h, BASE + lift, 0.0, d, "fill", front=0.14)]
    if arm_h:
        boxes.append(Box(w, w + aw, leg_h, arm_h + lift, 0.0, d, "fill", rolled=style in ("wingback", "tub", "swivel")))
    boxes.append(Box(1.0, w - 1, BASE + lift, CUSHION + lift, 0.0, d - 30, "fill"))
    if style == "wingback":
        boxes.append(Box(0.0, 10.0, 60.0 + lift, back_h - 4, d - 40, d - 10, "fill"))
    if arm_h:
        boxes.append(Box(-aw, 0.0, leg_h, arm_h + lift, 0.0, d, "fill", rolled=style in ("wingback", "tub", "swivel")))
    if style == "recliner":
        boxes.append(Box(6.0, w - 6, 22.0, 34.0, -46.0, -4.0, "fill"))

    def base(sheet: _Sheet) -> list[str]:
        if style != "swivel":
            return []
        cx, cy = (float(v) for v in sheet.p(w / 2, 0.0, d / 2).split(","))
        rx = 40 * sheet.s
        steel = LEG_FINISHES["chrome"]
        return [f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{rx * 0.32:.1f}" fill="{steel}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>']

    out = _draw(boxes, paint, fill, None)
    if style == "swivel":
        sheet = _Sheet(boxes)
        out = base(sheet) + out
    return out


def footstool(paint: str, fill: Fill, label: str | None, form: str = "rectangular", storage: str = "no", legs: str = "oak") -> list[str]:
    """A padded footstool, buttoned on top: a box on four legs, or a drum; a storage stool's lid shows."""
    if form == "round":
        cx, top, bottom, rx, ry = 200.0, 176.0, 286.0, 112.0, 40.0
        body = f"M{cx - rx:g},{top:g} L{cx - rx:g},{bottom:g} A{rx:g},{ry:g} 0 0 0 {cx + rx:g},{bottom:g} L{cx + rx:g},{top:g} Z"
        leg = LEG_FINISHES[legs]
        out = [
            *[f'<path d="M{x - 6:g},{bottom + ry - 12:g} L{x + 6:g},{bottom + ry - 12:g} L{x + 4:g},{bottom + ry + 18:g} L{x - 4:g},{bottom + ry + 18:g} Z" fill="{leg}" stroke="{INK}" stroke-width="{LW_DETAIL}" stroke-linejoin="round"/>' for x in (cx - rx * 0.62, cx + rx * 0.62)],
            _path(body, paint),
            _shade_over(f"M{cx - rx:g},{bottom - 30:g} L{cx - rx:g},{bottom:g} A{rx:g},{ry:g} 0 0 0 {cx + rx:g},{bottom:g} L{cx + rx:g},{bottom - 30:g} A{rx:g},{ry:g} 0 0 1 {cx - rx:g},{bottom - 30:g} Z", 0.12),
            f'<ellipse cx="{cx:g}" cy="{top:g}" rx="{rx:g}" ry="{ry:g}" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
            _lift(f"M{cx - rx:g},{top:g} A{rx:g},{ry:g} 0 0 1 {cx + rx:g},{top:g} A{rx:g},{ry:g} 0 0 1 {cx - rx:g},{top:g} Z", 0.14),
            *[f'<circle cx="{cx + dx:g}" cy="{top + dy:g}" r="3" fill="{_shade(fill.base, 0.35)}" stroke="{INK}" stroke-width="0.8"/>' for dx, dy in ((0, 0), (-50, -10), (50, -10), (-50, 10), (50, 10), (0, -22), (0, 22))],
        ]
        if storage == "yes":
            lid = top + 26
            out.append(_path(f"M{cx - rx:g},{lid:g} A{rx:g},{ry:g} 0 0 0 {cx + rx:g},{lid:g}", "none", 3.2))
            out.append(_path(f"M{cx - 18:g},{lid + ry + 4:g} L{cx + 18:g},{lid + ry + 4:g}", "none", 4.0))
        return out
    w, d, h = 100.0, 60.0, 32.0
    boxes = [*_legs(0.0, w, 0.0, d, legs), Box(0.0, w, LEG, LEG + h, 0.0, d, "fill", tufted=True)]

    def lid(sheet: _Sheet) -> list[str]:
        if storage != "yes":
            return []
        y = LEG + h - 9
        return [_path(f"M{sheet.p(0.0, y, 0.0)} L{sheet.p(w, y, 0.0)} M{sheet.p(0.0, y, 0.0)} L{sheet.p(0.0, y, d)}", "none", 3.2),
                _path(f"M{sheet.p(w * 0.4, y - 4, 0.0)} L{sheet.p(w * 0.6, y - 4, 0.0)}", "none", 4.0)]

    return _draw(boxes, paint, fill, lid)


SHAPES = {
    "sofa_seats": sofa_seats, "corner_sofa": corner_sofa, "chaise_sofa": chaise_sofa,
    "modular_sofa": modular_sofa, "recliner_sofa": recliner_sofa, "sofa_bed": sofa_bed,
    "armchair": armchair, "footstool": footstool,
}  # fmt: skip

register(SHAPES)

__all__ = ["LEG_FINISHES", "SHAPES", "_tint"]
