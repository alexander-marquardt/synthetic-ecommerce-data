"""Own-kind shapes for the bath and kitchen types the kit could not draw (gen#1022, slice 4).

Floor and wall tile, bathroom vanities, cabinet and drawer pulls, bathroom sink faucets,
bathroom storage and kitchen canisters, each a flat front drawing in the kit's house style with
the record's fill on the product itself, drawn from the attributes a record states, as slices 1
and 2's shapes (:mod:`kit_home_furniture`, :mod:`kit_storage_furniture`) are: the variant axis
that changes how the piece looks is a param, and the drawn count of sinks, doors, drawers,
handles, shelves and canisters is the stated count.

============  ==============================================  ==================================
shape         draws                                           params
============  ==============================================  ==================================
tile          a panel of tiles in their grout: square,        form, pattern, surface, grout
              subway (brick bond) or hexagon, plain, veined
              or with a motif, matte or with a gloss sheen
vanity        a bathroom vanity: vessel basins on a           sinks, doors, drawers, mount
              worktop, drawers over doors (neither: an open
              shelf of towels), on legs or hung on the wall
cabinet_pull  one pull on a cabinet door: a bar, a cup, a     style, size, backplate
              knob, a ring or an edge lip, with or without
              a backplate
sink_faucet   a basin tap on a worktop or on the wall: an     handles, spout, mount
              arc, straight or waterfall spout, a single
              lever or two handles
bath_storage  a bathroom unit: a tower, an over-the-toilet    form, shelves, cabinet
              unit or a wall unit, its open shelves of
              towels and bottles, a door or a mirror door
canister      a row of kitchen canisters, tallest first:      count, body, lid
              glazed, glass (its contents show) or metal,
              with a flat, domed or wooden lid
============  ==============================================  ==================================

:data:`PARAMS` is each shape's table of params and the values it draws; any other value is refused
with a ``ValueError`` naming the param. A White piece reads white (gen#226): what stands on a
shelf (towels, bottles, a canister's contents) is drawn in the kit's book colors and the metal
parts in its metal, and what the product is drawn against (a worktop, a door, a toilet, grout)
stays light.

``drawings.render`` (:mod:`synthetic_ecommerce_data.drawings`) is the public call that draws
these shapes in a finish; no generator product uses them yet.
"""

# ruff: noqa: E501 -- param tables and SVG path literals read better whole than wrapped.

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import (
    LW,
    LW_DETAIL,
    Fill,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_furniture import (
    BOOKS,
    GLASS,
    METAL,
    _drawer_fronts,
    _grain,
    _knob,
    _legs,
    _rect,
)
from synthetic_ecommerce_data.domains.retail.kit_home_furniture import FLOOR, _group, _slab
from synthetic_ecommerce_data.domains.retail.kit_storage_furniture import _bottle, _doors

#: Each shape's params and the values it draws, in the order a picker would list them.
PARAMS: dict[str, dict[str, tuple[str, ...]]] = {
    "tile": {"form": ("square", "subway", "hexagon"), "pattern": ("plain", "veined", "motif"), "surface": ("matte", "gloss"), "grout": ("light", "dark")},
    "vanity": {"sinks": ("1", "2"), "doors": ("0", "1", "2", "3", "4"), "drawers": ("0", "1", "2", "3"), "mount": ("floor", "wall")},
    "cabinet_pull": {"style": ("bar", "cup", "knob", "ring", "edge"), "size": ("small", "medium", "large"), "backplate": ("no", "yes")},
    "sink_faucet": {"handles": ("1", "2"), "spout": ("arc", "straight", "waterfall"), "mount": ("deck", "wall")},
    "bath_storage": {"form": ("tower", "over_toilet", "wall"), "shelves": ("2", "3", "4"), "cabinet": ("none", "door", "mirror")},
    "canister": {"count": ("1", "2", "3", "4"), "body": ("ceramic", "glass", "metal"), "lid": ("flat", "dome", "wood")},
}  # fmt: skip

#: What a product is drawn against, kept light so a White piece still reads white.
COUNTER = "#ece9e4"
PORCELAIN = "#f6f5f1"
DOOR = "#ebe6dc"
GROUT = {"light": "#e3dfd6", "dark": "#5b5750"}
WOOD_LID = "#c8a06a"
WHITE = "#ffffff"


def _valid(kind: str, /, **given: str) -> None:
    """Refuse a value the shape does not draw, naming the param."""
    for key, value in given.items():
        if value not in PARAMS[kind][key]:
            raise ValueError(f"unknown {kind} {key} {value!r}; one of {PARAMS[kind][key]}")


def _cls(element: str, cls: str) -> str:
    """``element`` (one ``<path>`` or ``<rect>``) with ``class="cls"``."""
    tag = element.split(" ", 1)[0]
    return element.replace(tag, f'{tag} class="{cls}"', 1)


def _box(x: float, y: float, w: float, h: float) -> str:
    return f"M{x:.1f},{y:.1f} L{x + w:.1f},{y:.1f} L{x + w:.1f},{y + h:.1f} L{x:.1f},{y + h:.1f} Z"


def _sheen(x: float, y: float, length: float, width: float = 2.5, cls: str = "sheen") -> str:
    """A short white highlight stroke: a glazed or polished surface."""
    return _line(f"M{x:.1f},{y:.1f} L{x + length:.1f},{y:.1f}", width, f' class="{cls}" stroke-opacity=".8"', WHITE)


def _tiles(form: str, x0: float, y0: float, s: float) -> list[tuple[str, float, float, float, float]]:
    """``(path, x, y, w, h)`` of each tile laid in the ``s``-square panel at (x0, y0)."""
    gap = 4
    out = []
    if form == "square":
        t = s / 4
        for r in range(4):
            for c in range(4):
                x, y = x0 + c * t + gap / 2, y0 + r * t + gap / 2
                out.append((_box(x, y, t - gap, t - gap), x, y, t - gap, t - gap))
    elif form == "subway":  # brick bond: every other row starts half a tile across
        tw, th = s / 4, s / 8
        for r in range(8):
            x = -tw / 2 if r % 2 else 0.0
            while x < s:
                a, b = max(0.0, x), min(s, x + tw)
                if b - a > gap:
                    bx, by = x0 + a + gap / 2, y0 + r * th + gap / 2
                    out.append((_box(bx, by, b - a - gap, th - gap), bx, by, b - a - gap, th - gap))
                x += tw
    else:  # hexagon, pointy side up, in a honeycomb
        r = 26.0
        dx, dy = math.sqrt(3) * r, 1.5 * r
        row, cy = 0, y0 + r
        while cy + r <= y0 + s:
            cx = x0 + dx / 2 + (dx / 2 if row % 2 else 0)
            while cx + dx / 2 <= x0 + s:
                pts = [(cx + (r - 2) * math.cos(math.radians(30 + 60 * k)), cy + (r - 2) * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
                d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts) + " Z"
                out.append((d, cx - dx / 2 + 2, cy - r + 2, dx - 4, 2 * r - 4))
                cx += dx
            row, cy = row + 1, cy + dy
    return out


def tile(paint: str, fill: Fill, label: str | None, form: str = "square", pattern: str = "plain", surface: str = "matte", grout: str = "light") -> list[str]:
    """A panel of tiles (each ``class="tile"``) set in ``grout``, its ``form`` ``square``, ``subway`` in a
    brick bond, or ``hexagon``; ``veined`` tiles carry a marble vein and ``motif`` ones a printed
    diamond; a ``gloss`` tile catches a highlight (``class="gloss"``, one a tile)."""
    _valid("tile", form=form, pattern=pattern, surface=surface, grout=grout)
    x0, y0, s = 64, 64, 272
    out = [_rect(x0, y0, s, s, GROUT[grout], LW)]
    for d, x, y, w, h in _tiles(form, x0, y0, s):
        out.append(_cls(_path(d, paint, LW_DETAIL), "tile"))
        cx, cy = x + w / 2, y + h / 2
        if pattern == "veined":
            out.append(_line(f"M{x + w * 0.1:.1f},{y + h * 0.3:.1f} Q{cx:.1f},{cy + h * 0.3:.1f} {x + w * 0.9:.1f},{y + h * 0.55:.1f}", 1.2, ' class="vein"', _shade(fill.base, 0.35)))
        elif pattern == "motif":
            out.append(_path(f"M{cx:.1f},{cy - h * 0.3:.1f} L{cx + w * 0.3:.1f},{cy:.1f} L{cx:.1f},{cy + h * 0.3:.1f} L{cx - w * 0.3:.1f},{cy:.1f} Z", _shade(fill.base, 0.18), 1.0))
        if surface == "gloss":
            out.append(_sheen(x + w * 0.18, y + h * 0.25, w * 0.3, cls="gloss"))
    return out


def vanity(paint: str, fill: Fill, label: str | None, sinks: str = "1", doors: str = "2", drawers: str = "0", mount: str = "floor") -> list[str]:
    """A bathroom vanity: exactly ``sinks`` vessel basins (``class="basin"``), a tap behind each,
    on a worktop; exactly ``drawers`` drawer fronts over exactly ``doors`` door fronts; with no
    door the lower part is an open shelf of rolled towels (``class="open_shelf"``). On legs
    (``floor``) or hung higher on the wall."""
    _valid("vanity", sinks=sinks, doors=doors, drawers=drawers, mount=mount)
    ns, nd, nr = int(sinks), int(doors), int(drawers)
    x0, w = 56, 288
    y0, y1 = (176, FLOOR - 26) if mount == "floor" else (136, FLOOR - 96)
    out = [_rect(x0, y0, w, y1 - y0, paint), _grain(x0, y0, w, y1 - y0, fill.base), _slab(x0 - 10, y0 - 14, w + 20, 14, COUNTER)]
    deck = y0 - 14
    for i in range(ns):
        cx = x0 + w * (i + 0.5) / ns
        top = deck - 34
        out += [_rect(cx - 5, top - 30, 10, 30 + 34, METAL, 1.0), _line(f"M{cx:.1f},{top - 30:.1f} Q{cx + 28:.1f},{top - 36:.1f} {cx + 28:.1f},{top - 12:.1f}", 6, stroke=METAL)]
        out.append(_cls(_path(f"M{cx - 46:.1f},{top:.1f} L{cx + 46:.1f},{top:.1f} Q{cx + 42:.1f},{deck:.1f} {cx:.1f},{deck:.1f} Q{cx - 42:.1f},{deck:.1f} {cx - 46:.1f},{top:.1f} Z", PORCELAIN), "basin"))
    band = 44 if nr else 0
    if nr:
        out += _drawer_fronts(x0 + 4, y0 + 4, w - 8, band, nr, paint, cols=nr)
    lo = y0 + 4 + band
    if nd:
        out += _doors(x0 + 4, lo, w - 8, y1 - lo - 4, nd, paint)
    else:
        out.append(_rect(x0 + 8, lo + 4, w - 16, y1 - lo - 12, _shade(fill.base, 0.12), LW_DETAIL, cls="open_shelf"))
        r = min(16.0, (y1 - lo - 16) / 2.4)
        for k, cx in enumerate(range(x0 + 34, x0 + w - 20, 40)):
            out.append(f'<circle cx="{cx}" cy="{y1 - 8 - r:.1f}" r="{r:.1f}" fill="{BOOKS[k % len(BOOKS)]}" stroke="#2b3440" stroke-width="1"/>')
    if mount == "floor":
        out += _legs([x0 + 16, x0 + w - 16], y1, FLOOR, paint, 14)
    return out


def _pull(style: str, span: float, k: float, cy: float, paint: str, base: str) -> list[str]:
    """The pull itself, centered on (200, ``cy``)."""
    a, b = 200 - span / 2, 200 + span / 2
    screws = [f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="3" fill="{_shade(base, 0.45)}" stroke="none"/>' for x in (a + 12, b - 12)]
    if style == "bar":
        return [_rect(a + 4, cy + 6, span, 12, _shade(DOOR, 0.15), 0, rx=6), _rect(a, cy - 7, span, 14, paint, LW_DETAIL, rx=7), *(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="9" fill="{paint}" stroke="#2b3440" stroke-width="1.6"/>' for x in (a + 12, b - 12)), *screws, _sheen(a + 20, cy - 3, span - 40)]
    if style == "cup":
        return [_rect(a + 4, cy, span, 14, _shade(DOOR, 0.15), 0, rx=4), _path(f"M{a:.1f},{cy - 12:.1f} L{b:.1f},{cy - 12:.1f} L{b:.1f},{cy + 2:.1f} Q200,{cy + 30 + 26 * k:.1f} {a:.1f},{cy + 2:.1f} Z", paint, LW_DETAIL), _path(f"M{a + 14:.1f},{cy + 2:.1f} L{b - 14:.1f},{cy + 2:.1f} Q200,{cy + 22 + 20 * k:.1f} {a + 14:.1f},{cy + 2:.1f} Z", _shade(base, 0.25), 1.0), *screws, _sheen(a + 16, cy - 7, span - 32)]
    if style == "knob":
        r = 30 * k
        return [f'<circle cx="{204:.1f}" cy="{cy + 5:.1f}" r="{r + 4:.1f}" fill="{_shade(DOOR, 0.15)}" stroke="none"/>', f'<circle cx="200" cy="{cy:.1f}" r="{r + 6:.1f}" fill="{_shade(base, 0.08)}" stroke="#2b3440" stroke-width="1.6"/>', f'<circle cx="200" cy="{cy:.1f}" r="{r:.1f}" fill="{paint}" stroke="#2b3440" stroke-width="{LW}"/>', f'<circle cx="200" cy="{cy:.1f}" r="{r * 0.6:.1f}" fill="none" stroke="{_shade(base, 0.2)}" stroke-width="1.2"/>', f'<circle cx="200" cy="{cy:.1f}" r="3" fill="{_shade(base, 0.3)}" stroke="none"/>', _line(f"M{200 - r * 0.6:.1f},{cy - r * 0.45:.1f} Q{200 - r * 0.2:.1f},{cy - r * 0.8:.1f} {200 + r * 0.2:.1f},{cy - r * 0.75:.1f}", 3, ' stroke-opacity=".8"', WHITE)]
    if style == "ring":
        r = 32 * k
        rosette = cy - r - 4
        return [f'<circle cx="203" cy="{cy + 4:.1f}" r="{r:.1f}" fill="none" stroke="{_shade(DOOR, 0.15)}" stroke-width="10"/>', f'<circle cx="200" cy="{rosette:.1f}" r="{14 * k:.1f}" fill="{paint}" stroke="#2b3440" stroke-width="1.6"/>', f'<circle cx="200" cy="{cy:.1f}" r="{r + 6:.1f}" fill="none" stroke="#2b3440" stroke-width="1.6"/>', f'<circle cx="200" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{paint}" stroke-width="10"/>', f'<circle cx="200" cy="{cy:.1f}" r="{r - 6:.1f}" fill="none" stroke="#2b3440" stroke-width="1.6"/>', f'<circle cx="200" cy="{rosette:.1f}" r="3" fill="{_shade(base, 0.4)}" stroke="none"/>', _line(f"M{200 - r * 0.7:.1f},{cy - r * 0.5:.1f} Q{200 - r * 0.3:.1f},{cy - r * 0.95:.1f} {200 + r * 0.2:.1f},{cy - r * 0.95:.1f}", 2.5, ' stroke-opacity=".8"', WHITE)]
    # edge: a lip over the door's top edge and a plate down its face
    top = 96
    return [_rect(a + 4, top + 34, span, 8, _shade(DOOR, 0.15), 0), _rect(a, top - 10, span, 16, paint, LW_DETAIL, rx=3), _rect(a + 6, top + 6, span - 12, 28, paint, LW_DETAIL, rx=2), *(f'<circle cx="{x:.1f}" cy="{top + 20:.1f}" r="3" fill="{_shade(base, 0.45)}" stroke="none"/>' for x in (a + 18, b - 18)), _sheen(a + 10, top - 5, span - 20)]


def cabinet_pull(paint: str, fill: Fill, label: str | None, style: str = "bar", size: str = "medium", backplate: str = "no") -> list[str]:
    """One pull on a cabinet door: a ``bar`` on two posts, a ``cup`` (bin) pull, a ``knob``, a
    drop ``ring`` or an ``edge`` lip over the door's top; ``size`` sets its length or diameter;
    a ``backplate`` (``class="backplate"``) behind it when it has one."""
    _valid("cabinet_pull", style=style, size=size, backplate=backplate)
    span = {"small": 112, "medium": 176, "large": 248}[size]
    k = {"small": 0.75, "medium": 1.0, "large": 1.3}[size]
    cy = 200
    out = [_rect(40, 96, 320, 220, DOOR, LW, rx=4), _rect(58, 114, 284, 184, _shade(DOOR, 0.04), LW_DETAIL, rx=2)]
    if backplate == "yes":
        if style in ("knob", "ring"):
            h = (92 if style == "knob" else 150) * k
            plate = _rect(200 - 46 * k, (cy - 46 * k) if style == "knob" else (cy - 32 * k - 30 * k), 92 * k, h, _shade(fill.base, 0.12), LW_DETAIL, rx=12, cls="backplate")
        elif style == "edge":
            plate = _rect(200 - span / 2 - 14, 104, span + 28, 44, _shade(fill.base, 0.12), LW_DETAIL, rx=4, cls="backplate")
        else:
            plate = _rect(200 - span / 2 - 22, cy - 28, span + 44, 56, _shade(fill.base, 0.12), LW_DETAIL, rx=10, cls="backplate")
        out.append(plate)
    return out + _pull(style, span, k, cy, paint, fill.base)


def _spout(spout: str, sx: float, sy: float, paint: str) -> list[str]:
    """The spout from (``sx``, ``sy``) to the right, and the water a waterfall pours."""
    if spout == "arc":
        d = f"M{sx:.1f},{sy:.1f} C{sx:.1f},{sy - 84:.1f} {sx + 96:.1f},{sy - 84:.1f} {sx + 96:.1f},{sy:.1f}"
        return [_line(d, 20), _line(d, 14, stroke=paint), _rect(sx + 87, sy, 18, 14, paint, LW_DETAIL, rx=3)]
    if spout == "straight":
        return [_rect(sx, sy - 8, 104, 16, paint, LW_DETAIL, rx=6), _rect(sx + 86, sy + 8, 16, 10, paint, LW_DETAIL, rx=2)]
    return [_path(f"M{sx:.1f},{sy - 8:.1f} L{sx + 100:.1f},{sy - 4:.1f} L{sx + 100:.1f},{sy + 8:.1f} L{sx:.1f},{sy + 8:.1f} Z", paint, LW_DETAIL), _rect(sx + 72, sy + 8, 26, 284 - sy, GLASS, 1.0, cls="water").replace("<rect", '<rect fill-opacity=".75"', 1)]


def _handle(cx: float, base: float, paint: str, lever: bool) -> list[str]:
    """One handle standing on ``base``: a lever, or a cross on its own stem."""
    if lever:
        return _group("handle", [_rect(cx - 12, base - 20, 24, 20, paint, LW_DETAIL, rx=3), _rect(cx - 58, base - 30, 50, 11, paint, LW_DETAIL, rx=5)])
    return _group("handle", [_rect(cx - 16, base - 10, 32, 10, paint, LW_DETAIL, rx=3), _rect(cx - 7, base - 34, 14, 26, paint, LW_DETAIL), _rect(cx - 24, base - 42, 48, 10, paint, LW_DETAIL, rx=4)])


def sink_faucet(paint: str, fill: Fill, label: str | None, handles: str = "1", spout: str = "arc", mount: str = "deck") -> list[str]:
    """A basin tap: on a worktop (``deck``: a column on its base) or on the ``wall`` over a
    wall-hung basin; an ``arc``, ``straight`` or ``waterfall`` spout; exactly ``handles``
    handles (``class="handle"``): one lever, or two cross handles either side."""
    _valid("sink_faucet", handles=handles, spout=spout, mount=mount)
    cx = 200
    if mount == "deck":
        sy = {"arc": 176, "straight": 190, "waterfall": 204}[spout]
        out = [_rect(40, 316, 320, 36, DOOR, LW_DETAIL), _slab(32, 300, 336, 16, COUNTER), _rect(cx - 30, 288, 60, 12, paint, LW_DETAIL, rx=4), _rect(cx - 14, sy, 28, 288 - sy, paint, LW_DETAIL, rx=3)]
        out += _spout(spout, cx, sy, paint)
        if handles == "1":
            out += _handle(cx - 2, sy + 52, paint, lever=True)
        else:
            out += [*_handle(cx - 86, 300, paint, lever=False), *_handle(cx + 150, 300, paint, lever=False)]
        return out
    sy = 168
    out = [_path("M72,284 L328,284 L308,340 L92,340 Z", PORCELAIN), _line("M84,292 L316,292", 1.2, stroke="#9aa0a6"), _rect(cx - 70, 120, 140, 72, paint, LW_DETAIL, rx=8)]
    out += _spout(spout, cx + 30, sy, paint)
    if handles == "1":
        out += _handle(cx + 12, 150, paint, lever=True)
    else:
        out += [*_handle(cx - 40, 150, paint, lever=False), *_handle(cx + 20, 150, paint, lever=False)]
    return out


def _toilet() -> list[str]:
    """A toilet under an over-the-toilet unit, so the form reads."""
    return [_rect(150, 214, 100, 60, PORCELAIN, LW_DETAIL, rx=6), _path("M132,274 L268,274 L256,296 Q200,322 144,296 Z", PORCELAIN, LW_DETAIL), _rect(176, 304, 48, FLOOR - 304, PORCELAIN, LW_DETAIL)]


def bath_storage(paint: str, fill: Fill, label: str | None, form: str = "tower", shelves: str = "3", cabinet: str = "none") -> list[str]:
    """A bathroom unit: a narrow ``tower`` on feet, an ``over_toilet`` unit on two tall legs, or a
    ``wall`` unit; exactly ``shelves`` open shelves (``class="shelf"``) of towels and bottles,
    under a cabinet with a ``door`` (``class="door"``) or a ``mirror`` door (``class="mirror"``)."""
    _valid("bath_storage", form=form, shelves=shelves, cabinet=cabinet)
    n = int(shelves)
    x0, w, top, bottom = {"tower": (136, 128, 52, FLOOR - 16), "over_toilet": (80, 240, 48, 198), "wall": (110, 180, 60, 252)}[form]
    out: list[str] = []
    if form == "over_toilet":
        out += _toilet()
        out += [_rect(x0 + 4, bottom, 12, FLOOR - bottom, paint, LW_DETAIL), _rect(x0 + w - 16, bottom, 12, FLOOR - bottom, paint, LW_DETAIL)]
    out += [_rect(x0, top, w, bottom - top, paint), _slab(x0 - 6, top - 10, w + 12, 10, paint)]
    cab = 0 if cabinet == "none" else round((bottom - top) * 0.38)
    if cabinet == "door":
        out += [_rect(x0 + 6, top + 6, w - 12, cab - 8, paint, LW_DETAIL, rx=2, cls="door"), _knob(x0 + w - 18, top + cab / 2)]
    elif cabinet == "mirror":
        out += [_rect(x0 + 6, top + 6, w - 12, cab - 8, paint, LW_DETAIL, rx=2), _rect(x0 + 12, top + 12, w - 24, cab - 20, GLASS, 1.0, cls="mirror"), _line(f"M{x0 + 22},{top + cab - 22} L{x0 + 46},{top + 22}", 2, ' stroke-opacity=".8"', WHITE)]
    a, b = top + cab + 4, bottom - 6
    out.append(_rect(x0 + 6, a, w - 12, b - a, _shade(fill.base, 0.1), LW_DETAIL))
    pitch = (b - a) / n
    for i in range(n):
        y = a + pitch * (i + 1) - 6
        items = range(int(x0 + 24), int(x0 + w - 16), 30)
        for j, ix in enumerate(items):
            if j % 2 == 0 or pitch < 48:
                r = min(13.0, pitch * 0.3)
                out.append(f'<circle cx="{ix}" cy="{y - r:.1f}" r="{r:.1f}" fill="{BOOKS[(i + j) % len(BOOKS)]}" stroke="#2b3440" stroke-width="1"/>')
            else:
                out += _bottle(ix, y, min(46.0, pitch - 12), BOOKS[(i + j + 2) % len(BOOKS)])
        out.append(_rect(x0 + 6, y, w - 12, 6, paint, LW_DETAIL, cls="shelf"))
    if form == "tower":
        out += _legs([x0 + 14, x0 + w - 14], bottom, FLOOR, paint, 12)
    return out


def canister(paint: str, fill: Fill, label: str | None, count: str = "3", body: str = "ceramic", lid: str = "flat") -> list[str]:
    """Exactly ``count`` kitchen canisters (``class="canister"``) in a row, tallest first: a
    glazed ``ceramic`` body, ``glass`` showing what it holds (``class="contents"``) or ribbed
    ``metal``; a ``flat`` lid, a ``dome`` with a knob or a ``wood`` lid."""
    _valid("canister", count=count, body=body, lid=lid)
    n = int(count)
    cw, gap = 72, 14
    x = 200 - (n * cw + (n - 1) * gap) / 2
    out: list[str] = []
    for i, h in enumerate((176, 148, 124, 104)[:n]):
        top = FLOOR - h
        if body == "glass":
            out.append(_rect(x + 6, top + h * 0.35, cw - 12, h * 0.65 - 6, BOOKS[i % len(BOOKS)], 1.0, rx=4, cls="contents"))
            out.append(_cls(_rect(x, top, cw, h, paint, LW, rx=8), "canister").replace("<rect", '<rect fill-opacity=".3"', 1))
        else:
            out.append(_cls(_rect(x, top, cw, h, paint, LW, rx=4 if body == "metal" else 10), "canister"))
            if body == "metal":
                out += [_line(f"M{x + 2:.1f},{top + h * t:.1f} L{x + cw - 2:.1f},{top + h * t:.1f}", 1.4, stroke=_shade(fill.base, 0.3)) for t in (0.2, 0.8)]
        out.append(_line(f"M{x + 12:.1f},{top + 18:.1f} L{x + 12:.1f},{top + h - 18:.1f}", 4, ' stroke-opacity=".7"', WHITE))
        if lid == "flat":
            out.append(_rect(x - 4, top - 12, cw + 8, 12, paint, LW_DETAIL, rx=3))
        elif lid == "dome":
            out += [_path(f"M{x - 3:.1f},{top:.1f} L{x + cw + 3:.1f},{top:.1f} Q{x + cw / 2:.1f},{top - 40:.1f} {x - 3:.1f},{top:.1f} Z", paint, LW_DETAIL), f'<circle cx="{x + cw / 2:.1f}" cy="{top - 22:.1f}" r="7" fill="{paint}" stroke="#2b3440" stroke-width="1.6"/>']
        else:
            out += [_rect(x - 4, top - 14, cw + 8, 14, WOOD_LID, LW_DETAIL, rx=3), _grain(x - 4, top - 14, cw + 8, 14, WOOD_LID)]
        x += cw + gap
    return out


register(
    {"tile": tile, "vanity": vanity, "cabinet_pull": cabinet_pull, "sink_faucet": sink_faucet,
     "bath_storage": bath_storage, "canister": canister},
)  # fmt: skip
